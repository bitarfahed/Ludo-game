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

## Prompt 5

Prompt ID: Prompt 5

Title: Capture & Protection Blocks

Goal: Implement outer-path occupancy, ordinary-square capture, safe-square protection, same-player
blocks, joining protected blocks, mixed-player block persistence, and block dissolution without
turns, bonus rolls, timers, ranking, or Pygame.

Context: Prompt 4 introduced movement proposals and logical destinations. This milestone consumes
those proposed moves to determine what happens when the destination is a shared outer-path square
with existing pieces.

Full prompt or faithful prompt record: Prompt 5 was provided as an attached pasted text file. Its
authoritative requirements included:

- read the relevant capture/block rules and architecture documentation;
- capture exactly one vulnerable opponent on an ordinary outer square;
- return captured pieces to `IN_YARD` with Yard-consistent location/progress;
- prevent capture on safe squares;
- allow safe-square stacking across any color combination;
- make same-player ordinary-square stacks protected;
- allow opponents to land on already protected ordinary blocks;
- preserve legally formed mixed-player blocks while at least two pieces remain;
- dissolve protection when an ordinary occupancy drops to one piece;
- prevent direct creation of a mixed block from two vulnerable opponents;
- keep Home Paths and Finished destinations outside outer-path collision rules;
- avoid bonus rolls, Triple Six, random dice generation, turns, timers, ranking, SDK/GameFacade,
  Pygame, rendering, animation, and audio.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/domain/__init__.py`
- `src/ludo/domain/occupancy.py`
- `tests/unit/domain/test_occupancy.py`

Constraints:

- Do not award capture bonuses.
- Do not implement turn sequencing or dice behavior.
- Do not add rendering, stack visualization, hover inspection, animation, audio, or Pygame logic.
- Do not change movement rules except for consuming proposed move destinations.

Verification performed:

- Ran `uv sync`.
- Ran `uv run pytest`.
- Ran `uv run pytest --cov`.
- Ran `uv run ruff check .`.

Result summary:

- Added `OuterPathOccupancy` for pieces sharing one global outer-path square.
- Added `CollisionResolver` for centralized outer-path capture/protection resolution.
- Added `CollisionOutcome` with moved piece, captured piece, destination occupancy, and destination
  protection status.
- Added 17 occupancy tests, bringing the test suite to 93 tests.

Issues discovered:

- Mixed-player protection needs a tiny bit of occupancy history. The implementation represents that
  as `OuterPathOccupancy.was_protected`, which persists only while at least two ordinary-square
  pieces remain.
- No conflicts with approved gameplay documentation were found.

Follow-up/refinement:

- Future turn/bonus logic should consume `CollisionOutcome.capture_occurred` rather than deciding
  capture itself.
- Future game-state/session code should maintain `OuterPathOccupancy.was_protected` as pieces leave
  ordinary protected stacks.

Lessons learned:

- Keeping collision resolution separate from movement preserved the Prompt 4 route logic and left
  occupancy effects inspectable for later systems.

## Prompt 6

Prompt ID: Prompt 6

Title: Turn Engine, Dice, Bonus Rolls & Timers

Goal: Implement deterministic domain turn sequencing, dice flow, bonus rolls, Triple Six handling,
roll and move decision timers, and no-legal-move flow without Pygame or ranking.

Context: Prompts 2 through 5 introduced players, pieces, board topology, movement proposals, and
outer-path collision outcomes. This milestone coordinates those existing domain services into
turn-level state transitions.

Full prompt or faithful prompt record: Prompt 6 was provided as an attached pasted text file. Its
authoritative requirements included:

- represent at least `WAITING_FOR_ROLL` and `WAITING_FOR_MOVE`;
- use injectable dice/randomness;
- use injectable time/clock for deterministic timeout tests;
- enforce 10-second roll and move decision windows;
- handle no-legal-move rolls without granting a bonus;
- grant one bonus roll for a resolved move with roll `6`, capture, or finish;
- avoid stacking multiple bonus rolls from one move;
- implement Triple Six cancellation of only the third consecutive six;
- rotate across active players only;
- integrate existing legal-move, movement, and capture/block resolution;
- avoid ranking, final-place assignment, random match setup, SDK/GameFacade, Pygame, visual
  countdowns, popup rendering, animation, audio, and pause-menu UI.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/domain/__init__.py`
- `src/ludo/domain/turns.py`
- `tests/unit/domain/test_turns.py`

Constraints:

- Do not implement full ranking logic or automatic final-place assignment.
- Do not implement random player/color assignment or start-screen setup.
- Do not move timer logic into Pygame.
- Do not implement visual countdowns, no-legal popup rendering, animations, audio, or pause menu.

Verification performed:

- Ran `uv sync`.
- Ran `uv run pytest`.
- Ran `uv run pytest --cov`.
- Ran `uv run ruff check .`.

Result summary:

- Added `TurnEngine` with roll, move-selection, no-legal-notice completion, and timeout handling.
- Added `TurnPhase`, `TurnEventKind`, and `TurnEvent`.
- Added injectable `Dice` and `Clock` protocols.
- Added `FixedDice`, `RandomDice`, and `FixedClock`.
- Added 15 turn-engine tests, bringing the test suite to 108 tests.

Issues discovered:

- Ranked-player skipping needs ranking state that does not exist yet. The current engine rotates
  only through the supplied active players, so inactive colors are skipped by construction; ranked
  player removal remains for the ranking milestone.
- No conflicts with approved gameplay documentation were found.

Follow-up/refinement:

- Future ranking logic should provide the eligibility hook for skipping ranked players.
- Future application/facade code should consume `TurnEvent` values for UI state and messages.

Lessons learned:

- Keeping dice and clock injected made timeout and Triple Six tests straightforward without tying
  turn logic to global randomness or real time.

## Prompt 7

Prompt ID: Prompt 7

Title: Match Setup, Ranking & Completion

Goal: Implement match-level setup, active-player eligibility, random valid color assignment,
rankings, ranked-player turn removal, final remaining player auto-rank, and match completion.

Context: Prompts 2 through 6 introduced players, pieces, board topology, movement, occupancy,
capture/block outcomes, and the deterministic turn engine. This milestone completes the core
match-level state around player counts, colors, turn eligibility, and standings.

Full prompt or faithful prompt record: Prompt 7 was provided directly in chat. Its authoritative
requirements included:

