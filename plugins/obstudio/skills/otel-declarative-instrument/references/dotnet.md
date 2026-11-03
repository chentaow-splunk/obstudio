# .NET native no-code rules

Upstream PR [4515](https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/pull/4515)
was merged and documents native method instrumentation. The Splunk distribution
inherits the implementation from upstream; looking only in Splunk's plugin
source does not establish absence of a feature.

Checked the upstream release commit
`bb2d0ef0cfb64bbe0d9c88640848e4a92f263fd6` and the distribution's release
configuration on 2026-10-31. Establish the installed distribution's bundled
upstream version before using this experimental schema.

Sources:

- [Released upstream guide](https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/blob/bb2d0ef0cfb64bbe0d9c88640848e4a92f263fd6/docs/nocode-instrumentation.md)
- [File-based activation](https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/blob/bb2d0ef0cfb64bbe0d9c88640848e4a92f263fd6/docs/file-based-configuration.md)
- [Target parser and registration](https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/blob/bb2d0ef0cfb64bbe0d9c88640848e4a92f263fd6/src/OpenTelemetry.AutoInstrumentation/Configurations/NoCodeSettings.cs)
- [Expression timing and activity lifecycle](https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/blob/bb2d0ef0cfb64bbe0d9c88640848e4a92f263fd6/src/OpenTelemetry.AutoInstrumentation/Instrumentations/NoCode/NoCodeIntegrationHelper.cs)
- [Working upstream configuration](https://github.com/open-telemetry/opentelemetry-dotnet-instrumentation/blob/bb2d0ef0cfb64bbe0d9c88640848e4a92f263fd6/test/test-applications/integrations/TestApplication.NoCode/config.yaml)
- [Splunk file-based plugin requirements](https://github.com/signalfx/splunk-otel-dotnet/blob/6e5e89159a3ed1c6d505658cb53bb8a449f4b05a/docs/file-based-configuration.md)
- [Splunk release's upstream dependency](https://github.com/signalfx/splunk-otel-dotnet/blob/6e5e89159a3ed1c6d505658cb53bb8a449f4b05a/README.md)

## Schema and compatibility

The PR's historical `no_code/development` root has changed. The checked release
uses `instrumentation/development.dotnet.no_code.targets` within a complete
file-based SDK document. Its schema header is shown in the complete example
below. Do not generate the historical root or copy Java's top-level list.

Each entry has `target` and `span`. Target fields are `assembly.name` (simple
assembly name, without .dll), fully qualified `type`, `method`, and `signature`.
The signature includes `return_type` and an ordered `parameter_types` list;
use `[]` for parameterless methods. Names must match CLR metadata, not C# aliases.
Both return type and parameter types matter. The checked implementation supports
at most nine parameters. Inspect compiled metadata and matching upstream tests
for nested/generic/byref signatures rather than guessing from C# syntax.

A nonempty `span.name` is required by the checked parser. `span.kind` is one of
`internal`, `server`, `client`, `producer`, `consumer`; omitted/unknown kinds
fall back to internal. Attribute entries have `name`, `type`, and either literal
`value` or expression `value_source`. Types are `string`, `bool`, `int`, `double`,
and their `_array` forms. Do not infer extraction support from Java's JEXL.

## Complete minimal example

Illustrative assembly `Checkout.Sample` has
`Checkout.CheckoutService.Submit(System.String)` returning `System.String`.
The argument is an approved bounded channel string. Adapt from real evidence.

```yaml
file_format: "1.0"
resource:
  attributes:
    - name: service.name
      value: checkout-dotnet
tracer_provider:
  processors:
    - batch:
        exporter:
          otlp_http:
            endpoint: ${OTEL_EXPORTER_OTLP_TRACES_ENDPOINT}
plugins/development:
  plugins:
    - Splunk.OpenTelemetry.AutoInstrumentation.Plugin, Splunk.OpenTelemetry.AutoInstrumentation
instrumentation/development:
  dotnet:
    no_code:
      targets:
        - target:
            assembly:
              name: Checkout.Sample
            type: Checkout.CheckoutService
            method: Submit
            signature:
              return_type: System.String
              parameter_types: [System.String]
          span:
            name: checkout.submit
            kind: internal
            attributes:
              - name: checkout.channel
                value_source: 'arguments[0] != null ? arguments[0] : "unknown"'
                type: string
```

The HTTP exporter endpoint here is signal-specific and includes `/v1/traces`.
Migrate existing resource, sampler, processors/exporters and plugin settings
into the active YAML; do not replace an operator's full SDK configuration with
this minimal example. File-based mode does not automatically inherit every
SDK environment setting. Splunk realm/token settings have documented limitations
in this mode; a credential-free local OTLP target avoids them for a smoke test.

Enable `OTEL_EXPERIMENTAL_FILE_BASED_CONFIGURATION_ENABLED=true` and set
`OTEL_CONFIG_FILE` to the full document's path in the application filesystem.
Retain `OTEL_DOTNET_AUTO_HOME`, the correct native CLR profiler path/CLSID,
`CORECLR_ENABLE_PROFILING` (or Framework equivalents), and startup hooks from
the distribution's supported launcher. Merely setting `OTEL_CONFIG_FILE` does
not activate method rewriting. Restart after edits; do not promise hot reload.
Use a supported Linux/Windows profiler environment for method tracing; verify
platform/architecture support separately from managed-only automatic libraries.

## Expressions and span lifecycle

The checked CEL subset provides `arguments[0]` through `arguments[8]`, `instance`,
`method`, `type`, public property/index access, comparisons, boolean operators,
ternaries, string concatenation, and a documented small function set. Do not
assume arbitrary C# calls or the entire CEL standard work. Null/invalid results
can be skipped, so verify emitted values rather than only parsing the YAML.

Dynamic attributes and `name_source` evaluate at method entry in the checked
helper. `return` is unavailable there even though the guide lists it among
expression identifiers. Use it in exit-time `span.status.rules` only, not in
entry-time attributes or names. A `name_source` requires a static fallback
`name`; keep both names bounded. Status rules are ordered and first-match wins;
they run after exception handling and can override an error, so do not add a
broad success rule that masks a thrown exception.

Task/Task<T> and supported ValueTask forms use async completion callbacks. Prove
span timing and exception behavior with the actual profiler, including methods
returning pending Tasks without `async`. Rules create new activities; no Java
`current_span` equivalent is established here. Avoid duplicate targets.

If a target already emits an ActivitySource, subscribing through supported
`OTEL_DOTNET_AUTO_TRACES_ADDITIONAL_SOURCES` configuration is a separate option;
it does not instrument an otherwise uninstrumented method. Use the installed
file-based schema's source subscription settings when that mode is active.
