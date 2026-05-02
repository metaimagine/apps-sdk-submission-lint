# Contributing

Thanks for helping improve `apps-sdk-submission-lint`.

This project is a small offline CLI. Contributions should keep it practical, conservative, and easy to run locally.

## Local Setup

```bash
cd projects/apps-sdk-submission-lint
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```

To try the CLI after installation:

```bash
.venv/bin/apps-sdk-submission-lint scan examples/invalid-app.json
.venv/bin/apps-sdk-submission-lint scan examples/invalid-app.json --format json
```

## Contribution Rules

- Keep checks static and offline unless a future issue explicitly scopes network behavior.
- Do not claim or imply OpenAI approval, certification, endorsement, or guaranteed submission acceptance.
- Prefer precise, actionable findings over broad policy language.
- Add or update focused tests when changing scanner behavior.
- Keep examples free of secrets, tokens, private URLs, or real customer data.
- Preserve backward-compatible JSON output unless a versioned change is documented.
- Use official or primary sources when documenting current Apps SDK, OpenAI, GitHub, package manager, or security claims.

## Pull Request Checklist

- Tests pass with `.venv/bin/python -m pytest -q`.
- README, examples, or changelog are updated when behavior changes.
- New rules include a rule id, clear message, and concrete fix guidance.
- The disclaimer remains clear: this tool is independent and does not approve or certify apps.
