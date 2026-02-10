# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-10

### Added
- **Spells Listing**: Introduced `list_spells` method to `Grimorium` for retrieving all available tools.
- **Access Control**: Implemented secure filtering in `list_spells` to respect `allowed_collections` restrictions.
- **Robustness**: Added initialization checks and refined type hinting across core toolset methods.
- **Updated Tests**: Expanded test suite to cover hierarchical tool discovery and unauthorized access scenarios.

## [1.0.0] - 2026-02-04

### Added
- **Dynamic Tool Discovery**: Core engine for identifying and loading Python functions as AI tools.
- **Strict Mode**: Security enforcement requiring `manifest.json` for all tool collections.
- **CLI Suite**: `uv run -m magetools init` and `uv run -m magetools scan` for collection management.
- **Provider Agnosticism**: Support for Google GenAI with automatic fallback to Mock providers.
- **Vector Search**: Integrated ChromaDB support for semantic tool lookups.
- **Modern Packaging**: Full migration to `uv` for dependency management and publishing.
- **Optional Dependencies**: Modular installation via extras (e.g., `magetools[google]`, `magetools[full]`).
- **Comprehensive Documentation**: Detailed MkDocs site with API references.
- **Resilient Initialization**: `auto_initialize` pattern with graceful error handling.

### Fixed
- Fixed blocking I/O in `Grimorium` constructor.
- Addressed security risks regarding arbitrary code execution via import sanitization and manifests.
- Optimized database locking issues during concurrent indexing.

### Security
- Introduced "Quarantine" mode for problematic spell files.
- Implemented permission-based tool execution.

### Detailed File Changes

#### Configuration & Meta
- `.github/ISSUE_TEMPLATE/bug_report.md`: Added a new bug report issue template.
- `.github/ISSUE_TEMPLATE/feature_request.md`: Added a new feature request issue template.
- `.github/PULL_REQUEST_TEMPLATE.md`: Added a new pull request template with sections for description, type of change, testing, and checklist.
- `.github/dependabot.yml`: Added Dependabot configuration for weekly uv dependency updates.
- `.github/milestone_trigger.json`: Removed this file.
- `.gitignore`: Added `.bvckpvck/` to the ignore list.
- `.pre-commit-config.yaml`: Added pre-commit configuration for isort, black, check-yaml, check-toml, end-of-file-fixer, and trailing-whitespace.
- `CHANGELOG.md`: Added a new changelog file detailing v1.0.0 features, fixes, and security enhancements.
- `CODE_OF_CONDUCT.md`: Added a Contributor Covenant Code of Conduct.
- `CONTRIBUTING.md`: Added a contributing guide with sections on bug reporting, pull requests, and coding style.
- `LICENSE`: Added an MIT License file.
- `README.md`: Significantly updated the README to reflect the v1.0.0 features, installation, usage, security, configuration, CLI reference, support, roadmap, and contributing guidelines.
- `RELEASE_NOTES.md`: Added release notes for v1.0.0 highlighting key features and internal stability improvements.
- `TODOs.md`: Removed this file.
- `magetools.yaml`: Added a new configuration file for magetools example.
- `mkdocs.yml`: Added MkDocs configuration for documentation generation.
- `pyproject.toml`: Updated project version to 1.0.0. Refined project description. Introduced optional dependencies. Added magetools CLI entry point.
- `uv.lock`: Updated dependencies.

#### Documentation
- `docs/index.md`: Added main documentation index.
- `docs/reference/adapters.md`: Added API reference for adapters.
- `docs/reference/config.md`: Added API reference for configuration.
- `docs/reference/grimorium.md`: Added API reference for Grimorium.
- `docs/reference/spellsync.md`: Added API reference for SpellSync.
- `docs/user_guide/cli.md`: Added CLI usage guide.
- `docs/user_guide/core_concepts.md`: Added core concepts documentation.
- `docs/user_guide/getting_started.md`: Added getting started guide.
- `docs/user_guide/security.md`: Added security and strict mode documentation.

#### Core Source Code (`src/magetools`)
- `init.py`: Updated version to 1.0.0. Added spell alias. Exposed new config/adapter components.
- `main.py`: Refactored CLI to use argparse. Added init_collection and scan_spells functions.
- `adapters.py`: Refactored for lazy imports. Introduced MockEmbeddingProvider. Added generate_content/close methods.
- `config.py`: Added MageToolsConfig class. Implemented path resolution and validation.
- `constants.py`: Added GRIMORIUMS_INDEX_NAME. Updated path constants.
- `exceptions.py`: Renamed GrimoriumError to MagetoolsError. Introduced SpellAccessDeniedError and QuarantineError.
- `grimorium.py`: Refactored for async init. Added discover_grimoriums/spells. Added strict_mode. Implemented cleanup.
- `interfaces.py`: Added generate_content and close methods to protocols.
- `prompts.py`: Updated usage guide for hierarchical discovery.
- `spell_registry.py`: Update attribute assignment logic.
- `spellsync.py`: Implemented metadata sync (LLM summarization). Added hash staleness detection. Added manifest support. Refactored discovery.

#### Examples & Tests
- `example/.magetools/...`: Added example summaries and manifests.
- `example/agent.py`: Updated agent initialization, logging, and cleanup.
- `tests/conftest.py`: Added fixtures for temp dirs, samples, and mocks.
- `tests/test_adapters.py`: Added tests for MockEmbeddingProvider.
- `tests/test_config.py`: Added tests for MageToolsConfig.
- `tests/test_exceptions.py`: Added tests for exception hierarchy.
- `tests/test_grimorium.py`: Added tests for Grimorium.
- `tests/test_main.py`: Added tests for CLI.
- `tests/test_manifest.py`: Added tests for manifests.
- `tests/test_spel_registry.py`: Added tests for decorators.
- `tests/test_spellsync.py`: Added tests for SpellSync.
