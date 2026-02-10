# Security & Strict Mode

Magetools is designed for safe execution of agentic tools.

## Strict Mode
By default, Magetools runs in **Strict Mode**. This means:
1. Every tool collection MUST have a `manifest.json`.
2. The manifest must have `"enabled": true`.
3. Only safe imports are allowed (imports are sanitized).

## The Manifest (`manifest.json`)
The manifest allows fine-grained control over what tools are exposed:

```json
{
  "name": "Math Collection",
  "description": "Basic arithmetic tools",
  "enabled": true,
  "whitelist": ["add_numbers", "multiply_numbers"],
  "blacklist": ["secret_function"]
}
```

## Quarantine
If a spell file contains syntax errors or fails to load during discovery, it is moved to a virtual **Quarantine**. This prevents a single broken file from crashing the entire system.

## Prompt Injection Protection
When generating metadata summaries, Magetools takes precautions against Indirect Prompt Injection:
- **Docstring Sanitization**: Common injection keywords are redacted from tool docstrings before being sent to the LLM.
- **Trusted Boundaries**: LLM prompts use explicit security delimiters to ensure the model treats tool documentation as data rather than instructions.
