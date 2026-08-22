# Ludo

Ludo is a planned professional Python desktop game built with Pygame. The project currently has its
core gameplay domain, application facade, and first runnable Pygame screen-flow shell in place. Full
board rendering, dice interaction, piece rendering, animations, and game polish are still planned.

The first playable version will support local Human vs Human matches for 2, 3, or 4 players. AI,
online play, networking, accounts, databases, and external APIs are intentionally out of scope for
V1.

## Planned Features

- Local desktop Ludo for 2, 3, or 4 human players.
- Random color assignment using Red, Green, Yellow, and Blue.
- Opposite-corner color assignment for 2-player games.
- Mouse and keyboard interaction with a polished Pygame interface.
- Deterministic, testable game rules independent from rendering.
- Exact-finish movement, safe squares, capture, bonus rolls, triple-six handling, timers, rankings,
  and the project's custom dynamic block/protection rule.
- Modern board presentation inspired by classic Ludo geometry.
- Stack summaries, hover inspection, legal-move highlighting, animation, pause, and final results.

## Gameplay Summary

The authoritative rules live in [docs/PRD_GAME_RULES.md](docs/PRD_GAME_RULES.md). At a high level:

- The shared outer path has exactly 52 logical positions.
- Each color has a private Home Path of exactly 5 squares, followed by a separate Finished state.
- There are exactly 8 safe squares: four starting squares and four additional star-marked squares.
- Each active player has 4 pieces.
- A piece leaves the Yard only on a roll of 6.
- A piece may finish only with an exact roll.
- Captures occur only against a single vulnerable opponent piece on an ordinary outer-path square.
- Protected same-player and legally evolved mixed-player blocks are not movement barriers.
- A player receives one bonus roll for a 6, capture, or finish; reasons do not stack for one move.
- The third consecutive six is cancelled, ends the turn, and does not undo the first two moves.

## Architecture Direction

The planned architecture separates game rules from Pygame. The GUI will interact through an
application/SDK facade rather than duplicating business logic. The core game engine should be
testable without opening a Pygame window.

Important planned boundaries:

- domain/game rules;
- application facade;
- board topology;
- board geometry and screen-coordinate mapping;
- rendering;
- input;
- animation;
- audio;
- configuration;
- deterministic randomness and time abstractions.

See [docs/PLAN.md](docs/PLAN.md) for the architecture plan and ADRs.

## Planned Technology Stack

- Python 3.11+
- Pygame for desktop rendering and input
- `uv` for dependency and task workflow
- Ruff for linting, with planned `line-length = 100`
- Pytest for automated tests
- Mermaid diagrams in Markdown documentation

Development setup:

```bash
uv sync
uv run pytest
uv run pytest --cov
uv run ruff check .
```

Run the current Pygame shell:

```bash
uv run python -m ludo.pygame_ui.main
```

The current tests cover the implemented domain rules, facade boundary, and screen-flow state. Broader
rendering and interaction tests will be added as later milestones introduce board geometry, dice UI,
piece rendering, and animations.

The approved initial application version is `1.00`. Python package metadata stores the normalized
PEP 440 version `1.0`, which is the authoritative package representation of that application
version.

## Testing and Quality Targets

Implementation is expected to follow RED -> GREEN -> REFACTOR. The planned test structure is:

```text
tests/
├── unit/
└── integration/
```

The global coverage target is `>= 85%`, with core game-rule logic expected to exceed that target
where practical. GUI rendering may be excluded from strict coverage where justified.

## Repository Structure

Current repository structure:

```text
README.md
pyproject.toml
uv.lock
src/
└── ludo/
tests/
├── unit/
└── integration/
docs/
├── PRD.md
├── PLAN.md
├── TODO.md
├── PRD_GAME_RULES.md
├── UX_DESIGN.md
└── PROMPTS_BOOK.md
```

Future gameplay source, behavioral tests, and assets are planned but not yet created.

## Documentation

- [Product Requirements](docs/PRD.md)
- [Gameplay Rules Specification](docs/PRD_GAME_RULES.md)
- [Architecture Plan](docs/PLAN.md)
- [UX Design](docs/UX_DESIGN.md)
- [Implementation Roadmap](docs/TODO.md)
- [Prompts Book](docs/PROMPTS_BOOK.md)

## Development Status

Status: Core domain rules, match facade, and initial Pygame shell/screen navigation are complete.
Full board rendering, dice UI, piece interaction, animations, and final polish have not started.

The roadmap in [docs/TODO.md](docs/TODO.md) distinguishes completed documentation work from future
implementation tasks.

## Screenshots and Media

Screenshots, GIFs, architecture images, and gameplay captures are future documentation artifacts.
They will be added only after the application exists.

## Contribution and Style Expectations

Planned development practices:

- small, meaningful commits;
- feature-oriented branches and changes;
- clear commit messages;
- modular source files, ideally at or below approximately 150 logical lines where practical;
- detailed docstrings for modules, classes, and public functions;
- comments that explain why, assumptions, and non-obvious decisions;
- deterministic tests for public game/domain operations;
- no external services required for tests.

## License and Credits

License, third-party attribution, and final asset credits are undecided and will be documented before
release.
