"""Defiant Language Generator v0.1.

Deterministic structured-intent-to-DL emission for the locked v0.2.4 parser.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from defiant_parser_v0_2_4 import DefiantParseError, DefiantParser


class GeneratorError(Exception):
    """Raised when an intent record cannot safely emit valid DL."""


_SNAKE_CASE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
_IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def generate_dl(intent_record: dict) -> str:
    _validate_intent_record(intent_record)

    sections: List[str] = []
    imports = [_emit_import(item) for item in intent_record["imports"]]
    declarations = [_emit_declaration(item) for item in intent_record["declarations"]]

    if imports:
        sections.append("\n".join(imports))
    if declarations:
        sections.append("\n".join(declarations))

    context_lines = [f'Hey {intent_record["context_type"]} {intent_record["context_id"]},']

    for sequence in intent_record["sequences"]:
        context_lines.append("")
        context_lines.append(f'So {sequence["name"]}:')
        for action in sequence["actions"]:
            context_lines.append(f"    {_emit_action(action)}")

    for rule in intent_record["rules"]:
        context_lines.append("")
        context_lines.append(f'{_emit_rule_header(rule)}:')
        for action in rule["actions"]:
            context_lines.append(f"    {_emit_action(action)}")

    for policy in intent_record["policies"]:
        context_lines.append("")
        context_lines.append("You know what,")
        for intercept in policy["intercepts"]:
            context_lines.append(f'{intercept["timing"]} action {intercept["action"]}:')
            for constraint in intercept["constraints"]:
                context_lines.append(f"    {_emit_action(constraint)}")

    sections.append("\n".join(context_lines))
    return "\n\n".join(sections) + "\n"


def generate_and_validate(intent_record: dict) -> dict:
    dl_source = generate_dl(intent_record)
    parser = DefiantParser()
    try:
        ast = parser.parse(dl_source)
    except DefiantParseError as exc:
        raise GeneratorError(f"Generated DL failed parser validation: {exc}") from exc
    return {"ok": True, "dl": dl_source, "ast": ast}


def _validate_intent_record(intent_record: dict) -> None:
    if not isinstance(intent_record, dict):
        raise GeneratorError("Intent record must be a dict")

    for key in ("imports", "declarations", "context_type", "context_id", "sequences", "rules", "policies"):
        if key not in intent_record:
            raise GeneratorError(f"Missing required key: {key}")

    _reject_tabs(intent_record)
    _validate_identifier(intent_record["context_type"], "context_type")
    _validate_identifier(intent_record["context_id"], "context_id")
    _validate_not_run(intent_record["context_type"], "context_type")
    _validate_not_run(intent_record["context_id"], "context_id")

    for key in ("imports", "declarations", "sequences", "rules", "policies"):
        if not isinstance(intent_record[key], list):
            raise GeneratorError(f"{key} must be a list")

    for item in intent_record["imports"]:
        _validate_import(item)
    for item in intent_record["declarations"]:
        _validate_declaration(item)
    for sequence in intent_record["sequences"]:
        _validate_sequence(sequence)
    for rule in intent_record["rules"]:
        _validate_rule(rule)
    for policy in intent_record["policies"]:
        _validate_policy(policy)


def _validate_import(item: dict) -> None:
    _require_dict(item, "import")
    for key in ("type", "id", "library"):
        _require_key(item, key, "import")
    _validate_identifier(item["type"], "import.type")
    _validate_identifier(item["id"], "import.id")
    _validate_not_run(item["id"], "import.id")
    if not isinstance(item["library"], str) or not item["library"]:
        raise GeneratorError("import.library must be a non-empty string")


def _validate_declaration(item: dict) -> None:
    _require_dict(item, "declaration")
    for key in ("type", "id"):
        _require_key(item, key, "declaration")
    _validate_identifier(item["type"], "declaration.type")
    _validate_identifier(item["id"], "declaration.id")
    _validate_not_run(item["id"], "declaration.id")
    if "at_type" in item:
        _validate_identifier(item["at_type"], "declaration.at_type")
        _require_key(item, "at_id", "declaration")
        _validate_token(item["at_id"], "declaration.at_id")
    if "as" in item and not isinstance(item["as"], str):
        raise GeneratorError("declaration.as must be a string")


def _validate_sequence(sequence: dict) -> None:
    _require_dict(sequence, "sequence")
    for key in ("name", "actions"):
        _require_key(sequence, key, "sequence")
    if not isinstance(sequence["name"], str) or not _SNAKE_CASE.match(sequence["name"]):
        raise GeneratorError("So sequence names must be snake_case")
    _validate_not_run(sequence["name"], "sequence.name")
    if not isinstance(sequence["actions"], list):
        raise GeneratorError("sequence.actions must be a list")
    for action in sequence["actions"]:
        if any(key in action for key in ("trigger", "subject", "event", "rules")):
            raise GeneratorError("Conditional blocks are not allowed inside sequences")
        _validate_action(action)


def _validate_rule(rule: dict) -> None:
    _require_dict(rule, "rule")
    for key in ("subject", "event", "actions"):
        _require_key(rule, key, "rule")
    _validate_token(rule["subject"], "rule.subject")
    if rule["event"] not in DefiantParser.EVENT_VERBS:
        raise GeneratorError(f"Unsupported event verb: {rule['event']}")
    if "detail" in rule:
        _validate_phrase(rule["detail"], "rule.detail")
    if not isinstance(rule["actions"], list):
        raise GeneratorError("rule.actions must be a list")
    for action in rule["actions"]:
        _validate_action(action)


def _validate_policy(policy: dict) -> None:
    _require_dict(policy, "policy")
    _require_key(policy, "intercepts", "policy")
    if not isinstance(policy["intercepts"], list):
        raise GeneratorError("policy.intercepts must be a list")
    for intercept in policy["intercepts"]:
        _require_dict(intercept, "intercept")
        for key in ("timing", "action", "constraints"):
            _require_key(intercept, key, "intercept")
        if intercept["timing"] not in {"before", "during", "after"}:
            raise GeneratorError(f"Unsupported intercept timing: {intercept['timing']}")
        if intercept["action"] not in DefiantParser.HIGH_RISK_ACTIONS:
            raise GeneratorError(f"Unsupported high-risk action: {intercept['action']}")
        if not isinstance(intercept["constraints"], list):
            raise GeneratorError("intercept.constraints must be a list")
        for constraint in intercept["constraints"]:
            _validate_action(constraint)


def _validate_action(action: dict) -> None:
    _require_dict(action, "action")
    _require_key(action, "verb", "action")
    if action["verb"] not in DefiantParser.VERBS:
        raise GeneratorError(f"Unsupported verb: {action['verb']}")

    if action["verb"] == "run":
        _require_key(action, "sequence_id", "action")
        if not isinstance(action["sequence_id"], str) or not _SNAKE_CASE.match(action["sequence_id"]):
            raise GeneratorError("run sequence_id must be snake_case")
        return

    has_typed_target = "target_type" in action or "target_id" in action
    if has_typed_target:
        for key in ("target_type", "target_id"):
            _require_key(action, key, "action")
        if action["target_type"] not in DefiantParser.TYPED_TARGETS:
            raise GeneratorError(f"Unsupported target type: {action['target_type']}")
        _validate_token(action["target_id"], "action.target_id")
    elif "noun" in action:
        _validate_token(action["noun"], "action.noun")
    else:
        raise GeneratorError("Action must include target_type/target_id, noun, or sequence_id")

    if "on_device" in action and action["on_device"] not in DefiantParser.DEVICE_POSITIONS:
        raise GeneratorError(f"Unsupported device position: {action['on_device']}")
    if "at" in action:
        _validate_at(action["at"])
    if "from_target" in action:
        _validate_token(action["from_target"], "action.from_target")


def _validate_at(value: Any) -> None:
    if not isinstance(value, dict):
        raise GeneratorError("action.at must be a dict")
    _require_key(value, "literal", "action.at")
    _validate_token(value["literal"], "action.at.literal")
    if "value" in value:
        _validate_token(value["value"], "action.at.value")
    if "unit" in value:
        _validate_token(value["unit"], "action.at.unit")


def _emit_import(item: dict) -> str:
    return f'import {item["type"]} {item["id"]} from library "{item["library"]}"'


def _emit_declaration(item: dict) -> str:
    line = f'define {item["type"]} {item["id"]}'
    if "at_type" in item:
        line += f' at {item["at_type"]} {item["at_id"]}'
    if "as" in item:
        line += f' as "{item["as"]}"'
    return line


def _emit_rule_header(rule: dict) -> str:
    header = f'when {rule["subject"]} {rule["event"]}'
    if "detail" in rule:
        header += f' {rule["detail"]}'
    return header


def _emit_action(action: dict) -> str:
    if action["verb"] == "run":
        return f'run {action["sequence_id"]}'

    if "target_type" in action:
        line = f'{action["verb"]} {action["target_type"]} {action["target_id"]}'
    else:
        line = f'{action["verb"]} {action["noun"]}'

    if "on_device" in action:
        line += f' on device {action["on_device"]}'
    if "at" in action:
        line += f' at {action["at"]["literal"]}'
        if "value" in action["at"]:
            value = f'{action["at"]["value"]}{action["at"].get("unit", "")}'
            line += f" {value}"
    if "from_target" in action:
        line += f' from {action["from_target"]}'
    return line


def _require_dict(value: Any, name: str) -> None:
    if not isinstance(value, dict):
        raise GeneratorError(f"{name} must be a dict")


def _require_key(value: dict, key: str, name: str) -> None:
    if key not in value:
        raise GeneratorError(f"Missing required key {name}.{key}")


def _validate_identifier(value: Any, name: str) -> None:
    if not isinstance(value, str) or not _IDENTIFIER.match(value):
        raise GeneratorError(f"{name} must be an identifier")


def _validate_token(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value or any(char.isspace() for char in value):
        raise GeneratorError(f"{name} must be a non-empty token")


def _validate_phrase(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise GeneratorError(f"{name} must be a non-empty phrase")


def _validate_not_run(value: str, name: str) -> None:
    if value == "run":
        raise GeneratorError(f"{name} cannot be 'run'")


def _reject_tabs(value: Any) -> None:
    if isinstance(value, str):
        if "\t" in value:
            raise GeneratorError("Tabs are not allowed in intent records")
    elif isinstance(value, dict):
        for item in value.values():
            _reject_tabs(item)
    elif isinstance(value, list):
        for item in value:
            _reject_tabs(item)


EXAMPLE_INTENTS = [
    {
        "name": "ar_workspace_defiantsky_tool_activation",
        "intent": {
            "imports": [{"type": "tool", "id": "glove_tools", "library": "defiant-ar-v1"}],
            "declarations": [
                {"type": "workspace", "id": "DefiantSky"},
                {"type": "window", "id": "main_cad"},
            ],
            "context_type": "workspace",
            "context_id": "DefiantSky",
            "sequences": [],
            "rules": [
                {
                    "subject": "project",
                    "event": "opens",
                    "actions": [
                        {"verb": "restore", "target_type": "layout", "target_id": "last"},
                        {
                            "verb": "anchor",
                            "target_type": "window",
                            "target_id": "main_cad",
                            "at": {"literal": "distance", "value": "1.2", "unit": "m"},
                        },
                        {
                            "verb": "enable",
                            "target_type": "tool",
                            "target_id": "glove_tools",
                            "on_device": "left_wrist",
                        },
                    ],
                }
            ],
            "policies": [],
        },
    },
    {
        "name": "agent_cleanup_plan",
        "intent": {
            "imports": [{"type": "tool", "id": "FileOrganizer", "library": "defiant-agents-v1"}],
            "declarations": [{"type": "workspace", "id": "DefiantSky"}],
            "context_type": "agent",
            "context_id": "FileOrganizer",
            "sequences": [
                {
                    "name": "cleanup_plan",
                    "actions": [
                        {"verb": "scan", "noun": "duplicates"},
                        {"verb": "prepare", "noun": "summary"},
                        {"verb": "require", "noun": "confirmation"},
                    ],
                }
            ],
            "rules": [
                {
                    "subject": "cleanup",
                    "event": "requested",
                    "actions": [{"verb": "run", "sequence_id": "cleanup_plan"}],
                }
            ],
            "policies": [
                {
                    "intercepts": [
                        {
                            "timing": "before",
                            "action": "delete",
                            "constraints": [
                                {"verb": "require", "noun": "confirmation"},
                                {"verb": "log", "target_type": "action", "target_id": "full"},
                            ],
                        }
                    ]
                }
            ],
        },
    },
    {
        "name": "optics_reading_zoom",
        "intent": {
            "imports": [],
            "declarations": [{"type": "optics", "id": "user_profile"}],
            "context_type": "optics",
            "context_id": "user_profile",
            "sequences": [],
            "rules": [
                {
                    "subject": "glasses",
                    "event": "is_worn",
                    "actions": [{"verb": "apply", "noun": "correction", "from_target": "profile"}],
                },
                {
                    "subject": "text",
                    "event": "is_detected",
                    "actions": [{"verb": "set", "noun": "reading_zoom", "at": {"literal": "1.6x"}}],
                },
            ],
            "policies": [],
        },
    },
]


def run_test_harness() -> dict:
    results = []
    for example in EXAMPLE_INTENTS:
        result = generate_and_validate(example["intent"])
        results.append({"name": example["name"], "ok": result["ok"]})
        print(f'PASS {example["name"]}')
    return {"ok": all(item["ok"] for item in results), "results": results}


if __name__ == "__main__":
    harness_result = run_test_harness()
    if not harness_result["ok"]:
        raise SystemExit(1)
