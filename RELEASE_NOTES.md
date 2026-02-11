# Release Notes - Magetools v1.2.0

We are excited to announce the **v1.2.0** release of **Magetools**! This version represents a major milestone in security, performance, and developer accessibility, making Magetools the most robust solution for hierarchical agentic tool discovery.

## 🌟 What's New in v1.2.0

### 🧠 Automatic Metadata Synchronization
Magetools now automatically generates `grimorium_summary.md` files for your tool collections. These high-density technical summaries are powered by Google Gemini and provide agents with the critical context needed to choose the right tools without reading every line of code.
- **Hierarchical Discovery**: Agents can now search high-level collection summaries before diving into specific spells.
- **Stale Detection**: Automatic hashing ensures summaries are re-generated whenever you modify your code.

### 🛡️ Security Hardening & ADK Alignment
We've significantly hardened our metadata generation path against Indirect Prompt Injection and simplified the developer flow.
- **ADK Source Alignment**: Full adherence to Google ADK `BaseToolset` standards (v0.1.0), including async resource cleanup and declarative configuration stubs.
- **Docstring Sanitization**: Docstrings are now sanitized to redact common injection keywords before being sent to the LLM.
- **IDE-Friendly Docs**: Resolved YAML validation errors in `mkdocs.yml` to ensure a smooth development experience in VS Code.

### ⚡ Performance Optimizations
- **Non-blocking Initialization**: We've decoupled metadata generation from the core `Grimorium` constructor. Tool loading is now lightning-fast, and building summaries is deferred to the CLI or explicit sync calls.
- **Concurrent Async Sync**: Metadata synchronization now supports parallel processing for large collections.

### 💻 Premium CLI Experience
The Magetools CLI has received several usability upgrades:
- **.env Support**: Automatically load your `GOOGLE_API_KEY` from a `.env` file for a smoother local development experience.
- **Improved Error Reporting**: Clear warnings when optional dependencies (like `python-dotenv`) are missing.
- **Windows Robustness**: Fixed encoding issues and removed problematic emojis to ensure a smooth experience on Windows terminals.

## 🛠️ Highlights from v1.1.0
- **Secure Spell Listing**: The new `list_spells` method allows agents to see available tools while respecting your `allowed_collections` security boundaries.
- **Enhanced Type Hinting**: Improved codebase robustness with comprehensive modern type hints.

## 📦 Getting Started with v1.2.0
Upgrade your project and rebuild your tool metadata:
```bash
# Update to latest version
uv add magetools[full]

# Refresh your tool summaries
uv run -m magetools scan
```

---
**Full Documentation**: [README.md](./README.md)
**Full Changelog**: [CHANGELOG.md](./CHANGELOG.md)
