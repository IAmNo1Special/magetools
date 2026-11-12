"""Unit tests for LocalEmbeddingProvider (free, no API key required)."""

import math
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from magetools.adapters import (
    LocalEmbeddingProvider,
    MockEmbeddingProvider,
    _hash_vector,
    get_default_provider,
)


def _cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def test_default_provider_prefers_local_over_mock():
    """No API key -> local provider, not the mock."""
    with patch.dict("os.environ", {}, clear=True):
        provider = get_default_provider()
    assert isinstance(provider, LocalEmbeddingProvider)
    assert not isinstance(provider, MockEmbeddingProvider)


def test_google_still_wins_with_key():
    """GOOGLE_API_KEY set -> GoogleGenAIProvider as before."""
    sentinel = object()

    class FakeGoogle:
        def __init__(self, config=None):
            pass

    with (
        patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}),
        patch("magetools.adapters._import_genai", return_value=object()),
        patch("magetools.adapters.GoogleGenAIProvider", FakeGoogle),
    ):
        provider = get_default_provider()
    assert isinstance(provider, FakeGoogle)


def test_hash_embeddings_deterministic_and_normalized():
    provider = LocalEmbeddingProvider(config=SimpleNamespace())
    assert provider._backend == "hash"  # sentence-transformers not installed here
    first = provider._embed(["hello world"])
    second = provider._embed(["hello world"])
    assert first == second
    assert len(first[0]) == 384
    norm = math.sqrt(sum(x * x for x in first[0]))
    assert norm == pytest.approx(1.0)


def test_similar_texts_score_higher():
    a = _hash_vector("the cat sat on the mat", 384)
    b = _hash_vector("the cat sat on the rug", 384)
    c = _hash_vector("quantum chromodynamics briefing notes", 384)
    assert _cosine(a, b) > _cosine(a, c)


def test_empty_text_gives_zero_vector():
    vec = _hash_vector("", 384)
    assert vec == [0.0] * 384


def test_embedding_function_is_chroma_compatible():
    provider = LocalEmbeddingProvider(config=SimpleNamespace())
    fn = provider.get_embedding_function()
    result = fn(["one", "two"])
    assert len(result) == 2
    assert all(len(v) == 384 for v in result)


def test_generate_content_placeholder():
    provider = LocalEmbeddingProvider(config=SimpleNamespace())
    assert "no LLM" in provider.generate_content("summarize this")
