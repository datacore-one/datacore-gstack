---
module: gstack
version: 0.1.0
summary: Sprint workflow integration powered by gstack (by Garry Tan) with persistent memory, nightshift gates, and enriched retros
triggers: ["sprint", "code review", "qa", "quality gate", "security audit", "retro", "ship", "investigate", "office hours", "gstack"]
context: on_match
---

# gstack Module

## Purpose

Integrates Garry Tan's gstack sprint workflow into Datacore. Adds persistent engram memory, autonomous nightshift quality gates, enriched retros with journal logging, and a sprint orchestrator. gstack is a runtime dependency, not bundled.

## Quick Start

> Say "start a sprint" or use `/sprint` to orchestrate idea-to-ship.
> Use `/gate` to run quality gates (review + QA + security) on current branch.
> Use `/retro-dc` after shipping to capture retro insights as engrams.

## How It Works

### Sprint Orchestration (`/sprint`)
Full sprint loop: office-hours (if new idea) then plan then build then gate then ship.
Delegates to gstack skills for each phase, adds Datacore plumbing between phases:
engram injection before, engram capture after, journal logging throughout.

### Quality Gates (`/gate`)
Runs gstack `/review`, `/qa`, and `/cso` in sequence as quality gates.
Designed for nightshift post-build: if all gates pass, proceeds to `/ship`.
If any gate fails, creates `:AI:` tasks for findings and stops.

### Enriched Retro (`/retro-dc`)
Wraps gstack `/retro` then post-processes output:
captures shipping insights as engram candidates, writes enriched journal entry
with velocity metrics and session classification, updates sprint tracking.

## Agents & Commands

| Name | Type | When to use |
|------|------|-------------|
| gstack-gate-runner | agent | Nightshift post-build quality gates |
| /sprint | skill | Full sprint orchestration |
| /retro-dc | skill | Milestone retro with engram capture |
| /gate | skill | Run quality gates on current branch |

## Key Paths

| Path | Purpose |
|------|---------|
| `~/.gstack/projects/{slug}/` | gstack state (learnings, reviews, retros) |
| `[space]/journal/` | Enriched retro journal entries |

## Setup

Requires gstack installed separately:
```bash
git clone https://github.com/garrytan/gstack ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup
```

## Boundaries

- Does NOT modify gstack skill files. Wraps and post-processes only.
- Does NOT replace existing Datacore skills (brainstorming, code-review, systematic-debugging). Runs alongside them.
- Does NOT bundle gstack. It is a runtime dependency.
- gstack updates independently via `cd ~/.claude/skills/gstack && git pull`.
