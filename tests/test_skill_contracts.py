"""Hosted checks for actual skill examples, including regressions that must fail."""

import copy
import json
import unittest
from pathlib import Path

import yaml

from skill_contracts import (
    code_blocks,
    frontmatter,
    seat_commands,
    validate_seat_commands,
    validate_standing_example,
)

ROOT = Path(__file__).resolve().parents[1]


class SkillContractsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills = {path.parent.name: path.read_text() for path in (ROOT / "skills").glob("*/SKILL.md")}
        cls.commands = seat_commands(cls.skills["proxy-cli"])
        maker = cls.skills["party-maker"]
        section = maker.split("For a Fable seat, use the existing Claude ID in `team`:", 1)[1]
        cls.team = yaml.safe_load(code_blocks(section, "yaml")[0])
        cls.loadout = frontmatter(code_blocks(section, "markdown")[0])

    def test_all_skills_have_loadable_metadata(self):
        self.assertTrue(self.skills, "No skills discovered")
        for name, text in self.skills.items():
            with self.subTest(skill=name):
                metadata = frontmatter(text)
                self.assertEqual(metadata["name"], name)
                self.assertIsInstance(metadata["description"], str)
                self.assertTrue(metadata["description"].strip())

    def test_cli_example_configures_then_seats_existing_identity(self):
        validate_seat_commands(self.commands)

    def test_standing_example_binds_existing_identity_to_loadout(self):
        validate_standing_example(self.team, self.loadout)

    def test_fable_examples_agree_on_model_provider_and_harness(self):
        cli = validate_seat_commands(self.commands)
        for cli_field, file_field in (("model_id", "model_id"), ("provider_id", "provider"), ("harness_id", "harness")):
            self.assertEqual(cli[cli_field], self.loadout[file_field])

    def test_party_skill_routes_to_both_concrete_workflows(self):
        text = self.skills["proxy-parties"]
        for name in ("proxy-cli", "party-maker"):
            self.assertIn(f"`{name}`", text)
            self.assertIn(name, self.skills)

    def test_standing_manifest_uses_matching_roles_and_disabled_schedule(self):
        manifest = yaml.safe_load(code_blocks(self.skills["party-maker"], "yaml")[0])
        self.assertEqual(set(manifest["team"]), set(manifest["roles"]))
        self.assertIs(manifest["schedule"]["enabled"], False)
        for output in manifest["outputs"]:
            self.assertIn(output["from"], manifest["roles"])
        for role in manifest["roles"].values():
            self.assertIsNone(role.get("model"), "Example must not override seat loadout models")

    def test_rejects_roster_creation_global_activation_or_early_sending(self):
        for command in (
            ["proxy", "agent", "create", '{"name":"Fable Coder"}'],
            ["proxy", "loadout", "activate", "<LOADOUT_ID>"],
            ["proxy", "party", "session", "send", "<SESSION_ID>", "--content", "Start"],
        ):
            with self.subTest(command=command):
                with self.assertRaisesRegex(ValueError, "unexpected command"):
                    validate_seat_commands([command, *self.commands])

    def test_rejects_stale_custom_model_or_mismatched_harness(self):
        for field, value, error in (
            ("backend_model", "old-custom-model", "backend model override"),
            ("harness_id", "codex", "Claude Code harness"),
            ("agent_id", "fable-coder", "existing Claude identity"),
            ("is_active", True, "global loadout"),
        ):
            with self.subTest(field=field):
                commands = copy.deepcopy(self.commands)
                payload = json.loads(commands[0][-1])
                payload[field] = value
                commands[0][-1] = json.dumps(payload)
                with self.assertRaisesRegex(ValueError, error):
                    validate_seat_commands(commands)

    def test_rejects_wrong_seat_owner_missing_binding_and_model_override(self):
        for field, value, error in (
            ("agent_id", "fable-coder", "loadout owner"),
            ("loadout_id", None, "bind the configured loadout"),
            ("config_overrides", {"seat_model": "old-model"}, "override the loadout model"),
        ):
            with self.subTest(field=field):
                commands = copy.deepcopy(self.commands)
                seat = next(command for command in commands if "add-participant" in command)
                payload = json.loads(seat[-1])
                payload[field] = value
                seat[-1] = json.dumps(payload)
                with self.assertRaisesRegex(ValueError, error):
                    validate_seat_commands(commands)

    def test_rejects_missing_or_late_equipment(self):
        commands = copy.deepcopy(self.commands)
        equipment = commands.pop(1)
        with self.assertRaisesRegex(ValueError, "equip both"):
            validate_seat_commands(commands)
        commands.append(equipment)
        with self.assertRaisesRegex(ValueError, "equip before seating"):
            validate_seat_commands(commands)

    def test_rejects_file_loadout_custom_model_override(self):
        loadout = dict(self.loadout, model="old-custom-model")
        with self.assertRaisesRegex(ValueError, "backend model override"):
            validate_standing_example(self.team, loadout)

    def test_rejects_unbound_file_loadout_and_role_model_override(self):
        team = copy.deepcopy(self.team)
        del team["team"]["worker"]["loadout"]
        with self.assertRaisesRegex(ValueError, "bind the file loadout"):
            validate_standing_example(team, self.loadout)
        team = dict(self.team, roles={"worker": {"model": "old-model"}})
        with self.assertRaisesRegex(ValueError, "override the loadout model"):
            validate_standing_example(team, self.loadout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
