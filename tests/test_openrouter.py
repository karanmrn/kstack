import json
import os
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "skills" / "openrouter" / "scripts" / "openrouter"
SECRET = "sk-or-v1-test-secret-do-not-print"

_loader = SourceFileLoader("openrouter_cli", str(SCRIPT))
openrouter = module_from_spec(spec_from_loader("openrouter_cli", _loader))
_loader.exec_module(openrouter)

MODELS = [
    {
        "id": "acme/big",
        "name": "Acme: Big",
        "context_length": 200000,
        "pricing": {"prompt": "0.000003", "completion": "0.000015"},
        "supported_parameters": ["tools", "max_tokens"],
    },
    {
        "id": "acme/tiny:free",
        "name": "Acme: Tiny (free)",
        "context_length": 32768,
        "pricing": {"prompt": "0", "completion": "0"},
        "supported_parameters": ["max_tokens"],
    },
    {
        "id": "openrouter/auto",
        "name": "Auto Router",
        "context_length": 2000000,
        "pricing": {"prompt": "-1", "completion": "-1"},
    },
]


class FakeOpenRouter(BaseHTTPRequestHandler):
    requests: list[dict] = []

    def log_message(self, *_args):
        pass

    def send_json(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/api/v1/models":
            self.send_json(200, {"data": MODELS})
        else:
            self.send_json(404, {"error": {"message": "not found"}})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        FakeOpenRouter.requests.append({"auth": self.headers.get("Authorization"), "body": body})
        if self.headers.get("Authorization") != f"Bearer {SECRET}":
            self.send_json(401, {"error": {"message": "No auth credentials found"}})
            return
        if body["model"] == "acme/broke":
            self.send_json(402, {"error": {"message": "Insufficient credits"}})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        words = ["Hello", " from ", body["model"], "."]
        for word in words:
            chunk = {"choices": [{"delta": {"content": word}}]}
            self.wfile.write(f": OPENROUTER PROCESSING\n\ndata: {json.dumps(chunk)}\n\n".encode())
        usage = {"prompt_tokens": 7, "completion_tokens": 4, "cost": 0.00012}
        self.wfile.write(f"data: {json.dumps({'choices': [], 'usage': usage})}\n\ndata: [DONE]\n\n".encode())


class OpenRouterCliTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FakeOpenRouter)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_address[1]}/api/v1"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        FakeOpenRouter.requests.clear()
        self.temp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp.cleanup()

    def run_cli(self, *args: str, key: str | None = SECRET, key_file: str | None = None, stdin: str = ""):
        env = {k: v for k, v in os.environ.items() if not k.startswith("OPENROUTER_")}
        env["OPENROUTER_BASE_URL"] = self.base
        if key is not None:
            env["OPENROUTER_API_KEY"] = key
        if key_file is not None:
            env["OPENROUTER_KEY_FILE"] = key_file
        result = subprocess.run(
            [sys.executable, str(SCRIPT), *args], input=stdin, capture_output=True, text=True, env=env, timeout=30
        )
        self.assertNotIn(SECRET, result.stdout + result.stderr)
        return result

    def test_list_shows_prices_per_million_and_free_marker(self):
        result = self.run_cli("list", key=None)
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertEqual(lines[0].split(), ["id", "context", "$/M", "in", "$/M", "out", "free"])
        self.assertEqual(lines[1].split(), ["acme/big", "200,000", "3.00", "15.00"])
        self.assertEqual(lines[2].split(), ["acme/tiny:free", "32,768", "0", "0", "free"])
        self.assertEqual(lines[3].split(), ["openrouter/auto", "2,000,000", "var", "var"])
        self.assertIn("3 models.", result.stderr)

    def test_list_filter_matches_id_or_name(self):
        result = self.run_cli("list", "AUTO ROUTER")
        self.assertEqual([line.split()[0] for line in result.stdout.splitlines()[1:]], ["openrouter/auto"])
        missing = self.run_cli("list", "nothing-like-this")
        self.assertEqual(missing.returncode, 1)
        self.assertIn("no model matches", missing.stderr)

    def test_ask_streams_reply_and_reports_usage(self):
        result = self.run_cli("ask", "acme/big", "Say hello", "--max-tokens", "50")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Hello from acme/big.\n")
        self.assertIn("acme/big: 7 prompt + 4 completion tokens, cost $0.00012,", result.stderr)
        body = FakeOpenRouter.requests[0]["body"]
        self.assertEqual(body["messages"], [{"role": "user", "content": "Say hello"}])
        self.assertTrue(body["stream"])
        self.assertEqual(body["max_tokens"], 50)

    def test_ask_reads_prompt_from_stdin(self):
        result = self.run_cli("ask", "acme/big", "-", stdin="from a file\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(FakeOpenRouter.requests[0]["body"]["messages"][0]["content"], "from a file\n")

    def test_ask_reports_api_errors_in_one_line(self):
        result = self.run_cli("ask", "acme/broke", "hi")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "openrouter: OpenRouter returned HTTP 402: Insufficient credits\n")
        wrong = self.run_cli("ask", "acme/big", "hi", key="sk-or-wrong")
        self.assertIn("HTTP 401", wrong.stderr)

    def test_key_file_accepts_env_line_or_bare_key(self):
        env_file = Path(self.temp.name) / "keys.env"
        env_file.write_text(f"# keys\nOTHER_KEY=nope\nexport OPENROUTER_API_KEY=\"{SECRET}\"\n", encoding="utf-8")
        bare_file = Path(self.temp.name) / "key.txt"
        bare_file.write_text(f"{SECRET}\n", encoding="utf-8")
        for path in (env_file, bare_file):
            result = self.run_cli("ask", "acme/big", "hi", key=None, key_file=str(path))
            self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({r["auth"] for r in FakeOpenRouter.requests}, {f"Bearer {SECRET}"})

    def test_missing_key_is_a_clear_error_and_sends_nothing(self):
        result = self.run_cli("ask", "acme/big", "hi", key=None)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no API key", result.stderr)
        other = Path(self.temp.name) / "other.env"
        other.write_text("OTHER_KEY=nope\nMORE=1\n", encoding="utf-8")
        result = self.run_cli("ask", "acme/big", "hi", key=None, key_file=str(other))
        self.assertIn("has no OPENROUTER_API_KEY=<key> line", result.stderr)
        self.assertEqual(FakeOpenRouter.requests, [])

    def test_compare_prints_both_replies_side_by_side(self):
        result = self.run_cli("compare", "acme/big", "acme/tiny:free", "hi", "--width", "80")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertRegex(lines[0], r"^acme/big +\| acme/tiny:free$")
        self.assertRegex(lines[2], r"^Hello from acme/big\. +\| Hello from acme/tiny:free\.$")
        self.assertTrue(all(len(line) <= 80 for line in lines))
        self.assertEqual(result.stderr.count("7 prompt + 4 completion tokens"), 2)

    def test_compare_shows_one_failure_and_exits_nonzero(self):
        result = self.run_cli("compare", "acme/big", "acme/broke", "hi", "--width", "100")
        self.assertEqual(result.returncode, 1)
        self.assertIn("Hello from acme/big.", result.stdout)
        self.assertIn("ERROR: OpenRouter returned HTTP 402", result.stdout)

    def test_launch_prints_commands_that_reference_the_key_variable(self):
        result = self.run_cli("launch", "acme/big")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(
            f'ANTHROPIC_BASE_URL={self.base[:-3]} ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY" '
            "ANTHROPIC_API_KEY= claude --model acme/big",
            result.stdout,
        )
        self.assertIn("-c model_provider=openrouter", result.stdout)
        self.assertIn(f'base_url="{self.base}",env_key="OPENROUTER_API_KEY",wire_api="responses"', result.stdout)
        self.assertNotIn("warning", result.stderr)
        only = self.run_cli("launch", "acme/big", "--tool", "codex")
        self.assertTrue(only.stdout.startswith("codex -c model_provider=openrouter"))
        self.assertEqual(len(only.stdout.splitlines()), 1)

    def test_launch_warns_without_tool_calling_and_rejects_unknown_models(self):
        result = self.run_cli("launch", "acme/tiny:free", key=None)
        self.assertIn("does not list tool calling", result.stderr)
        self.assertIn("export OPENROUTER_API_KEY", result.stderr)
        unknown = self.run_cli("launch", "acme")
        self.assertEqual(unknown.returncode, 1)
        self.assertIn("Close matches: acme/big, acme/tiny:free", unknown.stderr)

    def test_launch_quotes_model_ids_for_the_shell(self):
        command = openrouter.launch_commands("odd/model;rm -rf ~")["claude"]
        self.assertTrue(command.endswith("--model 'odd/model;rm -rf ~'"))


if __name__ == "__main__":
    unittest.main()
