---
name: gate
version: 0.1.0
description: |
  Quality gate runner. Executes gstack /review, /qa, and /cso in sequence
  as pre-ship quality gates. Designed for nightshift post-build automation.
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

# /gate -- Quality Gate Runner

Runs gstack's review, QA, and security audit skills as sequential quality gates.
Each gate must pass before proceeding to the next. Designed for both interactive
use and nightshift autonomous execution.

## Prerequisites

```bash
[ -d ~/.claude/skills/gstack ] && echo "GSTACK: $(cat ~/.claude/skills/gstack/VERSION 2>/dev/null || echo 'installed')" || echo "GSTACK: NOT FOUND"
git diff --stat origin/$(git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||' || echo main)..HEAD 2>/dev/null | tail -1
```

If GSTACK is NOT FOUND, stop with install instructions.
If no diff against base branch, stop: "No changes to gate. Nothing to review."

## Arguments

- `/gate` -- run all three gates (review + qa + cso)
- `/gate review` -- run only code review
- `/gate qa` -- run only QA
- `/gate cso` -- run only security audit
- `/gate --nightshift` -- autonomous mode: no AskUserQuestion, fail on any finding

## Inject Engrams

Before running gates, inject relevant learnings:

```
Call datacore.inject with scope=module:gstack
```

This loads past review findings, QA bug patterns, and security issues from previous
sprints. The agent should apply these as additional checklist items during review.

## Gate 1: Code Review (/review)

Invoke gstack `/review` skill. Let it run its full two-pass checklist.

**Post-processing:**
1. Read the review log from `~/.gstack/projects/{slug}/`
2. Classify findings:
   - **CRITICAL**: must fix before ship (SQL safety, race conditions, LLM trust boundaries)
   - **IMPORTANT**: should fix (dead code, missing tests, magic numbers)
   - **INFORMATIONAL**: nice to fix (style, naming, minor refactors)
3. Capture novel findings as engram candidates:
   - Bug patterns not seen before -> procedural engrams
   - Scope drift detection results -> behavioral engrams
4. If CRITICAL findings exist in nightshift mode: STOP, create :AI: tasks for each, exit
5. If interactive: present findings, ask user to fix or acknowledge

**Gate result:** PASS (no critical), PASS_WITH_CONCERNS (important only), FAIL (critical found)

## Gate 2: QA (/qa)

Only run if the project has a running URL or testable UI. Skip for pure libraries/CLIs.

```bash
# Detect if project has a dev server or URL
grep -r "localhost\|127.0.0.1\|dev server\|start.*server" package.json Makefile docker-compose.yml 2>/dev/null | head -3
```

Invoke gstack `/qa` skill if applicable. It handles browser automation, bug finding,
fix loops, and regression test generation.

**Post-processing:**
1. Read the QA report
2. Capture bug patterns as engrams:
   - "Auth redirect breaks on {condition}" -> procedural, scope:project
   - "Form validation missing for {field}" -> procedural, scope:project
3. Log QA health score delta to journal
4. If bugs were found and fixed: verify the fixes were committed
5. In nightshift mode: if bugs couldn't be auto-fixed, create :AI: tasks

**Gate result:** PASS (no bugs or all fixed), PASS_WITH_CONCERNS (cosmetic only), FAIL (unfixed bugs)

## Gate 3: Security Audit (/cso)

Invoke gstack `/cso` skill. It runs:
- Secrets archaeology (git history, env files, config)
- Dependency supply chain audit
- OWASP Top 10 checklist
- STRIDE threat model
- Active verification of findings

**Post-processing:**
1. Read the security audit report
2. Classify by severity (CRITICAL/HIGH/MEDIUM/LOW)
3. Capture security patterns as engrams:
   - Novel vulnerability patterns -> procedural, scope:global (security applies everywhere)
   - Dependency risks -> procedural, scope:project
4. CRITICAL or HIGH findings = gate FAIL
5. In nightshift mode: FAIL on any finding above LOW

**Gate result:** PASS (clean or low only), FAIL (medium+ findings)

## Gate Summary

After all gates run, produce a summary:

```
QUALITY GATE REPORT
====================
Project: {name}
Branch:  {branch}
Date:    {date}

Review:   {PASS|FAIL} -- {N findings: X critical, Y important, Z info}
QA:       {PASS|FAIL|SKIPPED} -- {N bugs found, M fixed, K remaining}
Security: {PASS|FAIL} -- {N findings: X critical, Y high, Z medium, W low}

Overall:  {PASS|FAIL}
====================
```

**If all PASS:** "All quality gates passed. Ready to ship."
- In sprint mode: proceed to /ship automatically
- In standalone mode: suggest `/ship`
- In nightshift mode: proceed to ship autonomously

**If any FAIL:** "Quality gates failed. Findings need attention."
- In interactive mode: present findings with fix suggestions
- In nightshift mode: create :AI: tasks for each finding, mark parent task as REVIEW

## Journal Logging

After gate completion, log to the space journal:

```markdown
## Quality Gates: {project} ({branch})

| Gate | Result | Findings |
|------|--------|----------|
| Review | {result} | {summary} |
| QA | {result} | {summary} |
| Security | {result} | {summary} |

Overall: {PASS|FAIL}
```

## Engram Capture

At the end of the gate run, batch-capture engrams from all findings:
- Use `datacore.learn` for each novel pattern
- Tag with: `gstack`, `quality`, and the gate name (`review`, `qa`, `cso`)
- Set scope to `module:gstack` for reuse in future gate runs
- Set confidence based on gate's own confidence rating

## Error Handling

**gstack not installed:**
```
gstack is required but not found at ~/.claude/skills/gstack/

Solution:
  git clone https://github.com/garrytan/gstack ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

**No changes to gate:**
```
No diff found between current branch and base. Nothing to review.

Solution:
  Ensure you're on the feature branch with committed changes, not main.
```

**QA gate cannot find dev server:**
```
No running dev server or testable URL detected. Skipping QA gate.

Note: QA gate is skipped for libraries and CLIs. This is expected.
If your project does have a UI, start the dev server before running /gate qa.
```

**Nightshift mode critical failure:**
```
CRITICAL finding in nightshift mode. Stopping gate run.
:AI: tasks created for each finding.

Solution:
  Review findings in next_actions.org, fix, then re-run /gate --nightshift.
```

## Your Boundaries

**YOU CAN:**
- Run gstack /review, /qa, /cso as sequential quality gates
- Classify findings by severity (CRITICAL/IMPORTANT/INFORMATIONAL)
- Capture novel findings as engrams
- Create :AI: tasks for unresolved findings in nightshift mode
- Skip QA gate for non-UI projects
- Produce gate summary reports and journal entries

**YOU CANNOT:**
- Auto-fix code (presents findings, human or nightshift fixes)
- Modify gstack skill files or review checklists
- Ship code (suggests /ship after all gates pass, does not execute it)
- Override a CRITICAL finding -- it always blocks shipping

**YOU MUST:**
- Stop on first CRITICAL finding in nightshift mode
- Present all findings before declaring gate pass/fail
- Log gate results to journal
- Inject engrams before running to apply past learnings
