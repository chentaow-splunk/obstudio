# Java native no-code rules

Checked against `signalfx/splunk-otel-java` commit
`bcaf26610008af02d2e3fb765a1bc3608b538558` on 2026-10-31.
This is an implementation snapshot; establish the deployed release separately.

Sources:

- [Native README](https://github.com/signalfx/splunk-otel-java/blob/bcaf26610008af02d2e3fb765a1bc3608b538558/instrumentation/nocode/README.md)
- [YAML parser](https://github.com/signalfx/splunk-otel-java/blob/bcaf26610008af02d2e3fb765a1bc3608b538558/instrumentation/nocode/src/main/java/com/splunk/opentelemetry/instrumentation/nocode/YamlParser.java)
- [Expression evaluation](https://github.com/signalfx/splunk-otel-java/blob/bcaf26610008af02d2e3fb765a1bc3608b538558/instrumentation/nocode/src/main/java/com/splunk/opentelemetry/instrumentation/nocode/JexlEvaluator.java)
- [Agent tests](https://github.com/signalfx/splunk-otel-java/blob/bcaf26610008af02d2e3fb765a1bc3608b538558/instrumentation/nocode/src/test/java/com/splunk/opentelemetry/instrumentation/nocode/NocodeInstrumentationTest.java)
- [AppDynamics migration discussion](https://github.com/breedx-splk/appd-pojo-rules-and-nocode-instrumentation/blob/main/README.md)

## Schema and expression rules

The native file is a top-level sequence of rules. Top-level rule fields are
`class`, `method`, `span_name`, `span_kind`, `span_status`, `attributes`, and
`current_span`. Use `class` and `method` in every rule. Unknown keys can be
ignored by the parser, so successful loading is not proof that every key works.

Class and method can be an exact-name string or a one-key matcher object.
Both support `name`, `name_regex`, `and`, `or`, `not`. Boolean combinations
nest matcher objects: `and`/`or` take lists, `not` takes one matcher. Multiple
keys alongside one another are invalid; combine them with `and`.
Only classes support `super_type` (exact qualified supertype/interface).
Only methods support `parameter_count` and `parameter: {index: 0, type: ...}`.
Use binary/declared type names from the actual application; verify overloads.
Use single-quoted, scoped regexes and escape package dots.

`span_kind` is a literal enum: `INTERNAL`, `SERVER`, `CLIENT`, `PRODUCER`,
`CONSUMER`. Use `INTERNAL` for local business operations; being a POJO rule does
not make a method a server or client. Default is `INTERNAL` in this snapshot.

`span_name`, `span_status`, and each attribute `value` are JEXL expressions.
YAML quoting alone does not turn an identifier into a JEXL string constant:
`span_name: '"checkout.submit"'` evaluates to the constant `checkout.submit`.
At entry, expressions can use `this` and zero-based `param0`, `param1`, etc.
`this` can be null for static methods. Only `span_status` can additionally use
`returnValue` and `error` at exit; null/void/throwing returns need guards.
Status expressions should yield `UNSET`, `OK`, or `ERROR`. Omitting the status
expression retains default exception handling; overriding it must preserve
the intended thrown-error semantics.

## Example: one verified overload

Illustrative target: `com.example.checkout.CheckoutService.submit(Order)`;
`Order.getChannel()` must be an established read-only bounded enum/string.
Replace these names using real application evidence before activation.

```yaml
- class: com.example.checkout.CheckoutService
  method:
    and:
      - name: submit
      - parameter_count: 1
      - parameter:
          index: 0
          type: com.example.checkout.Order
  span_name: '"checkout.submit"'
  span_kind: INTERNAL
  attributes:
    - key: checkout.channel
      value: 'param0 != null ? param0.getChannel() : "unknown"'
```

Load with `SPLUNK_OTEL_INSTRUMENTATION_NOCODE_YML_FILE` set to the absolute
path in the JVM's filesystem, with the existing Splunk `-javaagent` startup.
Check the module is enabled under the installed agent's instrumentation policy.
For example, an env snippet can contain:

```sh
SPLUNK_OTEL_INSTRUMENTATION_NOCODE_YML_FILE=/opt/app/instrumentation/nocode/java-nocode.yaml
```

Restart the application to establish activation; do not promise live reload.

## Enrichment and migration

For attributes on an existing span, use `current_span: true`, `class`, `method`,
and `attributes`. Omit `span_name`, `span_kind`, `span_status`: this mode ignores
those fields. It creates no span and does nothing if no span is active. Rules
are ordered; an enrichment rule can target a span created by an earlier rule
on the same method, so preserve and test order when merging.

Map POJO exact names to exact selectors, interfaces/superclasses to
`super_type`, lists to `or`, inversions to `not`, and starts/ends/contains to
scoped `name_regex`. Class annotations and BT splitting have no verified
equivalent in this snapshot. Report such gaps instead of widening a matcher.
Span rules do not themselves inject or extract remote trace context.
