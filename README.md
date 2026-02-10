# Magetools

> A Portable Grimorium for Agentic Tool Discovery.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-pass-brightgreen.svg)]()

Magetools gives autonomous AI agents scalable access to thousands of tools ("Spells") without overwhelming their context window. It uses a **Hierarchical Active Discovery** pattern to organize tools into collections ("Grimoriums") and lets agents discover only what they need, when they need it.

## Features

- **Active Discovery Protocol**: Agents search for capabilities, not specific function names.
- **Safe by Default**: Strict Mode requires explicit `manifest.json` to load any code.
- **Auto-Summarization**: Uses Google Gemini to automatically generate technical summaries for your tool collections (Performance optimized: non-blocking).
- **Stale Summary Detection**: Automatically detects code changes via folder hashing and triggers re-summarization via CLI.
- **Framework Agnostic**: Works with LangChain, Google ADK, or any custom agent loop.
- **Graceful Degradation**: Works without API keys using MockProvider (limited functionality).

## Installation

Using [uv](https://github.com/astral-sh/uv) (Recommended):

```bash
# Core package (minimal dependencies)
uv add magetools

# Full installation with all features
uv add magetools[full]
```

Using pip:

```bash
pip install magetools[full]
```

### Optional Dependencies

| Extra | Description |
|-------|-------------|
| `[google]` | Google GenAI provider for embeddings and summaries |
| `[vectordb]` | ChromaDB for vector storage |
| `[adk]` | Google ADK integration for agents |
| `[full]` | All of the above |

## Usage

### Quick Start

```bash
# 1. Create a collection folder
mkdir -p .magetools/file_ops

# 2. Initialize with manifest.json (required for Strict Mode)
uv run -m magetools init .magetools/file_ops
```

### Add Spells (Tools)

```python
# .magetools/file_ops/files.py
from magetools import spell

@spell
def list_files(path: str = "."):
    """Lists all files in the given directory."""
    import os
    return os.listdir(path)

@spell
def read_file(path: str):
    """Reads and returns the contents of a file."""
    with open(path, "r") as f:
        return f.read()
```

### Use with an Agent

```python
import asyncio
from magetools import Grimorium

async def main():
    # Initialize (scans .magetools folder and indexes spells)
    grimorium = Grimorium()
    
    try:
        # Get tools for your agent
        tools = await grimorium.get_tools()
        
        # Use with your agent framework
        # agent = Agent(tools=tools)
        # await agent.run("Find and read data.csv")
    finally:
        await grimorium.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Agent Discovery Flow

Magetools exposes 3 tools to your agent:

1. `discover_grimoriums(query)` – Search collection summaries
2. `discover_spells(grimorium_id, query)` – Search within a collection
3. `execute_spell(spell_name, arguments)` – Run a spell

**Example:**

> **User**: "Find and read the data.csv file."
>
> **Agent**:
> 1. `discover_grimoriums("file reading")` → `file_ops`
> 2. `discover_spells("file_ops", "read csv")` → `read_file`  
> 3. `execute_spell("file_ops.read_file", {"path": "data.csv"})`

## Strict Mode (Security)

> ⚠️ **Magetools runs in Strict Mode by default.**

Collections **require** a `manifest.json` file to load any Python code. This prevents accidental execution of arbitrary code.

```bash
# Enable a collection
uv run -m magetools init .magetools/my_collection
```

**manifest.json example:**

```json
{
  "version": "1.0",
  "enabled": true,
  "whitelist": ["list_files", "read_file"]
}
```

To disable Strict Mode (development only):

```python
grimorium = Grimorium(strict_mode=False)
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOOGLE_API_KEY` | – | Required for Google GenAI (can be set in `.env` file) |
| `MAGETOOLS_MODEL` | `gemini-2.5-flash` | LLM model for technical summaries |
| `MAGETOOLS_DEBUG` | `false` | Enable debug logging |

### YAML Configuration

Create `magetools.yaml` in your project root:

```yaml
model_name: gemini-2.5-flash
embedding_model: models/text-embedding-004
debug: false
```

## CLI Reference

```bash
uv run -m magetools init <directory>  # Generate manifest.json for a collection
uv run -m magetools scan              # Scan spells and build metadata summaries
uv run -m magetools --help            # Show all commands and options
```

## Support

- **Documentation**: [Full documentation site](https://IAmNo1Special.github.io/magetools)
- **Issues**: [GitHub Issues](https://github.com/IAmNo1Special/magetools/issues)
- **Discussions**: Open an issue for questions

## Roadmap

- [ ] Local embedding provider (no API key required)
- [ ] LangChain integration example
- [ ] Web UI for spell management

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Run tests: `uv run pytest`
4. Submit a pull request

For major changes, open an issue first to discuss.

## Authors

- **Malcom Godlike** - *Initial work*

## License

[MIT](https://choosealicense.com/licenses/mit/)

## Project Status

🚀 **Active Development** – This project is actively maintained and accepting contributions.
