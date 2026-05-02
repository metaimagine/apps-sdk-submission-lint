"""Static offline lint rules for Apps SDK-style submission metadata."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable


MIN_DESCRIPTION_CHARS = 24
REQUIRED_HINTS = ("readOnlyHint", "destructiveHint", "openWorldHint")
UNSAFE_APPROVAL_PHRASES = (
    "approved by openai",
    "certified by openai",
    "openai approved",
    "openai certified",
    "officially certified",
    "officially approved",
)
BROAD_DOMAINS = {"*", "*://*", "https://*", "http://*"}


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    message: str
    path: str
    help: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def scan_manifest(manifest: dict[str, Any]) -> list[Finding]:
    """Return lint findings for a parsed manifest object."""
    findings: list[Finding] = []
    app_name = _first_text(manifest, "name", "appName", "title")
    app_description = _first_text(manifest, "description", "appDescription")

    if not app_name:
        findings.append(
            Finding(
                "app.name.missing",
                "error",
                "App name is missing.",
                "$.name",
                "Add a clear app or tool name.",
            )
        )

    if not app_description or len(app_description.strip()) < MIN_DESCRIPTION_CHARS:
        findings.append(
            Finding(
                "app.description.too_short",
                "error",
                "Description is missing or too short.",
                "$.description",
                f"Add a specific description with at least {MIN_DESCRIPTION_CHARS} characters.",
            )
        )

    if not _first_text(manifest, "privacyPolicyUrl", "privacy_policy_url", "privacyPolicy"):
        findings.append(
            Finding(
                "privacy_policy.missing",
                "error",
                "Privacy policy URL is missing.",
                "$.privacyPolicyUrl",
                "Provide a public URL explaining data collection, use, and retention.",
            )
        )

    _check_csp(findings, manifest)
    _check_tools(findings, manifest)
    _check_screenshots(findings, manifest)
    _check_unsafe_wording(findings, manifest)
    return findings


def _check_csp(findings: list[Finding], manifest: dict[str, Any]) -> None:
    csp = manifest.get("csp") or manifest.get("contentSecurityPolicy") or {}
    if not isinstance(csp, dict):
        csp = {}

    connect_domains = _domains(csp, "connect_domains", "connectDomains", "connect-src")
    resource_domains = _domains(csp, "resource_domains", "resourceDomains", "resource-src", "img-src")

    for label, domains in (("connect", connect_domains), ("resource", resource_domains)):
        if not domains:
            findings.append(
                Finding(
                    f"csp.{label}.missing_domains",
                    "error",
                    f"CSP {label} domains are missing.",
                    f"$.csp.{label}_domains",
                    "Declare the specific domains this app needs instead of relying on implicit access.",
                )
            )
            continue
        for index, domain in enumerate(domains):
            if _is_broad_domain(domain):
                findings.append(
                    Finding(
                        f"csp.{label}.broad_domain",
                        "error",
                        f"CSP {label} domain is too broad: {domain}",
                        f"$.csp.{label}_domains[{index}]",
                        "Replace wildcards with exact origins such as https://api.example.com.",
                    )
                )


def _check_tools(findings: list[Finding], manifest: dict[str, Any]) -> None:
    tools = manifest.get("tools")
    if not isinstance(tools, list) or not tools:
        return

    for tool_index, tool in enumerate(tools):
        if not isinstance(tool, dict):
            continue
        if not _first_text(tool, "name", "toolName"):
            findings.append(
                Finding(
                    "tool.name.missing",
                    "error",
                    "Tool name is missing.",
                    f"$.tools[{tool_index}].name",
                    "Give every exposed tool a stable, descriptive name.",
                )
            )
        if not _first_text(tool, "description") or len(_first_text(tool, "description")) < MIN_DESCRIPTION_CHARS:
            findings.append(
                Finding(
                    "tool.description.too_short",
                    "warning",
                    "Tool description is missing or too short.",
                    f"$.tools[{tool_index}].description",
                    "Explain what the tool does and when the model should use it.",
                )
            )

        annotations = tool.get("annotations")
        if not isinstance(annotations, dict):
            annotations = {}
        for hint in REQUIRED_HINTS:
            if hint not in annotations:
                findings.append(
                    Finding(
                        "tool.annotations.missing_hint",
                        "error",
                        f"Tool annotation is missing: {hint}",
                        f"$.tools[{tool_index}].annotations.{hint}",
                        "Set readOnlyHint, destructiveHint, and openWorldHint explicitly for each tool.",
                    )
                )


def _check_screenshots(findings: list[Finding], manifest: dict[str, Any]) -> None:
    screenshots = manifest.get("screenshots") or manifest.get("screenshotChecklist")
    if not screenshots:
        findings.append(
            Finding(
                "screenshots.missing",
                "warning",
                "Screenshots checklist is missing.",
                "$.screenshots",
                "Track required screenshots or review images before submission.",
            )
        )


def _check_unsafe_wording(findings: list[Finding], manifest: dict[str, Any]) -> None:
    text = " ".join(str(value) for value in _walk_values(manifest)).lower()
    if any(phrase in text for phrase in UNSAFE_APPROVAL_PHRASES):
        findings.append(
            Finding(
                "wording.unsafe_approval_claim",
                "error",
                "Wording implies OpenAI approval or certification.",
                "$",
                "Use factual language and avoid claiming approval, certification, or endorsement.",
            )
        )


def _first_text(mapping: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _domains(mapping: dict[str, Any], *keys: str) -> list[str]:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str) and value.strip():
            return [value.strip()]
    return []


def _is_broad_domain(domain: str) -> bool:
    normalized = domain.strip().lower()
    return normalized in BROAD_DOMAINS or normalized.startswith("*.") or normalized.startswith("https://*.")


def _walk_values(value: Any) -> Iterable[Any]:
    if isinstance(value, dict):
        for nested in value.values():
            yield from _walk_values(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _walk_values(nested)
    else:
        yield value
