# Implementation Roadmap

Status values:

- `Complete`: done in the current project state.
- `Planned`: not started.
- `Blocked`: cannot proceed until dependencies are complete.

Default owner: Developer / Codex-assisted.

## Phase 0: Documentation Approval

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Create initial README | Complete | High | Developer / Codex-assisted | None | README accurately states the current playable baseline and links documentation. |
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
| Implement pause/resume workflow | Complete | Medium | Developer / Codex-assisted | Timer state model | Pause preserves game state and remaining timer. |

## Phase 5: Pygame Shell and Rendering

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Add Pygame dependency | Complete | High | Developer / Codex-assisted | Tooling bootstrap | Pygame is added through `uv add pygame`. |
| Create window/application shell | Complete | High | Developer / Codex-assisted | Pygame dependency | Application opens a desktop window and can exit cleanly. |
| Implement screen flow | Complete | High | Developer / Codex-assisted | Facade contracts | Start, name entry, game, pause, and final results screens are routable. |
| Implement board geometry mapper | Complete | High | Developer / Codex-assisted | Board topology | Logical positions map to stable screen coordinates. |
| Render static board | Complete | High | Developer / Codex-assisted | Geometry mapper | Board, Yards, Home Paths, safe squares, and Finish regions render clearly. |
| Render pieces | Complete | High | Developer / Codex-assisted | Static board rendering | Pieces render clearly on Yards, outer path, Home Paths, and Finish regions. |
| Render stacks and hover inspection | Complete | High | Developer / Codex-assisted | Rendering | Stack summaries and hover panel display occupancy/protection/safe-square details. |
| Implement input handling | Complete | High | Developer / Codex-assisted | Screen flow | Dice clicks, legal piece selection, hover, and `ESC` pause map to facade commands. |

## Phase 6: UX Polish

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Add legal-move highlights | Complete | High | Developer / Codex-assisted | Input/rendering | Only legal pieces are selectable and visibly highlighted. |
| Add destination preview | Complete | Medium | Developer / Codex-assisted | Legal-move highlights | Hovering legal pieces previews destination without changing state. |
| Add movement animation | Complete | High | Developer / Codex-assisted | Rendering | Pieces animate square-by-square using resolved domain events. |
| Add capture animation | Complete | Medium | Developer / Codex-assisted | Movement animation | Captures show short feedback and return captured piece visually to Yard. |
| Add timer presentation | Complete | High | Developer / Codex-assisted | Timer state | Numeric and progress indicators appear near active player. |
| Add no-legal-move notification | Complete | High | Developer / Codex-assisted | Timer presentation | 5-second message appears and then advances turn. |
| Add audio service | Complete | Low | Developer / Codex-assisted | Core UX complete | Optional sound effects respect configured volumes. |
| Add final results polish | Complete | Medium | Developer / Codex-assisted | Ranking/rendering | Final rankings and Play Again/Main Menu/Quit paths are polished. |

## Phase 7: Quality, Documentation, and Release

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Expand test coverage | Complete | High | Developer / Codex-assisted | Domain/facade implementation | Global coverage reaches `>= 85%`; core rules exceed target where practical. |
| Run lint and tests | Complete | High | Developer / Codex-assisted | Tests/tooling | `uv run ruff check .` and `uv run pytest` pass. |
| Add screenshots/GIFs | Planned | Medium | Developer / Codex-assisted | Playable UI | Real screenshots/GIFs are captured and added to README. |
| Add architecture diagrams as artifacts | Planned | Low | Developer / Codex-assisted | Architecture stabilization | Useful diagrams are exported or linked without duplicating stale content. |
| Choose license | Planned | Medium | Developer / Codex-assisted | Release preparation | License file and README license section are accurate. |
| Add third-party attribution | Planned | Medium | Developer / Codex-assisted | Dependencies/assets | Dependency and asset credits are documented. |
| Tag meaningful release | Planned | Medium | Developer / Codex-assisted | Final QA | Version tag matches the authoritative application version. |

