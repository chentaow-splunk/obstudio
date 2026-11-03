# Node.js native no-code rules

Checked against `signalfx/splunk-otel-js` commit
`4faf2d29aec03cd6968bfbcd6241a76197377407` on 2026-10-31.
Recheck the deployed package: this feature is described as under development.

Sources:

- [Native guide](https://github.com/signalfx/splunk-otel-js/blob/4faf2d29aec03cd6968bfbcd6241a76197377407/src/instrumentations/external/nocode/nocode.md)
- [Loader, types, and wrappers](https://github.com/signalfx/splunk-otel-js/blob/4faf2d29aec03cd6968bfbcd6241a76197377407/src/instrumentations/external/nocode/nocode.ts)
- [Bundled registration and enablement](https://github.com/signalfx/splunk-otel-js/blob/4faf2d29aec03cd6968bfbcd6241a76197377407/src/instrumentations/index.ts)
- [Export, attribute, and Promise tests](https://github.com/signalfx/splunk-otel-js/blob/4faf2d29aec03cd6968bfbcd6241a76197377407/test/instrumentation/external/nocode/nocode.test.ts)

## Schema

The file is a JSON array. Each definition selects exactly one of:

- `moduleName`: actual npm package name. Optional `supportedVersions` is an
  array of semver ranges; match the installed package version, not the agent
  version. `mainModuleMethods` selects properties of the main module exports.
  `files` selects exports of package files using a relative `name` including
  the extension where the package's actual loader requires it.
- `absolutePath`: absolute path to the actual application module file as seen
  by the process. Use `files`, with extensionless file `name`, following the
  checked agent test pattern. Resolve emitted JavaScript rather than TypeScript
  source when the deployed app executes compiled JS. `supportedVersions` and
  `mainModuleMethods` do not apply to this branch.

Each method entry has `methodName`, optional constant `spanName`, and optional
`attributes`. File entries additionally require `name`. Attributes have a
nonnegative zero-based integer `attrIndex`, string `key`, and optional dotted
`attrPath`. Omit `attrPath` only for a known primitive argument. A path selects
properties, including numeric array positions; it is not an expression language.
Missing paths produce no attribute in the checked implementation.

Only direct function properties such as `module.exports.submit` are wrapped.
Unexported functions, nested object methods, prototype methods, default function
exports, and ESM/bundler transforms must not be assumed compatible. Establish
the actual export shape and loader behavior with the installed agent.

## Example: package's main exported function

Illustrative package `checkout-core` exports `submit(order)`, where
`order.channel` is a bounded string. The example omits the optional version
filter; add `supportedVersions` from the real lockfile before deployment when
multiple package versions might otherwise match.

```json
[
  {
    "moduleName": "checkout-core",
    "mainModuleMethods": [
      {
        "methodName": "submit",
        "spanName": "checkout.submit",
        "attributes": [
          {"attrIndex": 0, "attrPath": "channel", "key": "checkout.channel"}
        ]
      }
    ]
  }
]
```

For an internal file `/opt/app/dist/checkout.js` exporting `submit`, use:

```json
[
  {
    "absolutePath": "/opt/app/dist/checkout.js",
    "files": [{"name": "checkout", "methodName": "submit", "spanName": "checkout.submit"}]
  }
]
```

Set `NOCODE_CONFIG_PATH=/opt/app/instrumentation/nocode/node-nocode.json`.
The loader otherwise looks for `nocode.config.json` in the process working
directory. Confirm the existing Splunk preload/start runs before target module
imports. In the checked registration the short name is `nocode`, and
`OTEL_INSTRUMENTATION_NOCODE_ENABLED` controls enablement; preserve an explicit
disable and report it rather than silently overriding it. Restart after edits.

## Limits that affect generated rules

There is no verified `spanKind`, `span_status`, `current_span`, JEXL, regex
method matching, return-value extraction, or redaction/truncation configuration
in this schema. Generated spans use the default kind (`INTERNAL`). Do not copy
Java keys into Node JSON or promise enrichment without a new span.

The wrapper preserves synchronous results and throws, and waits for native
Promises to settle before ending spans. Custom thenables, callback completion,
streams, and iterators need separate proof; a return from their function does
not establish operation completion. Error objects are recorded by the checked
wrapper. A duplicate rule can wrap the same export more than once.

Values can appear in instrumentation diagnostic logs as well as spans. Select
only approved bounded primitives; no whole-object capture or invented hashing,
redaction, or truncation expression. If safe extraction cannot be expressed,
omit the attribute and report the gap.
