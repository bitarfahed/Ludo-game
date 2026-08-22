# Implementation Roadmap

Status values:

- `Complete`: done in the current project state.
- `Planned`: not started.
- `Blocked`: cannot proceed until dependencies are complete.

Default owner: Developer / Codex-assisted.

## Phase 0: Documentation Approval

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Create initial README | Complete | High | Developer / Codex-assisted | None | README accurately states planning-only status and links documentation. |
| Create PRD | Complete | High | Developer / Codex-assisted | None | Product requirements, scope, goals, constraints, and milestones documented. |
| Create rules specification | Complete | High | Developer / Codex-assisted | None | Authoritative gameplay rules and critical test scenarios documented. |
| Create UX design document | Complete | High | Developer / Codex-assisted | None | Planned screens, interactions, feedback, and accessibility notes documented. |
| Create architecture plan | Complete | High | Developer / Codex-assisted | None | Architecture boundaries, diagrams, SDK facade, testing strategy, and ADRs documented. |
| Create prompts book | Complete | Medium | Developer / Codex-assisted | None | Prompt 0 is recorded and reusable entry format exists. |
| Review and approve documentation | Complete | High | Developer / Codex-assisted | Documentation package | Human reviewer accepts docs or requests revisions. |

## Phase 1: Project and Tooling Bootstrap

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Configure package metadata | Complete | High | Developer / Codex-assisted | Documentation approval | `pyproject.toml` reflects package name, version strategy, Python version, and tooling plan. |
| Add `uv.lock` | Complete | High | Developer / Codex-assisted | Package metadata | Dependencies are locked through `uv`. |
| Add Ruff configuration | Complete | High | Developer / Codex-assisted | Package metadata | `uv run ruff check .` is the documented lint command with `line-length = 100`. |
| Create source package skeleton | Complete | High | Developer / Codex-assisted | Package metadata | `src/ludo/` exists with package `__init__.py` files and no gameplay shortcuts. |
| Create test skeleton | Complete | High | Developer / Codex-assisted | Package metadata | `tests/unit/` and `tests/integration/` exist. |

## Phase 2: Core Domain Foundation

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Define colors and piece states | Complete | High | Developer / Codex-assisted | Source/test skeleton | Enums or equivalent types represent colors and piece states. |
| Define player and piece models | Complete | High | Developer / Codex-assisted | Colors and states | Active players own 4 pieces; inactive colors have none. |
| Define board topology | Complete | High | Developer / Codex-assisted | Colors | 52 outer positions, 5 Home-Path squares, starts, and 8 safe squares are represented and tested. |
| Add deterministic randomness abstraction | Complete | High | Developer / Codex-assisted | Source skeleton | Dice behavior and color assignment can be controlled in tests. |
| Implement color assignment | Complete | High | Developer / Codex-assisted | Randomness abstraction | 2-player opposite pairs, 3-player random inactive color, and 4-player assignment are tested. |

## Phase 3: Rules and State Machine

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Implement legal-move calculation | Complete | High | Developer / Codex-assisted | Board topology | Legal pieces are calculated for Yard, outer, Home Path, exact finish, and overshoot cases. |
| Implement move resolution | Complete | High | Developer / Codex-assisted | Legal moves | Moving a selected legal piece updates state and emits useful events. |
| Implement capture rules | Complete | High | Developer / Codex-assisted | Move resolution | Vulnerable single opponent capture and safe-square non-capture are tested. |
| Implement block/protection rules | Complete | High | Developer / Codex-assisted | Capture rules | Same-player blocks, joining protected occupancy, mixed blocks, and loss of protection are tested. |
| Implement bonus roll rules | Complete | High | Developer / Codex-assisted | Move resolution | 6, capture, finish, non-stacking reasons, chained bonuses, and unusable roll behavior are tested. |
| Implement triple-six rule | Complete | High | Developer / Codex-assisted | Bonus rules | Third consecutive six is cancelled without undoing first two moves. |
| Implement turn manager | Complete | High | Developer / Codex-assisted | Player models | Clockwise active-player rotation skips inactive colors; ranked-player skipping remains for the ranking milestone. |
| Implement ranking | Complete | High | Developer / Codex-assisted | Turn manager | Rankings for 2, 3, and 4 players and automatic final rank are tested. |
| Implement timer state model | Complete | High | Developer / Codex-assisted | Turn state machine | Roll/move 10-second windows and no-legal notice completion are deterministic in tests. |

