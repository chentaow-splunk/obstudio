# otel-declarative-instrument Codex Eval Validation Report

This report validates eval JSON, eval directory availability, and skill source availability. It does not run Codex execution.

## Environment

| Field | Value |
|---|---|
| Mode | validation |
| Eval kind | validation |
| Skill | otel-declarative-instrument |
| Run ID | 20261031T222839687864Z |
| Workers | 1 |
| Config | evals/codex-evals.validation.toml |

## Eval Summary

| Eval | Service | Prompts | Eval File | Sanity Checks | Rubric Checks | Runtime Checks |
|---|---|---:|---|---:|---:|---:|
| dotnet/nocode-support/qual/declarative | dotnet/nocode-support | 2 | evals/dotnet/nocode-support/eval/qual/declarative.json | 0 | 8 | 0 |
| java/nocode-overloads/qual/declarative | java/nocode-overloads | 3 | evals/java/nocode-overloads/eval/qual/declarative.json | 0 | 8 | 0 |
| node/nocode-exports/qual/declarative | node/nocode-exports | 1 | evals/node/nocode-exports/eval/qual/declarative.json | 0 | 8 | 0 |
