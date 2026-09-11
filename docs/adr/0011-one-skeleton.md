# ADR-0011 — One skeleton for every repository

**Status:** Accepted

## Context

Independent repository layouts made plugin discovery, checks, documentation and exact dependency evidence inconsistent.

## Decision

Adopt the toolchain skeleton and S01–S26 structure check: a flat schema module, sibling Python validators, testenv, userDoc and companion tools. Ranges belong in library.json; exact checked refs belong in dependencies.json. Generated installation files go to out, not version control.

## Consequences

Library repositories omit the use-case example requirements. Core retains six hand-authored stages plus a minimal alias for the skeleton. Modular repositories and Nix are the declared differences from the OpenUSD module layout. Source and installation discovery paths are documented, and public flake refs may be locally overridden.
