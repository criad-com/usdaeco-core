# ADR-0010 — Validators are UsdValidation plugins

**Status:** Accepted

## Context

Companion-only registration hides rules from standard USD tools and permits separate check paths to drift.

## Decision

Ship a sibling Python plugin with Type python and one registry entry per rule. Use the shared validation adapter, keyword UsdAecoValidators and names usdAecoValidators:<Rule>Checker. Preserve the existing error codes; new error names are ProperCase.

## Consequences

usdchecker, conformance checks and the companion select the same registry rules. Source Python modules or installed companion packages must be importable. The data schema remains a resource-only plugin. Legacy lowercase error tokens are kept separately from ERROR_NAMES, which declares the new ProperCase tokens.
