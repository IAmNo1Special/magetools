# Magetools: Dynamic Tool Discovery for AI Agents

Magetools is a high-performance framework for **Active Tool Discovery**. It allows AI agents to dynamically find, load, and execute Python functions as tools at runtime, using a decentralized "Grimorium" (portable spellbook) pattern.

## 🧙‍♂️ Why Magetools?

- **Active Discovery Protocol**: Agents search for capabilities, not specific function names.
- **Hierarchical Discovery**: Agents can search high-level collection summaries powered by **Auto-Summarization** (Google Gemini).
- **Strict Security**: Optional "Strict Mode" requires cryptographic manifests for every tool collection.
- **Provider Agnostic**: Works with any LLM, with built-in optimizations for Google GenAI.
- **Zero Config**: Drop tools into a folder, and the agent finds them.

## 🚀 Quick Start

```python
from magetools.grimorium import Grimorium

# 1. Initialize the spellbook
grim = Grimorium()

# 2. Discover tools in .magetools/
await grim.initialize()

# 3. Use tools in your agent
# (Magetools handles the indexing and semantic search)
```

## 📚 Contents

- [Getting Started](user_guide/getting_started.md)
- [Core Concepts](user_guide/core_concepts.md)
- [Security & Strict Mode](user_guide/security.md)
- [CLI Reference](user_guide/cli.md)
