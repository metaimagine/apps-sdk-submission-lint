# apps-sdk-submission-lint

`apps-sdk-submission-lint` is a small offline CLI for catching common Apps SDK-style submission metadata gaps before a human review pass.

It scans a local JSON manifest or app metadata file and reports practical issues around naming, descriptions, privacy policy links, content security policy domains, tool annotations, screenshots, and unsafe wording.

This tool is not OpenAI approval, certification, endorsement, or a guarantee that an app will pass any submission review.

## Why

App submission readiness often fails on simple metadata hygiene:

- vague or missing product descriptions
- missing privacy policy URL
- wildcard CSP domains
- tool metadata that does not explain read-only, destructive, or open-world behavior
- missing screenshots or review checklist
- wording that implies certification or approval

This CLI gives maintainers a fast local check that can run before publishing docs, opening a release PR, or asking someone else to review the package.

## Quickstart

```bash
cd projects/apps-sdk-submission-lint
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/apps-sdk-submission-lint scan examples/invalid-app.json
```

JSON output is available for CI or automation:

```bash
.venv/bin/apps-sdk-submission-lint scan examples/invalid-app.json --format json
```

## Example Output

```text
apps-sdk-submission-lint scan: examples/invalid-app.json
8 finding(s)

[ERROR] app.name.missing at $.name
  App name is missing.
  Fix: Add a clear app or tool name.

[ERROR] csp.connect.broad_domain at $.csp.connect_domains[0]
  CSP connect domain is too broad: *
  Fix: Replace wildcards with exact origins such as https://api.example.com.
```

## Manifest Shape

V0 intentionally accepts a flexible JSON object rather than enforcing one schema. The scanner recognizes common keys such as:

- `name`, `appName`, or `title`
- `description` or `appDescription`
- `privacyPolicyUrl`, `privacy_policy_url`, or `privacyPolicy`
- `csp.connect_domains` / `csp.connectDomains`
- `csp.resource_domains` / `csp.resourceDomains`
- `tools[].annotations.readOnlyHint`
- `tools[].annotations.destructiveHint`
- `tools[].annotations.openWorldHint`
- `screenshots` or `screenshotChecklist`

See [examples/valid-app.json](examples/valid-app.json) and [examples/invalid-app.json](examples/invalid-app.json).

## Rules

The MVP includes static checks for:

- missing app or tool name
- missing or too-short app/tool description
- missing privacy policy URL
- missing CSP connect/resource domains
- broad wildcard CSP connect/resource domains
- missing Apps SDK-style tool annotation hints: `readOnlyHint`, `destructiveHint`, `openWorldHint`
- missing screenshots checklist
- unsafe wording implying approval, certification, or endorsement

## Scope

`apps-sdk-submission-lint` is:

- static and offline
- focused on local JSON metadata
- designed for early submission hygiene checks
- intentionally conservative about wildcard domains and certification language

## Non-Goals

V0 does not:

- call OpenAI APIs or external services
- validate against an official submission schema
- inspect source code, screenshots, or hosted URLs
- prove legal, privacy, security, or policy compliance
- certify or approve any app

## Development

```bash
cd projects/apps-sdk-submission-lint
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest -q
```
