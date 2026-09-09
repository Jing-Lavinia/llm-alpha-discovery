# System overview

## Purpose

The system turns a quantitative research domain into a continuing alpha-discovery program. It combines machine-scale hypothesis exploration with deterministic empirical evaluation, allowing factor research to become repeatable and cumulative rather than a sequence of disconnected manual experiments.

## Public capability map

```text
Research domain and constraints
              │
              ▼
┌─────────────────────────────────────────┐
│   Proprietary LLM alpha discovery       │
│   system                                │
└─────────────────────────────────────────┘
              │
              ▼
Structured, executable factor candidates
              │
              ▼
Deterministic empirical evaluation
              │
              ▼
Validated alpha evidence and research assets
```

Public documentation describes the system at the capability level. Its internal methods and implementation remain private.

## Separation of responsibilities

The generative component expands and formalizes the hypothesis space. The quantitative layer remains responsible for measurement: information timing, chronological out-of-sample evaluation, portfolio construction, frictions, risk diagnostics, and evidence generation are deterministic.

That separation matters because plausible reasoning is not itself alpha. A candidate becomes a research asset only after it survives the same empirical standard applied to every other candidate.

## Public evidence layer

This repository exposes a deliberately narrow verification surface:

- a closed JSON contract for aggregate research evidence;
- a checksum manifest binding figures to the released evidence set;
- deterministic chart generation from the aggregate file;
- automated tests for schema closure, numerical consistency, and artifact integrity.

These controls make the published claims auditable without publishing a partial imitation of the discovery system or enough connected detail to reconstruct it.
