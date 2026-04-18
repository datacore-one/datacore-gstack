---
name: retro-dc
version: 0.1.0
description: |
  Enriched retrospective. Wraps gstack /retro then captures shipping
  insights as engrams, writes enriched journal entry with velocity metrics,
  and generates engram candidates for the garry-tan knowledge pack.
  Built on gstack by Garry Tan.
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - AskUserQuestion
---

# /retro-dc -- Datacore-Enriched Retrospective

Wraps gstack's `/retro` with Datacore post-processing: engram capture, enriched
journal entries, and sprint tracking updates.

## When to Run

- After `/ship` completes (milestone-triggered retro)
- End of sprint
- End of week (if weekly retros preferred)
- After a significant nightshift batch completes

## Prerequisites

```bash
[ -d ~/.claude/skills/gstack ] && echo "GSTACK: $(cat ~/.claude/skills/gstack/VERSION 2>/dev/null || echo 'installed')" || echo "GSTACK: NOT FOUND"
```

## Arguments

- `/retro-dc` -- default: retro since last retro or 7 days
- `/retro-dc 24h` -- last 24 hours
- `/retro-dc 14d` -- last 14 days
- `/retro-dc sprint` -- retro for current sprint (reads .gstack-sprint.md for start date)

## Step 1: Run gstack /retro

Invoke the gstack `/retro` skill with the appropriate time window argument.
Let it run its full flow: git data collection, metrics computation, narrative generation.

Capture the full retro output text for post-processing.

## Step 2: Extract Structured Data

From the retro output, extract:

### Metrics
- Commits to main
- Net LOC added
- Test LOC ratio
- Active days / detected sessions
- Avg LOC per session-hour
- Version range (if versioned)

### Session Classification
Parse the session analysis:
- Deep sessions (50+ min): count and what was worked on
- Medium sessions (20-50 min): count
- Micro sessions (<20 min): count
- Total session hours

### Shipping Insights
From the "3 Things to Improve" and "3 Habits for Next Week":
- Extract each as a potential engram
- From "Top 3 Wins": extract as positive patterns

### Per-Person Data (if team)
- Who shipped what
- Individual hotspots
- Growth opportunities mentioned

## Step 3: Enriched Journal Entry

Write a journal entry to the current space's journal path:

```markdown
## Retro: {project} ({date range})

### Sprint Summary
{one-line tweetable summary from gstack retro}

### Metrics
| Metric | Value | Trend |
|--------|-------|-------|
| Commits | {n} | {up/down/flat vs last retro} |
| Net LOC | {n} | |
| Test ratio | {n}% | |
| Sessions | {n} ({deep}/{medium}/{micro}) | |
| Velocity | {n} LOC/session-hr | |

### What Shipped
{bullet list of shipped items}

### Key Decisions
{decisions made during this sprint, from sprint tracking file if available}

### Wins
{top 3 wins}

### Improvements
{3 things to improve, with specific actions}

### Habits
{3 habits for next period}
```

Determine the journal path:
```bash
[ -d "notes/journals" ] && echo "JOURNAL: notes/journals" || echo "JOURNAL: journal"
```

Write to `{journal_path}/{date}.md`, appending if the file already exists.

## Step 4: Engram Capture

For each improvement, habit, and notable pattern, create an engram candidate:

### From "3 Things to Improve"
- Type: `behavioral`
- Confidence: 7 (derived from retro analysis, not yet battle-tested)
- Tag: `gstack`, `retro`, `improvement`

### From "3 Habits for Next Week"
- Type: `behavioral`
- Confidence: 6 (aspirational, needs validation)
- Tag: `gstack`, `retro`, `habit`

### From "Top 3 Wins"
- Type: `behavioral` or `procedural`
- Confidence: 8 (these worked, proven)
- Tag: `gstack`, `retro`, `win`, `pattern`

### From Bug Patterns / Quality Issues
- Type: `procedural`
- Confidence: 8 (observed)
- Tag: `gstack`, `retro`, `quality`

Use `plur_learn` for each engram. The statement should be:
- **Generalizable**: not "we fixed the auth bug" but "auth redirects after session expiry need explicit handling in SPA middleware"
- **Actionable**: something a future sprint can apply
- **Testable**: can verify if the pattern was followed

### Pack Eligibility

Engrams tagged `gstack` + `retro` that reach confidence >= 8 after validation
are candidates for the `garry-tan-v1` knowledge pack. The pack captures
shipping methodology insights, not project-specific facts.

Pack-eligible patterns must pass the stranger test: "Would this be useful to
someone who has never seen this codebase?" If yes, mark with visibility: `public`.

## Step 5: Sprint Tracking Update

If `.gstack-sprint.md` exists:
1. Check off the Retro phase
2. Add the retro date and key metrics
3. Mark sprint as COMPLETE

```markdown
## Sprint Complete
Completed: {date}
Duration: {days}
Velocity: {LOC/session-hr}
Quality: Review {PASS/FAIL}, QA {PASS/FAIL}, Security {PASS/FAIL}
Engrams captured: {count}
```

## Step 6: Summary

Present to user:
- Retro highlights (from gstack output)
- Engrams captured (list with IDs)
- Journal entry location
- Sprint status (if applicable)
- Suggestion for next action

## Error Handling

**gstack not installed:**
```
gstack is required but not found at ~/.claude/skills/gstack/

Solution:
  git clone https://github.com/garrytan/gstack ~/.claude/skills/gstack && cd ~/.claude/skills/gstack && ./setup
```

**No git history for retro period:**
```
No commits found in the specified time window ({period}).

Solution:
  Try a wider window: /retro-dc 14d
  Or check you're on the correct branch with the shipped work.
```

**Journal path not found:**
```
Could not detect journal path (neither notes/journals/ nor journal/ exist).

Solution:
  Create the journal directory for this space, or set journal_path in space config.
```

**Sprint tracking file missing (when using /retro-dc sprint):**
```
No .gstack-sprint.md found in project root.

Solution:
  Use /retro-dc with a time window instead: /retro-dc 7d
```

## Your Boundaries

**YOU CAN:**
- Run gstack /retro and post-process its output
- Extract structured metrics from retro data
- Write enriched journal entries with velocity metrics
- Capture shipping insights as engrams (improvements, habits, wins)
- Update sprint tracking file
- Evaluate engrams for pack eligibility (garry-tan-v1)

**YOU CANNOT:**
- Modify gstack retro output or state files
- Create engrams without generalizable, actionable statements
- Skip the gstack /retro phase (always runs upstream retro first)
- Write journal entries to paths outside the current space

**YOU MUST:**
- Run gstack /retro before any post-processing
- Make engram statements generalizable (pass the "stranger test")
- Append to existing journal files, never overwrite
- Present captured engrams to user with IDs for review
