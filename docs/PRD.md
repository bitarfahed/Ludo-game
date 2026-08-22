# Product Requirements Document

## Overview

Ludo is a planned desktop PC game written in Python with Pygame. The first version is a local
Human vs Human game for 2, 3, or 4 players. The project is intended as a public GitHub/portfolio
project demonstrating professional Python architecture, deterministic game logic, test-driven
development, polished desktop UX, and maintainable documentation.

This PRD defines product requirements. Detailed gameplay rules are authoritative in
[PRD_GAME_RULES.md](PRD_GAME_RULES.md), architecture is planned in [PLAN.md](PLAN.md), and interface
direction is described in [UX_DESIGN.md](UX_DESIGN.md).

## Problem and Context

The project needs to implement a familiar board-game experience while remaining maintainable enough
for incremental Codex-assisted development. The game must avoid mixing business rules with rendering
or input handling so the rules can be tested deterministically without a Pygame window.

## Target Users

- Local players sharing one desktop computer.
- Developers reviewing the project as a portfolio example.
- Future maintainers or Codex sessions implementing features from the approved documentation.

## Product Goals

- Provide a polished local Ludo experience for 2, 3, and 4 human players.
- Preserve recognizable Ludo structure while documenting this project's custom rule choices.
- Keep game state independent from screen coordinates.
- Route GUI actions through a clean application/SDK facade.
- Support future Human vs Bot extension without redesigning the game engine.
- Maintain clear documentation, clean commits, and high automated test coverage.

## Measurable Quality Goals

- Global automated coverage target: `>= 85%`.
- Core game-rule logic should exceed the global target where practical.
- `uv run ruff check .` should eventually pass with 0 violations.
- Ruff line length should be 100.
- Public domain/application operations should have unit or integration coverage.
- Source files should stay at or below approximately 150 logical lines where practical, splitting
  responsibilities instead of compressing code.

## Functional Requirements

- Start screen supports 2 Players, 3 Players, and 4 Players.
- Players enter names with a maximum length of 10 characters.
- The start screen prevents invalid player names from starting a match.
- Colors are randomly assigned.
- 2-player matches always use opposite corners: Red/Yellow or Green/Blue.
- 3-player matches randomly use three of the four colors.
- 4-player matches use all four colors.
- Inactive colors have no pieces, turns, timers, dice interaction, or progress.
- Active players each own 4 pieces.
- Gameplay follows the rules in [PRD_GAME_RULES.md](PRD_GAME_RULES.md).
- The current player, legal moves, timer state, no-legal-move feedback, rankings, and final results
  are visible to players.
- `ESC` pauses the game and stops timers, input, and animations until resumed.
- Final results show complete rankings and provide Play Again, Main Menu, and exit paths.

## Non-Functional Requirements

- Desktop PC only for V1.
- Pygame UI must not contain authoritative gameplay rules.
- Rendering must not determine legal movement.
- Screen coordinates must not determine game state.
- Game-rule logic must be testable without opening a Pygame window.
- Time and randomness must be injectable or otherwise controllable for deterministic tests.
- The project must use `uv`; documentation must not recommend `pip install`, `requirements.txt`,
  `venv`, `virtualenv`, or `python -m pytest` workflows.
- No external APIs, databases, authentication, accounts, networking, or paid services are required.

## User Stories

- As a player, I can choose whether a match has 2, 3, or 4 players.
- As a player, I can enter a short name so my pieces and Yard are identifiable.
- As a player, I can see the randomly assigned colors when the match begins.
- As a player, I can click the center dice when it is my roll phase.
- As a player, I can select only legal pieces after rolling.
- As a player, I can understand why my turn passed when no legal move exists.
- As a player, I can inspect stacked squares by hovering.
- As a player, I can pause and resume without losing the current timer state.
- As a player, I can see rankings as players finish and at the final results screen.
- As a maintainer, I can test game rules deterministically without rendering.

## Assumptions

- One local computer is shared by all players.
- Mouse and keyboard are available.
- Player names are plain display names only, not account identities.
- Pygame will be the rendering/input library unless a future approved plan changes that.
- Rules in [PRD_GAME_RULES.md](PRD_GAME_RULES.md) override traditional Ludo variants when they differ.

## Dependencies

Planned dependencies:

- Python 3.11+;
- Pygame;
- pytest;
- Ruff;
- `uv` and `uv.lock`.

No implementation dependencies have been installed by this documentation task.

## Constraints

- V1 is local Human vs Human only.
- No bots, online multiplayer, networking, accounts, databases, external APIs, mobile/touch support,
  or service integrations in V1.
- Do not fabricate screenshots, benchmarks, coverage, or passing tests before they exist.
- Maintain proportional architecture for a local desktop game; no microservices, REST API,
  rate-limit queues, token-cost systems, or secret-management architecture beyond normal repository
  hygiene.

## Acceptance Criteria

- A match can be configured for 2, 3, or 4 players with valid names.
- Color assignment follows all player-count constraints.
- The game enforces the authoritative gameplay rules.
- The GUI obtains state and legal actions through the application facade.
- Turn timers and no-legal-move notification durations match the specification.
- Rankings are assigned correctly and the match ends when only one unranked player remains.
- Core rules have deterministic automated coverage.
- The application can be paused and resumed without resetting the current decision window.

## Milestones

1. Documentation approval.
2. Project/package bootstrap.
3. Core domain model and board topology.
4. Legal movement, capture, blocks, bonus rolls, timers, and ranking.
5. Application/SDK facade.
6. Tests and quality tooling.
7. Pygame shell, board geometry, rendering, and input.
8. Animation, hover/stack UX, pause, audio, and final results.
9. README screenshots/GIFs, release QA, and portfolio polish.
