---
name: otel-declarative-instrument
description: >-
  Generate version-checked no-code instrumentation rules for Splunk OpenTelemetry
  Java, .NET, and Node.js agents. Writes actual configuration files to disk for
  declarative custom spans, enriching existing Java spans, or migrating AppDynamics POJO rules
  without changing application source. Produces native agent files, loading
  instructions, and a verification handoff. Selects each runtime's native schema
  and preserves its agent, profiler, and SDK configuration.
---

# Declarative instrumentation

Translate a concrete telemetry gap into configuration that the application's
installed Splunk OTel agent actually understands. Rules are consumed by agents
running with the application; GitHub repositories are source references, not
configuration delivery endpoints. OBStudio receives the resulting telemetry.
## Establish the target

Inspect the application, deployment manifests, lockfiles, agent startup, and any
existing rules. Determine runtime, exact agent version/build, loaded artifact,
target operation, method signature or module exports, and whether the goal is a
new span or enrichment of an existing span. When source is unavailable, use
operator-supplied signatures, artifacts, or documented library APIs and identify
what still needs runtime proof. Never infer target names from an example.

Use the user's explicit scope. If an OBStudio audit/selection is supplied,
preserve its finding and scenario IDs and restrict changes to selected gaps.
Keep the declarative handoff separate; do not invent fields for canonical audit,
selection, instrumentation, or verification JSON schemas. An audit is useful but
is not required for an explicitly requested no-code rule.

Check existing automatic instrumentation before adding a second span at the same
boundary. For Java attribute-only gaps, consider `current_span: true`. Honor an
explicit no-source-change constraint. If a request cannot be expressed in the
native rule format, explain the exact missing capability and offer an alternative
without silently switching to application code or a different agent.
## Select a native format

Read only the reference for each requested runtime:

| Runtime | Reference | Observed capability; recheck installed version |
|---|---|---|
| Java | [Java rules](references/java.md) | YAML method selectors, new spans, current-span attributes, JEXL expressions |
| Node.js | [Node.js rules](references/nodejs.md) | JSON module/export selectors, new spans, argument attributes |
| .NET | [.NET rules](references/dotnet.md) | File-based YAML method targets, typed attributes, CEL subset, async spans |

The references record upstream snapshots, not minimum supported releases.
Verify the installed tag/commit's documentation, parser, registration, and
relevant tests before declaring compatibility. A feature on `main` does not prove
that a released or installed agent contains it. If the version or schema cannot
be established, mark the draft `compatibility unverified` and keep it out of the
active startup configuration. Continue independently supported runtimes.
## Write the files

Write native rules under an existing operator-owned configuration directory, or
default to `instrumentation/nocode/`. Use `java-nocode.yaml` and
`node-nocode.json` for new files. For .NET, merge targets into the existing
file-based SDK configuration, or create a complete `dotnet-nocode.yaml` with
resource, exporter, and Splunk plugin settings; a targets-only file is insufficient.
Merge existing rule files carefully, preserving
rule order and unrelated entries; avoid duplicate selectors. Put explanatory
prose in the handoff, not in JSON or extra native configuration keys.

For each rule, resolve an exact class/signature or an actual exported function,
choose a bounded span name and truthful span kind, and select only useful,
approved attributes. Use scalar values with known types and bounded strings.
Do not capture credentials, authorization headers, customer payloads, or entire
objects by default. Java expressions execute in the application; use constants
or known read-only accessors, handle nulls, and avoid mutation, I/O, reflection,
or process control. Node's checked implementation can also log extracted values;
assess diagnostic output as well as span attributes.

For AppDynamics migration, map supported selectors and explicitly list unmatched
semantics. A Business Transaction is not equivalent to an OTel trace. Do not
promise transaction splitting, automatic cross-process context propagation, or
custom metrics from method span rules.
## Required file outputs

Write the native files to disk before finishing, using the user's requested
output directory when supplied. For the selected supported runtimes, deliver
`java-nocode.yaml`, complete `dotnet-nocode.yaml`, and `node-nocode.json`.
Java/.NET consume YAML; the checked Node agent consumes JSON, so do not replace
its JSON with a YAML document even when the user calls all outputs "YAML files".
A chat code block, a proposed filename, or a report without actual configuration
files does not fulfill a generation request. Keep prose outside native files.
Link each generated file in the final response with its loader variable, runtime
path, and restart requirement. Unsupported targets remain explicit gaps.

When the user requests generation only or says they will validate manually,
write and statically check the files, then stop before starting Studio/apps,
running traffic, or deploying. Record runtime verification as user-owned and
not run. Do not turn a file-generation request into automatic activation.
## Prepare loading and delivery

Produce a small environment snippet or edit the existing authorized launcher
with the verified native configuration-path variable. For .NET enable file-based
configuration and retain CLR profiler/startup-hook activation separately.
Preserve existing SDK,
agent, exporter, sampling, plugin, and profiler settings. Resolve paths from the
application process/container's filesystem, not the developer host; show the
required file mount/copy for container targets. Keep Java `-javaagent` and Node
preload initialization before application loading, with one agent/SDK owner.

Read [local receiver resolution](../references/local-otlp-receiver.md) when
selecting a local test destination. Preserve explicit destinations and describe
any proposed temporary local override. Configure the installed agent's supported
OTLP protocol consistently with the chosen endpoint and service identity.

Files are activated through the application's deployment mechanism. Do not claim
OBStudio can push rules, hot reload them, or use OpAMP for them without verified
support for that exact agent, rule payload, and management path. Restart/redeploy
instructions must identify the affected process. Writing files alone does not
mean they have been delivered or activated. Perform deployment only when it is
in the user's authorized scope.
## Validate and hand off

Parse YAML/JSON with available project tools; check native keys, types, selector
composition, duplicate rules, expression quoting, module export shape, and
startup paths against the pinned agent implementation. A YAML/JSON parse alone
does not validate JEXL, matching, agent loading, or telemetry.

Unless generation-only/manual validation was selected, run a safe local smoke
test when the agent and runnable fixture/application are available. Exercise the selected method with normal input, null/missing input,
and a thrown exception or rejected Promise where applicable. Check unchanged
return/exception behavior, expected span count, parent/trace IDs, name, kind,
status, attributes, and no duplicate automatic spans. For current-span rules,
also prove no new span and no effect without an active span. For async methods,
check actual completion timing; do not assume a method-return span covers later
work. Inspect received spans in OBStudio using its discovered MCP capabilities
or the verified REST API; a synthetic span emitted by a separate test SDK does
not prove the no-code agent loaded the file. Do not fetch new application
dependencies or start a production process merely to claim proof.

Write `.observe/declarative-instrumentation.md` with:

- Runtime and exact agent version/build, source commit/tag and evidence links.
- Selected finding IDs when supplied, target signatures/exports, native file
  paths, rule purpose, expected span shape, and any unsupported semantics.
- Exact loader settings and target paths, deployment/restart steps, OTLP
  destination/protocol and service name, plus rollback to prior files/settings.
- Checks actually executed and their results, with separate states for syntax,
  compatibility, delivery, activation, and observed telemetry. Name concrete
  prerequisites for anything unproven; never call a generated draft verified.

Summarize the file links and runtime limitations to the user. Keep unsupported
features and unverified agent versions visible for every runtime.
