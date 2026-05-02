import json

from apps_sdk_submission_lint.cli import main
from apps_sdk_submission_lint.manifest import load_manifest
from apps_sdk_submission_lint.rules import scan_manifest


def test_load_manifest_reads_json_file(tmp_path):
    manifest_path = tmp_path / "app.json"
    manifest_path.write_text(
        json.dumps(
            {
                "name": "Calendar Scout",
                "description": "Finds free meeting windows across team calendars.",
            }
        ),
        encoding="utf-8",
    )

    manifest = load_manifest(manifest_path)

    assert manifest["name"] == "Calendar Scout"
    assert manifest["description"].startswith("Finds free")


def test_scan_reports_core_submission_gaps():
    findings = scan_manifest(
        {
            "name": "",
            "description": "Short.",
            "privacyPolicyUrl": "",
            "csp": {
                "connect_domains": ["*"],
                "resource_domains": ["https://cdn.example.com"],
            },
            "tools": [
                {
                    "name": "delete_event",
                    "description": "Deletes calendar events.",
                    "annotations": {"readOnlyHint": False},
                }
            ],
            "screenshots": [],
        }
    )

    rule_ids = {finding.rule_id for finding in findings}
    assert "app.name.missing" in rule_ids
    assert "app.description.too_short" in rule_ids
    assert "privacy_policy.missing" in rule_ids
    assert "csp.connect.broad_domain" in rule_ids
    assert "tool.annotations.missing_hint" in rule_ids
    assert "screenshots.missing" in rule_ids


def test_scan_flags_unsafe_approval_wording():
    findings = scan_manifest(
        {
            "name": "Approved App",
            "description": "Officially certified by OpenAI for every workspace.",
            "privacyPolicyUrl": "https://example.com/privacy",
            "csp": {
                "connect_domains": ["https://api.example.com"],
                "resource_domains": ["https://cdn.example.com"],
            },
            "tools": [
                {
                    "name": "search_docs",
                    "description": "Searches documents without changing them.",
                    "annotations": {
                        "readOnlyHint": True,
                        "destructiveHint": False,
                        "openWorldHint": False,
                    },
                }
            ],
            "screenshots": [{"path": "screenshots/search.png"}],
        }
    )

    assert [finding.rule_id for finding in findings] == ["wording.unsafe_approval_claim"]


def test_cli_json_output_contains_findings(tmp_path, capsys):
    manifest_path = tmp_path / "app.json"
    manifest_path.write_text(
        json.dumps(
            {
                "name": "Expense Helper",
                "description": "Tracks expenses.",
                "privacyPolicyUrl": "https://example.com/privacy",
                "csp": {
                    "connect_domains": [],
                    "resource_domains": ["*"],
                },
                "tools": [],
                "screenshots": [{"path": "screenshots/home.png"}],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(["scan", str(manifest_path), "--format", "json"])
    output = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert output["summary"]["findings"] == 3
    assert {item["rule_id"] for item in output["findings"]} == {
        "app.description.too_short",
        "csp.connect.missing_domains",
        "csp.resource.broad_domain",
    }
