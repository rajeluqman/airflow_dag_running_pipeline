# ADR-009 — Conversational language: English default, Manglish opt-in

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** repo owner  

## Context

The repo owner is bilingual (English / Malay-English / Manglish). Some prior working sessions in
sibling repos used Manglish fluidly for chat while keeping committed documentation in English.
The question is whether the AI assistant should switch into Manglish proactively (based on the
owner's locale or prior session history) or wait for an explicit signal.

## Decision

**English is the default** for all conversation and every committed document (ADRs, runbooks,
CLAUDE.md, PROJECT_STATUS.md, and this file). English applies from the start of every session
regardless of the owner's locale or what language was used in a prior session.

**Manglish is opt-in per session:** the assistant switches into Manglish *only* if the owner
explicitly uses it first in the current session. The signal must be fresh — prior-session usage
or locale inference is not sufficient.

**Committed documentation stays English** regardless of the conversational register used in
chat. A runbook written during a Manglish session is committed in English.

## Consequences

- **Positive:** Committed docs are consistently readable by collaborators, reviewers, and a future
  Opus doing a PR review — none of whom should need to understand Manglish to read the repo.
- **Positive:** The assistant never misreads a locale signal or prior-session memory as permission
  to switch language without the owner's current-session intent.
- **Trade-off:** The owner must re-signal Manglish preference each session. This is a deliberate
  friction point, not an oversight.

Implementation: `CLAUDE.md` §6 Conversational language.
