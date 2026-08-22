# Prompts Book

This project is intended to be built through controlled Codex prompts. This log records prompts,
constraints, verification, and lessons so future sessions can continue from approved project
context instead of relying on memory.

## Entry Format

```text
Prompt ID:
Title:
Goal:
Context:
Full prompt or faithful prompt record:
Files expected to change:
Constraints:
Verification performed:
Result summary:
Issues discovered:
Follow-up/refinement:
Lessons learned:
```

## Prompt 0

Prompt ID: Prompt 0

Title: Documentation Bootstrap

Goal: Create the complete initial documentation package for a professional Python/Pygame desktop
Ludo project without implementing game source code, tests, dependencies, or assets.

Context: The project is a new local Human vs Human Ludo desktop game planned for Python, Pygame,
PyCharm, `uv`, TDD, Ruff, high coverage, and professional portfolio presentation. The first version
supports 2, 3, and 4 local human players. Bots, online play, networking, accounts, databases,
external APIs, and mobile/touch support are out of scope for V1.

Full prompt or faithful prompt record: The full Prompt 0 request was provided as an attached pasted
text file. Its authoritative requirements included:

- create `README.md`;
- create `docs/PRD.md`;
- create `docs/PLAN.md`;
- create `docs/TODO.md`;
- create `docs/PRD_GAME_RULES.md`;
- create `docs/UX_DESIGN.md`;
- create this `docs/PROMPTS_BOOK.md`;
- document but do not implement the game;
- preserve a 52-square outer path, 5-square Home Path, separate Finished destination, and exactly
  8 safe squares;
- document random color assignment, opposite corners for 2-player games, 10-character player names,
  10-second roll/move timers, 5-second no-legal-move feedback, exact finish, bonus rolls,
  triple-six handling, ranking, and the custom dynamic block/protection rules;
- plan a Pygame-independent domain engine and application/SDK facade;
- use `uv`, TDD, Ruff, and coverage targets in documentation;
- avoid unnecessary API, network, database, authentication, token, or service architecture.

Files expected to change:

- `README.md`
- `docs/PRD.md`
- `docs/PLAN.md`
- `docs/TODO.md`
- `docs/PRD_GAME_RULES.md`
- `docs/UX_DESIGN.md`
- `docs/PROMPTS_BOOK.md`

Constraints:

- Do not implement Python source code.
- Do not create tests.
- Do not install dependencies.
- Do not implement Pygame rendering.
- Do not invent gameplay rules not specified in the prompt.
- Do not fabricate screenshots, benchmark results, test results, or implementation status.
- Keep documentation internally consistent and useful for future Codex sessions.

Verification performed:

- Confirmed all requested documentation files exist.
- Audited that README states planning-only status and does not claim a running game.
- Audited rule constants across documents: 52 outer squares, 5 Home-Path squares, separate Finished
  destination, 8 safe squares, 10-second roll/move timers, and 5-second no-legal notification.
- Audited that the custom dynamic block/protection rule is documented as intentional.
- Audited that 2-player color assignment uses opposite corners only.
- Audited that implementation tasks remain planned in TODO.

Result summary:

- Documentation package created.
- Architecture plan includes diagrams, facade boundary, deterministic testing strategy, and ADRs.
- Rules specification defines gameplay behavior and critical test scenarios.
- UX design defines planned screens, board presentation, timers, dice, stacks, hover inspection,
  animation, pause, and final results.
- Roadmap separates completed documentation work from future implementation.

Issues discovered:

- No material contradictions were found in the prompt requirements.
- Existing project metadata may not yet match the planned `1.00` application version, but changing
  package metadata is reserved for a future implementation/tooling prompt.

Follow-up/refinement:

- Review and approve documentation before starting package/source bootstrap.
- In a future prompt, update package metadata and tooling consistently with the documentation.
- In a future prompt, begin TDD with domain models and board topology.

Lessons learned:

- The custom dynamic block rule should be treated as a core domain concept, not a rendering detail.
- Future prompts should read `PRD_GAME_RULES.md` and `PLAN.md` before implementing gameplay logic.

## Prompt 1

Prompt ID: Prompt 1

Title: Repository & Tooling Bootstrap

Goal: Prepare the repository for professional Python development using `uv`, `pyproject.toml`,
`uv.lock`, Ruff, pytest, pytest-cov, `.gitignore`, a clean package/test skeleton, and project
versioning without implementing gameplay or Pygame application logic.

Context: Documentation was completed and reviewed in Prompt 0. The approved architecture requires a
Pygame-independent domain engine, `uv` workflow, Ruff, pytest, coverage target `>= 85%`, and a
minimal package skeleton aligned with `docs/PLAN.md`.

Full prompt or faithful prompt record: The Prompt 1 request was provided as an attached pasted text
file. Its authoritative requirements included:

- read the existing documentation first;
- create or improve `.gitignore`;
- remove tracked `.idea/` files from Git tracking while keeping local files intact;
- use `uv` as the only dependency/project workflow;
- add only currently needed dependencies, with dev dependencies including pytest, pytest-cov, and
  Ruff;
