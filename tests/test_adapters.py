"""Unit tests for magetools adapters module."""

import os
from unittest.mock import MagicMock, patch

import pytest

from magetools.adapters import (
    ChromaVectorStore,
    GoogleGenAIProvider,
    MockEmbeddingProvider,
    _import_chromadb,
    _import_genai,
    _MockEmbeddingFunction,
    get_default_provider,
)
from magetools.exceptions import ConfigurationError


def test_mock_provider_basics():
    """Verify MockEmbeddingProvider provides basic fallback functionality."""
    p = MockEmbeddingProvider()
    assert "Mock" in p.generate_content("test")
    func = p.get_embedding_function()
    assert isinstance(func, _MockEmbeddingFunction)
    assert len(func(["hello"])[0]) == 768


def test_get_default_provider_no_key():
    """Fallback to MockProvider when API key is missing."""
    os.environ.pop("GOOGLE_API_KEY", None)
    p = get_default_provider()
    assert isinstance(p, MockEmbeddingProvider)


def test_import_genai_error_handling():
    """Ensure ConfigurationError is raised when genai is missing."""
    with (
        patch("builtins.__import__", side_effect=ImportError),
        pytest.raises(ConfigurationError),
    ):
        _import_genai()


def test_import_chromadb_error_handling():
    """Ensure ConfigurationError is raised when chromadb is missing."""
    with (
        patch("builtins.__import__", side_effect=ImportError),
        pytest.raises(ConfigurationError),
    ):
        _import_chromadb()


def test_google_genai_provider_init():
    """Verify initialization of GoogleGenAIProvider."""
    with (
        patch("magetools.adapters._import_genai") as mock_import,
        patch("os.environ.get", return_value="fake-key"),
    ):
        mock_genai = MagicMock()
        mock_import.return_value = mock_genai
        provider = GoogleGenAIProvider()
        assert provider.client is not None
        mock_genai.Client.assert_called_once()


def test_google_genai_provider_methods():
    """Verify methods of GoogleGenAIProvider."""
    with (
        patch("magetools.adapters._import_genai"),
        patch("magetools.adapters._import_chromadb") as mock_chroma,
    ):
        mock_ef_factory = MagicMock()
        mock_chroma.return_value = (MagicMock(), mock_ef_factory)

        provider = GoogleGenAIProvider()
        provider.client = MagicMock()

        # Test get_embedding_function
        provider.get_embedding_function()
        mock_ef_factory.GoogleGenerativeAiEmbeddingFunction.assert_called()

        # Test generate_content
        provider.client.models.generate_content.return_value.text = "generated"
        assert provider.generate_content("prompt") == "generated"

        # Test close
        import asyncio

        asyncio.run(provider.close())


def test_chroma_vector_store_lifecycle(tmp_path):
    """Verify ChromaVectorStore lifecycle and methods."""
    with patch("magetools.adapters._import_chromadb") as mock_import:
        mock_chroma = MagicMock()
        mock_import.return_value = (mock_chroma, MagicMock())

        store = ChromaVectorStore(path=tmp_path)
        mock_chroma.PersistentClient.assert_called_once_with(path=str(tmp_path))

        # Test collection methods
        store.get_collection("test", None)
        store.client.get_collection.assert_called_with(
            name="test", embedding_function=None
        )

        store.list_collections()
        store.client.list_collections.assert_called_once()

        store.get_or_create_collection("test", None)
        store.client.get_or_create_collection.assert_called_with(
            name="test", embedding_function=None
        )

        # Test close
        import asyncio

        asyncio.run(store.close())
        assert store.client is None


def test_import_chromadb_success():
    """Verify successful lazy import of chromadb."""
    # This might fail in environments without chromadb, so we mock the successful path too
    with patch("builtins.__import__") as mock_import:
        mock_import.return_value = MagicMock()
        _import_chromadb()


def test_get_default_provider_import_error():
    """Verify fallback to MockProvider when _import_genai raises ConfigurationError."""
    with patch(
        "magetools.adapters._import_genai", side_effect=ConfigurationError("Missing")
    ):
        provider = get_default_provider()
        assert isinstance(provider, MockEmbeddingProvider)


def test_mock_embedding_provider_close():
    """Verify close() method of MockEmbeddingProvider (for coverage)."""
    p = MockEmbeddingProvider()
    import asyncio

    asyncio.run(p.close())


def test_get_default_provider_success():
    """Verify successful provider selection when key is present."""
    with (
        patch("magetools.adapters._import_genai"),
        patch("os.environ.get", return_value="fake-key"),
        patch("magetools.adapters.GoogleGenAIProvider") as mock_provider,
    ):
        p = get_default_provider()
        assert p == mock_provider.return_value
