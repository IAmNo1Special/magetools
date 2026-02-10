# Core Concepts

## Grimorium (The Spellbook)
The `Grimorium` is the central coordinator. It manages the lifecycle of tools, their discovery, and their execution. It acts as a standard ADK `BaseToolset`.

## Spells (The Tools)
A "Spell" is simply a Python function. Magetools extracts the name, docstring, and signature to represent the tool to the LLM.

## Collections (The Chapters)
Tools are grouped into directories called **Collections**. Each collection can have its own `manifest.json` to control permissions and metadata.

## Active Discovery
Unlike static tool definitions, Magetools scans for new files and changes at runtime. This allows you to add capabilities to an agent without restarting the process or redeploying code.

## Metadata Summaries
To optimize discovery in large toolsets, Magetools uses LLMs to generate high-density technical summaries of tool collections. These "Grimorium Summaries" allow agents to perform hierarchical search, identifying relevant collections before searching for individual spells.