- set the approved initial application version strategy for `1.00`;
- clean up `pyproject.toml`;
- create a minimal package and test skeleton;
- update documentation facts;
- run `uv sync` and `uv run ruff check .`;
- run pytest only if meaningful tests exist;
- do not implement gameplay, Ludo rules, Pygame rendering, or domain classes.

Files expected to change:

- `.gitignore`
- `pyproject.toml`
- `uv.lock`
- `README.md`
- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/__init__.py`
- package directory `__init__.py` files
- `tests/unit/.gitkeep`
- `tests/integration/.gitkeep`

Constraints:

- Do not implement gameplay.
- Do not implement Ludo rules.
- Do not create Pygame rendering.
- Do not create game-domain classes.
- Do not manually edit `uv.lock`.
- Do not use `pip`, `requirements.txt`, virtualenv commands, or `python -m pytest`.
- Do not rewrite Git history or delete local IDE files.

Verification performed:

- Ran `uv sync`.
- Ran `uv run ruff check .`.
- Checked Git tracking for `.idea/`.
- Confirmed no `src/ludo` files contain gameplay or Pygame application logic.

Result summary:

- Repository/tooling bootstrap completed.
- `pyproject.toml` now contains project metadata, Ruff config, pytest config, and coverage config.
- `uv.lock` was generated through `uv`.
- Minimal package and test skeletons were created.
- `.idea/` was removed from Git tracking while local IDE files were left on disk.

Issues discovered:

- Python package metadata uses normalized version `1.0` for the approved application version
  `1.00`. This keeps packaging standards compliant while preserving the documented application
  version decision.
- No meaningful behavioral tests exist yet, so pytest was not run as a success signal.

Follow-up/refinement:

- Begin future development with TDD for domain models and board topology.
- Add meaningful tests before making pytest a required passing verification step.

Lessons learned:

- Keep the bootstrap intentionally small so later prompts can introduce behavior under tests.

## Prompt 2

Prompt ID: Prompt 2

Title: Core Domain Models

Goal: Implement the minimal core domain models needed to represent Ludo player colors, piece states,
pieces, and players while avoiding board topology, movement, rules, turns, timers, ranking, SDK, or
Pygame work.

Context: Documentation and repository/tooling bootstrap were already complete. The approved rules
require exactly four player colors, exactly four piece states, exactly four pieces per active
player, no fake players for inactive colors, and a 10-character maximum player name.

Full prompt or faithful prompt record: The Prompt 2 request was provided as an attached pasted text
file. Its authoritative requirements included:

- read the existing documentation and `pyproject.toml`;
- follow RED -> GREEN -> REFACTOR;
- create a `PieceState` enum with `IN_YARD`, `ON_OUTER_PATH`, `ON_HOME_PATH`, and `FINISHED`;
- create a `PlayerColor` enum with `RED`, `GREEN`, `YELLOW`, and `BLUE`;
- implement a small focused `Piece` model with stable identity, owner color, state, and minimal
  logical progress/location information;
- implement a focused `Player` model with stable identity, name, assigned color, and exactly four
  owned pieces;
- enforce player-name and model invariants;
- write meaningful unit tests;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`.

Files expected to change:

- `README.md`
- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/domain/__init__.py`
- `src/ludo/domain/colors.py`
- `src/ludo/domain/pieces.py`
- `src/ludo/domain/players.py`
- `tests/unit/domain/test_piece.py`
- `tests/unit/domain/test_player.py`

Constraints:

- Do not implement board topology.
- Do not implement movement or legal moves.
- Do not implement captures, blocks, bonus rolls, Triple Six, dice, turns, timers, ranking, SDK, or
  Pygame.
- Do not store screen coordinates, rendering state, animation state, or UI state in domain models.
- Keep public exports deliberate and minimal.

Verification performed:

- Ran `uv sync`.
- Ran `uv run pytest`.
- Ran `uv run pytest --cov`.
- Ran `uv run ruff check .`.

Result summary:

- Added `PlayerColor` and `PieceState` enums.
- Added immutable `Piece` and `Player` dataclasses with validation.
- Added minimal path-progress metadata for pieces without implementing movement.
- Added public domain exports for the new types and constants.
- Added 24 focused unit tests for model construction and invariants.

Issues discovered:

- The approved docs do not define whether player names should be trimmed. The implementation strips
  surrounding whitespace and rejects blank normalized names as the conservative domain policy.
- No conflicts with approved gameplay documentation were found.

Follow-up/refinement:

- Implement board topology in a later TDD milestone.
- Keep movement, legal-move, turn, timer, ranking, and Pygame concerns out of these models.

Lessons learned:

- `path_progress` gives future movement code a clean logical hook while keeping Yard and Finished
  pieces off the traversable path.

## Future Entries

Future prompt entries should be added only after the work is actually requested and performed. Do
not claim future implementation has happened before it exists.
