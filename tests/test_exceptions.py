"""Unit tests for magetools exceptions module."""

import pytest

from magetools.exceptions import (
    ConfigurationError,
    EmbeddingError,
    GrimoriumError,
    MagetoolsError,
    QuarantineError,
    SpellAccessDeniedError,
    SpellDiscoveryError,
    SpellExecutionError,
)


class TestExceptionHierarchy:
    """Tests for exception inheritance hierarchy."""

    def test_all_exceptions_inherit_from_base(self):
        """All custom exceptions should inherit from MagetoolsError."""
        exceptions = [
            SpellDiscoveryError,
            SpellExecutionError,
            SpellAccessDeniedError,
            ConfigurationError,
            EmbeddingError,
            QuarantineError,
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, MagetoolsError)
            assert issubclass(exc_class, Exception)

    def test_quarantine_error_inherits_from_discovery(self):
        """QuarantineError should inherit from SpellDiscoveryError."""
        assert issubclass(QuarantineError, SpellDiscoveryError)

    def test_grimorium_error_alias(self):
        """GrimoriumError should be alias for MagetoolsError."""
        assert GrimoriumError is MagetoolsError


class TestExceptionRaising:
    """Tests for raising exceptions."""

    def test_magetools_error_is_runtime_error(self):
        """MagetoolsError stays catchable as RuntimeError.

        The base error subclasses RuntimeError so existing handlers keep
        working while callers can also catch the library's own base type.
        """
        assert issubclass(MagetoolsError, RuntimeError)

        with pytest.raises(RuntimeError):
            raise MagetoolsError("test")

    def test_magetools_error_message(self):
        """Should preserve error message."""
        with pytest.raises(MagetoolsError) as exc_info:
            raise MagetoolsError("Test error message")

        assert "Test error message" in str(exc_info.value)

    def test_spell_discovery_error(self):
        """Should raise SpellDiscoveryError."""
        with pytest.raises(SpellDiscoveryError):
            raise SpellDiscoveryError("Failed to discover spells")

    def test_spell_execution_error(self):
        """Should raise SpellExecutionError."""
        with pytest.raises(SpellExecutionError):
            raise SpellExecutionError("Failed to execute spell")

    def test_spell_access_denied_error(self):
        """Should raise SpellAccessDeniedError."""
        with pytest.raises(SpellAccessDeniedError):
            raise SpellAccessDeniedError("Access denied to collection")

    def test_configuration_error(self):
        """Should raise ConfigurationError."""
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Missing API key")

    def test_embedding_error(self):
        """Should raise EmbeddingError."""
        with pytest.raises(EmbeddingError):
            raise EmbeddingError("Failed to generate embedding")

    def test_quarantine_error(self):
        """Should raise QuarantineError."""
        with pytest.raises(QuarantineError):
            raise QuarantineError("File quarantined due to syntax error")


class TestExceptionCatching:
    """Tests for catching exceptions at different levels."""

    def test_catch_specific_as_base(self):
        """Should be catchable as base MagetoolsError."""
        try:
            raise ConfigurationError("test")
        except MagetoolsError as e:
            assert isinstance(e, ConfigurationError)

    def test_catch_quarantine_as_discovery(self):
        """QuarantineError should be catchable as SpellDiscoveryError."""
        try:
            raise QuarantineError("test")
        except SpellDiscoveryError as e:
            assert isinstance(e, QuarantineError)

    def test_catch_as_exception(self):
        """All should be catchable as Exception."""
        exceptions = [
            MagetoolsError("test"),
            SpellDiscoveryError("test"),
            SpellExecutionError("test"),
            ConfigurationError("test"),
        ]

        for exc in exceptions:
            try:
                raise exc
            except Exception as e:
                assert e is exc
