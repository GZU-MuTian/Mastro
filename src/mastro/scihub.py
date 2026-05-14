"""Sci-Hub PDF download client.

Support dynamic mirror discovery, multiple extraction strategies,
CAPTCHA detection, and robust error handling.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class SciHubError(Exception):
    """Base exception for all Sci-Hub related errors."""


class NoMirrorAvailable(SciHubError):
    """No working Sci-Hub mirror could be found."""


class CaptchaError(SciHubError):
    """Sci-Hub returned a CAPTCHA page.

    Attributes
    ----------
    captcha_url:
        URL that triggered the CAPTCHA.
    """

    def __init__(self, url: str) -> None:
        self.captcha_url = url
        super().__init__(f"CAPTCHA required for {url}")


class PdfNotFoundError(SciHubError):
    """Could not locate a PDF link on the Sci-Hub page."""


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------


class SciHubClient:
    """Client for downloading PDFs from Sci-Hub mirrors.

    Parameters
    ----------
    mirrors:
        List of Sci-Hub mirror base URLs. If ``None``, mirrors are
        discovered dynamically from the ``sci-hub.now.sh`` API.
    timeout:
        Default request timeout in seconds.
    max_mirror_tries:
        Maximum number of mirrors to attempt before giving up.
    """

    # Known fallback mirrors used when dynamic discovery fails.
    _STATIC_MIRRORS = [
        "https://sci-hub.ru",
        "https://sci-hub.se",
        "https://sci-hub.st",
    ]

    _HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    }

    _MIRROR_API = "https://sci-hub.now.sh/"

    def __init__(
        self,
        mirrors: Optional[list[str]] = None,
        timeout: int = 60,
        max_mirror_tries: int = 5,
    ) -> None:
        self._timeout = timeout
        self._max_mirror_tries = max(max_mirror_tries, 1)

        self._session = requests.Session()
        self._session.headers.update(self._HEADERS)

        # Resolve mirrors: explicit > dynamic > static fallback
        self._mirrors: list[str] = []
        if mirrors:
            self._mirrors = list(mirrors)
        else:
            self._mirrors = self._discover_mirrors()
            if not self._mirrors:
                logger.warning(
                    "Dynamic mirror discovery failed, using static fallbacks"
                )
                self._mirrors = list(self._STATIC_MIRRORS)

        logger.info("Sci-Hub mirrors: %s", self._mirrors)

    # ------------------------------------------------------------------
    # Mirror discovery
    # ------------------------------------------------------------------

    @staticmethod
    def _discover_mirrors() -> list[str]:
        """Discover available Sci-Hub mirrors from the now.sh API.

        Returns
        -------
        list[str]
            Sorted mirror URLs (fastest-likely first, based on API order).
        """
        try:
            resp = requests.get(
                SciHubClient._MIRROR_API,
                timeout=15,
                headers=SciHubClient._HEADERS,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.content, "html.parser")
            mirrors: list[str] = []
            for a_tag in soup.find_all("a", href=True):
                href = a_tag["href"].strip()
                if "sci-hub." in href:
                    mirrors.append(href.rstrip("/"))
            return mirrors
        except Exception:
            logger.debug("Mirror discovery failed", exc_info=True)
            return []

    def _is_mirror_alive(self, mirror: str) -> bool:
        """Quick health check: HEAD request to verify mirror is reachable."""
        try:
            resp = self._session.head(
                mirror, timeout=10, allow_redirects=True
            )
            return resp.status_code < 500
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Core download logic
    # ------------------------------------------------------------------

    def download(
        self,
        doi: str,
        output_path: Path,
        *,
        timeout: Optional[int] = None,
    ) -> str:
        """Download a PDF from Sci-Hub by DOI.

        Parameters
        ----------
        doi:
            DOI of the paper (e.g. ``"10.1038/nature14539"``).
        output_path:
            File path where the PDF should be saved.
        timeout:
            Per-request timeout. Falls back to instance default.

        Returns
        -------
        str
            ``output_path`` as string on success.

        Raises
        ------
        NoMirrorAvailable
            No working Sci-Hub mirror could be found.
        PdfNotFoundError
            Could not locate a PDF on the Sci-Hub page.
        CaptchaError
            CAPTCHA was triggered and needs manual intervention.
        requests.RequestException
            Network or HTTP errors.
        """
        tout = timeout or self._timeout

        tried = 0
        last_error: Optional[Exception] = None

        for mirror in self._mirrors[: self._max_mirror_tries]:
            tried += 1

            if not self._is_mirror_alive(mirror):
                logger.debug("Mirror %s is unreachable", mirror)
                continue

            try:
                self._download_one(mirror, doi, output_path, tout)
                size_kb = output_path.stat().st_size / 1024
                logger.info(
                    "Downloaded %s (%.1f KB) via %s", doi, size_kb, mirror
                )
                return str(output_path)

            except CaptchaError:
                # CAPTCHA won't resolve by switching mirrors immediately;
                # re-raise so the caller can wait and retry.
                raise

            except (PdfNotFoundError, requests.RequestException) as exc:
                logger.debug("Mirror %s failed: %s", mirror, exc)
                last_error = exc
                continue

        if last_error:
            raise NoMirrorAvailable(
                f"Failed after {tried} mirror(s). "
                f"Last error: {last_error}"
            ) from last_error
        raise NoMirrorAvailable(
            f"No reachable Sci-Hub mirror found (tried {tried})."
        )

    def _download_one(
        self,
        mirror: str,
        doi: str,
        output_path: Path,
        timeout: int,
    ) -> None:
        """Attempt download from a single mirror."""
        page_url = f"{mirror}/{doi}"
        logger.debug("Trying %s", page_url)

        resp = self._session.get(
            page_url, timeout=timeout, allow_redirects=True
        )

        if resp.status_code == 403:
            raise CaptchaError(page_url)
        resp.raise_for_status()

        # Detect CAPTCHA by page content
        if self._is_captcha(resp):
            raise CaptchaError(page_url)

        # Extract PDF URL
        pdf_url = self._extract_pdf_url(resp.text, mirror)
        if not pdf_url:
            raise PdfNotFoundError(f"No PDF link found on {page_url}")

        logger.debug("PDF URL: %s", pdf_url)

        # Download PDF
        pdf_resp = self._session.get(
            pdf_url, timeout=timeout, stream=True
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
        else:
            raise PdfNotFoundError(
                f"Response from {pdf_url} is not a PDF "
                f"(content-type={content_type})"
            )

    # ------------------------------------------------------------------
    # PDF URL extraction
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_pdf_url(html: str, base_url: str) -> Optional[str]:
        """Extract the direct PDF URL from a Sci-Hub page.

        Tries multiple strategies, from most to least reliable.
        """
        soup = BeautifulSoup(html, "html.parser")

        # Strategy 1: iframe#pdf (most common)
        iframe = soup.find("iframe", id="pdf") or soup.find("iframe")
        if iframe and iframe.get("src"):
            src = iframe["src"]
            if "#" in src:
                src = src.rsplit("#", 1)[0]
            return SciHubClient._resolve_url(src, base_url)

        # Strategy 2: embed tag
        embed = soup.find("embed")
        if embed and embed.get("src"):
            return SciHubClient._resolve_url(embed["src"], base_url)

        # Strategy 3: citation_pdf_url meta tag
        for meta_name in ("citation_pdf_url",):
            meta = soup.find("meta", attrs={"name": meta_name})
            if meta and meta.get("content"):
                return SciHubClient._resolve_url(meta["content"], base_url)

        # Strategy 4: any link ending with .pdf
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            if href.endswith(".pdf") or "/pdf/" in href:
                return SciHubClient._resolve_url(href, base_url)

        return None

    @staticmethod
    def _resolve_url(url: str, base_url: str) -> str:
        """Resolve a possibly relative URL against the base mirror URL."""
        url = url.strip()
        if url.startswith("//"):
            return "https:" + url
        if url.startswith("/"):
            # Relative to domain root
            from urllib.parse import urljoin

            return urljoin(base_url, url)
        return url

    # ------------------------------------------------------------------
    # CAPTCHA detection
    # ------------------------------------------------------------------

    @staticmethod
    def _is_captcha(resp: requests.Response) -> bool:
        """Heuristics to detect whether the response is a CAPTCHA page."""
        text = resp.text[:2000].lower()
        captcha_indicators = [
            "captcha",
            "recaptcha",
            "g-recaptcha",
            "please verify",
            "are you a robot",
            "cloudflare",
        ]
        return any(ind in text for ind in captcha_indicators)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> SciHubClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()
