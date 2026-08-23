# Ludo

Ludo is a playable local desktop Ludo game built with Python and Pygame. It supports 2, 3, or 4
local human players on one computer and keeps the authoritative game rules independent from the
Pygame presentation layer.

The project is also a portfolio-style Python codebase: deterministic domain logic, an
application-facing facade, tested board geometry, interactive Pygame screens, animations, audio
feedback, and documentation are kept in separate responsibilities.

## Implemented Features

- Local Human vs Human matches for 2, 3, or 4 players.
- Player setup with validated names up to 10 characters.
- Random color assignment:
  - 2 players use Red/Yellow or Green/Blue opposite corners;
  - 3 players use three distinct active colors;
  - 4 players use all colors.
- Logical 52-square outer path, 5-square private Home Paths, separate Finished destination, and 8
  safe outer squares.
- Yard exit on 6, exact finish, overshoot rejection, legal-move calculation, and facade-exposed
  legal choices.
- Capture on ordinary vulnerable single opponents.
- Safe-square stacking and the project's custom dynamic protected-block behavior.
- Bonus rolls for 6, capture, or finish, with non-stacking bonus reasons.
- Triple-six cancellation.
- 10-second roll and move decision timers.
- 5-second no-legal-move notification and automatic turn passing.
- Ranking for 2-, 3-, and 4-player matches, including automatic final rank assignment.
- Pygame main menu, player setup, game board, pause overlay, and final results screen.
- Static board rendering, live pieces, dice display, current-player cues, timers, stack summaries,
  hover inspection, legal-piece highlighting, destination preview, movement/capture/finish/dice
  animations, and generated audio feedback.

Not included in the current baseline: online play, networking, accounts, databases, external APIs,
unimplemented experimental gameplay expansions, screenshots/GIFs, packaging, release tags, and
final asset attribution.

## Gameplay Overview

Each active player owns four pieces. A piece starts in the Yard, leaves only on a roll of 6, travels
the shared 52-square outer path relative to its color's start, enters its 5-square Home Path, and
reaches Finished only by exact roll.

The UI only allows legal selections after a roll. Ordinary vulnerable single opponents are captured
and returned to Yard. Safe squares never capture. Ordinary squares with two or more pieces can be
protected blocks; opponents may pass through or join already protected occupancies, but mixed-player
coexistence cannot be created by declining a required capture.

Full current rules are in [docs/PRD_GAME_RULES.md](docs/PRD_GAME_RULES.md).

## Technology Stack

- Python 3.11+
- Pygame
- `uv`
- pytest
- pytest-cov
- Ruff

## Installation

```bash
uv sync
```

## Run The Game

```bash
uv run python -m ludo.pygame_ui.main
```

For a quick launch smoke check:

```bash
uv run python -m ludo.pygame_ui.main --smoke
```

## Run Tests And Lint

```bash
uv run pytest
uv run pytest --cov
uv run ruff check .
```

Current baseline verification from the latest documentation audit:

- `uv run pytest`: 1478 tests passed.
- `uv run pytest --cov`: 86.82% total coverage, above the configured 85% threshold.
- `uv run ruff check .`: all checks passed.

## Architecture Overview

The code follows this dependency direction:

```text
Pygame UI
   -> GameFacade / application snapshots
      -> domain rules and match state

Pygame UI
   -> board geometry
      -> logical board topology identifiers
```

Important boundaries:

- `ludo.domain`: board topology, pieces, players, movement, occupancy/capture/protection, turns,
  timers, dice abstractions, color assignment, ranking, and match completion.
- `ludo.app`: `GameFacade`, immutable public snapshots, legal move routes, public command results,
  and pause-aware UI clock integration.
- `ludo.geometry`: logical-to-screen board mapping and hit testing.
- `ludo.pygame_ui`: screens, controls, rendering, interaction, animation, and presentation state.
- `ludo.audio`: generated audio cues and no-op fallback behavior.
- `ludo.config`: animation and audio tuning defaults.

See [docs/PLAN.md](docs/PLAN.md) for the architecture baseline and rationale.

## Repository Structure

```text
README.md
pyproject.toml
uv.lock
docs/
├── PLAN.md
├── PRD.md
├── PRD_GAME_RULES.md
├── PROMPTS_BOOK.md
├── TODO.md
└── UX_DESIGN.md
src/
└── ludo/
    ├── app/
    ├── audio/
    ├── config/
    ├── domain/
    ├── geometry/
    └── pygame_ui/
tests/
├── integration/
└── unit/
```

## Documentation

- [Product Requirements](docs/PRD.md)
- [Gameplay Rules Specification](docs/PRD_GAME_RULES.md)
- [Architecture Plan](docs/PLAN.md)
- [UX Design](docs/UX_DESIGN.md)
- [Implementation Roadmap](docs/TODO.md)
- [Prompts Book](docs/PROMPTS_BOOK.md)

## Development Notes

- Use `uv` for dependency and command workflow.
- Keep game rules out of Pygame rendering/input code.
- Keep screen coordinates out of authoritative game state.
- Prefer deterministic tests with injected dice, clock, and color randomization.
- Do not fabricate screenshots, benchmark claims, release status, or unimplemented features.

## License And Credits

License, third-party attribution, and final asset credits are still release-preparation tasks.