## Phase 4: Application Facade

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Design facade contracts | Complete | High | Developer / Codex-assisted | Domain foundation | GUI-facing commands and snapshots are explicit and tested. |
| Implement match start workflow | Complete | High | Developer / Codex-assisted | Color assignment | Player count and names validate through the facade. |
| Implement roll workflow | Complete | High | Developer / Codex-assisted | Legal moves, timers | Roll phase returns dice result, legal choices, no-legal state, or triple-six cancellation. |
| Implement move selection workflow | Complete | High | Developer / Codex-assisted | Move resolution | Selecting a piece resolves the move and returns snapshot/events. |
| Implement pause/resume workflow | Planned | Medium | Developer / Codex-assisted | Timer state model | Pause preserves game state and remaining timer. |

## Phase 5: Pygame Shell and Rendering

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Add Pygame dependency | Complete | High | Developer / Codex-assisted | Tooling bootstrap | Pygame is added through `uv add pygame`. |
| Create window/application shell | Complete | High | Developer / Codex-assisted | Pygame dependency | Application opens a desktop window and can exit cleanly. |
| Implement screen flow | Complete | High | Developer / Codex-assisted | Facade contracts | Start, name entry, game, pause, and final results screens are routable. |
| Implement board geometry mapper | Complete | High | Developer / Codex-assisted | Board topology | Logical positions map to stable screen coordinates. |
| Render static board | Complete | High | Developer / Codex-assisted | Geometry mapper | Board, Yards, Home Paths, safe squares, and Finish regions render clearly. |
| Render pieces | Complete | High | Developer / Codex-assisted | Static board rendering | Pieces render clearly on Yards, outer path, Home Paths, and Finish regions. |
| Render stacks and hover inspection | Planned | High | Developer / Codex-assisted | Rendering | Stack summaries and hover panel display occupancy/protection/safe-square details. |
| Implement input handling | Complete | High | Developer / Codex-assisted | Screen flow | Dice clicks, legal piece selection, hover, and `ESC` pause map to facade commands. |

## Phase 6: UX Polish

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Add legal-move highlights | Complete | High | Developer / Codex-assisted | Input/rendering | Only legal pieces are selectable and visibly highlighted. |
| Add destination preview | Complete | Medium | Developer / Codex-assisted | Legal-move highlights | Hovering legal pieces previews destination without changing state. |
| Add movement animation | Planned | High | Developer / Codex-assisted | Rendering | Pieces animate square-by-square using resolved domain events. |
| Add capture animation | Planned | Medium | Developer / Codex-assisted | Movement animation | Captures show short feedback and return captured piece visually to Yard. |
| Add timer presentation | Complete | High | Developer / Codex-assisted | Timer state | Numeric and progress indicators appear near active player. |
| Add no-legal-move notification | Planned | High | Developer / Codex-assisted | Timer presentation | 5-second message appears and then advances turn. |
| Add audio service | Planned | Low | Developer / Codex-assisted | Core UX complete | Optional sound effects respect configured volumes. |
| Add final results polish | Planned | Medium | Developer / Codex-assisted | Ranking/rendering | Final rankings and Play Again/Main Menu/Quit paths are polished. |

## Phase 7: Quality, Documentation, and Release

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Expand test coverage | Planned | High | Developer / Codex-assisted | Domain/facade implementation | Global coverage reaches `>= 85%`; core rules exceed target where practical. |
| Run lint and tests | Planned | High | Developer / Codex-assisted | Tests/tooling | `uv run ruff check .` and `uv run pytest` pass. |
| Add screenshots/GIFs | Planned | Medium | Developer / Codex-assisted | Playable UI | Real screenshots/GIFs are captured and added to README. |
| Add architecture diagrams as artifacts | Planned | Low | Developer / Codex-assisted | Architecture stabilization | Useful diagrams are exported or linked without duplicating stale content. |
| Choose license | Planned | Medium | Developer / Codex-assisted | Release preparation | License file and README license section are accurate. |
| Add third-party attribution | Planned | Medium | Developer / Codex-assisted | Dependencies/assets | Dependency and asset credits are documented. |
| Tag meaningful release | Planned | Medium | Developer / Codex-assisted | Final QA | Version tag matches the authoritative application version. |

Future implementation tasks remain uncompleted by design.
