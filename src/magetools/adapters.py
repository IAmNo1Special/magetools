"""Adapters for Magetools.

This module provides concrete implementations of the embedding and vector store
protocols. Dependencies (chromadb, google-genai) are lazily imported to allow
the core magetools package to be used with alternative providers.
"""

import os
from logging import getLogger
from typing import TYPE_CHECKING, Any

from .config import MageToolsConfig, get_config
from .exceptions import ConfigurationError
from .interfaces import EmbeddingProviderProtocol, VectorStoreProtocol

# Type hints only - no runtime import
# This is to allow the core magetools package to be used with alternative providers.
if TYPE_CHECKING:
    import chromadb  # noqa: F401
    from google import genai  # noqa: F401

logger = getLogger(__name__)


def get_default_provider(
    config: MageToolsConfig | None = None,
) -> EmbeddingProviderProtocol:
    """Get the best available embedding provider.

    Returns GoogleGenAIProvider if google-genai is installed and GOOGLE_API_KEY is set.
    Falls back to MockEmbeddingProvider otherwise (graceful degradation).
    """
    # Check if google-genai is available and API key is set
    try:
        _import_genai()
        if os.environ.get("GOOGLE_API_KEY"):
            return GoogleGenAIProvider(config)
        else:
            logger.warning("GOOGLE_API_KEY not set - falling back to MockProvider")
            return MockEmbeddingProvider(config)
    except ConfigurationError:
        # google-genai not installed
        return MockEmbeddingProvider(config)


def _import_chromadb():
    """Lazily import chromadb with helpful error message."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        return chromadb, embedding_functions
    except ImportError as e:
        raise ConfigurationError(
            "chromadb is required for vector storage. "
            "Install it with: uv add chromadb"
        ) from e


def _import_genai():
    """Lazily import google-genai with helpful error message."""
    try:
        from google import genai

        return genai
    except ImportError as e:
        raise ConfigurationError(
            "google-genai is required for the GoogleGenAIProvider. "
            "Install it with: uv add google-genai"
        ) from e


class GoogleGenAIProvider(EmbeddingProviderProtocol):
    """Provider for Google Generative AI embeddings."""

    def __init__(self, config: MageToolsConfig | None = None):
        self.config = config or get_config()
        genai = _import_genai()
        self.client = genai.Client()
        self._genai = genai

    def get_embedding_function(self) -> Any:
        _, embedding_functions = _import_chromadb()
        return embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            model_name=self.config.embedding_model, task_type="SEMANTIC_SIMILARITY"
        )

    def generate_content(self, prompt: str) -> str:
        """Generates content using Google Gemini model."""
        logger.debug(f"Generating content with model {self.config.model_name}...")
        response = self.client.models.generate_content(
            model=self.config.model_name, contents=prompt
        )
        logger.debug("Generated content.")
        return response.text

    async def close(self) -> None:
        """Cleanup AI client."""
        pass


class ChromaVectorStore(VectorStoreProtocol):
    """Adapter for ChromaDB."""

    def __init__(self, path: str):
        chromadb, _ = _import_chromadb()
        self.client = chromadb.PersistentClient(path=str(path))

    def get_collection(self, name: str, embedding_function: Any) -> Any:
        return self.client.get_collection(
            name=name, embedding_function=embedding_function
        )

    def list_collections(self) -> list[Any]:
        return self.client.list_collections()

    def get_or_create_collection(self, name: str, embedding_function: Any) -> Any:
        return self.client.get_or_create_collection(
            name=name, embedding_function=embedding_function
        )

    async def close(self) -> None:
        """Close database connection."""
        self.client = None


class MockEmbeddingProvider(EmbeddingProviderProtocol):
    """Mock provider for when google-genai is not available.

    This allows users to try the library without credentials.
    Search functionality will be degraded but the app won't crash.
    """

    def __init__(self, config: MageToolsConfig | None = None):
        self.config = config or get_config()
        logger.warning(
            "Using MockEmbeddingProvider - search functionality will be limited. "
            "Install google-genai and set GOOGLE_API_KEY for full functionality."
        )

    def get_embedding_function(self) -> Any:
        """Return a simple mock embedding function."""
        return _MockEmbeddingFunction()

    def generate_content(self, prompt: str) -> str:
        """Return a placeholder summary."""
        logger.debug("MockProvider: Returning placeholder summary")
        return "Summary not available (MockProvider - no LLM configured)"

    async def close(self) -> None:
        """No-op cleanup."""
        pass


class _MockEmbeddingFunction:
    """Mock embedding function that returns zero vectors."""

    def __init__(self):
        self.name = "mock"

    def __call__(self, input: list[str]) -> list[list[float]]:
        """Return zero vectors for compatibility."""
        # ChromaDB expects 768-dim vectors for most models
        return [[0.0] * 768 for _ in input]
