# Getting Started

Follow these steps to set up Magetools and start building your own autonomous agentic toolsets.

---

## :material-numeric-1-circle: Installation

Install the full suite with all recommended providers:

```bash
uv add magetools[full]
```

> [!TIP]
> Use `magetools[full]` to automatically include **Google GenAI** for summaries and **ChromaDB** for vector indexing.

---

## :material-numeric-2-circle: Your First Collection

1.  **Create a folder** for your tools:
    ```bash
    mkdir .magetools
    ```

2.  **Add a Spell (Tool)**:
    Create `.magetools/math.py`:
    ```python
    from magetools import spell

    @spell
    def add(x: int, y: int) -> int:
        """Adds two integers for the agent."""
        return x + y
    ```

3.  **Initialize Security**:
    ```bash
    uv run -m magetools init .magetools
    ```

---

## :material-numeric-3-circle: Sync & Discover

Run the scanner to build your semantic index and technical summaries:

```bash
uv run -m magetools scan
```

---

## :material-numeric-4-circle: Run the Agent

```python
import asyncio
from magetools import Grimorium

async def main():
    # .env files are automatically loaded by the CLI
    grim = Grimorium()
    await grim.initialize()
    
    print(f"🧙‍♂️ Magetools loaded {len(grim.registry)} spells.")

asyncio.run(main())
```
