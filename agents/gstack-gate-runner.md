# Agent: gstack-gate-runner

## Agent Context

| Field | Value |
|-------|-------|
| **Name** | gstack-gate-runner |
| **Module** | gstack |
| **Type** | autonomous |
| **Spawned By** | nightshift-orchestrator, ai-task-executor, sprint skill |
| **Spawns** | None (invokes gstack skills directly) |

## Purpose

Runs gstack quality gates (review, QA, security audit) on a completed build.
Designed for nightshift post-build automation. Collects gate results, captures
engrams from findings, and determines if the build is ship-ready.

## When to Use

- After nightshift completes an :AI: build task
- When a sprint reaches the Gate phase
- When user requests quality gates on current branch
- As a pre-merge check on pull requests

## Inputs

- `branch`: Branch to gate (default: current branch)
- `mode`: "interactive" (default) or "nightshift" (autonomous, strict)
- `gates`: Which gates to run (default: "review,qa,cso")
- `project_url`: URL for QA testing (optional, auto-detected if possible)

## Workflow

1. Verify gstack is installed and branch has changes vs base
2. Inject engrams: `plur_inject_hybrid scope=module:gstack`
3. Run each gate in sequence:
   a. `/review` -- code review with scope drift detection
   b. `/qa` -- browser QA (skipped if no UI/URL)
   c. `/cso` -- security audit
4. Collect results from each gate
5. Capture novel findings as engrams via `plur_learn`
6. Produce gate summary report
7. In nightshift mode:
   - All pass: mark task DONE, optionally proceed to ship
   - Any fail: mark task REVIEW, create follow-up :AI: tasks for findings

## Output

Gate summary report (markdown) with per-gate results, findings, and overall verdict.
Engram IDs for captured learnings.
Journal entry with gate results.

## Constraints

- Does not modify gstack skill files
- Does not auto-ship in nightshift mode unless explicitly configured
- Stops on first CRITICAL finding in nightshift mode
- Maximum 3 QA fix loop iterations before escalating
