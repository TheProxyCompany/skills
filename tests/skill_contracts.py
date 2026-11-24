"""Validate the party examples as data, without a Proxy app or live agent."""

import json
import re
import shlex

import yaml


def require(condition, message):
    if not condition:
        raise ValueError(message)


def frontmatter(text):
    match = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    require(match is not None, "missing YAML frontmatter")
    data = yaml.safe_load(match.group(1))
    require(isinstance(data, dict), "frontmatter must be a mapping")
    return data


def code_blocks(text, language):
    return re.findall(r"^```" + re.escape(language) + r"\n(.*?)^```\s*$", text, re.M | re.S)


def seat_commands(text):
    section = text.split("### Configure a seat without growing the roster", 1)
    require(len(section) == 2, "missing explicit seat workflow")
    blocks = code_blocks(section[1].split("### ", 1)[0], "bash")
    require(len(blocks) == 1, "expected one executable seat workflow")
    return [shlex.split(line) for line in blocks[0].splitlines() if line.strip()]


def validate_seat_commands(commands):
    """Reject roster mutations and ensure the configured loadout reaches the seat."""
    allowed = {
        ("proxy", "loadout", "create"),
        ("proxy", "loadout", "skill", "equip"),
        ("proxy", "loadout", "integration", "equip"),
        ("proxy", "party", "session", "add-participant"),
        ("proxy", "party", "session", "participants"),
        ("proxy", "agent", "self"),
    }
    groups = {}
    for index, command in enumerate(commands):
        matches = [prefix for prefix in allowed if tuple(command[:len(prefix)]) == prefix]
        require(len(matches) == 1, "unexpected command in seat workflow")
        groups.setdefault(matches[0][-1], []).append((index, command[len(matches[0]):]))

    for verb in ("create", "add-participant", "participants", "self"):
        require(len(groups.get(verb, [])) == 1, f"expected one {verb} command")
    created_at, create_args = groups["create"][0]
    seated_at, seat_args = groups["add-participant"][0]
    require(len(create_args) == 1 and len(seat_args) == 2, "invalid command arguments")
    loadout = json.loads(create_args[0])
    seat = json.loads(seat_args[1])
    require(loadout.get("agent_id") == "<EXISTING_CLAUDE_ID>", "reuse the existing Claude identity")
    require(seat.get("agent_id") == loadout["agent_id"], "seat must reuse the loadout owner")
    require(seat.get("loadout_id") == "<LOADOUT_ID>", "seat must bind the configured loadout")
    require(loadout.get("model_id") == "claude-fable-5-1", "select the catalog Fable model")
    require(loadout.get("provider_id") == "anthropic", "select the Fable provider")
    require(loadout.get("harness_id") == "claude-code", "select the Claude Code harness")
    require("backend_model" in loadout and loadout["backend_model"] is None,
            "clear the custom backend model override")
    require(not loadout.get("is_active"), "do not activate a global loadout")
    require(not seat.get("config_overrides", {}).get("seat_model"), "do not override the loadout model")

    equipment = groups.get("equip", [])
    require(len(equipment) == 2, "equip both the requested skill and integration")
    for index, args in equipment:
        require(created_at < index < seated_at, "equip before seating")
        require(len(args) == 2 and args[0] == seat["loadout_id"], "equip the selected loadout")
    require({tuple(command[:4]) for command in commands if command[3:4] == ["equip"]} == {
        ("proxy", "loadout", "skill", "equip"),
        ("proxy", "loadout", "integration", "equip"),
    }, "equip both the requested skill and integration")
    inspect_at, inspect_args = groups["participants"][0]
    self_at, self_args = groups["self"][0]
    require(inspect_at > seated_at and inspect_args == [seat_args[0]], "inspect the seated session")
    require(self_at > seated_at and self_args == ["--session", seat_args[0], "--agent", seat["agent_id"]],
            "inspect the effective agent loadout")
    return loadout


def validate_standing_example(team, loadout):
    seat = team.get("team", {}).get("worker", {})
    require(seat.get("agent") == "<EXISTING_CLAUDE_ID>", "reuse the existing Claude identity")
    require(seat.get("loadout") == "loadouts/fable-worker.md", "bind the file loadout to the seat")
    require(not team.get("roles", {}).get("worker", {}).get("model"), "do not override the loadout model")
    require(loadout.get("model_id") == "claude-fable-5-1", "select the catalog Fable model")
    require(not loadout.get("model"), "omit the custom backend model override")
    require(loadout.get("provider") == "anthropic", "select the Fable provider")
    require(loadout.get("harness") == "claude-code", "select the Claude Code harness")
    require(isinstance(loadout.get("name"), str) and bool(loadout["name"].strip()), "name the seat loadout")
    for field in ("skills", "integrations"):
        require(isinstance(loadout.get(field), list), f"{field} must be an explicit equipment list")
