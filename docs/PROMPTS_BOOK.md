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

## Prompt 3

Prompt ID: Prompt 3

Title: Board Topology & Paths

Goal: Implement the logical board topology and path representation for the shared 52-square outer
path, color start positions, 8 safe outer squares, 5-square private Home Paths, separate Finished
destinations, and player-relative to global outer-index mapping.

Context: Prompt 2 had already added the core player and piece models. The approved board
architecture requires a purely logical 1D topology independent from screen coordinates and separate
from mutable piece state.

Full prompt or faithful prompt record: Prompt 3 was provided directly in chat. Its authoritative
requirements included:

- read the relevant board rules and architecture documentation;
- preserve existing Prompt 2 domain models;
- represent exactly 52 shared outer positions;
- represent exactly 4 player start positions;
- represent exactly 8 safe outer positions with all starts safe;
- represent exactly 5 private Home-Path positions per color;
- keep Finished conceptually separate from Home Path squares;
- map player-relative outer progress to the shared global outer-path index;
- handle wraparound on the 52-square path;
- write focused unit tests;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/domain/__init__.py`
- `src/ludo/domain/board.py`
- `tests/unit/domain/test_board.py`

Constraints:

- Do not implement piece movement.
- Do not implement legal-move calculation.
- Do not implement Yard exit, exact-roll logic, captures, blocks, dice, bonus rolls, Triple Six,
  turns, timers, ranking, SDK/GameFacade, Pygame, screen coordinates, or rendering.
- Keep topology constants separate from mutable piece state.

Verification performed:

- Ran `uv sync`.
- Ran `uv run pytest`.
- Ran `uv run pytest --cov`.
- Ran `uv run ruff check .`.

Result summary:

- Added immutable logical `BoardTopology`.
- Added `HomePathPosition` and `FinishedDestination` value objects.
- Added board constants for 52 outer positions and 5 Home-Path positions.
- Added default start positions Red 0, Green 13, Yellow 26, Blue 39.
- Added default safe squares `{0, 8, 13, 21, 26, 34, 39, 47}`.
- Added 29 focused topology tests, bringing the test suite to 53 tests.

Issues discovered:

- The approved documentation requires color-specific starts but does not prescribe exact numeric
  start indices or star-safe indices. The implementation uses evenly spaced starts every 13 squares
  and star-safe positions 8 squares after each start.
- No conflicts with approved gameplay documentation were found.

Follow-up/refinement:

- Future movement/rules code should consume `BoardTopology` rather than duplicating topology
  constants.
- Board geometry/rendering should map these logical positions to pixels in a later UI milestone.

Lessons learned:

- Keeping Finished as a distinct value object makes it hard to accidentally treat it as a sixth
  Home-Path square.

## Prompt 4

Prompt ID: Prompt 4

Title: Movement & Legal Moves

Goal: Implement basic domain movement and legal-move calculation for the route
`Yard -> Outer Path -> Home Path -> Finished`, independent from Pygame, turns, occupancy, capture,
and blocks.

Context: Prompt 2 added core player/piece models and Prompt 3 added logical board topology. This
milestone builds on those pieces to answer whether a piece can use a dice value and what logical
state/progress it would reach.

Full prompt or faithful prompt record: Prompt 4 was provided directly in chat. Its authoritative
requirements included:

- read only relevant movement/rules and architecture documentation;
- accept dice values `1..6`;
- allow Yard exit only on exactly `6`;
- place Yard exits on the owner's start square;
- advance outer-path pieces by player-relative progress;
- transition correctly from Outer Path into the 5-position private Home Path;
- require exact rolls to reach Finished;
- reject overshoots beyond Finished;
- prevent Finished pieces from moving;
- provide legal-move checks for one piece and for a player's pieces;
- avoid duplication between validation and execution;
- avoid capture, blocks, dice random generation, turns, timers, ranking, SDK, Pygame, animation, and
  rendering.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/domain/__init__.py`
- `src/ludo/domain/movement.py`
- `tests/unit/domain/test_movement.py`

Constraints:

- Do not implement capture.
- Do not inspect occupancy, safe-square collision behavior, same-player blocks, or mixed-player
  blocks.
- Do not implement bonus rolls, Triple Six, dice generation, turns, timers, ranking, random color
  assignment, SDK/GameFacade, Pygame, animations, or rendering.
- Keep screen/global coordinates separate from player-relative journey progress.

Verification performed:

- Ran `uv sync`.
- Ran `uv run pytest`.
- Ran `uv run pytest --cov`.
- Ran `uv run ruff check .`.

Result summary:

- Added `MovementRules` with `propose_move`, `can_move`, `resolve_move`, and `legal_pieces`.
- Added `ProposedMove`, `MoveDestination`, and `MoveDestinationKind`.
- Added `DiceValueError` for invalid dice inputs.
- Added 23 movement tests, bringing the test suite to 76 tests.
- Basic move proposals now return a new moved `Piece` rather than mutating existing piece state.

Issues discovered:

- Prompt 2's `path_progress` model was sufficient and did not need a structural change. The
  implementation documents and uses it state-specifically: outer pieces use `0..51`, Home-Path
  pieces use `0..4`, and Yard/Finished pieces use `None`.
- A piece at outer progress `51` with dice `6` reaches Finished exactly; it is not an overshoot.
  Overshoot tests therefore focus on Home-Path positions where dice values exceed the remaining
  distance.

Follow-up/refinement:

- Future capture/block logic should consume `ProposedMove` destinations instead of duplicating route
  calculations.
- Future facade/UI code can use `legal_pieces` to highlight selectable pieces.

Lessons learned:

- Calculating a proposed move first keeps legality checks and resolution tied to one authoritative
  route calculation.

## Future Entries

Future prompt entries should be added only after the work is actually requested and performed. Do
not claim future implementation has happened before it exists.
