# ADR-0006 — The register row leaves the core; groups are referents

**Status:** Accepted (supersedes the v0.5 record-type design)

## Context

The previous core unified systems and zones with documents, parties,
activities, milestones, work packages, issues and changes under one
abstract `AecoRecordBase` carrying a seven-property register row (id,
title, category, discipline, status, party, about), with three
cross-cutting applied schemas for dates, money and responsibility. The
unification was sound as a *domain* observation — every register is the
same row — but it pulled the entire project record into the core: nine
typed schemas, three applied schemas, four registries, and rules E13/E14
existed only to police it. More than half the core by volume described
what projects *say*, not what they *are made of*; and the one referent
family in the group — systems and zones — inherited a status, a party and
an "about" relationship it had no honest use for.

## Decision

Core groups are referents. `AecoSystem` and `AecoZone` inherit
`AecoGroupBase`, which carries exactly `aeco:id` and the built-in
`CollectionAPI:members`. A system adds `aeco:serves`; a zone adds nothing.
A group's human label is `displayName` metadata and its kind is
classification. No status, party, title-as-data or about relationship is
part of a core group.

## Consequences

The core has eight concrete types, two abstract bases and, after the
representation changes, five applied schemas. Group membership is a core
collection query. Removing a layer of statements about a group leaves its
identity, membership and spatial structure intact. The schema adds no
register vocabulary or second identity mechanism.

## Precedent

ADR-0001's referent test; `IfcGroup` as membership and identity;
`CollectionAPI` as USD's existing membership mechanism.
