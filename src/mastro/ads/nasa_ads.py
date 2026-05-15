"""ADS API client for search, export, and PDF download."""

from __future__ import annotations

import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import unquote

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ADS endpoints
_API_BASE = "https://api.adsabs.harvard.edu/v1"
_GATEWAY = "https://ui.adsabs.harvard.edu/link_gateway/{}/{}"

# PDF endpoint fallback order
_PDF_ENDPOINTS = ["EPRINT_PDF", "PUB_PDF", "ARTICLE"]

# Patterns for extracting bibcodes from ADS URLs
_BIBCODE_PATTERNS = [
    re.compile(r"#abs/([A-Za-z0-9.+&;:\-_]+)"),
    re.compile(r"/abs/([A-Za-z0-9.+&;:\-_]+)"),
    re.compile(r"/link_gateway/([A-Za-z0-9.+&;:\-_]+)/"),
]

# Default fields returned by search()
_DEFAULT_FIELDS = (
    "bibcode,title,author,first_author,year,pub,pubdate,"
    "citation_count,doctype,property,doi,identifier"
)

EXPORT_FORMATS: Dict[str, str] = {
    "bibtex": "BibTeX",
    "bibtexabs": "BibTeX ABS (with abstract)",
    "ads": "ADS custom format",
    "endnote": "EndNote",
    "procite": "ProCite",
    "ris": "RIS",
    "refworks": "RefWorks",
    "rss": "RSS",
    "medlars": "MEDLARS",
    "dcxml": "Dublin Core XML",
    "refxml": "REF-XML",
    "refabsxml": "REFABS-XML",
    "aastex": "AASTeX",
    "icarus": "Icarus",
    "mnras": "MNRAS",
    "soph": "Solar Physics",
    "votable": "VOTable",
    "custom": "Custom format",
}


def extract_bibcode(url: str) -> Optional[str]:
    """Extract an ADS bibcode from a URL, if present."""
    if not url:
        return None

    decoded = unquote(url)
    for pattern in _BIBCODE_PATTERNS:
        match = pattern.search(decoded)
        if match:
            return match.group(1).replace("&amp;", "&").replace("&#177;", "\u00b1")

    return None