- validate match creation for exactly 2, 3, or 4 players;
- use existing `Player` and name validation;
- assign colors randomly through an injectable abstraction;
- enforce opposite colors for 2-player matches;
- use three distinct colors for 3-player matches, with one inactive color;
- use all four colors for 4-player matches;
- keep inactive colors from having fake players or turns;
- order active players clockwise by board/color order;
- detect players whose four pieces are all `FINISHED`;
- assign permanent rankings and never rank a player twice;
- remove ranked players from future turn rotation;
- automatically rank the final remaining player and mark the match complete;
- integrate ranked-player eligibility with the existing turn engine;
- avoid SDK/GameFacade, Pygame, UI widgets, rendering, animations, audio, and Bot logic.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/domain/__init__.py`
- `src/ludo/domain/match.py`
- `src/ludo/domain/turns.py`
- `tests/unit/domain/test_match.py`

Constraints:

- Do not implement GameFacade/SDK.
- Do not implement Pygame, start-screen widgets, name text boxes, rendering, visual timers,
  animations, audio, or Bot logic.
- Do not refactor unrelated existing modules unless required for ranking/turn eligibility.

Verification performed:

- Ran `uv sync`.
- Ran `uv run pytest`.
- Ran `uv run pytest --cov`.
- Ran `uv run ruff check .`.

Result summary:

- Added `Match` for validated match setup, active player ordering, ranking, and completion.
- Added `RankingEntry`.
- Added `ColorRandomizer`, `FixedColorRandomizer`, and `RandomColorRandomizer`.
- Added `TurnEngine.replace_player` and `TurnEngine.remove_player` eligibility hooks.
- Added 15 match tests, bringing the test suite to 123 tests.

Issues discovered:

- For a 2-player match, ranking the first completed player immediately auto-ranks the final player
  and completes the match, leaving no remaining turn rotation. Ongoing ranked-player skipping is
  therefore most naturally verified with 3+ active players.
- No conflicts with approved gameplay documentation were found.

Follow-up/refinement:

- Future SDK/facade code should expose match setup and final standings without duplicating match
  rules.
- Future UI setup should collect names only; color assignment remains in the domain match layer.

Lessons learned:

- Sorting active players by `CLOCKWISE_COLORS` after assignment keeps turn order independent from
  the order in which player names were entered.

## Prompt 8

Prompt ID: Prompt 8

Title: GameFacade / SDK Boundary

Goal: Implement the application-facing `GameFacade` boundary so future Pygame UI and non-UI
controllers can start matches, inspect state, roll, query legal moves, select pieces, inspect
timers, and consume structured results without depending directly on internal domain services.

Context: Prompts 2 through 7 completed the Pygame-independent domain foundation: players, pieces,
board topology, movement, capture/protection, turn engine, timers, match setup, ranking, and match
completion. This milestone exposes those capabilities through an application/SDK layer.

Full prompt or faithful prompt record: Prompt 8 was provided directly in chat. Its authoritative
requirements included:

- read only relevant facade, TODO, and public-operation rules documentation;
- expose match creation/start, current match state, current player, turn phase, dice rolling, legal
  moves, piece movement, timers, player/piece state, rankings, and completion;
- prefer immutable/read-only public snapshots so UI code cannot mutate domain state;
- expose structured result/event information for dice rolls, no legal moves, moves, captures,
  finishes, bonus availability, turn changes, rankings, and match completion;
- preserve dependency direction `Pygame UI -> GameFacade / SDK -> Domain / Services`;
- keep future Bot compatibility by using the same public state/action boundary;
- reject invalid facade operations cleanly;
- add focused facade integration tests;
- update `docs/TODO.md` and this prompts book;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/__init__.py`
- `src/ludo/app/facade.py`
- `tests/integration/test_game_facade.py`

Constraints:

- Do not implement Pygame, windows, screens, board drawing, input handling, visual timers,
  animations, audio, pause menu, Bot logic, or network/API services.
- Do not move business rules into the facade.
- Do not redesign established domain rules unless required for a real integration defect.

Verification performed:

- Ran `uv run pytest` during implementation.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`, and
  `uv run ruff check .`.

Result summary:

- Added `GameFacade` as the app-layer public boundary over `Match` and `TurnEngine`.
- Added frozen public snapshots for game state, players, pieces, legal moves, and rankings.
- Added structured facade results for match start, dice rolls, no-legal moves, piece movement,
  captures, finishes, bonus state, turn changes, timeouts, ranking, and match completion.
- Added facade validation errors for wrong phases, illegal piece choices, missing matches, and
  completed matches.
- Added integration tests for facade setup, query, roll, move, capture, finish, ranking,
  completion, timer, invalid actions, and snapshot immutability.

Issues discovered:

- Finishing a final piece can both produce a domain finish bonus reason and immediately rank/remove
  that player. The facade reports the finish reason while exposing no usable bonus roll once the
  player has been ranked or the match is complete.

Follow-up/refinement:

- Future UI work should call the facade instead of importing internal domain movement, capture,
  topology, ranking, or turn-engine modules.
- Pause/resume remains a separate planned application workflow.

Lessons learned:

- Wrapping domain events into immutable app-layer results keeps UI needs visible without duplicating
  gameplay decisions.

## Prompt 9

Prompt ID: Prompt 9

Title: Pygame Application Shell & Screen Flow

Goal: Create the first runnable Pygame application shell with clean screen/state navigation through
`MAIN_MENU`, `PLAYER_SETUP`, `GAME`, `RESULTS`, and a paused game overlay, without rendering the
real Ludo board or implementing dice/piece interaction.

Context: Prompt 8 introduced the `GameFacade` application boundary. This milestone creates the
first Pygame layer above that boundary while keeping gameplay rules inside the facade/domain.

Full prompt or faithful prompt record: Prompt 9 was provided as an attached pasted text file. Its
authoritative requirements included:

- add Pygame through `uv` if absent;
- initialize Pygame cleanly, open the main window, run a stable loop, and close cleanly;
- implement screen states `MAIN_MENU`, `PLAYER_SETUP`, `GAME`, and `RESULTS`;
- implement Start Game and Quit on the main menu;
- implement setup for 2, 3, or 4 players with dynamic name fields and 10-character name limits;
- prevent match start with invalid or blank names;
- start matches through the existing facade rather than assigning colors in Pygame;
- create a placeholder game screen showing player names, assigned colors, and current player;
- create a placeholder results screen with Play Again, Main Menu, and Quit;
- toggle a pause overlay from the game screen with `ESC`;
- keep UI, screen manager, controls, and application loop responsibilities separated;
- avoid full board rendering, dice UI, piece rendering, legal highlights, timer visualization,
  animations, audio, and Bot logic;
- add meaningful tests for screen-state transitions and setup behavior;
- update `docs/TODO.md`, `docs/PROMPTS_BOOK.md`, and README only if a runnable command exists;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- launch the app once through `uv run` and report manual verification honestly.

Files expected to change:

- `README.md`
- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `pyproject.toml`
- `uv.lock`
- `src/ludo/pygame_ui/__init__.py`
- `src/ludo/pygame_ui/controls.py`
- `src/ludo/pygame_ui/main.py`
- `src/ludo/pygame_ui/screens.py`
- `src/ludo/pygame_ui/state.py`
- `src/ludo/pygame_ui/theme.py`
- `tests/unit/pygame_ui/test_screens.py`
- `tests/unit/pygame_ui/test_state.py`

Constraints:

- Do not implement full Ludo board rendering, 52-square geometry, Home Path drawing, safe-square
  graphics, dice rendering/rolling UI, piece rendering, legal-move highlighting, timer
  visualization, hover inspection, stack visualization, movement animations, capture animations,
  audio, or Bot logic.
- Do not duplicate color-assignment rules in Pygame.
- Keep gameplay interaction through the facade.

Verification performed:

- Added Pygame with `uv add pygame`.
- Added state and Pygame smoke tests.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`,
  `uv run ruff check .`, and a Pygame smoke launch.

Result summary:

- Added a runnable Pygame shell at `uv run python -m ludo.pygame_ui.main`.
- Added a testable `ScreenController` with setup, game, results, pause, menu, and shutdown state.
- Added lightweight Pygame controls, theme constants, screen rendering, and event dispatch.
- Connected setup start to `GameFacade.start_match`.
- Placeholder game screen displays facade snapshot data: player names, assigned colors, and current
  player.
- Placeholder results screen can display facade ranking data.

Issues discovered:

- Full pause/resume timer synchronization remains out of scope for this prompt; the current pause is
  a UI overlay/state toggle over the game screen.

Follow-up/refinement:

- Future prompts should add board geometry/rendering and then dice/piece input through the facade.
- Timer-aware pause/resume should be implemented when timer presentation and gameplay interactions
  are added.

