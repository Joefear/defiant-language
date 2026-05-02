# Defiant Language (DL)

Defiant Language (DL) is an intent-governed execution language designed to be human-readable, strictly parseable, and fully governed by policy at runtime.

## Overview

DL is a structured language for expressing executable intent in a form that remains readable to humans while staying rigid enough for deterministic parsing and runtime governance. The project currently centers on a Python parser baseline that validates DL syntax, structure, and policy-facing language constraints.

## Current Status

The current parser baseline is `v0.2.4`, implemented in `defiant_parser_v0_2_4.py`.

The test harness currently passes:

- 7 valid examples
- 15 stress scenarios

Validation errors from `DL-E001` through `DL-E017` are supported.

## What DL Supports

The current parser supports strict validation for the DL baseline, including:

- Human-readable intent blocks
- Parseable structure suitable for execution pipelines
- Runtime-governance-oriented validation rules
- Explicit validation errors using the `DL-E001` through `DL-E017` error range
- Stress-scenario coverage for malformed or boundary-case input

## Parser Baseline

- Current baseline: `v0.2.4`
- Current parser file: `defiant_parser_v0_2_4.py`
- Current validation range: `DL-E001` through `DL-E017`

This baseline should be treated as the reference implementation for the current DL syntax and validation behavior.

## Running the Parser

Run the parser directly with Python:

```bash
python defiant_parser_v0_2_4.py
```

If using a virtual environment, activate it first and then run the same command.

## Project Structure

```text
.
├── defiant_parser_v0_2_4.py
├── dl_examples.py
├── README.md
└── .gitignore
```

## Next Steps

Planned work includes:

- DGCE integration
- Natural-language-to-DL generation

## License

License placeholder. Add the selected project license here.
