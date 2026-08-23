# Ludo

Ludo is a working local desktop Ludo game built with Python and Pygame. It supports 2, 3, or 4
local human players on one computer, with all authoritative rules kept outside the Pygame rendering
and input layer.

The repository is also a portfolio-style Python codebase: deterministic domain logic, an
application-facing facade, tested board geometry, interactive screens, animations, generated audio
feedback, and current documentation are separated by responsibility.

## Key Gameplay Features

- 2-, 3-, and 4-player local Human vs Human matches.
- Validated player names up to 10 characters.
- Random color assignment:
  - 2 players use an opposite pair: Red/Yellow or Green/Blue;
  - 3 players use three distinct colors;
  - 4 players use all colors.
- Four pieces per active player, Yard release on a base 6, exact finish, and overshoot rejection.
- Logical 52-square shared Outer Path, player-specific Start squares, 8 Safe Squares, private
  5-square Home Paths, and separate Finished destination.
- Legal-move calculation exposed through the facade for UI highlighting and destination markers.
- Capture, safe-square coexistence, same-player blocks, and custom evolved mixed-player protected
  blocks.
- Bonus rolls for base 6, capture, or finish, with Triple Six cancellation.
- 10-second decision timers and 5-second no-legal-move notice.
- Ranking for 2, 3, and 4 players, including automatic final rank assignment.
- Pygame main menu, setup, game board, pause overlay, and final results screen.
- Stack summaries, hover inspection, legal destination `V` markers, movement/capture/finish/dice
  animations, and generated audio cues.

## Custom Strategic Rules

This project intentionally includes several documented custom rules:

- **Normal die plus Special Die**: after the base die, the player explicitly rolls a Special Die.
  A successful Special Die grants an optional `+2` movement value when legal.
- **Forced Yard release anti-stall**: a player who starts and ends a turn with every piece still in
  Yard receives a forced base 6 on a later normal turn.
- **Hazard Squares**: 8 fixed-per-match Hazard squares, two per sector. Direct landing forces a
  2-step backward penalty clamped at the player's Start.
- **Boost Squares**: 4 fixed-per-match Boost squares, one per sector. Direct landing forces an
  automatic 2-step forward displacement.
- **Shield Squares**: 4 fixed-per-match Shield squares, one per sector. Direct landing grants a
  one-use shield against player capture.
- **Backward Capture**: a tactical backward move exists only when the current legal movement value
  produces an actual capture. It is not general backward movement.

Full current rules are in [docs/PRD_GAME_RULES.md](docs/PRD_GAME_RULES.md).

## Technology Stack

- Python 3.11+
- Pygame
- `uv`
- pytest
- pytest-cov
- Ruff

## Architecture

The dependency direction is:

```text
Pygame UI
   -> GameFacade / public snapshots
      -> domain rules and match state

Pygame UI
   -> board geometry
      -> logical board topology identifiers
```

Important packages:

- `ludo.domain`: board topology, pieces, players, movement, occupancy/capture/protection, special
  squares, turns, dice, timers, ranking, and match completion.
- `ludo.app`: `GameFacade`, immutable public snapshots, legal move routes, and command results.
- `ludo.geometry`: logical-to-screen board mapping and hit testing.
- `ludo.pygame_ui`: screens, controls, rendering, interaction, animation, and presentation state.
- `ludo.audio`: generated audio cues and no-op fallback behavior.
- `ludo.config`: animation and audio tuning defaults.

See [docs/PLAN.md](docs/PLAN.md) for the architecture baseline and rationale.

## Installation

```bash
uv sync
```

## Running The Game

```bash
uv run python -m ludo.pygame_ui.main
```

For a quick non-interactive launch check:

```bash
uv run python -m ludo.pygame_ui.main --smoke
```

## Controls And Game Flow

- Choose player count and enter valid names.
- Click the center normal die during the roll phase.
- Click the center Special Die during the special-roll phase.
- Select a highlighted legal piece or click a legal destination `V` marker.
- Hover legal moves to preview destinations.
- Hover occupied outer squares to inspect stacks and protection.
- Press `ESC` to pause or resume.
- Use the final results screen to play again, return to the menu, or quit.

## Tests And Quality

```bash
uv run pytest
uv run pytest --cov
uv run ruff check .
```

Current verification from this documentation update:

- `uv run pytest`: 1553 tests passed.
- `uv run pytest --cov`: 86.63% total coverage.
- Configured coverage threshold: 85%.
- `uv run ruff check .`: all checks passed.
- Launch command smoke check: `uv run python -m ludo.pygame_ui.main --smoke` passed.

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

## Not Implemented

The current game does not include online play, accounts, databases, external APIs, Bot/AI players,
networking, Portal, Double-or-Nothing, Coins/Shop, Time Crystal/Undo, Split Dice, screenshots/GIFs,
release packaging, or final license/asset attribution.

## License And Credits

License, third-party attribution, and final asset credits are still release-preparation tasks.