Lessons learned:

- Keeping screen navigation in a non-rendering controller made the shell practical to test without
  brittle screenshot assertions.

## Prompt 10

Prompt ID: Prompt 10

Title: Board Geometry & Rendering

Goal: Render the complete static Ludo board in Pygame while keeping logical game state independent
from screen coordinates.

Context: Prompt 9 added the runnable Pygame shell and screen navigation. Prompt 10 adds the
geometry responsibility and static board drawing consumed by the existing game screen.

Full prompt or faithful prompt record: Prompt 10 was provided directly in chat. Its authoritative
requirements included:

- read only relevant UX, architecture, and TODO documentation;
- create a dedicated board-geometry responsibility that maps logical positions to screen
  coordinates;
- support visual placement for the 52 shared outer-path squares, four start squares, eight safe
  squares, four 5-square Home Paths, four Yards, four Finish regions, center dice area,
  player-name areas, and timer areas;
- keep game state independent from screen coordinates;
- render a recognizable classic Ludo structure with modern restrained visual treatment;
- provide query APIs for outer rectangles/centers, Home Path squares, Yard positions, Finish
  regions, center dice area, player label/timer areas, and hit-testing where practical;
- render safe squares distinctly without implementing capture/protection behavior;
- display player names near Yards using facade/UI state;
- add meaningful non-screenshot geometry tests;
- avoid dice interaction, dice animation, piece movement interaction, legal highlights, destination
  previews, stack rendering, hover popups, countdown visualization, movement/capture animations,
  audio, and Bot logic;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, `uv run ruff check .`, and launch the
  application for visual verification.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/geometry/__init__.py`
- `src/ludo/geometry/board_geometry.py`
- `src/ludo/geometry/grid.py`
- `src/ludo/pygame_ui/board_renderer.py`
- `src/ludo/pygame_ui/screens.py`
- `tests/unit/geometry/test_board_geometry.py`

Constraints:

- Do not implement dice interaction, dice rolling animation, piece movement interaction,
  legal-move highlighting, destination preview, stack rendering, hover inspection popup, countdown
  visualization, capture animation, movement animation, audio, or Bot logic.
- Do not put gameplay rules into geometry.
- Do not create screenshot-comparison tests.

Verification performed:

- Added focused geometry tests for outer squares, Home Paths, Yards, Finish regions, safe/start
  mapping, required regions, representative hit-testing, and centered layout adaptation.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`,
  `uv run ruff check .`, and Pygame launch.

Result summary:

- Added pure `BoardGeometry` APIs using immutable `ScreenRect` and `BoardHit` value objects.
- Mapped a classic 15x15 Ludo grid to the current 960x640 shell window.
- Rendered all static board regions from geometry on the game screen.
- Rendered active/inactive Yards, Home Paths, Finish cells, center dice placeholder area, player
  labels, timer placeholder areas, start squares, and star safe squares.

Issues discovered:

- The existing roadmap had one combined "Render board and pieces" row. It was split so static board
  rendering can be marked complete while actual piece rendering remains planned.

Follow-up/refinement:

- Future prompts should render pieces and stacks using the geometry API rather than hard-coded
  coordinates.
- Dice UI and timer visualization should use the existing center dice and timer-area geometry.

Lessons learned:

- A 15x15 grid gives a recognizable board while keeping coordinates centralized and simple to test.

## Prompt 11

Prompt ID: Prompt 11

Title: Pieces, Dice & Gameplay HUD

Goal: Render live match state on top of the static board: pieces, center dice, current-player cues,
player status, and timer HUD, without implementing mouse gameplay interaction.

Context: Prompt 10 added board geometry and static board rendering. Prompt 11 consumes public
facade snapshots and existing board geometry to place live gameplay presentation.

Full prompt or faithful prompt record: Prompt 11 was provided directly in chat. Its authoritative
requirements included:

- read only relevant UX, architecture, and TODO documentation;
- render active pieces according to `IN_YARD`, `ON_OUTER_PATH`, `ON_HOME_PATH`, and `FINISHED`;
- use geometry for all placement rather than domain screen coordinates;
- render compact circular pieces with color symbols `r`, `g`, `y`, and `b`;
- render single occupancy as a normal piece;
- render a temporary compact placeholder for multiple occupancy without implementing final stack UX;
- render the center dice area with current rolled value when available;
- visually indicate dice availability during the roll phase without implementing click-to-roll;
- show current-player feedback through name/status, Yard emphasis, and dice accent;
- display numeric decision seconds and a small progress bar using facade timer state;
- show compact player status such as finished-piece count or rank;
- keep rendering focused and facade/public-state based;
- add non-screenshot tests for render-state preparation;
- avoid mouse click to roll, piece selection, legal-move highlighting, destination preview, final
  stack UX, hover inspection, movement/capture animations, dice animation, audio, and Bot logic;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, `uv run ruff check .`, and launch the
  application for visual verification.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/facade.py`
- `src/ludo/pygame_ui/board_renderer.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/render_models.py`
- `src/ludo/pygame_ui/render_state.py`
- `src/ludo/pygame_ui/screens.py`
- `tests/unit/pygame_ui/test_render_state.py`

Constraints:

- Do not implement gameplay clicking, piece selection, legal-move highlighting, destination
  previews, final stack summaries, hover inspection, movement animation, capture animation, dice
  animation, audio, or Bot logic.
- Do not import internal movement/rule services into Pygame rendering.
- Avoid screenshot-comparison tests.

Verification performed:

- Added render-state tests for Yard, outer, Home Path, Finished placement, temporary stack
  placeholders, dice state, current-player state, timer state, inactive colors, and ranked status.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`,
  `uv run ruff check .`, and Pygame launch/visual inspection.

Result summary:

- Added public facade snapshot fields for current dice value and decision timeout duration.
- Added `render_state.py` to map facade snapshots and board geometry into draw-ready HUD state.
- Added `GameplayRenderer` for live pieces, dice, player status, active-player cues, and timer bar.
- Static board rendering now leaves live names/timers to the gameplay renderer while preserving
  inactive corner labels.
- Multiple occupancy currently renders as a compact placeholder label such as `2r`.

Issues discovered:

- The facade needed to expose current dice value and decision timeout in public snapshot state so
  Pygame did not need to reach into the turn engine.

Follow-up/refinement:

- Prompt 13 should replace the temporary multiple-occupancy placeholder with the final stack summary
  and hover inspection UX.
- Future input work should use the already-rendered dice/piece state but route actions through the
  facade.

Lessons learned:

- Preparing render state separately from drawing keeps UI tests stable while preserving the
  gameplay/domain boundary.

## Prompt 12

Prompt ID: Prompt 12

Title: Gameplay Interaction & Legal Move UX

Goal: Make the board actively playable through mouse dice rolling, legal piece selection,
legal-move highlighting, and destination preview while keeping authoritative gameplay rules inside
the facade/domain layers.

Context: Prompt 11 rendered live pieces, dice, player status, and timer HUD. Prompt 12 adds
gameplay mouse interaction above that rendering without implementing animation, final stack UX, or
audio.

Full prompt or faithful prompt record: Prompt 12 was provided directly in chat. Its authoritative
requirements included:

- read only relevant UX, architecture, and TODO documentation;
- allow center dice clicks only during the valid roll phase;
- route dice and piece actions through `GameFacade`;
- update displayed dice result from facade state;
- query legal moves through the facade after a valid roll;
- make only legal pieces selectable and visually highlighted;
- require explicit selection even when exactly one legal move exists;
- preview the resolved destination when hovering a legal piece using facade/public move information;
- submit legal piece clicks through the facade and update rendered state;
- avoid mutating pieces, players, occupancy, or turn state in the UI;
- handle outside clicks, inactive/illegal piece clicks, dice clicks in move phase, piece clicks in
  roll phase, and repeated clicks gracefully;
