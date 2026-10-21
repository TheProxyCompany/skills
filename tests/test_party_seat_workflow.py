"""Replay the documented seat workflow through the real CLI into a local fixture.

Run: python3 -m unittest discover -s tests -v
Optional: PROXY_CLI=/path/to/proxy-cli
No requests reach a running Proxy instance; each test owns an ephemeral port.
"""

import json
import os
import re
import shlex
import shutil
import subprocess
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CLI = os.environ.get("PROXY_CLI") or shutil.which("proxy")
text = (ROOT / "skills/proxy-cli/SKILL.md").read_text()
section = text.split("### Configure a seat without growing the roster", 1)[1]
block = re.search(r"```bash\n(.*?)```", section, re.S).group(1)
fixtures = {
    "<EXISTING_CLAUDE_ID>": "claude",
    "<LOADOUT_ID>": "loadout-fable",
    "<SKILL_ID>": "repo-guide",
    "<CONNECTED_INTEGRATION_ID>": "github-1",
    "<SESSION_ID>": "fixture-party",
}
for old, new in fixtures.items():
    block = block.replace(old, new)
commands = [
    shlex.split(line)[1:] for line in block.splitlines() if line.startswith("proxy ")
]


class PartySeatWorkflowTests(unittest.TestCase):
    def setUp(self):
        if not CLI:
            self.skipTest("Install proxy or set PROXY_CLI to the CLI binary")
        self.requests = []
        self.fail_tuning = False
        self.loadout = {"id": "loadout-fable", "agent_id": "claude", "is_active": False}
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def run(self):
                body = json.loads(
                    self.rfile.read(int(self.headers.get("Content-Length", 0))) or "{}"
                )
                owner.requests.append((self.command, self.path, body))
                path = urlparse(self.path).path
                status = 200
                data = owner.loadout
                if path == "/cli/loadouts" and self.command == "POST":
                    owner.loadout.update(body)
                elif path.endswith("/tuning") and self.command == "PUT":
                    if owner.fail_tuning:
                        status = 400
                    else:
                        owner.loadout.update(body)
                elif path.endswith("/participants"):
                    data = (
                        dict(body, id="fixture-seat") if self.command == "POST" else []
                    )
                elif path == "/cli/agents/self":
                    data = {"participant_id": "fixture-seat", "loadout": owner.loadout}
                elif "/skills/" in path or "/integrations/" in path:
                    data = {"equipped": True}
                else:
                    status = 404
                result = (
                    {"ok": True, "data": data}
                    if status == 200
                    else {
                        "ok": False,
                        "error": (
                            "fixture tuning rejection"
                            if status == 400
                            else "unexpected route"
                        ),
                    }
                )
                payload = json.dumps(result).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_POST = do_PUT = do_GET = run

        self.server = HTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def call(self, args):
        self.assertFalse(
            any(
                arg in {"--host", "--port", "-p"}
                or arg.startswith(("--host=", "--port="))
                for arg in args
            ),
            "Documented commands must not override the isolated fixture address",
        )
        return subprocess.run(
            [CLI, "--host", "127.0.0.1", "--port", str(self.server.server_port), *args],
            text=True,
            capture_output=True,
            timeout=10,
            env={
                **os.environ,
                "NO_PROXY": "127.0.0.1,localhost",
                "no_proxy": "127.0.0.1,localhost",
            },
        )

    def test_documented_commands_keep_identity_model_harness_and_equipment(self):
        self.assertEqual(len(commands), 6)
        for args in commands:
            result = self.call(args)
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.loadout["agent_id"], "claude")
        self.assertEqual(self.loadout["model_id"], "claude-fable-5-1")
        self.assertEqual(self.loadout["provider_id"], "anthropic")
        self.assertEqual(self.loadout["harness_id"], "claude-code")
        self.assertIsNone(self.loadout["backend_model"])
        self.assertFalse(self.loadout["is_active"])
        routes = [(method, urlparse(path).path) for method, path, _ in self.requests]
        self.assertIn(("POST", "/cli/loadouts/loadout-fable/skills/repo-guide"), routes)
        self.assertIn(
            ("POST", "/cli/loadouts/loadout-fable/integrations/github-1"), routes
        )
        seat = next(
            body
            for method, path, body in self.requests
            if method == "POST" and path.endswith("/participants")
        )
        self.assertEqual(seat["agent_id"], "claude")
        self.assertEqual(seat["loadout_id"], "loadout-fable")
        self.assertNotIn(("POST", "/cli/agents"), routes)
        self.assertFalse(any(path.endswith("/activate") for _, path in routes))

    def test_tuning_rejection_surfaces_partial_creation_without_agent_fallback(self):
        self.fail_tuning = True
        result = self.call(commands[0])
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("fixture tuning rejection", result.stderr)
        self.assertEqual(
            [(method, path) for method, path, _ in self.requests],
            [("POST", "/cli/loadouts"), ("PUT", "/cli/loadouts/loadout-fable/tuning")],
        )
        self.assertEqual(self.loadout["name"], "Pricing review - Fable")
        self.assertNotIn("model_id", self.loadout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
