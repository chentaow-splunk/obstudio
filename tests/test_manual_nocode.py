import copy
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "examples/nocode-manual/check_spans.py"
SPEC = importlib.util.spec_from_file_location("manual_nocode", SCRIPT)
LAB = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(LAB)


def receipt(language):
    spans = []
    for index, channel in enumerate(("web", "unknown", "throw"), start=1):
        attributes = {"checkout.channel": channel}
        if language == "node" and channel == "unknown":
            attributes = {}
        spans.append({
            "traceId": f"{index:032x}", "spanId": f"{index:016x}",
            "name": f"lab.{language}.checkout", "kind": "internal",
            "scope": {"name": "OpenTelemetry.NoCode"}, "durationMs": 80,
            "attributes": attributes,
            "status": {"code": "ERROR" if channel == "throw" else "UNSET"},
            "events": [{"name": "exception"}] if channel == "throw" else [],
        })
    return spans


class NativeAgentReceiptTests(unittest.TestCase):
    def test_accepts_all_native_runtime_contracts(self):
        for language in ("java", "node", "dotnet"):
            with self.subTest(language=language):
                LAB.assert_instrumented(language, receipt(language))

    def test_rejects_duplicate_spans(self):
        spans = receipt("java")
        with self.assertRaises(ValueError):
            LAB.assert_instrumented("java", spans + [copy.deepcopy(spans[0])])

    def test_rejects_wrong_overload_or_untargeted_export(self):
        spans = receipt("dotnet")
        spans[0]["name"] = "lab.dotnet.integer-overload"
        with self.assertRaises(ValueError):
            LAB.assert_instrumented("dotnet", spans)

    def test_rejects_early_async_completion(self):
        spans = receipt("node")
        spans[0]["durationMs"] = 1
        with self.assertRaises(ValueError):
            LAB.assert_instrumented("node", spans)

    def test_rejects_masked_exception(self):
        spans = receipt("dotnet")
        spans[2]["status"]["code"] = "OK"
        with self.assertRaises(ValueError):
            LAB.assert_instrumented("dotnet", spans)

    def test_rejects_claimed_node_null_fallback(self):
        spans = receipt("node")
        spans[1]["attributes"]["checkout.channel"] = "unknown"
        with self.assertRaises(ValueError):
            LAB.assert_instrumented("node", spans)

    def test_rejects_synthetic_sdk_receipt(self):
        spans = receipt("java")
        spans[0]["scope"]["name"] = "manually-created-test-span"
        with self.assertRaises(ValueError):
            LAB.assert_instrumented("java", spans)

    def test_rejects_zero_trace_identity(self):
        spans = receipt("java")
        spans[0]["traceId"] = "0" * 32
        with self.assertRaises(ValueError):
            LAB.assert_instrumented("java", spans)


@unittest.skipUnless(shutil.which("docker"), "Docker Compose CLI required")
class ManualEndpointTests(unittest.TestCase):
    def compose_services(self, endpoint):
        environment = os.environ.copy()
        environment.pop("SAMPLE_OTLP_ENDPOINT", None)
        if endpoint is not None:
            environment["SAMPLE_OTLP_ENDPOINT"] = endpoint
        result = subprocess.run(
            ["docker", "compose", "--profile", "apps", "config", "--format", "json"],
            cwd=SCRIPT.parent, env=environment, capture_output=True, text=True,
            check=True, timeout=30,
        )
        return json.loads(result.stdout)["services"]

    def assert_endpoints(self, services, expected):
        for language in ("java", "node", "dotnet"):
            with self.subTest(language=language):
                self.assertEqual(services[language]["environment"]["OTEL_EXPORTER_OTLP_ENDPOINT"], expected)
        self.assertEqual(
            services["dotnet"]["environment"]["OTEL_EXPORTER_OTLP_TRACES_ENDPOINT"],
            expected + "/v1/traces",
        )

    def test_default_remains_docker_studio(self):
        self.assert_endpoints(self.compose_services(None), "http://studio:14318")

    def test_native_studio_override_applies_to_all_languages(self):
        endpoint = "http://host.docker.internal:4318"
        self.assert_endpoints(self.compose_services(endpoint), endpoint)


if __name__ == "__main__":
    unittest.main()