- keep hit-testing/input separate from game rules;
- add non-screenshot interaction/state tests;
- avoid final stack-summary rendering, hover stack inspection, movement/capture animation, dice
  animation, audio, final 5-second no-legal visual flow, and Bot logic;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, `uv run ruff check .`, and launch the
  application for manual verification.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/__init__.py`
- `src/ludo/app/facade.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/interaction.py`
- `src/ludo/pygame_ui/screens.py`
- `tests/unit/pygame_ui/test_interaction.py`

Constraints:

- Do not implement final stack summary UX, hover stack inspection popup, piece movement animation,
  capture animation, dice animation, audio, final no-legal 5-second visual flow, or Bot logic.
- Do not modify approved domain rules.
- Do not import internal movement/rule services into Pygame.

Verification performed:

- Added interaction tests for dice click phase rules, facade-routed rolling, legal/illegal piece
  selection, no auto-selection for one legal move, legal hover destination preview, outside-click
  safety, roll/move phase safety, no-legal rolls, and repeated-click no-ops.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`,
  `uv run ruff check .`, and Pygame launch/visual inspection.

Result summary:

- Added `GameplayInteractionController` for gameplay mouse clicks and hover state.
- Added public legal-move destination snapshots to the facade for UI previews.
- Added legal piece rings and destination preview rendering.
- Connected dice and legal piece clicks from the Pygame game screen to the facade.
- Fixed facade snapshots to read active live players from the turn engine so moved pieces appear
  correctly in UI-facing state.

Issues discovered:

- Prompt 12 exposed a stale facade snapshot path: live piece updates were in `TurnEngine.players`
  while `GameFacade.snapshot()` still read active players from `Match.players`. The facade now uses
  the turn engine for active live player state and ranked entries for completed players.

Follow-up/refinement:

- Future no-legal prompt should add the 5-second user-facing notification flow.
- Prompt 13 should replace the temporary multi-piece placeholder with final stack summary and hover
  inspection UX.

Lessons learned:

- Destination preview belongs at the facade boundary: once legal moves include destination data,
  Pygame can preview moves without duplicating movement rules.

## Prompt 13

Prompt ID: Prompt 13

Title: Stack Rendering & Hover Inspection

Goal: Replace the temporary multiple-occupancy placeholder with final compact stack summaries and a
hover inspection popup, without changing gameplay rules.

Context: Prompt 12 made dice rolling, legal piece selection, highlighting, and destination preview
playable through the facade. Prompt 13 improves shared-square readability above the existing board
geometry, rendering, interaction layer, and GameFacade.

Full prompt or faithful prompt record: Prompt 13 was provided directly in chat. Its authoritative
requirements included:

- read only relevant UX, architecture, and TODO documentation;
- render a compact summary when multiple pieces occupy the same logical outer square, using
  notation such as `2r`, `3y`, or `2r 1b`;
- color each summary component with the corresponding player color;
- keep single-piece rendering unchanged;
- show a hover inspection popup for occupied board squares with per-color counts;
- indicate ordinary protected blocks and Safe Squares from public facade/state information derived
  from authoritative game logic;
- keep popups visible inside the application window where practical;
- avoid movement animation, capture animation, dice animation, audio, no-legal timed notification,
  additional gameplay rules, and Bot logic;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- launch the application and verify stack summaries and hover popups manually.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/__init__.py`
- `src/ludo/app/facade.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/interaction.py`
- `src/ludo/pygame_ui/render_models.py`
- `src/ludo/pygame_ui/render_state.py`
- `src/ludo/pygame_ui/screens.py`
- `tests/integration/test_game_facade.py`
- `tests/unit/pygame_ui/test_render_state.py`

Constraints:

- Do not implement animations, audio, final no-legal timed notification, additional gameplay
  rules, or Bot logic.
- Do not modify capture/block rules to simplify rendering.
- Do not import internal movement/rule services into Pygame rendering.
- Avoid screenshot-comparison tests.

Verification performed:

- Added facade integration coverage for public outer occupancy snapshots with safe/protected
  status.
- Added render-state tests for single pieces, same-color stacks, mixed-color stacks, 3+ color
  stacks, large Safe Square stacks, protected-block status, Safe Square status, empty hover,
  occupied hover counts, and popup bounds.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`,
  `uv run ruff check .`, and Pygame launch/visual inspection.

Result summary:

- Added public `OuterOccupancySnapshot` data to facade snapshots.
- Changed outer-square render grouping to use the shared global square instead of owner color, so
  mixed-color stacks draw as one occupancy.
- Added structured stack summary components and hover inspection models.
- Rendered colored compact stack summaries for multiple occupancy while keeping normal single-piece
  rendering.
- Added hover inspection popups with per-color counts, `SAFE SQUARE`, and ordinary
  `PROTECTED BLOCK` labels.
- Wired mouse hover state through the interaction controller and game renderer.

Issues discovered:

- The domain correctly treats occupied Safe Squares as protected for capture purposes. The UI keeps
  the labels distinct by showing `SAFE SQUARE` for Safe Squares and reserving `PROTECTED BLOCK` for
  ordinary non-safe protected stacks.

Follow-up/refinement:

- Future polish can tune the exact visual density of stack summaries if the board art changes.
- Movement/capture/dice animations and no-legal timed notification remain planned future work.

Lessons learned:

- Exposing occupancy metadata at the facade boundary keeps the Pygame layer visual-only while still
  letting it present rules-derived safe/protected context accurately.

## Prompt 14

Prompt ID: Prompt 14

Title: Animations & Audio

Goal: Add non-blocking gameplay animations and audio feedback while keeping all authoritative game
rules inside the existing domain/facade layers.

Context: Prompt 13 completed stack summaries and hover inspection. Prompt 14 adds presentation
feedback above the existing GameFacade, board geometry, rendering, and interaction flow.

Full prompt or faithful prompt record: Prompt 14 was provided as an attached pasted text file. Its
authoritative requirements included:

- read only relevant UX, architecture, and TODO documentation;
- animate piece movement square-by-square along the already resolved logical route;
- make Outer Path to Home Path transitions visually clear;
- keep animation duration configurable;
- animate capture as move arrival, brief captured-piece feedback, and visual return to Yard;
- animate final transition into the player's Finish region;
- add a short dice-roll animation before showing the authoritative facade dice value;
- keep animations non-blocking and pause/resume aware;
- prevent duplicate interaction during critical animation state;
- add audio feedback for dice roll, move, capture, finish, ranking, and UI button clicks;
- use lightweight legal placeholder/generated audio if suitable;
- move tunable animation/audio values into configuration;
- add state/control tests rather than screenshot or waveform tests;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- launch and manually verify gameplay animations, pause/resume, audio, and unchanged rules.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/__init__.py`
- `src/ludo/app/facade.py`
- `src/ludo/audio/__init__.py`
- `src/ludo/audio/service.py`
- `src/ludo/config/__init__.py`
- `src/ludo/config/defaults.py`
- `src/ludo/pygame_ui/animation.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/interaction.py`
- `src/ludo/pygame_ui/main.py`
- `src/ludo/pygame_ui/screens.py`
- `tests/integration/test_game_facade.py`
- `tests/unit/pygame_ui/test_animation.py`
- `tests/unit/pygame_ui/test_interaction.py`
- `tests/unit/test_audio.py`

Constraints:

- Do not implement Bot logic, network play, new gameplay rules, rule variants, major UI redesign,
  or portfolio/README polish.
- Do not modify domain outcomes merely to make animations easier.
- Avoid blocking sleeps or frozen Pygame event loops.
- Do not use copyrighted commercial audio assets.

Verification performed:

- Added facade integration coverage for visual move routes, including Outer Path to Home Path
  boundary transitions.
- Added animation tests for route intake, step progression, once-only completion events, capture
  sequence order, finish completion, authoritative dice result preservation, input lock behavior,
  pause freeze, and resume continuation.
- Added audio tests for facade-result mapping, muted playback, and configured volume routing.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`,
  `uv run ruff check .`, and Pygame launch/visual/audio inspection.

