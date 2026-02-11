# CLI Reference

The Magetools CLI is your toolkit for managing, auditing, and synchronizing distributed tool collections.

---

## `magetools init`
**Bootstrap a new collection.**

| Argument | Description |
|----------|-------------|
| `<directory>` | Target folder to initialize. |

**Key Actions:**
- Scans directory for Python spells.
- Generates a local `manifest.json`.
- Prepares the folder for **Strict Mode** loading.

---

## `magetools scan`
**Audit and Synchronize.**

This is the most critical command for production environments. It performs a deep audit of your tool ecosystem.

**Key Actions:**
- **Discovery**: Identifies all valid spells in the `.magetools` root.
- **Security Check**: Verifies manifest integrity and quarantine status.
- **Semantic Sync**: Indexes spells into the vector database for discovery query support.
- **Metadata Sync**: Generates technical summaries via LLM if code changes are detected.

---

## 🔧 Environment Variables

Magetools CLI automatically loads configurations from a `.env` file in your project root.

| Variable | Default | Role |
|----------|---------|------|
| `GOOGLE_API_KEY` | - | Required for primary embedding/summary providers. |
| `MAGETOOLS_MODEL` | `gemini-2.0-flash` | The model used for technical auto-summaries. |
| `MAGETOOLS_DEBUG` | `false` | Enables verbose trace logging for discovery. |
