---
name: sprint
version: 0.1.0
description: |
  Sprint orchestrator. Guides idea-to-ship workflow using gstack skills
  with Datacore memory, journal logging, and quality gates between phases.
  Built on gstack by Garry Tan.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Agent
  - Skill
  - AskUserQuestion
  - WebSearch
---

# /sprint -- Datacore Sprint Orchestrator

Orchestrates a full sprint from idea to shipped product, delegating to gstack
skills for execution and adding Datacore plumbing (memory, journal, tasks) between phases.

## Prerequisites

```bash
[ -d ~/.claude/skills/gstack ] && echo "GSTACK: $(cat ~/.claude/skills/gstack/VERSION 2>/dev/null || echo 'installed')" || echo "GSTACK: NOT FOUND"
```

If GSTACK is NOT FOUND, stop and tell the user:
"gstack is required. Install: `git clone https://github.com/garrytan/gstack ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup`"

## Phase 0: Sprint Setup

Ask the user what they want to build. Determine the sprint mode:

- **New idea** -- no existing design doc or issues. Start at Phase 1 (Office Hours).
- **Existing plan** -- design doc, GitHub issues, or :AI: tasks exist. Start at Phase 3 (Build).
- **Review only** -- code is written, needs quality gates. Start at Phase 4 (Gate).

Inject relevant engrams before starting:
```
Call datacore.inject with scope=module:gstack to load shipping patterns and past sprint learnings.
```

Create a sprint tracking file:

```markdown
# Sprint: {title}
Started: {date}
Mode: {new-idea | existing-plan | review-only}
Branch: {branch}

## Phases
- [ ] Office Hours (design doc)
- [ ] Planning (architecture + test plan)
- [ ] Build (implementation)
- [ ] Gate (review + QA + security)
- [ ] Ship (PR + deploy)
- [ ] Retro (learnings capture)

## Decisions
{track key decisions made during the sprint}

## Findings
{track review/QA/security findings}
```

Write to `.gstack-sprint.md` in the project root.

## Phase 1: Office Hours (new ideas only)

Tell the user: "Starting product discovery with gstack /office-hours."

Invoke the gstack `/office-hours` skill. Let it run its full flow (YC-style questioning,
design doc generation).

**After /office-hours completes:**
1. Read the generated design doc from `~/.gstack/projects/{slug}/`
2. Log to journal: "Sprint started: {title}. Design doc generated via /office-hours."
3. Capture any product insights as engram candidates:
   - User's "narrowest wedge" definition
   - Demand evidence findings
   - Key product decisions
4. Update sprint tracking: check off Office Hours phase
5. Ask: "Design doc ready. Continue to planning phase? (A) Yes, run /autoplan (B) Yes, just eng review (C) I'll plan manually"

## Phase 2: Planning

Based on user's choice:
- **/autoplan**: Invoke gstack `/autoplan` (runs CEO review, design review, eng review in sequence)
- **eng review only**: Invoke gstack `/plan-eng-review`
- **manual**: User plans their own way, skip to Phase 3

**After planning completes:**
1. Read the generated test plan and architecture notes
2. Capture architectural decisions as engrams (type: architectural)
3. If there are actionable items, create :AI: tasks or GitHub issues
4. Update sprint tracking
5. Ask: "Planning complete. Ready to build? (A) Yes, start coding (B) Create GitHub issues first (C) Create :AI: tasks for nightshift"

## Phase 3: Build

This phase is mostly the user (or nightshift) writing code. The sprint skill's role is:
1. Remind the user of the test plan from Phase 2
2. Suggest `/investigate` if they hit bugs during development
3. Track progress against the plan

When the user says they're done building (or nightshift completes the :AI: tasks):
"Code complete. Running quality gates."

Proceed to Phase 4 automatically.

## Phase 4: Quality Gates

Invoke the `/gate` skill (defined in this module). This runs:
1. `/review` -- code review with scope drift detection
2. `/qa` -- browser-based QA (if applicable)
3. `/cso` -- security audit

**After gates complete:**
- If all pass: "All gates passed. Ready to ship."
- If findings exist: present them, ask user to fix or accept
- If critical failures: "Gate failed. Fix these before shipping:" + list

Loop back through gates after fixes until clean.

## Phase 5: Ship

Invoke gstack `/ship`. Let it run its full pipeline (tests, version bump, changelog,
bisectable commits, PR creation).

**After /ship completes:**
1. Log to journal: "Shipped: {title}. PR: {url}. Version: {version}."
2. Update sprint tracking: check off Ship phase
3. Ask: "Shipped! Run a retro to capture learnings? (A) Yes, /retro-dc (B) Skip retro"

## Phase 6: Retro

Invoke `/retro-dc` skill (defined in this module).

**After retro completes:**
Sprint is done. Final journal entry with full sprint summary.

## Sprint Resume

If `.gstack-sprint.md` exists in the project root, read it and determine which phase
to resume from. Tell the user: "Found an in-progress sprint: {title}. Resuming at {phase}."

## Engram Capture Throughout

At each phase transition, evaluate whether any insights should become engrams:
- Product decisions (from office hours) -> behavioral engrams
- Architecture choices (from planning) -> architectural engrams
- Bug patterns (from QA/review) -> procedural engrams
- Shipping patterns (from retro) -> behavioral engrams

Use `datacore.learn` for immediate captures. Tag all with `gstack` and `sprint`.
