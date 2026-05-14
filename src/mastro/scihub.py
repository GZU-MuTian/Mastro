"""Sci-Hub PDF download client."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class SciHubClient:
    """Client for downloading PDFs from Sci-Hub mirrors.

    Parameters
    ----------
    mirrors:
        List of Sci-Hub mirror URLs to try. Defaults to common mirrors.
    timeout:
        Default request timeout in seconds.
    """

    DEFAULT_MIRRORS = [
        "https://sci-hub.ru",
        "https://sci-hub.box",
        "https://sci-hub.st/",
    ]

    def __init__(
        self,
        mirrors: Optional[list[str]] = None,
        timeout: int = 60,
    ) -> None:
        self.mirrors = mirrors or self.DEFAULT_MIRRORS
        self.timeout = timeout

        self._session = requests.Session()
        self._session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Accept": "application/pdf,text/html,*/*",
            }
        )

    def download(
        self,
        doi: str,
        output_path: Path,
        *,
        timeout: Optional[int] = None,
    ) -> Optional[str]:
        """Try to download PDF from Sci-Hub mirrors.

        Parameters
        ----------
        doi:
            DOI of the paper to download.
        output_path:
            Path where the PDF should be saved.
        timeout:
            Request timeout in seconds. Falls back to instance default.

        Returns
        -------
        str or None
            Path to the saved file on success, None on failure.
        """
        tout = timeout or self.timeout

        for mirror in self.mirrors:
            try:
                page_url = f"{mirror}/{doi}"
                logger.info("Trying Sci-Hub: %s", page_url)

                resp = self._session.get(
                    page_url, timeout=tout, allow_redirects=True
                )

                if resp.status_code != 200:
                    logger.debug("Sci-Hub %s returned %d", mirror, resp.status_code)
                    continue

                # Sci-Hub puts PDF URL in citation_pdf_url meta tag
                pdf_match = re.search(
                    r'<meta\s+name=["\']citation_pdf_url["\']\s+content=["\']([^"\']+)["\']',
                    resp.text,
                )
                if not pdf_match:
                    # Fallback: look for iframe or embed
                    pdf_match = re.search(
                        r'<(?:iframe|embed)[^>]+src=["\']([^"\']+)["\']',
                        resp.text,
                    )

                if not pdf_match:
                    logger.debug("No PDF link found on Sci-Hub page")
                    continue

                pdf_url = pdf_match.group(1)

                # Handle relative URLs
                if pdf_url.startswith("//"):
                    pdf_url = "https:" + pdf_url
                elif pdf_url.startswith("/"):
                    pdf_url = mirror + pdf_url

                # Download the PDF
                logger.info("Downloading from Sci-Hub: %s", pdf_url)
                pdf_resp = self._session.get(
                    pdf_url, timeout=tout, stream=True
                )
                pdf_resp.raise_for_status()

                content_type = pdf_resp.headers.get("content-type", "").lower()
                first_chunk = next(pdf_resp.iter_content(chunk_size=8192), b"")

                if (
                    "application/pdf" in content_type
                    or first_chunk.startswith(b"%PDF")
                ):
                    with open(output_path, "wb") as fobj:
                        fobj.write(first_chunk)
                        for chunk in pdf_resp.iter_content(chunk_size=8192):
                            if chunk:
                                fobj.write(chunk)

                    size_kb = output_path.stat().st_size / 1024
                    logger.info(
                        "Downloaded %s via Sci-Hub (%.1f KB)", doi, size_kb
                    )
                    return str(output_path)

            except Exception as exc:
                logger.debug("Sci-Hub %s failed: %s", mirror, exc)
                continue

        return None

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> SciHubClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