class ADSClient:
    """REST client for NASA ADS.

    Parameters
    ----------
    api_key:
        ADS API token. Falls back to the ``ADS_API_TOKEN`` env-var.
    base_url:
        Override the ADS API base URL.
    timeout:
        Default request timeout in seconds.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = _API_BASE,
        timeout: int = 60,
    ) -> None:
        self.api_key = api_key or os.getenv("ADS_API_TOKEN")
        if not self.api_key:
            raise ValueError(
                "ADS API key not found. Set the ADS_API_TOKEN environment variable "
                "or pass api_key explicitly."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        )

        # Separate session for PDF downloads (publishers may reject API headers)
        self._pdf_session = requests.Session()
        self._pdf_session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/pdf,text/html,*/*",
            }
        )

    def search(
        self,
        q: str,
        *,
        fl: str = _DEFAULT_FIELDS,
        rows: int = 10,
        start: int = 0,
        sort: Optional[str] = None,
        fq: Optional[Union[str, List[str]]] = None,
        hl: bool = False,
        hl_fl: str = "body",
        hl_snippets: int = 2,
        hl_fragsize: int = 100,
    ) -> Dict[str, Any]:
        """Execute an ADS search query and return the parsed JSON response."""
        params: Dict[str, Any] = {
            "q": q,
            "fl": fl,
            "rows": rows,
            "start": start,
        }
        if sort:
            params["sort"] = sort
        if fq:
            params["fq"] = fq if isinstance(fq, list) else [fq]
        if hl:
            params.update(
                {
                    "hl": "true",
                    "hl.fl": hl_fl,
                    "hl.snippets": hl_snippets,
                    "hl.fragsize": hl_fragsize,
                }
            )

        url = f"{self.base_url}/search/query"
        logger.info("ADS search: q=%r  rows=%d  start=%d", q, rows, start)

        resp = self._session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        data = resp.json()

        num = data.get("response", {}).get("numFound", 0)
        logger.info("  -> %d results found", num)

        return data

    def export(
        self,
        bibcodes: List[str],
        fmt: str = "bibtex",
        *,
        sort: Optional[str] = None,
        custom_format: Optional[str] = None,
    ) -> str:
        """Export metadata for *bibcodes* in the given *fmt*."""
        if fmt not in EXPORT_FORMATS:
            supported = ", ".join(EXPORT_FORMATS)
            raise ValueError(
                f"Unknown format {fmt!r}. Supported: {supported}"
            )

        url = f"{self.base_url}/export/{fmt}"
        payload: Dict[str, Any] = {"bibcode": bibcodes}
        if sort:
            payload["sort"] = sort
        if custom_format:
            payload["format"] = custom_format

        logger.info(
            "ADS export: %d bibcodes -> %s", len(bibcodes), EXPORT_FORMATS[fmt]
        )

        # Single bibcode can use GET; multi-bibcode must use POST
        if len(bibcodes) == 1 and not sort and not custom_format:
            resp = self._session.get(
                f"{url}/{bibcodes[0]}", timeout=self.timeout
            )
        else:
            resp = self._session.post(
                url, data=json.dumps(payload), timeout=self.timeout
            )
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        if "json" in content_type:
            data = resp.json()
            return data.get("export", resp.text)

        return resp.text

    def _fetch_pdf(
        self,
        bibcode: str,
        *,
        save_dir: Path,
        timeout: int,
    ) -> str:
        """Fetch a single PDF via the three-tier ADS gateway fallback.

        Returns the path to the saved PDF file.
        Raises RuntimeError on failure.
        """
        filename = re.sub(r"[^\w.\-]", "_", bibcode)
        filepath = save_dir / f"{filename}.pdf"
        last_error = ""

        for endpoint in _PDF_ENDPOINTS:
            pdf_url = _GATEWAY.format(bibcode, endpoint)
            logger.info("Trying %s -> %s", pdf_url, filepath)

            try:
                resp = self._pdf_session.get(
                    pdf_url,
                    timeout=timeout,
                    stream=True,
                    allow_redirects=True,
                )
                resp.raise_for_status()
            except requests.RequestException as exc:
                last_error = f"{endpoint}: {exc}"
                logger.warning("  %s failed - %s", endpoint, exc)
                continue

            content_type = resp.headers.get("content-type", "").lower()

            if "application/pdf" in content_type:
                with open(filepath, "wb") as fobj:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            fobj.write(chunk)

                size_kb = filepath.stat().st_size / 1024
                logger.info(
                    "Downloaded %s via %s (%.1f KB)", bibcode, endpoint, size_kb
                )
                return str(filepath)

            # Some publishers return PDF with wrong content-type, check magic bytes
            if "text/html" not in content_type:
                first_chunk = next(resp.iter_content(chunk_size=8192), b"")
                if first_chunk.startswith(b"%PDF"):
                    with open(filepath, "wb") as fobj:
                        fobj.write(first_chunk)
                        for chunk in resp.iter_content(chunk_size=8192):
                            if chunk:
                                fobj.write(chunk)

                    size_kb = filepath.stat().st_size / 1024
                    logger.info(
                        "Downloaded %s via %s (%.1f KB, fixed content-type)",
                        bibcode,
                        endpoint,
                        size_kb,
                    )
                    return str(filepath)

            last_error = (
                f"{endpoint}: not a PDF (content-type: {content_type})"
            )
            logger.warning("  %s - %s", endpoint, last_error)
            continue

        raise RuntimeError(f"All endpoints failed ({bibcode}): {last_error}")

    def fetch(
        self,
        bibcodes: List[str],
        *,
        output_dir: Union[str, Path],
        timeout: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Fetch PDFs for *bibcodes* and return per-item results.

        Each element in *bibcodes* may be a bare bibcode or an ADS URL
        containing one.  Returns a list of dicts with ``bibcode``,
        ``success``, and ``message`` keys.
        """
        save_dir = Path(output_dir)
        if not save_dir.exists():
            save_dir.mkdir(parents=True, exist_ok=True)

        tout = timeout or self.timeout
        results: List[Dict[str, Any]] = []

        for item in bibcodes:
            bibcode = extract_bibcode(item) or item
            try:
                path = self._fetch_pdf(
                    bibcode, save_dir=save_dir, timeout=tout
                )
                results.append({"bibcode": bibcode, "success": True, "message": path})
            except Exception as exc:
                logger.error("Failed %s: %s", bibcode, exc)
                results.append({"bibcode": bibcode, "success": False, "message": str(exc)})

        return results

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()
        self._pdf_session.close()

    def __enter__(self) -> ADSClient:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
