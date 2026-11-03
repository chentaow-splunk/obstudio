Use $otel-declarative-instrument to create native no-code instrumentation for
the three plain applications in examples/nocode-manual. This is **generation
only**: I will start OBStudio and run the apps myself. Do not start Studio,
the apps, traffic, or deploy. Do not modify app source, Dockerfiles, Compose,
baseline/, source-sha256.json, or add an application SDK.

Inspect the actual code and pinned agent dependencies. Create these actual
files on disk before finishing:

- examples/nocode-manual/generated/java-nocode.yaml
- examples/nocode-manual/generated/node-nocode.json
- examples/nocode-manual/generated/dotnet-nocode.yaml

Instrument these business methods, using one new internal span per call:

- Java: lab.CheckoutService.submit(java.lang.String), named lab.java.checkout.
  Exclude the integer overload.
- Node.js: exported submit(channel) in /app/checkout.js, named lab.node.checkout.
  Exclude the other exported function and the unexported helper.
- .NET: Lab.CheckoutService.SubmitAsync(System.String) in assembly
  Checkout.Sample, returning Task<System.String>, named lab.dotnet.checkout.
  Exclude the integer overload and preserve actual Task completion timing.

Capture only the bounded checkout.channel argument. Use unknown for null in
Java and .NET. Node's native JSON cannot express a null fallback, so leave its
null attribute absent and explain that limitation. Preserve thrown/rejected
error status. Do not mask exceptions with a generic success status rule.

Use the runtime versions pinned in the sample Dockerfiles and package-lock.
The .NET distribution bundles the upstream no-code implementation. Its file
must be a complete file-based SDK YAML with the supported nested no_code
targets, the Splunk plugin, resource service.name=${OTEL_SERVICE_NAME}, and
an otlp_http exporter endpoint=${OTEL_EXPORTER_OTLP_TRACES_ENDPOINT}.
The container's trace endpoint is http://studio:14318/v1/traces. Compose already
provides the native loaders and .NET profiler/startup hooks.

Keep the requested files in native format: Java/.NET YAML and Node JSON.
Statically check the files without starting the application. Write
.observe/declarative-instrumentation.md with source/version evidence and
manual loading, restart, and rollback instructions. End with clickable links
to all three configuration files. Do not finish with only chat snippets or a
plan, and do not claim runtime verification before I run the apps.
