# Getting Started with Magetools

## Installation

Install the core package:

```bash
uv add magetools
```

For full functionality (including Google GenAI and ChromaDB):

```bash
uv add magetools[full]
```

## Your First Spellbook (Grimorium)

1. **Create a tools directory**:
   ```bash
   mkdir .magetools
   ```

2. **Add a "Spell" (Tool)**:
   Create `.magetools/math_spells.py`:
   ```python
   def add_numbers(x: int, y: int) -> int:
       """Add two numbers together."""
       return x + y
   ```

3. **Initialize the Manifest**:
   Magetools requires a manifest for security:
   ```bash
   uv run -m magetools init .magetools
   ```

4. **Synchronize and Build Summaries**:
   Generate the vector search index and collection summaries:
   ```bash
   uv run -m magetools scan
   ```

4. **Use it in Python**:
   ```python
   from magetools.grimorium import Grimorium
   import asyncio

   async def main():
       # Google API Key can be set in a .env file
       grim = Grimorium()
       await grim.initialize()
       print(f"Loaded {len(grim.registry)} tools!")

   asyncio.run(main())
   ```
