# ADR-010 — Token-efficiency and session discipline

**Status:** Accepted  
**Date:** 2026-06-30  
**Deciders:** @platform-architect (Opus), repo owner  

## Context

Long sessions building cross-stack orchestration consume large amounts of context. Without
discipline, a session either (a) cold-re-derives state that was already established, burning
tokens and risking drift, or (b) pushes past the 75% context bar into degraded-context territory
where responses become less reliable. The repo's PROJECT_STATUS.md checkpoint system and gate
scripts exist precisely to avoid both failure modes.

## Decision

Four mechanical rules, every session:

1. **Checkpoint-first:** Read `PROJECT_STATUS.md`'s "▶ RESUME HERE" block before reading any
   source code at the start of a session. Resume from the checkpoint; do not cold-re-derive state
   that's already on record.

2. **Gate-over-reread:** If a question can be answered by running a contract or gate script (exit
   code + message), run the gate. Do not re-read source files to manually re-derive an answer a
   script already gives deterministically.

3. **Context-bar checkpointing:** When context usage crosses ~75% (red zone): stop work, write
   the checkpoint to `PROJECT_STATUS.md`, and continue in a fresh session via the RESUME-HERE
   block. Do not push further into degraded-context territory.

4. **Model routing:** Heavy cross-stack orchestration design → `@platform-architect` (Opus,
   ultimate veto). Minor rulings → `@scope-guardian` or a Sonnet agent, or better, a
   deterministic gate script.

Max ~3 files per turn; if more files are needed to scope a task, delegate to the `Explore`
subagent so the answer comes back as a pointer, not a context burn.

## Consequences

- **Positive:** Sessions start cheap (one read of PROJECT_STATUS.md) and run gates rather than
  re-reading source, keeping per-turn context cost low.
- **Positive:** The 75% checkpoint rule ensures handoff happens while context is still coherent,
  not after the quality cliff.
- **Requires:** PROJECT_STATUS.md's RESUME-HERE block must be updated before ending every
  substantive session. A stale checkpoint is worse than no checkpoint.

Implementation: `CLAUDE.md` §4–5.
