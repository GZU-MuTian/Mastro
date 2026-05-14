"""Tests for scihub.py — all HTTP calls are mocked."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from mastro.scihub import (
    CaptchaError,
    NoMirrorAvailable,
    PdfNotFoundError,
    SciHubClient,
    SciHubError,
)


# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class TestExceptions:
    def test_scihub_error_is_base(self):
        assert issubclass(CaptchaError, SciHubError)
        assert issubclass(NoMirrorAvailable, SciHubError)
        assert issubclass(PdfNotFoundError, SciHubError)

    def test_captcha_error_stores_url(self):
        err = CaptchaError("https://sci-hub.ru/10.1234/test")
        assert err.captcha_url == "https://sci-hub.ru/10.1234/test"
        assert "CAPTCHA" in str(err)

    def test_pdf_not_found(self):
        err = PdfNotFoundError("no link")
        assert "no link" in str(err)

    def test_no_mirror_available(self):
        err = NoMirrorAvailable("all failed")
        assert "all failed" in str(err)


# ---------------------------------------------------------------------------
# _resolve_url
# ---------------------------------------------------------------------------


class TestResolveURL:
    """Tests for the _resolve_url static helper."""

    def test_absolute_url_passthrough(self):
        url = "https://example.com/path/file.pdf"
        assert SciHubClient._resolve_url(url, "https://sci-hub.ru") == url

    def test_protocol_relative_url(self):
        result = SciHubClient._resolve_url(
            "//example.com/pdf/123.pdf", "https://sci-hub.ru"
        )
        assert result == "https://example.com/pdf/123.pdf"

    def test_relative_url(self):
        result = SciHubClient._resolve_url(
            "/downloads/paper.pdf", "https://sci-hub.ru"
        )
        assert result == "https://sci-hub.ru/downloads/paper.pdf"

    def test_url_with_fragment_appended_to_base(self):
        result = SciHubClient._resolve_url(
            "/abc", "https://sci-hub.ru/sub/"
        )
        assert result == "https://sci-hub.ru/abc"


# ---------------------------------------------------------------------------
# _extract_pdf_url
# ---------------------------------------------------------------------------


class TestExtractPDFURL:
    """Tests for _extract_pdf_url static method with HTML snippets."""

    def test_iframe_with_pdf_id(self):
        html = '<html><iframe id="pdf" src="//example.com/paper.pdf#nav"></iframe></html>'
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result == "https://example.com/paper.pdf"

    def test_iframe_without_id(self):
        html = '<html><iframe src="https://other.com/doc.pdf"></iframe></html>'
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result == "https://other.com/doc.pdf"

    def test_embed_tag(self):
        html = '<html><embed src="/dl/file.pdf"></embed></html>'
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result == "https://sci-hub.ru/dl/file.pdf"

    def test_citation_pdf_url_meta(self):
        html = '<html><meta name="citation_pdf_url" content="https://journal.com/paper.pdf"></html>'
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result == "https://journal.com/paper.pdf"

    def test_meta_without_content_ignored(self):
        html = '<html><meta name="citation_pdf_url"></html>'
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result is None

    def test_pdf_link_fallback(self):
        html = '<html><a href="https://cdn.org/10.1234/article.pdf">PDF</a></html>'
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result == "https://cdn.org/10.1234/article.pdf"

    def test_no_pdf_link_returns_none(self):
        html = "<html><body>no download here</body></html>"
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result is None

    def test_strategy_priority_iframe_over_embed(self):
        """iframe should be preferred even if embed also exists."""
        html = (
            '<html>'
            '<iframe id="pdf" src="//cdn.org/real.pdf"></iframe>'
            '<embed src="/wrong.pdf"></embed>'
            "</html>"
        )
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result == "https://cdn.org/real.pdf"

    def test_strategy_iframe_over_meta(self):
        """iframe should be preferred over citation_pdf_url meta."""
        html = (
            '<html>'
            '<iframe src="//cdn.org/if.pdf"></iframe>'
            '<meta name="citation_pdf_url" content="https://j.org/meta.pdf">'
            "</html>"
        )
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result == "https://cdn.org/if.pdf"

    def test_iframe_with_fragment_removed(self):
        html = '<iframe id="pdf" src="https://moscow.sci-hub.io/file.pdf#view=FitH"></iframe>'
        result = SciHubClient._extract_pdf_url(html, "https://sci-hub.ru")
        assert result.startswith("https://moscow.sci-hub.io/file.pdf")
        assert "#" not in result


# ---------------------------------------------------------------------------
# _is_captcha
# ---------------------------------------------------------------------------


class TestIsCaptcha:
    """Tests for CAPTCHA detection heuristics."""

    def test_cloudflare_captcha(self):
        resp = MagicMock()
        resp.text = "<html><body>Cloudflare captcha challenge</body></html>"
        assert SciHubClient._is_captcha(resp) is True

    def test_recaptcha(self):
        resp = MagicMock()
        resp.text = '<html><div class="g-recaptcha"></div></html>'
        assert SciHubClient._is_captcha(resp) is True

    def test_please_verify(self):
        resp = MagicMock()
        resp.text = "<html>Please verify you are human</html>"
        assert SciHubClient._is_captcha(resp) is True

    def test_normal_scihub_page(self):
        resp = MagicMock()
        resp.text = (
            '<html><title>Sci-Hub</title>'
            '<iframe id="pdf" src="//cdn.org/paper.pdf"></iframe>'
            "</html>"
        )
        assert SciHubClient._is_captcha(resp) is False

    def test_empty_page(self):
        resp = MagicMock()
        resp.text = ""
        assert SciHubClient._is_captcha(resp) is False


# ---------------------------------------------------------------------------
# _discover_mirrors
# ---------------------------------------------------------------------------


class TestDiscoverMirrors:
    """Tests for dynamic mirror discovery."""

    def test_finds_scihub_links(self):
        html = (
            "<html><body>"
            '<a href="https://sci-hub.ru">ru</a>'
            '<a href="https://sci-hub.se">se</a>'
            '<a href="https://sci-hub.st/"></a>'
            '<a href="https://other.com">other</a>'
            "</body></html>"
        )
        with patch("mastro.scihub.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = html.encode()
            mock_get.return_value = mock_resp

            mirrors = SciHubClient._discover_mirrors()
            assert mirrors == [
                "https://sci-hub.ru",
                "https://sci-hub.se",
                "https://sci-hub.st",
            ]

    def test_no_scihub_links_returns_empty(self):
        html = '<html><a href="https://google.com">google</a></html>'
        with patch("mastro.scihub.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = html.encode()
            mock_get.return_value = mock_resp

            mirrors = SciHubClient._discover_mirrors()
            assert mirrors == []

    def test_network_error_returns_empty(self):
        with patch("mastro.scihub.requests.get", side_effect=Exception("timeout")):
            mirrors = SciHubClient._discover_mirrors()
            assert mirrors == []

    def test_http_error_returns_empty(self):
        with patch("mastro.scihub.requests.get") as mock_get:
            mock_get.return_value.raise_for_status.side_effect = Exception("500")
            mirrors = SciHubClient._discover_mirrors()
            assert mirrors == []

    def test_trailing_slash_stripped(self):
        html = '<a href="https://sci-hub.ru/">ru</a>'
        with patch("mastro.scihub.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.content = html.encode()
            mock_get.return_value = mock_resp
            mirrors = SciHubClient._discover_mirrors()
            assert mirrors == ["https://sci-hub.ru"]


# ---------------------------------------------------------------------------
# _is_mirror_alive
# ---------------------------------------------------------------------------


class TestIsMirrorAlive:
    def test_healthy_mirror(self):
        client = SciHubClient(mirrors=["https://sci-hub.test"], timeout=30)
        mock_head = MagicMock()
        mock_head.status_code = 200
        with patch.object(client._session, "head", return_value=mock_head):
            assert client._is_mirror_alive("https://sci-hub.test") is True

    def test_server_error_is_down(self):
        client = SciHubClient(mirrors=["https://sci-hub.test"], timeout=30)
        mock_head = MagicMock()
        mock_head.status_code = 502
        with patch.object(client._session, "head", return_value=mock_head):
            assert client._is_mirror_alive("https://sci-hub.test") is False

    def test_network_error_is_down(self):
        client = SciHubClient(mirrors=["https://sci-hub.test"], timeout=30)
        with patch.object(client._session, "head", side_effect=Exception("timeout")):
            assert client._is_mirror_alive("https://sci-hub.test") is False


# ---------------------------------------------------------------------------
# __init__
# ---------------------------------------------------------------------------


class TestInit:
    def test_explicit_mirrors(self):
        client = SciHubClient(
            mirrors=["https://a.test", "https://b.test"], timeout=30
        )
        assert client._mirrors == ["https://a.test", "https://b.test"]

    def test_dynamic_discovery_when_no_mirrors(self):
        with patch.object(
            SciHubClient, "_discover_mirrors", return_value=["https://sci-hub.dyn"]
        ):
            client = SciHubClient(timeout=30)
            assert client._mirrors == ["https://sci-hub.dyn"]

    def test_falls_back_to_static_when_discovery_fails(self):
        with patch.object(SciHubClient, "_discover_mirrors", return_value=[]):
            client = SciHubClient(timeout=30)
            assert client._mirrors == SciHubClient._STATIC_MIRRORS

    def test_max_mirror_tries_clamped_to_one(self):
        client = SciHubClient(mirrors=["https://a.test"], max_mirror_tries=0)
        assert client._max_mirror_tries == 1

    def test_session_has_user_agent(self):
        client = SciHubClient(mirrors=["https://a.test"])
        ua = client._session.headers.get("User-Agent", "")
        assert "Mozilla" in ua


# ---------------------------------------------------------------------------
# download
# ---------------------------------------------------------------------------


class TestDownload:
    """End-to-end tests for the download() method."""

    DOI = "10.1234/test.paper"
    PDF_CONTENT = b"%PDF-1.4\nfake pdf content\n%%EOF"

    def _make_client(self, mirrors=None):
        return SciHubClient(mirrors=mirrors or ["https://sci-hub.test"], timeout=30)

    def _mock_head_ok(self, client):
        """Make _is_mirror_alive return True."""
        return patch.object(
            client, "_is_mirror_alive", return_value=True
        )

    def _mock_download_one_success(self, client, tmp_path):
        """Make _download_one write a fake PDF to output_path."""
        def _write_pdf(mirror, doi, output_path, timeout):
            output_path.write_bytes(self.PDF_CONTENT)

        return patch.object(client, "_download_one", side_effect=_write_pdf)

    def test_successful_download(self, tmp_path):
        client = self._make_client()
        out = tmp_path / "paper.pdf"

        with self._mock_head_ok(client), self._mock_download_one_success(client, tmp_path):
            result = client.download(self.DOI, out)
            assert result == str(out)
            assert out.read_bytes() == self.PDF_CONTENT

    def test_captcha_re_raises(self, tmp_path):
        client = self._make_client()
        out = tmp_path / "paper.pdf"

        with self._mock_head_ok(client):
            with patch.object(
                client, "_download_one", side_effect=CaptchaError("https://sci-hub.test/10.1234")
            ):
                with pytest.raises(CaptchaError):
                    client.download(self.DOI, out)

    def test_no_mirror_reachable(self, tmp_path):
        client = self._make_client(["https://bad.test"])
        out = tmp_path / "paper.pdf"

        with patch.object(client, "_is_mirror_alive", return_value=False):
            with pytest.raises(NoMirrorAvailable):
                client.download(self.DOI, out)

    def test_all_mirrors_fail_with_pdf_not_found(self, tmp_path):
        client = self._make_client(["https://m1.test", "https://m2.test"])
        out = tmp_path / "paper.pdf"

        with self._mock_head_ok(client):
            with patch.object(
                client, "_download_one", side_effect=PdfNotFoundError("no pdf")
            ):
                with pytest.raises(NoMirrorAvailable) as exc_info:
                    client.download(self.DOI, out)
                assert "2 mirror" in str(exc_info.value)

    def test_timeout_override(self, tmp_path):
        client = self._make_client()
        out = tmp_path / "paper.pdf"

        def _write_pdf(mirror, doi, output_path, timeout):
            output_path.write_bytes(self.PDF_CONTENT)

        with patch.object(client, "_is_mirror_alive", return_value=True):
            with patch.object(client, "_download_one", side_effect=_write_pdf) as mock_dl:
                client.download(self.DOI, out, timeout=5)
                mock_dl.assert_called_once_with(
                    "https://sci-hub.test", self.DOI, out, 5
                )

    def test_second_mirror_succeeds_after_first_fails(self, tmp_path):
        client = self._make_client(["https://bad.test", "https://ok.test"])
        out = tmp_path / "paper.pdf"

        # First mirror: alive but PDF not found. Second mirror: alive and works.
        with patch.object(client, "_is_mirror_alive", return_value=True):
            # _download_one: first call raises, second succeeds
            call_count = 0

            def _dl(mirror, doi, output_path, timeout):
                nonlocal call_count
                call_count += 1
                if call_count == 1:
                    raise PdfNotFoundError("no pdf")
                output_path.write_bytes(self.PDF_CONTENT)

            with patch.object(client, "_download_one", side_effect=_dl):
                result = client.download(self.DOI, out)
                assert result == str(out)
                assert out.read_bytes() == self.PDF_CONTENT

    def test_max_mirror_tries_limits_attempts(self, tmp_path):
        mirrors = [f"https://m{i}.test" for i in range(10)]
        client = SciHubClient(mirrors=mirrors, max_mirror_tries=3)
        out = tmp_path / "paper.pdf"

        call_log = []

        def _head_log(url):
            call_log.append(url)
            return True

        with patch.object(client, "_is_mirror_alive", side_effect=_head_log):
            with patch.object(
                client, "_download_one", side_effect=PdfNotFoundError("nope")
            ):
                with pytest.raises(NoMirrorAvailable):
                    client.download(self.DOI, out)

        assert len(call_log) == 3  # only first 3 mirrors checked


# ---------------------------------------------------------------------------
# _download_one
# ---------------------------------------------------------------------------


class TestDownloadOne:
    """Tests for the _download_one helper method."""

    DOI = "10.5678/other"
    MIRROR = "https://sci-hub.test"

    @staticmethod
    def _mock_response(status=200, text="", headers=None, content=None):
        resp = MagicMock()
        resp.status_code = status
        resp.text = text
        resp.headers = headers or {}
        if content:
            resp.iter_content.return_value = iter([content])
        return resp

    def _client_with_mirrors(self):
        return SciHubClient(mirrors=["https://sci-hub.test"], timeout=30)

    def test_403_raises_captcha(self, tmp_path):
        client = self._client_with_mirrors()
        mock_resp = self._mock_response(status=403)

        with patch.object(client._session, "get", return_value=mock_resp):
            with pytest.raises(CaptchaError) as exc_info:
                client._download_one(
                    self.MIRROR, self.DOI, tmp_path / "p.pdf", timeout=30
                )
            assert self.MIRROR in str(exc_info.value)

    def test_captcha_content_raises(self, tmp_path):
        client = self._client_with_mirrors()
        mock_resp = self._mock_response(
            status=200, text="<html>Please verify you are not a robot</html>"
        )

        with patch.object(client._session, "get", return_value=mock_resp):
            with pytest.raises(CaptchaError):
                client._download_one(
                    self.MIRROR, self.DOI, tmp_path / "p.pdf", timeout=30
                )

    def test_no_pdf_link_raises(self, tmp_path):
        client = self._client_with_mirrors()
        mock_resp = self._mock_response(
            status=200, text="<html><body>no iframe</body></html>"
        )

        with patch.object(client._session, "get", return_value=mock_resp):
            with pytest.raises(PdfNotFoundError):
                client._download_one(
                    self.MIRROR, self.DOI, tmp_path / "p.pdf", timeout=30
                )

    def test_pdf_content_type_saves_file(self, tmp_path):
        client = self._client_with_mirrors()
        page_html = '<html><iframe src="/paper.pdf"></iframe></html>'
        pdf_bytes = b"%PDF-1.5\nreal content"

        # Two GET calls: page + PDF
        responses = {
            f"{self.MIRROR}/{self.DOI}": self._mock_response(
                status=200, text=page_html
            ),
            f"{self.MIRROR}/paper.pdf": self._mock_response(
                status=200,
                headers={"content-type": "application/pdf"},
                content=pdf_bytes,
            ),
        }

        def _get(url, **kwargs):
            return responses[url]

        out = tmp_path / "paper.pdf"
        with patch.object(client._session, "get", side_effect=_get):
            client._download_one(self.MIRROR, self.DOI, out, timeout=30)
        assert out.read_bytes() == pdf_bytes

    def test_magic_bytes_save_even_with_wrong_content_type(self, tmp_path):
        client = self._client_with_mirrors()
        page_html = '<html><iframe src="/file.pdf"></iframe></html>'
        pdf_bytes = b"%PDF-1.3\nmagic!"  # correct magic

        responses = {
            f"{self.MIRROR}/{self.DOI}": self._mock_response(
                status=200, text=page_html
            ),
            f"{self.MIRROR}/file.pdf": self._mock_response(
                status=200,
                headers={"content-type": "text/html"},  # wrong type
                content=pdf_bytes,  # but correct magic
            ),
        }

        def _get(url, **kwargs):
            return responses[url]

        out = tmp_path / "paper.pdf"
        with patch.object(client._session, "get", side_effect=_get):
            client._download_one(self.MIRROR, self.DOI, out, timeout=30)
        assert out.read_bytes() == pdf_bytes

    def test_wrong_content_type_and_not_pdf_magic_raises(self, tmp_path):
        client = self._client_with_mirrors()
        page_html = '<html><iframe src="/not.pdf"></iframe></html>'
        html_bytes = b"<html>not a pdf</html>"

        responses = {
            f"{self.MIRROR}/{self.DOI}": self._mock_response(
                status=200, text=page_html
            ),
            f"{self.MIRROR}/not.pdf": self._mock_response(
                status=200,
                headers={"content-type": "text/html"},
                content=html_bytes,
            ),
        }

        def _get(url, **kwargs):
            return responses[url]

        out = tmp_path / "paper.pdf"
        with patch.object(client._session, "get", side_effect=_get):
            with pytest.raises(PdfNotFoundError):
                client._download_one(self.MIRROR, self.DOI, out, timeout=30)


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    def test_enter_exit(self):
        client = SciHubClient(mirrors=["https://a.test"])
        with patch.object(client._session, "close") as mock_close:
            with client as ctx:
                assert ctx is client
            mock_close.assert_called_once()

    def test_close(self):
        client = SciHubClient(mirrors=["https://a.test"])
        with patch.object(client._session, "close") as mock_close:
            client.close()
            mock_close.assert_called_once()
