# Manual no-code instrumentation exercise

These are three ordinary console applications with no OpenTelemetry SDK calls
or custom instrumentation. Their Docker images include the Splunk agents and
launchers, but **no completed method-instrumentation rules are supplied**.
The AI coding agent must use the skill to create those files as its result.
You start Studio and run every app yourself. Nothing auto-starts when the skill
is used with the generation-only prompt below.

The samples use Splunk Java v2.33.1/JDK 21, `@splunk/otel` 4.12.1/Node 22, and
Splunk .NET v1.16.0/.NET 8 (bundled upstream v1.17.0). Java and .NET downloads
are checksum verified; Node uses its lockfile. You need Python 3.9+ and Docker
with Compose; the language runtimes are inside the images.

## 1. Build without starting anything

From this repository's root:

```sh
cd examples/nocode-manual
docker compose --profile studio --profile apps build
```

There is intentionally no `generated/` directory yet. Do not copy baseline
files there: they contain no method rules. Missing generated files fail at
container creation rather than becoming empty directories.

## 2. Start OBStudio manually

```sh
docker compose up -d studio
curl --fail http://127.0.0.1:17900/api/health
```

Open [OBStudio](http://127.0.0.1:17900). Retry health after a few seconds if
startup is still in progress. Only host loopback ports are published. The
isolated collector uses the supported Docker runtime-evaluation mode so other
containers can send to it; HTTP OTLP uses port 14318. No cloud account/token
is required. The Studio image is built from this checkout and embeds the skill.
The coding agent reads the local skill; the collector receives the telemetry.

If another Studio already owns 17900/14318, stop that instance deliberately
before this exercise. Do not stop unrelated processes automatically. This image
omits the optional Weaver binary; inspect actual spans for this exercise.

## 3. Optionally run the uninstrumented baseline yourself

```sh
RUN_LABEL=baseline CONFIG_DIR=baseline docker compose run --rm --no-deps java
RUN_LABEL=baseline CONFIG_DIR=baseline docker compose run --rm --no-deps node
RUN_LABEL=baseline CONFIG_DIR=baseline docker compose run --rm --no-deps dotnet
```

Each process executes three string calls (normal, null, and failure), then the
excluded integer overload/helper, and exits. It prints:

```text
LAB_RESULT {"results":["web","unknown","error"],"excluded":42}
```

No custom method spans should appear for the `nocode-*-baseline` services.
Console output alone does not prove instrumentation.

## 4. Invoke the skill to generate the native files

Open this **repository root** in your coding agent, where `.agents/skills/` or
`.cursor/skills/` discovers `$otel-declarative-instrument`. Start a new chat
after opening the project if the skill list was already loaded elsewhere.

Paste the contents of [PROMPT.md](PROMPT.md), or ask:

```text
Use $otel-declarative-instrument and follow examples/nocode-manual/PROMPT.md.
Generate the actual three native files on disk. I will run Studio and the
applications manually; do not start or deploy anything.
```

The required results are:

```text
generated/java-nocode.yaml
generated/dotnet-nocode.yaml
generated/node-nocode.json
```

Java and .NET agents consume YAML. Node's agent consumes JSON, so its result
must remain JSON. A chat-only code block or a prose report is not a completed
skill run. The final response must link the files so you can review them.

For .NET, inspect that the file includes the full SDK exporter/resource/plugin
configuration and `instrumentation/development.dotnet.no_code.targets`.
The old PR's `no_code/development` root is not the pinned release's schema.
Keep `${OTEL_SERVICE_NAME}` and `${OTEL_EXPORTER_OTLP_TRACES_ENDPOINT}` in the
.NET YAML: Compose supplies their values at runtime.

## 5. Run the instrumented apps yourself

Use a fresh label for each attempt, and run each app exactly once per label:

```sh
export RUN_LABEL=try1
docker compose run --rm --no-deps java
docker compose run --rm --no-deps node
docker compose run --rm --no-deps dotnet
```

These commands mount the skill's generated files read-only. The launchers use
`SPLUNK_OTEL_INSTRUMENTATION_NOCODE_YML_FILE`, `NOCODE_CONFIG_PATH`, and
`OTEL_CONFIG_FILE`; .NET's native CLR profiler/startup hooks and experimental
file-based mode are already configured. The app endpoint is
`http://studio:14318` (the .NET trace exporter includes `/v1/traces`).

In Studio, filter for `nocode-java-try1`, `nocode-node-try1`, and
`nocode-dotnet-try1`. You should see exactly three spans per service, named
`lab.java.checkout`, `lab.node.checkout`, and `lab.dotnet.checkout` respectively.
Each must be internal and last about 80 ms or more. The failure call must have
ERROR status and an exception event. The integer overload/helper adds no span.
The channel attribute should be `web`, `unknown`, `throw` for Java/.NET;
for Node, the null call's attribute is absent because its native schema has
no fallback expression. Business output remains the same as the baseline.

You may run this optional **read-only** receipt check after the manual runs:

```sh
python3 check_spans.py --label "$RUN_LABEL"
```

It starts no applications or collector. It checks actual native-agent span
receipts, IDs/scope, target count, attributes, errors and async completion;
it also checks source hashes and that all three generated files exist.
Successful output has three PASS lines and writes `.results/<label>.json`.
Repeated app runs with the same label produce duplicate spans and fail the
exact-count check; choose `try2`, rerun all apps, and inspect that fresh label.

## 6. Iterate or stop

Edit/regenerate the rule files, choose a fresh label, and rerun the app commands.
Rules load at application startup, so no image rebuild is needed for config
edits. Inspect missing-loader/path/signature errors in the console output.
Only source or dependency changes require rebuilding images.

```sh
docker compose down
```

This stops this exercise's collector and removes its network. Generated files
and saved receipts remain local and are ignored by Git. Source Studio telemetry
is held in memory and disappears when that process stops. No automatic rule
delivery, hot reload, or cloud-ingestion proof is claimed.
