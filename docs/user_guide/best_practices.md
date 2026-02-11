# Best Practices

To get the most out of Magetools, follow these production-tested patterns for tool design and agentic architecture.

## Tool Design (Spells)

### 1. Granularity is Key
Don't create "God Spells" that do 50 things. Instead, create small, focused functions. This makes discovery more accurate and execution cheaper for the agent.

### 2. High-Quality Docstrings
Magetools uses your docstrings for semantic search and summarization. 
- **Good**: `def scan_logs(path: str): """Analyzes error patterns in the specified log file."""`
- **Bad**: `def logs(p): """Get logs."""`

---

## Agent Integration

### The Discovery Cycle
Instead of loading all tools at once, train your agent to follow the **Hierarchical Discovery** pattern:

1. **Broad Search**: Use `discover_grimoriums` to find relevant collections.
2. **Deep Search**: Use `discover_spells` to find the specific tool within a collection.
3. **Execution**: Call `execute_spell`.

This reduces context bloat and prevents the agent from getting "confused" by irrelevant tools.

### Graceful Teardown
Always use the `close()` method when your agent is finished to release ChromaDB and AI client resources.
```python
try:
    await grim.initialize()
    # ... logic ...
finally:
    await grim.close()
```