Result summary:

- Added public `MoveRouteStepSnapshot` route data to legal-move snapshots.
- Added configurable `AnimationSettings` and `AudioSettings`.
- Added a non-blocking `AnimationManager` for dice, movement, capture, and finish feedback.
- Wired gameplay clicks to start animations from facade results and lock duplicate input while
  critical animations run.
- Added renderer support for dice rolling values, animated piece overlays, captured-piece return,
  and finish pulse feedback.
- Added `AudioService` with generated placeholder tones and a no-op fallback path.

Issues discovered:

- The facade previously exposed legal destinations but not visual routes. Prompt 14 added route
  snapshots at the facade boundary so Pygame can animate resolved moves without recalculating
  movement legality.
- Audio uses generated tones instead of external assets, so no third-party asset license is needed.

Follow-up/refinement:

- Future UX work can replace generated tones with curated licensed assets if desired.
- The no-legal-move timed notification remains planned for a later milestone.

Lessons learned:

- Animation state can be kept presentation-only if the facade exposes enough resolved event data:
  route, final dice value, capture result, finish result, and ranking result.

## Prompt 15

Prompt ID: Prompt 15

Title: Complete UX Integration & Match Flow

Goal: Complete the remaining user-facing local Human-vs-Human flow from main menu through final
results without adding new gameplay rules.

Context: Prompt 14 added animations and audio. Prompt 15 integrates the remaining UX states:
no-legal-move countdown, timeout feedback, completed pause/restart flow, ranking feedback, final
results, and clean reset paths.

Full prompt or faithful prompt record: Prompt 15 was provided as an attached pasted text file. Its
authoritative requirements included:

- read only relevant UX, rules, and TODO documentation;
- show `NO LEGAL MOVE` for 5 seconds with countdown and block gameplay input;
- automatically continue to the next player after the no-legal notice;
- represent roll and move decision windows and provide timeout feedback;
- complete pause with Resume, Restart Match, Main Menu, and Quit;
- freeze timers, animations, and gameplay input while paused;
- restart matches without stale state;
- show brief ranking feedback when a player finishes all four pieces;
- transition to final Results when the match completes;
- support final standings for 2, 3, and 4 players, including automatic final rank;
- ensure Play Again, Main Menu, and Quit clear stale state correctly;
- add integration/state tests for the complete flow and alternate paths;
- update `docs/TODO.md` and `docs/PROMPTS_BOOK.md`;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- manually launch and verify representative complete flows without fabricating checks.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/__init__.py`
- `src/ludo/app/facade.py`
- `src/ludo/config/defaults.py`
- `src/ludo/pygame_ui/interaction.py`
- `src/ludo/pygame_ui/layout.py`
- `src/ludo/pygame_ui/screens.py`
- `src/ludo/pygame_ui/state.py`
- `tests/integration/test_game_facade.py`
- `tests/unit/pygame_ui/test_screens.py`
- `tests/unit/pygame_ui/test_state.py`

Constraints:

- Do not implement Bot/AI, networking, online multiplayer, new Ludo rules, rule variants, major
  redesign, screenshots/GIFs, release work, or tagging.
- Do not reproduce legal-move logic in Pygame.
- Avoid brittle screenshot tests.

Verification performed:

- Added tests for the 5-second no-legal flow, roll timeout, move timeout, pause freeze, resume,
  restart cleanup, rank notification, ranked-player removal from turn rotation, standings for 2/3/4
  players, automatic final rank, Play Again clean state, Main Menu cleanup, and representative
  match completion reaching Results.
- Added a facade pause-clock test showing UI-created matches preserve remaining time while paused.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`, and
  `uv run ruff check .`.

Result summary:

- Added a pausable real clock for UI-created facade matches while preserving injected clocks for
  deterministic tests.
- Added facade `pause()` and `resume()` methods.
- Added screen-flow state for no-legal countdowns and transient feedback messages.
- Added automatic no-legal turn passing, timeout processing, ranking feedback, and final Results
  transition in the Pygame screen update loop.
- Added Restart Match to the pause overlay.
- Made Play Again immediately start a fresh match from the previous setup.
- Centralized presentation reset so Main Menu, Restart, Play Again, and new Start Game do not leak
  stale animations, hover state, or facade results.

Issues discovered:

- UI-created matches were using the deterministic `FixedClock`, so real gameplay timers did not
  naturally expire. Prompt 15 fixed this by creating a pausable real clock at the facade boundary
  when no test clock is injected.
- The pause menu was missing Restart Match; Prompt 15 added it and wired it to a clean restart.

Follow-up/refinement:

- Final QA/release work remains a separate future milestone.
- Manual full-path testing should be repeated during final QA with real human input and screenshots
  only when requested by the release prompt.

Lessons learned:

- Keeping timeout/no-legal progression in the UI update loop still preserves the rule boundary when
  every transition is routed through existing facade commands.

## Bugfix — Audit Visual Step Count at Board Corners

Prompt ID: Bugfix

Title: Audit Visual Step Count at Board Corners

Goal: Verify and correct the full path from piece-relative progress through global outer index,
board-grid coordinates, facade animation route, and Pygame movement rendering so every legal outer
move visually corresponds to exactly the dice value.

Context: A manual playtest found that pieces sometimes appeared to move one extra visible square,
especially around 2D board corners. The authoritative domain path is 1D, while the board renderer
maps it onto a 15x15 grid.

Full prompt or faithful prompt record: The bugfix prompt was provided directly in chat. Its
authoritative requirements included:

- inspect only the relevant board, movement, geometry, facade route, animation, and test code;
- audit all four corner transitions in `OUTER_GRID_PATH`;
- determine whether the defect was domain movement, animation route generation, grid mapping,
  corner coordinates, or visual presentation;
- verify every color, every outer starting progress, and dice values `1..6`;
- verify route length, route destination, wraparound, and Outer Path to Home Path transitions;
- preserve approved Ludo rules and avoid unrelated gameplay changes;
- update this prompts book and `docs/TODO.md` only if appropriate;
- run `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- manually inspect representative moves crossing each board corner.

Files expected to change:

- `docs/PROMPTS_BOOK.md`
- `src/ludo/pygame_ui/animation.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `tests/integration/test_move_routes.py`
- `tests/unit/geometry/test_board_geometry.py`
- `tests/unit/pygame_ui/test_animation.py`

Constraints:

- Do not change approved domain movement rules.
- Do not alter dice probabilities, capture/block rules, bonus rules, Triple Six, timers, ranking,
  audio, or unrelated UI design.
- Do not compensate for rendering by changing domain progress.
- Do not add extra animation points, count the starting square as a moved step, or duplicate final
  destinations.

Verification performed:

- Added exhaustive route regression tests for all colors, all 52 outer progresses, and dice values
  `1..6`.
