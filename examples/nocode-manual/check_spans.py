#!/usr/bin/env python3
"""Read local OBStudio receipts after the user manually runs the three apps."""

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlencode
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent
RULE_FILES = {"java": "java-nocode.yaml", "node": "node-nocode.json", "dotnet": "dotnet-nocode.yaml"}
APP_FILES = ("java/CheckoutService.java", "node/app.js", "node/checkout.js", "dotnet/Program.cs")


def source_hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in APP_FILES}


def request_json(base, path):
    with urlopen(base.rstrip("/") + path, timeout=5) as response:
        return json.load(response)


def received_spans(base, service):
    summaries = request_json(base, "/api/query/traces?" + urlencode({"serviceName": service, "limit": 1000}))
    if not isinstance(summaries, list):
        raise ValueError("Unexpected OBStudio trace-list response; inspect the server version")
    spans = []
    seen = set()
    for summary in summaries:
        detail = request_json(base, "/api/query/traces/" + summary["traceId"])
        if detail.get("retentionTruncated") or detail.get("retentionUnknown"):
            raise ValueError("Trace retention is incomplete; rerun against a quiet local Studio")
        for span in detail["spans"]:
            identity = (span["traceId"], span["spanId"])
            if span.get("resource", {}).get("serviceName") == service and identity not in seen:
                seen.add(identity)
                spans.append(span)
    return spans


def assert_instrumented(language, spans):
    expected_name = f"lab.{language}.checkout"
    if len(spans) != 3 or any(span["name"] != expected_name for span in spans):
        raise ValueError(f"{language}: expected exactly 3 {expected_name} spans, got {[s['name'] for s in spans]}")
    missing = "<missing>"
    channels = Counter(s.get("attributes", {}).get("checkout.channel", missing) for s in spans)
    # Node's schema has no null-fallback expression; the SDK drops the null value.
    null_channel = missing if language == "node" else "unknown"
    if channels != Counter(["web", null_channel, "throw"]):
        raise ValueError(f"{language}: wrong argument/null attributes: {channels}")
    for span in spans:
        for field, width in (("traceId", 32), ("spanId", 16)):
            value = span[field]
            if not re.fullmatch(f"[0-9a-f]{{{width}}}", value) or int(value, 16) == 0:
                raise ValueError(f"{language}: invalid {field}")
        if span["kind"].lower() != "internal":
            raise ValueError(f"{language}: wrong kind: {span['kind']}")
        if span.get("parentSpanId", "").strip("0"):
            raise ValueError(f"{language}: these standalone calls should be roots")
        if "nocode" not in span.get("scope", {}).get("name", "").replace("-", "").replace("_", "").lower():
            raise ValueError(f"{language}: scope does not identify the no-code agent")
        if span["durationMs"] < 50:
            raise ValueError(f"{language}: span ended before the 80ms operation completed")
        channel = span.get("attributes", {}).get("checkout.channel")
        is_error = str(span.get("status", {}).get("code", "")).upper() == "ERROR"
        if is_error != (channel == "throw"):
            raise ValueError(f"{language}: exception status does not match the executed call")
        if is_error and not any(event["name"] == "exception" for event in span.get("events") or []):
            raise ValueError(f"{language}: missing exception event")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="RUN_LABEL used for the manual app runs")
    parser.add_argument("--url", default="http://127.0.0.1:17900")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", args.label):
        parser.error("label must use only letters, digits, underscore or hyphen")
    for filename in RULE_FILES.values():
        path = ROOT / "generated" / filename
        if not path.is_file() or not path.read_text().strip():
            parser.error(f"the skill has not delivered a nonempty {path}")
    if source_hashes() != json.loads((ROOT / "source-sha256.json").read_text()):
        parser.error("application source changed from the supplied plain-code baseline")
    request_json(args.url, "/api/health")
    report = {"label": args.label, "results": []}
    for language in RULE_FILES:
        service = f"nocode-{language}-{args.label}"
        spans = received_spans(args.url, service)
        assert_instrumented(language, spans)
        report["results"].append({"language": language, "service": service, "spans": spans})
        print(f"PASS {language}: 3 native no-code spans; attributes, errors, timing and target scope match")
    report["status"] = "pass"
    destination = ROOT / ".results" / f"{args.label}.json"
    destination.parent.mkdir(exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n")
    print(f"Receipt report: {destination}")


if __name__ == "__main__":
    main()
