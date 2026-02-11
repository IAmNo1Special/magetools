# Magetools

> A Portable Grimorium for Agentic Tool Discovery.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-100%25-brightgreen.svg)]()

Magetools gives autonomous AI agents scalable access to thousands of tools ("Spells") without overwhelming their context window. It uses a **Hierarchical Active Discovery** pattern to organize tools into collections/directories ("Grimoriums") and files ("Chapters") and functions ("Spells"), allowing agents to discover only what they need, when they need it.

## Features

- **100% Test Coverage**: Fully verified core logic for maximum reliability.
- **Active Discovery Protocol**: Agents search for capabilities, not specific function names.
- **Safe by Default**: Strict Mode requires explicit `manifest.json` to load any code.
- **Auto-Summarization**: Uses Google Gemini to automatically generate technical summaries for your tool collections (Performance optimized: non-blocking).
- **Stale Summary Detection**: Automatically detects code changes via folder hashing and triggers re-summarization via CLI.
- **Google ADK Integration**: Works with Google ADK agents with more framework integrations coming soon.
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
# 1. Create a Grimorium(folder) in the .magetools directory
mkdir -p .magetools/file_ops

# 2. Creates the manifest.json for the provided Grimorium(required for Strict Mode)
uv run -m magetools init .magetools/file_ops

# 3. Scan the Grimorium for spells(functions)
# This creates a grimorium_summary.md file with the technical summary of the spells
# and stores the vector embeddings of the spells in a vector database
uv run -m magetools scan
```

### Add Spells (Tools)

```python
# .magetools/file_ops/files.py (A Grimorium chapter is just a .py file in a Grimorium.)
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
from google.adk.agents import LlmAgent
from magetools import Grimorium


# Initialize (scans .magetools folder and indexes spells)
grimorium = Grimorium()

# Initialize the root agent
root_agent = LlmAgent(
    name="magetools_agent",
    model="gemini-2.5-flash",
    description="Agent that uses magetools to discover and execute spells.",
    instruction=f"""You are an advanced AI assistant with access to magetools.
    Be helpful, concise, and focus on solving the user's request effectively.
    {grimorium.usage_guide}""",
    tools=[grimorium],
)

```

### Agent Discovery Flow

A Magetools Grimorium exposes 4 tools to your agent:

1. `discover_grimoriums(query)` – Search for a grimorium using a query
2. `discover_spells(grimorium_id, query)` – Search for a spell within a grimorium
3. `execute_spell(spell_name, arguments)` – Run a spell
4. `list_spells()` – List the names of all available spells from all linked grimoriums(may remove this soon...)

**Example:**

> **User**: "Find and read the data.csv file."
>
> **Agent**:
> 1. `discover_grimoriums("file reading")` → `file_ops`
> 2. `discover_spells("file_ops", "read csv")` → `read_file`  
> 3. `execute_spell("file_ops.read_file", {"path": "data.csv"})`

## Strict Mode (Security)

> ⚠️ **Magetools runs in Strict Mode by default.**

Grimoriums **require** a `manifest.json` file to load any Python code. This prevents accidental execution of arbitrary code.

```bash
# Enable a grimorium
uv run -m magetools init .magetools/my_grimorium
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
uv run -m magetools init <directory>  # Generate manifest.json for a grimorium
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