- Added explicit tests for all four diagonal corner transitions.
- Added wraparound and Outer Path to Home Path route tests.
- Added `OUTER_GRID_PATH` topology tests for 52 unique ordered positions.
- Added animation rendering regression coverage for using the current source square as the visual
  start of a one-step corner move.
- Ran `uv run pytest`.
- Ran `uv run pytest --cov`.
- Ran `uv run ruff check .`.
- Manually inspected representative rendered corner animations.

Result summary:

- Domain movement and facade route counts were correct.
- `OUTER_GRID_PATH` intentionally contains four diagonal one-step corner transitions to preserve
  the 52-square topology on the 15x15 board.
- The misleading visual behavior came from rendering movement at route centers without retaining
  the piece's source square for interpolation.
- Movement animation now records a presentation-only source step and interpolates continuously from
  source to each authoritative route step, producing one visible progression per logical route
  step.

Issues discovered:

- No off-by-one domain movement bug was found.
- No duplicated or skipped outer-grid coordinate was found.
- The diagonal corner transitions are valid logical single steps, but they needed smoother visual
  presentation.

Follow-up/refinement:

- Future animation polish can tune easing or duration, but route step counts should remain tied to
  facade-provided route snapshots.

Lessons learned:

- A 1D-to-2D path can be logically correct while still feeling wrong if the animation omits the
  source position and jumps directly between destination route points.

## Documentation Baseline — Current Implemented Game

Prompt ID: Documentation Baseline

Title: Current Implemented Game Documentation Audit

Goal: Perform a documentation-only audit and update so project documentation accurately reflects
the currently implemented and tested game.

Context: The project has progressed beyond the early planning documents. The implemented baseline
now includes playable local Human vs Human Ludo through Pygame, domain rules, a facade boundary,
board geometry, rendering, interaction, animations, audio, pause/restart/results flow, and automated
tests.

Full prompt or faithful prompt record: The documentation-baseline prompt was provided as an
attached pasted text file. Its authoritative requirements included:

- inspect actual implementation, tests, metadata, and documentation;
- document only functionality that currently exists;
- do not document experimental gameplay expansions such as special/bonus die variants, hazards,
  bombs, backward capture, coins/shop, split dice, Time Crystal/Undo, or Bot/AI gameplay;
- update README, rules, UX, architecture/plan, TODO, project metadata if stale, and this prompts
  book;
- preserve historical prompt entries rather than rewriting old milestones;
- modify no gameplay code and no tests;
- run `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- verify the documented application launch command when practical.

Files expected to change:

- `README.md`
- `docs/PRD.md`
- `docs/PRD_GAME_RULES.md`
- `docs/UX_DESIGN.md`
- `docs/PLAN.md`
- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `pyproject.toml`

Constraints:

- Documentation-only change.
- Do not modify gameplay code or tests.
- Do not add features or refactor source code.
- Do not change game rules.
- Do not add or describe unimplemented experimental expansions.
- Do not fabricate screenshots, media, performance claims, or manual gameplay verification.

Verification performed:

- Audited documentation against implementation and tests.
- Updated project metadata description only.
- Ran `uv run pytest`: 1478 passed.
- Ran `uv run pytest --cov`: 86.82% total coverage, above the configured 85% threshold.
- Ran `uv run ruff check .`: all checks passed.
- Ran `uv run python -m ludo.pygame_ui.main --smoke`: application entry point started and exited.

Result summary:

- README now presents the project as a playable implemented game rather than a planned project.
- PRD, UX, and architecture documents now describe the current baseline.
- Rules documentation now records the implemented start and safe-square indexes.
- TODO now marks the current coverage and lint/test baseline as complete while leaving release
  media, licensing, attribution, and tagging planned.

Issues discovered:

- README, PRD, UX, PLAN, and `pyproject.toml` still contained planning-era language.
- Historical prompts-book entries intentionally retain their original milestone context.

Follow-up/refinement:

- Add real screenshots/GIFs only after a separate release/media task captures them.
- License, attribution, packaging, and release tagging remain future release-preparation work.

Lessons learned:

- Current-state documents and historical prompt records serve different purposes; only the former
  should be rewritten as the implementation evolves.

## Gameplay Expansion — Bonus Die, Hazards & Backward Capture

Prompt ID: Gameplay Expansion

Title: Bonus Die, Hazards & Backward Capture

Goal: Implement three approved gameplay extensions on top of the existing Ludo game: Special Bonus
Die, Hazard Squares, and Backward Capture.

Context: The current game already had a tested domain engine, facade boundary, board geometry,
Pygame rendering/interaction, animations, audio, timers, ranking, and final results. This milestone
extends gameplay while preserving the existing architecture direction:

```text
Pygame UI -> GameFacade -> domain/services
```

Full prompt or faithful prompt record: The expansion prompt was provided as an attached pasted text
file. Its authoritative requirements included:

- add a configurable/injectable binary special die with 80% no effect and 20% `+2`;
- keep `base_roll`, `special_bonus`, and `effective_move` distinct;
- make Triple Six and six-based bonus rolls depend only on the base roll;
- discard `+2` only when no effective-value legal action exists and a base-value legal action does;
- add exactly four fixed match Hazard Squares, one per sector, never overlapping safe/start squares;
- apply a two-step backward hazard penalty only on direct destination landing;
- resolve collision normally after hazard penalty and prevent hazard chains;
- add backward capture only when moving backward by the approved movement value immediately captures
  a vulnerable opponent;
- expose direction/action information through facade snapshots;
- update UI/facade/rendering without duplicating rules in Pygame;
- update only `docs/TODO.md` and this prompts book during the implementation prompt;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- launch the game manually where practical without fabricating manual cases.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/facade.py`
- `src/ludo/audio/service.py`
- `src/ludo/domain/__init__.py`
- `src/ludo/domain/bonus_die.py`
- `src/ludo/domain/hazards.py`
- `src/ludo/domain/match.py`
- `src/ludo/domain/movement.py`
- `src/ludo/domain/turns.py`
- `src/ludo/pygame_ui/board_renderer.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/interaction.py`
- `src/ludo/pygame_ui/render_models.py`
- `src/ludo/pygame_ui/render_state.py`
- affected tests under `tests/`

Constraints:

- Do not implement Time Crystal/Undo, coins/shop, Exact Dice purchase, Shockwave purchase,
  split-dice movement, Bot/AI, networking, or unrelated mechanics.
- Do not redesign the board/UI.
- Do not perform the full post-expansion documentation rewrite.

Verification performed:

- Ran `uv sync`.
- Ran `uv run pytest`: 1497 passed.
- Ran `uv run pytest --cov`: 86.35% total coverage, above the configured 85% threshold.
- Ran `uv run ruff check .`: all checks passed.
- Ran `uv run python -m ludo.pygame_ui.main --smoke`: application entry point started and exited.

Result summary:

- Added special-die providers with deterministic and random implementations.
- Extended turn flow with base roll, special bonus, approved movement value, fallback handling, and
  action IDs.
- Added fixed match hazards with deterministic generation and domain-resolved two-step penalties.
- Added backward capture as a capture-only legal action, not a general backward move mode.
- Extended facade snapshots/results with hazard positions, special-die state, movement value,
  action kind, action ID, and hazard-trigger result data.
- Rendered hazard markers and compact special-die movement feedback.
- Added action-aware interaction so ambiguous same-piece choices can be selected explicitly by
  action/destination instead of silently picking one.
- Added audio mapping for hazard-triggered moves.

Issues discovered:

- Existing route-count regression tests needed explicit no-hazard setup because hazard penalty
  routes intentionally add forced penalty route steps after approved movement.
