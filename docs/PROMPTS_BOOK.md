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

## Future Entries

Future prompt entries should be added only after the work is actually requested and performed. Do
not claim future implementation has happened before it exists.
