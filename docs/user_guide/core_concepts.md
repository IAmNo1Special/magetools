# Core Concepts

Magetools is built on the philosophy of **Decentralized Discovery**. Instead of a monolithic tool registry, your tools are treated as first-class citizens of the filesystem.

---

## 📘 Grimorium (The Spellbook)
The `Grimorium` is the central coordinator of the Magetools framework. It manages the lifecycle of tools, their discovery, and their execution. It implements the standard ADK `BaseToolset` interface, making it drop-in compatible with modern agent frameworks.

---

## 🪄 Spells (The Tools)
A **Spell** is a standard Python function decorated with `@spell`. Magetools extracts the name, docstring, and type-hinted signature to represent the tool to the LLM. 

> [!NOTE]
> High-quality docstrings are critical for semantic discovery.

---

## 📁 Collections (The Chapters)
Tools are logically grouped into directories called **Collections**. Each collection is a self-contained unit with its own:
- **`manifest.json`**: Security and permission settings.
- **`grimorium_summary.md`**: Technical overview for agents.

---

## 🔍 Active Discovery
Unlike static tool definitions, Magetools scans for new files and edits at runtime. This allows you to hot-swap capabilities in an agent without downtime or redeploys.

---

## 🧠 Metadata Summaries
To optimize discovery in massive toolsets, Magetools uses LLMs to generate high-density technical summaries. These summaries enable **Hierarchical Search**, allowing agents to find the general "domain" before searching for a specific function.