- Existing snapshot test builders needed default values for new facade fields.

Follow-up/refinement:

- A separate documentation prompt should update README, PRD, rules, UX, and architecture documents
  for these new rules after the implementation is reviewed.
- Future UI polish can improve multi-action selection presentation beyond destination clicking.

Lessons learned:

- Keeping action IDs at the facade boundary lets the UI distinguish forward movement from backward
  capture without importing domain rules.

## Gameplay Fix — Dice Flow, Yard Release, Home Entry & Action UX

Prompt ID: Gameplay Fix

Title: Dice Flow, Yard Release, Home Entry & Action UX

Goal: Implement targeted fixes from manual playtest/audit findings: separate the normal and
special dice, make `+2` optional, enforce base-die-only Yard release, add forced-six anti-stall
behavior, correct Outer Path to Home Path geometry, improve visual path clarity, and keep
same-piece multi-action selection explicit.

Context: The game already included the Bonus Die, Hazard Squares, and Backward Capture expansion.
The audit found that the special die was rolled automatically, synthetic sixes could release Yard
pieces, fully trapped players could stall, and the 2D home-entry coordinates made pieces appear to
overshoot their private Home Path.

Full prompt or faithful prompt record: The gameplay-fix prompt was provided as an attached pasted
text file. Its authoritative requirements included:

- split normal die and special die into separate authoritative turn phases and facade/UI actions;
- keep the special die configurable/injectable and explicitly clickable;
- expose `base` and `base + 2` movement choices without automatically preferring the bonus value;
- keep Triple Six, six-based bonus rolls, and Yard release tied only to the real base die;
- add a forced real base six after a player begins fully in Yard and completes a turn without any
  piece leaving Yard;
- avoid marking a stall during a bonus-roll chain;
- correct all four visual Outer Path to Home Path entries while preserving the 52-square topology;
- improve static-board distinction between shared outer path, private Home Paths, Finish, and dice
  areas;
- preserve friendly-piece protection, private Home Paths, Hazard behavior, and Backward Capture
  rules;
- update only `docs/TODO.md` and this prompts book;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- manually inspect representative dice flow and Home-entry behavior where practical.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/facade.py`
- `src/ludo/audio/service.py`
- `src/ludo/domain/turns.py`
- `src/ludo/geometry/board_geometry.py`
- `src/ludo/geometry/grid.py`
- `src/ludo/pygame_ui/board_renderer.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/interaction.py`
- `src/ludo/pygame_ui/render_models.py`
- `src/ludo/pygame_ui/render_state.py`
- affected tests under `tests/`

Constraints:

- Do not implement Time Crystal, coins/shop, Split Dice, Bot/AI, networking, new power-ups, or
  unrelated visual redesign.
- Do not move authority for dice phases, forced-six state, Triple Six, Yard release, Home ownership,
  or Backward Capture legality into Pygame.
- Do not rewrite final documentation beyond TODO and this prompt log.

Verification performed:

- Added/updated tests for explicit base and special dice, no automatic special roll, Triple Six
  skipping special roll, optional `+2` action exposure, synthetic six Yard rejection, real base-six
  Yard release, forced-six stall recovery, route/home geometry continuity, multi-action selection,
  screen flows, audio mapping, and existing route-count invariants.
- Ran `uv run pytest`: 1506 passed.
- Final verification to run: `uv sync`, `uv run pytest --cov`, `uv run ruff check .`, and practical
  manual launch/inspection.

Result summary:

- Added `WAITING_FOR_SPECIAL_ROLL`, explicit `roll_special()`, and separate facade result kinds for
  base and special dice.
- Legal move construction now exposes explicit action IDs by movement value and keeps Yard release
  attached to a real base six.
- Added forced-six state to the turn engine for full-Yard stall recovery.
- Corrected `OUTER_GRID_PATH` so each color's final outer entry is adjacent to that color's first
  Home Path square.
- Split the center dice UI into normal/special die controls and kept multi-action selection
  destination/action aware.

Issues discovered:

- The earlier automatic special-die fallback was incompatible with strategic optional `+2`.
- The domain route counts were still correct; the Home-entry defect was a 2D coordinate mapping
  issue.

Follow-up/refinement:

- A future documentation prompt should update README, PRD, rules, UX, and architecture documents
  after manual review of this corrected gameplay flow.

Lessons learned:

- Optional movement modifiers need to be represented as legal actions, not as a single approved
  movement value chosen during dice resolution.

## Visual Clarity Fix — Start Safe Squares, Legal Destinations & Center Cells

Prompt ID: Visual Clarity Fix

Title: Start Safe Squares, Legal Destinations & Center Cells

Goal: Improve board readability and move selection without changing gameplay rules: lock Start/Safe
visual alignment, show legal destination `V` markers, support destination-oriented action
selection, and make non-traversable center cells visually distinct.

Context: Manual playtesting found that players could misread Start/Safe squares, legal landing
destinations, and central Finish-adjacent cells. The game already had facade-provided legal actions,
two-dice flow, hazards, backward capture, and corrected Outer Path to Home Path geometry.

Full prompt or faithful prompt record: The visual-clarity prompt was provided as an attached pasted
text file. Its authoritative requirements included:

- ensure Yard release destination, player start index, Start/Safe membership, and visual Start/Safe
  marker identify the same square for all four colors;
- preserve exactly eight unique Safe Squares and Hazard exclusion from all Safe Squares;
- render a visible active-color `V` marker on every facade-exposed legal destination;
- include base, `base + 2`, and Backward Capture destinations when legal;
- allow clicking the legal destination to execute the exact action ID that produced the marker;
- clear markers immediately after move selection and hide markers during animation;
- make center cells that are not Outer Path, Home Path, Finish, or dice visibly non-traversable;
- avoid altering the 52-square topology, movement distance, hazards, capture/block rules, timers,
  ranking, audio behavior, or bonus probabilities;
- update only `docs/TODO.md` and this prompts book;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- manually inspect all four player sides where practical without fabricating checks.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/geometry/board_geometry.py`
- `src/ludo/geometry/grid.py`
- `src/ludo/pygame_ui/board_renderer.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/render_models.py`
- `src/ludo/pygame_ui/render_state.py`
- affected tests under `tests/`

Constraints:

- Do not change gameplay rules or topology counts.
- Do not calculate legality in Pygame.
- Do not add screenshot-comparison tests.
- Do not perform the final documentation rewrite.

Verification performed:

- Added tests for Start/Safe/Yard-release visual alignment, non-traversable center-cell
  classification, legal destination marker generation, base and `+2` marker coverage, Backward
  Capture marker coverage, destination-click action execution, marker clearing, marker suppression
  during animation, and Hazard exclusion from safe squares.
- Ran `uv run pytest`: 1514 passed.
- Final verification to run: `uv sync`, `uv run pytest --cov`, `uv run ruff check .`, and practical
  smoke/manual launch inspection.

Result summary:

- Confirmed current logical Start/Safe and Yard-release indices already agree; tests now lock that
  invariant to the rendered square.
- Added non-playable center-cell geometry and dark center-cell rendering.
- Added `DestinationMarkerState` derived from facade legal moves.
- Rendered active-color `V` markers for all legal destinations while suppressing them during
  animation locks.
- Destination clicks continue to resolve through facade action IDs, with marker state clearing from
  the subsequent snapshot.

Issues discovered:

- The visual confusion was partly from center cells that inherited board background styling rather
  than an explicit non-traversable treatment.
- No domain Start/Safe mismatch was found in the current implementation; the risk is now covered by
  regression tests.

