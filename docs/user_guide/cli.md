# CLI Reference

Magetools provides a command-line interface for managing your tool collections.

## `uv run -m magetools init`

Initialize a new tool collection directory.

**Usage:**
```bash
uv run -m magetools init <directory>
```

**What it does:**
- Scans the directory for Python files.
- Creates a `manifest.json` file.
- Enables the collection for Strict Mode.

---

## `uv run -m magetools scan`

Audit your tools and verify synchronization status.

**Usage:**
```bash
uv run -m magetools scan
```

**What it does:**
- Discovers all tools in the `.magetools` directory.
- Verifies manifest validity.
- Indexes spells into the vector store.
- **Synchronizes Metadata**: Automatically generates or updates `grimorium_summary.md` files for collections.
- Reports any failed imports (Quarantine).
---

## Environment Variables

Magetools supports loading environment variables from a `.env` file in your project root when using the CLI.

### Supporting `.env` Files
To enable `.env` support, ensure you have `python-dotenv` installed:
```bash
pip install python-dotenv
```

### Key Variables
| Variable | Description |
|----------|-------------|
| `GOOGLE_API_KEY` | Required for Google GenAI providers. |
| `MAGETOOLS_MODEL` | LLM model used for generating collection summaries. |
