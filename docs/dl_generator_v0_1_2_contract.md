# DL Generator v0.1.2 Usage Contract

## Purpose

DL Generator v0.1.2 deterministically converts structured intent records into Defiant Language source text compatible with the locked DL v0.3.0 parser.

## Input Contract

The generator accepts a structured Python `dict` intent record. The record must describe supported DL v0.3.0 constructs using explicit fields rather than free-form natural language.

Supported top-level intent fields:

- `imports`
- `declarations`
- `context_type`
- `context_id`
- `sequences`
- `rules`
- `policies`

## Output Contract

The generator emits a Defiant Language v0.3.0 string. Output is deterministic and ordered as:

- imports
- declarations
- `Hey` context block
- `So` sequence blocks
- rule blocks
- policy blocks

## Validation Contract

Generated DL is always validated through:

```python
DefiantParser().parse(...)
```

If parser validation fails, the generator treats that as a generator-layer failure and raises `GeneratorError`.

## Unsupported / Non-Goals

- No LLM generation
- No parser modification
- No vocabulary beyond the locked v0.3 additions
- No execution layer

## Harness Coverage

The current harness covers:

- 8 valid examples (including v0.3 example)
- 9 negative intent cases

## Current Commit Reference

`b758f27`

## How To Run

```bash
python defiant_generator_v0_1.py
```

## v0.3 Vocabulary Support

The generator now supports Defiant Language v0.3 vocabulary additions:

Types:
- gesture
- component

Verbs:
- select
- bind

Parser baseline:
- defiant_parser_v0_3_0.py