Follow-up/refinement:

- Full manual mouse-play verification should still be repeated in a real window before final
  release/media documentation.

Lessons learned:

- Legal-destination affordances are safest when treated as a projection of facade actions, not as
  a separate UI movement calculation.

## Board Expansion — Hazards, Boost Squares & Shields

Prompt ID: Board Expansion

Title: Hazards, Boost Squares & Shields

Goal: Extend the implemented game with a larger per-match special-square layout, direct-landing
Boost effects, and per-piece Shields without changing approved Ludo core rules.

Context: The game already included the playable facade/Pygame flow, optional Special Bonus Die,
Backward Capture, four-Hazard behavior, destination markers, animation routes, and static/audio
feedback systems.

Full prompt or faithful prompt record: The board-expansion prompt was provided as an attached
pasted text file. Its authoritative requirements included:

- generate 8 Hazard squares, 4 Boost squares, and 4 Shield squares per match;
- distribute special squares by sector: 2 Hazards, 1 Boost, and 1 Shield per sector;
- prevent overlap between special-square categories and with all safe/start squares;
- keep the layout fixed for the match and deterministic through injectable randomness;
- preserve Hazard direct-landing behavior as a mandatory two-step backward forced move with no
  chains;
- add Boost direct-landing behavior as a mandatory two-step forward forced move with final
  collision resolution and no chains;
- add Shield-square direct landing that grants one carried shield, with reacquisition allowed after
  consumption;
- make shields protect only against player capture, consuming the shield while leaving both pieces
  in place, with no Yard return and no capture bonus;
- keep Backward Capture from targeting shielded pieces;
- remove carried shields on Home Path entry and Finished;
- expose expansion state through facade snapshots/results and keep rendering dependent on public
  state;
- render Hazards, Boosts, Shield squares, and shielded pieces distinctly while preserving legal
  destination markers;
- add generated audio cues for Boost, Shield acquired, and Shield broken;
- do not implement Portals, Double-or-Nothing, Coins/Shop, Time Crystal, Split Dice, Bot logic, or
  networking;
- update only `docs/TODO.md` and this prompts book;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/domain/hazards.py`
- `src/ludo/domain/pieces.py`
- `src/ludo/domain/movement.py`
- `src/ludo/domain/occupancy.py`
- `src/ludo/domain/turns.py`
- `src/ludo/domain/match.py`
- `src/ludo/domain/__init__.py`
- `src/ludo/app/facade.py`
- `src/ludo/pygame_ui/board_renderer.py`
- `src/ludo/pygame_ui/gameplay_renderer.py`
- `src/ludo/pygame_ui/render_models.py`
- `src/ludo/pygame_ui/render_state.py`
- `src/ludo/audio/service.py`
- affected tests under `tests/`

Constraints:

- Do not alter dice probabilities, Triple Six, forced-six, ranking, timers, the 52-square topology,
  safe-square rules, or unrelated gameplay behavior.
- Do not add new movement chains from forced Hazard/Boost destinations.
- Do not infer shield/capture rules inside Pygame rendering.
- Do not add copyrighted audio assets.

Verification performed:

- Added tests for special-square generation counts, sector distribution, uniqueness, safe-square
  exclusion, facade exposure, Boost movement/capture/no-chain behavior, Shield acquisition,
  non-stacking, shield break, reacquisition, Hazard/shield interaction, Backward Capture shielding,
  and shield removal on Home Path/Finished.
- Added UI/facade/audio tests for shield state projection and Boost/Shield result cues.
- Final verification to run: `uv sync`, `uv run pytest`, `uv run pytest --cov`,
  `uv run ruff check .`, and practical smoke/manual launch inspection.

Result summary:

- Special-square generation now produces 16 non-overlapping match-fixed positions: 8 Hazards, 4
  Boosts, and 4 Shield squares.
- Boosts are domain-resolved direct-landing effects that force two forward outer steps and resolve
  the final occupancy once.
- Shields are stored on immutable piece state, exposed through facade snapshots, consumed by player
  capture, and cleared on Home Path entry or Finished.
- The Pygame layer renders Boost/Shield squares and shielded pieces from facade/render state only.
- Generated audio cues were added for Boost, Shield acquired, and Shield broken.

Issues discovered:

- Shield reacquisition tests must respect turn ownership; the final regression uses a focused
  current-player setup rather than selecting another player's piece out of turn.

Follow-up/refinement:

- A later UX polish pass can refine iconography for Boost/Shield squares once visual assets or a
  final symbol set are approved.

Lessons learned:

- Forced board effects stay easier to reason about when the landing square is resolved first, then
  a single authoritative forced displacement is applied without re-entering special-square logic.

## Bugfix — Prevent Hazard Shortcut Into Home Path

Prompt ID: Bugfix Hazard Home Shortcut

Title: Prevent Hazard Shortcut Into Home Path

Goal: Fix a manual-play edge case where a Hazard penalty near a player's Start square could wrap a
recently released piece to high relative outer progress, allowing premature Home Path entry.

Context: Hazard penalties previously used global-index wraparound to move two squares backward.
That was valid for shared board coordinates but invalid for player-relative journey progress near
Start.

Full prompt or faithful prompt record: The bugfix prompt required:

- forced backward outer movement must never reduce player-relative progress below `0`;
- Hazard penalty should clamp with `max(0, current_progress - 2)` or equivalent;
- clamped Start remains a Safe Square and uses existing collision/protection rules;
- Home Path entry must depend on authoritative player-relative journey progress, not geometric
  proximity or wrapped global indices;
- Backward Capture and future backward effects must not create early Home eligibility;
- Boost behavior, Hazard counts, Shield behavior, Bonus Die, Triple Six, Yard release, ranking, and
  UI design must not change;
- update only `docs/PROMPTS_BOOK.md` and `docs/TODO.md` where appropriate;
- run `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`;
- do not claim manual reproduction unless actually performed.

Files expected to change:

- `docs/TODO.md`
- `docs/PROMPTS_BOOK.md`
- `src/ludo/app/facade.py`
- `src/ludo/domain/hazards.py`
- `src/ludo/domain/movement.py`
- `src/ludo/domain/turns.py`
- affected tests under `tests/`

Verification performed:

- Added regressions for Hazard clamping from progress `1` to Start for all four colors.
- Added checks that Hazard penalty at Start stays at Start, never creates negative progress, and
  does not wrap to outer index `51`.
- Added a regression that an early Hazard clamp cannot create premature Home Path entry.
- Added all-color confirmation that genuine full-lap Home entry still works.
- Added Start/Safe collision coverage after a clamped Hazard penalty.
- Added no-regression coverage for normal Hazard behavior, Backward Capture, Boost forward
  displacement, and facade route previews.
- Ran `uv sync`, `uv run pytest`, `uv run pytest --cov`, and `uv run ruff check .`.

Result summary:

- Root cause was modulo conversion from global Hazard penalty index back to player-relative
  progress, which could turn near-Start progress into near-complete-lap progress.
- Hazard penalty now clamps by player-relative progress before mapping back to a global square.
- Backward Capture no longer exposes capture actions that would require crossing before Start.
- Facade route generation now displays the clamped Hazard penalty route instead of wrapped
  penalty steps.

Follow-up/refinement:

- The original manual scenario should still be replayed in a live window before release notes or
  media capture.

Lessons learned:

- Global board wraparound and player-relative journey progress are different invariants; backward
  forced movement must operate on journey progress first.

## Future Entries

Future prompt entries should be added only after the work is actually requested and performed. Do
not claim future implementation has happened before it exists.