## Gameplay Expansion: Bonus Die, Hazards, and Backward Capture

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Implement Special Bonus Die | Complete | High | Developer / Codex-assisted | Turn engine and facade | Base roll, special bonus, effective movement, fallback, and Triple-Six interactions are tested. |
| Implement Hazard Squares | Complete | High | Developer / Codex-assisted | Board topology and collision rules | Four fixed match hazards, two-step penalty, collision after penalty, and facade exposure are tested. |
| Implement Backward Capture | Complete | High | Developer / Codex-assisted | Occupancy/capture rules | Capture-only backward actions, action disambiguation, and capture bonus behavior are tested. |

## Gameplay Fix: Dice Flow, Yard Release, Home Entry, and Action UX

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Separate normal and special dice | Complete | High | Developer / Codex-assisted | Gameplay expansion | Base roll and special roll are separate facade/domain/UI actions with timer phases and tests. |
| Make `+2` movement optional | Complete | High | Developer / Codex-assisted | Special die | Base and bonus movement choices are exposed as distinct legal actions when available. |
| Enforce base-die-only Yard release | Complete | High | Developer / Codex-assisted | Movement rules | Synthetic six cannot release from Yard; real base six can. |
| Add forced-six anti-stall rule | Complete | High | Developer / Codex-assisted | Turn engine | Full-Yard stall sets a forced real six on the player's next normal turn and resets correctly. |
| Correct Home-entry geometry | Complete | High | Developer / Codex-assisted | Board geometry | All four Outer Path to Home Path entries are visually continuous while preserving 52 outer squares. |
| Clarify multi-action selection UX | Complete | Medium | Developer / Codex-assisted | Backward Capture | Same-piece forward/backward actions remain selectable by explicit destination/action ID. |

## Visual Clarity Fix: Start Safe Squares, Legal Destinations, and Center Cells

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Lock Start/Safe visual alignment | Complete | High | Developer / Codex-assisted | Board topology and geometry | Yard release, start index, safe square, and visual marker all reference the same square for each color. |
| Render legal destination markers | Complete | High | Developer / Codex-assisted | Facade legal moves | UI derives `V` markers from facade legal actions for base, bonus, and backward-capture destinations. |
| Support destination-oriented selection | Complete | High | Developer / Codex-assisted | Interaction layer | Clicking a legal destination resolves the action ID that produced that marker and clears markers after selection. |
| Mark center cells non-traversable | Complete | Medium | Developer / Codex-assisted | Board renderer | Non-playable center cells around Finish regions are dark and separate from Outer/Home/Finish/Dice cells. |
| Preserve hazard/safe compatibility | Complete | High | Developer / Codex-assisted | Hazard generation | Hazards remain one per sector and do not overlap corrected safe/start squares. |

## Board Expansion: Hazards, Boost Squares, and Shields

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Expand special-square layout | Complete | High | Developer / Codex-assisted | Board topology and safe-square rules | Each match generates 8 Hazards, 4 Boosts, and 4 Shield squares with per-sector distribution and no overlap with safe/start squares. |
| Implement Boost Squares | Complete | High | Developer / Codex-assisted | Movement and collision rules | Direct Boost landings force two outer steps forward, resolve final collision, and do not chain additional special-square effects. |
| Implement Shield Squares and state | Complete | High | Developer / Codex-assisted | Piece state and facade snapshots | Direct Shield-square landings grant at most one shield, shields can be reacquired after use, and shields are removed on Home Path entry or Finish. |
| Integrate shielded capture behavior | Complete | High | Developer / Codex-assisted | Capture/block rules | Player capture consumes a defender shield without Yard return, capture bonus, or Backward Capture legality against that target. |
| Render and expose expansion state | Complete | Medium | Developer / Codex-assisted | Pygame rendering and audio service | Boost/Shield squares, shielded pieces, facade result flags, and generated audio cues are represented without adding new UI rules. |

## Bugfix: Prevent Hazard Shortcut Into Home Path

| Task | Status | Priority | Owner | Dependencies | Definition of Done |
| --- | --- | --- | --- | --- | --- |
| Clamp forced backward outer movement at Start | Complete | High | Developer / Codex-assisted | Hazard and Backward Capture rules | Hazard penalties and Backward Capture cannot wrap below player-relative progress `0`, route previews show the clamped destination, and Home entry still requires a genuine full outer lap. |

Remaining planned work is release/documentation polish, not core gameplay implementation.
