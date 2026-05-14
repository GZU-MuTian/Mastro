"""Tests for nasa_ads.py — all HTTP calls are mocked."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from mastro.nasa_ads import (
    EXPORT_FORMATS,
    _PDF_ENDPOINTS,
    ADSClient,
    extract_bibcode,
)


# ---------------------------------------------------------------------------
# extract_bibcode
# ---------------------------------------------------------------------------


class TestExtractBibcode:
    """Unit tests for the extract_bibcode helper."""

    def test_empty_string(self):
        assert extract_bibcode("") is None

    def test_none(self):
        assert extract_bibcode(None) is None  # type: ignore[arg-type]

    def test_abs_hash_url(self):
        url = "https://ui.adsabs.harvard.edu/abs/2024ApJ...960L..14S/abstract"
        assert extract_bibcode(url) == "2024ApJ...960L..14S"

    def test_link_gateway_url(self):
        url = "https://ui.adsabs.harvard.edu/link_gateway/2024ApJ...960L..14S/PUB_PDF"
        assert extract_bibcode(url) == "2024ApJ...960L..14S"

    def test_bare_bibcode_returns_none(self):
        """A bare bibcode without a URL path should not match."""
        assert extract_bibcode("2024ApJ...960L..14S") is None

    def test_url_encoded_ampersand(self):
        url = "https://ui.adsabs.harvard.edu/abs/2020A%26A...641A...1P/abstract"
        bibcode = extract_bibcode(url)
        assert bibcode == "2020A&A...641A...1P"

    def test_html_entity_ampersand(self):
        url = "https://ui.adsabs.harvard.edu/abs/2020A&amp;A...641A...1P/abstract"
        assert extract_bibcode(url) == "2020A&A...641A...1P"


# ---------------------------------------------------------------------------
# ADSClient construction
# ---------------------------------------------------------------------------


class TestADSClientInit:
    """Test constructor behaviour (API key handling, sessions)."""

    def test_api_key_from_argument(self):
        client = ADSClient(api_key="test-key")
        assert client.api_key == "test-key"
        client.close()

    def test_api_key_from_env(self, monkeypatch):
        monkeypatch.setenv("ADS_API_TOKEN", "env-key")
        client = ADSClient()
        assert client.api_key == "env-key"
        client.close()

    def test_no_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("ADS_API_TOKEN", raising=False)
        with pytest.raises(ValueError, match="ADS API key not found"):
            ADSClient()

    def test_context_manager(self):
        with ADSClient(api_key="k") as client:
            assert isinstance(client, ADSClient)


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------


class TestSearch:
    """Test ADSClient.search with mocked HTTP."""

    def _mock_response(self, payload: dict) -> MagicMock:
        resp = MagicMock()
        resp.status_code = 200
        resp.json.return_value = payload
        resp.raise_for_status = MagicMock()
        return resp

    def test_basic_search(self):
        expected = {"response": {"numFound": 42, "docs": []}}
        with ADSClient(api_key="k") as client:
            with patch.object(client._session, "get", return_value=self._mock_response(expected)) as mock_get:
                result = client.search("star formation")
                assert result == expected
                args, kwargs = mock_get.call_args
                assert kwargs["params"]["q"] == "star formation"
                assert kwargs["params"]["rows"] == 10

    def test_search_with_sort_and_fq(self):
        expected = {"response": {"numFound": 0, "docs": []}}
        with ADSClient(api_key="k") as client:
            with patch.object(client._session, "get", return_value=self._mock_response(expected)) as mock_get:
                client.search("q", sort="date desc", fq="year:2024")
                params = mock_get.call_args.kwargs["params"]
                assert params["sort"] == "date desc"
                assert params["fq"] == ["year:2024"]

    def test_search_with_highlight(self):
        expected = {"response": {"numFound": 0, "docs": []}}
        with ADSClient(api_key="k") as client:
            with patch.object(client._session, "get", return_value=self._mock_response(expected)) as mock_get:
                client.search("q", hl=True, hl_fl="title", hl_snippets=5)
                params = mock_get.call_args.kwargs["params"]
                assert params["hl"] == "true"
                assert params["hl.fl"] == "title"
                assert params["hl.snippets"] == 5


# ---------------------------------------------------------------------------
# export
# ---------------------------------------------------------------------------


class TestExport:
    """Test ADSClient.export with mocked HTTP."""

    def test_single_bibcode_uses_get(self):
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "text/plain"}
        resp.text = "@article{...}"
        resp.raise_for_status = MagicMock()

        with ADSClient(api_key="k") as client:
            with patch.object(client._session, "get", return_value=resp) as mock_get:
                result = client.export(["2024ApJ...960L..14S"])
                mock_get.assert_called_once()
                assert result == "@article{...}"

    def test_multi_bibcode_uses_post(self):
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "application/json"}
        resp.json.return_value = {"export": "@article{a}\n@article{b}"}
        resp.raise_for_status = MagicMock()

        with ADSClient(api_key="k") as client:
            with patch.object(client._session, "post", return_value=resp) as mock_post:
                result = client.export(["bib1", "bib2"])
                mock_post.assert_called_once()
                assert "article" in result

    def test_unknown_format_raises(self):
        with ADSClient(api_key="k") as client:
            with pytest.raises(ValueError, match="Unknown format"):
                client.export(["bib"], fmt="invalid_format")


# ---------------------------------------------------------------------------
# _fetch_pdf
# ---------------------------------------------------------------------------


class TestFetchPdf:
    """Test _fetch_pdf fallback logic with mocked HTTP."""

    def _make_client(self):
        return ADSClient(api_key="k")

    def test_pdf_content_type(self, tmp_path):
        pdf_bytes = b"%PDF-1.4 fake pdf content"
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "application/pdf"}
        resp.iter_content.return_value = [pdf_bytes]
        resp.raise_for_status = MagicMock()

        client = self._make_client()
        with patch.object(client._pdf_session, "get", return_value=resp):
            result = client._fetch_pdf("2024ApJ...960L..14S", save_dir=tmp_path, timeout=10)
            assert result.endswith(".pdf")
            assert Path(result).read_bytes() == pdf_bytes
        client.close()

    def test_wrong_content_type_but_pdf_magic(self, tmp_path):
        pdf_bytes = b"%PDF-1.4 fake pdf"
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "application/octet-stream"}
        resp.iter_content.return_value = iter([pdf_bytes])
        resp.raise_for_status = MagicMock()

        client = self._make_client()
        with patch.object(client._pdf_session, "get", return_value=resp):
            result = client._fetch_pdf("2024Test", save_dir=tmp_path, timeout=10)
            assert Path(result).read_bytes() == pdf_bytes
        client.close()

    def test_html_response_skips(self, tmp_path):
        html_resp = MagicMock()
        html_resp.status_code = 200
        html_resp.headers = {"content-type": "text/html"}
        html_resp.raise_for_status = MagicMock()

        pdf_resp = MagicMock()
        pdf_resp.status_code = 200
        pdf_resp.headers = {"content-type": "application/pdf"}
        pdf_resp.iter_content.return_value = [b"%PDF"]
        pdf_resp.raise_for_status = MagicMock()

        client = self._make_client()
        with patch.object(client._pdf_session, "get", side_effect=[html_resp, pdf_resp]):
            result = client._fetch_pdf("2024Test", save_dir=tmp_path, timeout=10)
            assert result.endswith(".pdf")
        client.close()

    def test_all_endpoints_fail(self, tmp_path):
        resp = MagicMock()
        resp.status_code = 200
        resp.headers = {"content-type": "text/html"}
        resp.raise_for_status = MagicMock()

        client = self._make_client()
        with patch.object(client._pdf_session, "get", return_value=resp):
            with pytest.raises(RuntimeError, match="All endpoints failed"):
                client._fetch_pdf("2024Test", save_dir=tmp_path, timeout=10)
        client.close()

    def test_network_error_fallback(self, tmp_path):
        import requests as req

        error_resp = MagicMock()
        error_resp.raise_for_status.side_effect = req.ConnectionError("timeout")

        pdf_resp = MagicMock()
        pdf_resp.status_code = 200
        pdf_resp.headers = {"content-type": "application/pdf"}
        pdf_resp.iter_content.return_value = [b"%PDF"]
        pdf_resp.raise_for_status = MagicMock()

        client = self._make_client()
        with patch.object(client._pdf_session, "get", side_effect=[error_resp, pdf_resp]):
            result = client._fetch_pdf("2024Test", save_dir=tmp_path, timeout=10)
            assert result.endswith(".pdf")
        client.close()


# ---------------------------------------------------------------------------
# fetch (batch)
# ---------------------------------------------------------------------------


class TestFetch:
    """Test the batch fetch method."""

    def test_success_and_failure(self, tmp_path):
        pdf_bytes = b"%PDF-1.4"
        ok_resp = MagicMock()
        ok_resp.status_code = 200
        ok_resp.headers = {"content-type": "application/pdf"}
        ok_resp.iter_content.return_value = [pdf_bytes]
        ok_resp.raise_for_status = MagicMock()

        fail_resp = MagicMock()
        fail_resp.status_code = 200
        fail_resp.headers = {"content-type": "text/html"}
        fail_resp.raise_for_status = MagicMock()

        with ADSClient(api_key="k") as client:
            with patch.object(
                client._pdf_session,
                "get",
                side_effect=[
                    ok_resp,              # bib1: EPRINT_PDF succeeds
                    fail_resp, fail_resp, fail_resp,  # bib2: all 3 fail
                ],
            ):
                results = client.fetch(["bib1", "bib2"], output_dir=tmp_path)

        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[0]["bibcode"] == "bib1"
        assert results[1]["success"] is False
        assert results[1]["bibcode"] == "bib2"

    def test_creates_output_dir(self, tmp_path):
        new_dir = tmp_path / "subdir"

        pdf_resp = MagicMock()
        pdf_resp.status_code = 200
        pdf_resp.headers = {"content-type": "application/pdf"}
        pdf_resp.iter_content.return_value = [b"%PDF"]
        pdf_resp.raise_for_status = MagicMock()

        with ADSClient(api_key="k") as client:
            with patch.object(client._pdf_session, "get", return_value=pdf_resp):
                results = client.fetch(["bib"], output_dir=new_dir)

        assert new_dir.exists()
        assert results[0]["success"] is True

    def test_url_input_extracts_bibcode(self, tmp_path):
        pdf_resp = MagicMock()
        pdf_resp.status_code = 200
        pdf_resp.headers = {"content-type": "application/pdf"}
        pdf_resp.iter_content.return_value = [b"%PDF"]
        pdf_resp.raise_for_status = MagicMock()

        url = "https://ui.adsabs.harvard.edu/abs/2024ApJ...960L..14S/abstract"

        with ADSClient(api_key="k") as client:
            with patch.object(client._pdf_session, "get", return_value=pdf_resp):
                results = client.fetch([url], output_dir=tmp_path)

        assert results[0]["bibcode"] == "2024ApJ...960L..14S"
        assert results[0]["success"] is True
