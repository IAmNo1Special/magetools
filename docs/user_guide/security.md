# Security & Strict Mode

Magetools is designed from the ground up to prevent unauthorized code execution by AI agents.

---

## 🛡️ Strict Mode

By default, Magetools runs in **Strict Mode**. This is a safety layer that ensures no code is loaded or executed without explicit developer consent.

> [!IMPORTANT]
> In Strict Mode, Magetools will ignore any directory that does not contain a valid `manifest.json`.

---

## 📄 The Manifest (`manifest.json`)

The manifest is your control plane for collection-level security.

```json
{
  "name": "Math Collection",
  "description": "Basic arithmetic tools",
  "enabled": true,
  "whitelist": ["add_numbers", "multiply_numbers"]
}
```

- **`enabled`**: Set to `false` to instantly disable a collection.
- **`whitelist`**: Only functions listed here will be exposed to the agent.
- **`blacklist`**: Explicitly forbid specific functions, even if they have the `@spell` decorator.

---

## 🧪 Prompt Injection Protection

When generating automated metadata summaries, Magetools defends against **Indirect Prompt Injection**:

1.  **Sanitization**: We redact common "jailbreak" keywords from tool docstrings.
2.  **Delimitation**: Tool data is wrapped in hardened security markers to prevent the model from following instructions found in docstrings.

---

## 🏥 Quarantine

If a tool file fails to load due to syntax errors or security violations, it is moved to a virtual **Quarantine**. 

> [!WARNING]
> Tools in quarantine are completely inaccessible to the agent and will trigger a warning in the `magetools scan` report.
