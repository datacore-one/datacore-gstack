# datacore-gstack

Sprint workflow integration for [Datacore](https://github.com/datacore-one/datacore), powered by [gstack](https://github.com/garrytan/gstack) by Garry Tan.

Adds persistent memory, autonomous quality gates, enriched retros, and a sprint orchestrator on top of gstack's battle-tested sprint skills.

## What it does

| Skill | Purpose |
|-------|---------|
| `/sprint` | Orchestrates idea-to-ship: office hours, planning, build, quality gates, ship, retro |
| `/gate` | Runs code review + QA + security audit as sequential quality gates |
| `/retro-dc` | Wraps gstack `/retro` with engram capture and enriched journal entries |

## What Datacore adds on top of gstack

- **Persistent memory**: review findings, bug patterns, and shipping insights become engrams that inform future sprints
- **Autonomous execution**: quality gates run overnight via nightshift after AI builds complete
- **Enriched retros**: velocity metrics, session classification, and improvement insights captured as engrams
- **Sprint tracking**: full audit trail from idea through shipped product
- **Journal integration**: every phase logs to the Datacore knowledge base

## Requirements

- [Datacore](https://github.com/datacore-one/datacore) installed
- [gstack](https://github.com/garrytan/gstack) installed at `~/.claude/skills/gstack/`

## Install

```bash
# Install gstack first (if not already)
git clone https://github.com/garrytan/gstack ~/.claude/skills/gstack
cd ~/.claude/skills/gstack && ./setup

# Copy this module into your Datacore
cp -r . ~/.datacore/modules/gstack/
# Or clone directly:
git clone https://github.com/datacore-one/datacore-gstack .datacore/modules/gstack
```

## Engram Pack: garry-tan-v1

This module includes a knowledge pack distilling shipping methodology from gstack into reusable engrams:

- 3-Strike Debugging Rule
- WTF-Likelihood Heuristic
- Fix-First Code Review Flow
- Scope Drift Detection
- Verification-Before-Claims Protocol
- Session Classification
- Boil the Lake Principle
- Anti-Sycophancy
- Scope Lock During Debugging
- Blast Radius Gate

These patterns work independently of gstack and improve any AI-assisted development workflow.

## Architecture

```
gstack (Garry maintains, you update via git pull)
  ~/.claude/skills/gstack/

datacore-gstack (this module, thin integration layer)
  .datacore/modules/gstack/
    skills/sprint/    -- orchestrates gstack skills with Datacore plumbing
    skills/gate/      -- quality gate runner for nightshift
    skills/retro-dc/  -- retro wrapper with engram capture
    agents/           -- nightshift gate runner agent
    lib/              -- bridge: reads gstack outputs, routes to Datacore
```

gstack is a runtime dependency, not bundled. Updates are independent.

## Credits

Built on [gstack](https://github.com/garrytan/gstack) by [Garry Tan](https://github.com/garrytan). The sprint workflow, quality gates, and prompt engineering are his work. This module adds the Datacore integration layer.

## License

MIT
