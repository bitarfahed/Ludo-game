# Product Requirements Document

## Overview

Ludo is a local desktop PC game written in Python with Pygame. The current implemented baseline is
a playable Human vs Human game for 2, 3, or 4 players on one computer. The project demonstrates
professional Python architecture, deterministic game logic, test-driven development, a facade
boundary between UI and rules, and maintainable documentation.

Detailed gameplay rules are authoritative in [PRD_GAME_RULES.md](PRD_GAME_RULES.md), architecture
is described in [PLAN.md](PLAN.md), and implemented interface behavior is described in
[UX_DESIGN.md](UX_DESIGN.md).

## Problem and Context

The project implements a familiar board-game experience while keeping business rules out of
rendering and input code. Domain logic is tested without opening a Pygame window, while the Pygame
application consumes public facade snapshots and commands.

## Target Users

- Local players sharing one desktop computer.
- Developers reviewing the project as a portfolio example.
- Future maintainers or Codex sessions extending the current baseline.

## Product Goals

- Provide a playable local Ludo experience for 2, 3, and 4 human players.
- Preserve recognizable Ludo structure while documenting this project's custom rule choices.
- Keep game state independent from screen coordinates.
- Route GUI actions through a clean application/SDK facade.
- Preserve a future Human vs Bot extension point without implementing Bot gameplay now.
- Maintain clear documentation, clean checks, and high automated test coverage.

## Measurable Quality Goals

- Global automated coverage target: `>= 85%`.
- Current baseline coverage: 86.82% from `uv run pytest --cov`.
- `uv run ruff check .` passes with 0 violations.
- Ruff line length is 100.
- Public domain/application operations have unit or integration coverage.
- Source files are kept focused by responsibility where practical.

## Functional Requirements

- Main menu opens player setup.
- Player setup supports 2 Players, 3 Players, and 4 Players.
- Players enter names with a maximum length of 10 characters.
- Invalid or incomplete player names prevent match start.
- Colors are randomly assigned.
- 2-player matches always use opposite corners: Red/Yellow or Green/Blue.
- 3-player matches randomly use three of the four colors.
- 4-player matches use all four colors.
- Inactive colors have no pieces, turns, timers, dice interaction, or progress.
- Active players each own 4 pieces.
- Gameplay follows the rules in [PRD_GAME_RULES.md](PRD_GAME_RULES.md).
- Current player, dice phase, legal moves, timer state, no-legal-move feedback, rankings, and final
  results are visible to players.
- Players roll the center dice during roll phase and select highlighted legal pieces during move
  phase.
- Hovering legal pieces previews the destination.
- Hovering occupied outer squares shows stack inspection details.
- `ESC` pauses the game and stops timers, input, and animations until resumed.
- Pause supports Resume, Restart Match, Main Menu, and Quit.
- Final results show complete rankings and provide Play Again, Main Menu, and Quit.

## Non-Functional Requirements

- Desktop PC only for the current baseline.
- Pygame UI must not contain authoritative gameplay rules.
- Rendering must not determine legal movement.
- Screen coordinates must not determine game state.
- Game-rule logic must be testable without opening a Pygame window.
- Time, dice, and color assignment are injectable or controllable for deterministic tests.
- The project uses `uv`; documentation must not recommend `pip install`, `requirements.txt`,
  `venv`, `virtualenv`, or `python -m pytest` workflows.
- No external APIs, databases, authentication, accounts, networking, or paid services are required.

## User Stories

- As a player, I can choose whether a match has 2, 3, or 4 players.
- As a player, I can enter a short name so my pieces and Yard are identifiable.
- As a player, I can see the randomly assigned colors when the match begins.
- As a player, I can click the center dice when it is my roll phase.
- As a player, I can select only legal pieces after rolling.
- As a player, I can preview where a legal move will land.
- As a player, I can understand why my turn passed when no legal move exists.
- As a player, I can inspect stacked squares by hovering.
- As a player, I can pause and resume without losing the current timer state.
- As a player, I can restart, return to the main menu, or play again without stale state.
- As a player, I can see rankings as players finish and at the final results screen.
- As a maintainer, I can test game rules deterministically without rendering.

## Assumptions

- One local computer is shared by all players.
- Mouse and keyboard are available.
- Player names are plain display names only, not account identities.
- Pygame is the rendering/input library.
- Rules in [PRD_GAME_RULES.md](PRD_GAME_RULES.md) override traditional Ludo variants when they
  differ.

## Dependencies

Implemented dependencies:

- Python 3.11+;
- Pygame;
- pytest;
- pytest-cov;
- Ruff;
- `uv` and `uv.lock`.

## Constraints

- Current baseline is local Human vs Human only.
- No bots, online multiplayer, networking, accounts, databases, external APIs, mobile/touch support,
  or service integrations are implemented.
- Do not fabricate screenshots, benchmarks, coverage, release status, or passing tests.
- Maintain proportional architecture for a local desktop game; no microservices, REST API,
  rate-limit queues, token-cost systems, or secret-management architecture beyond normal repository
  hygiene.

## Acceptance Criteria

- A match can be configured for 2, 3, or 4 players with valid names.
- Color assignment follows all player-count constraints.
- The game enforces the authoritative gameplay rules.
- The GUI obtains state and legal actions through the application facade.
- Turn timers and no-legal-move notification durations match the specification.
- Legal pieces are highlighted and illegal pieces are not accepted as valid moves.
- Move, capture, finish, and dice feedback are presented without changing rules in the UI.
- Rankings are assigned correctly and the match ends when only one unranked player remains.
- Core rules have deterministic automated coverage.
- The application can be paused and resumed without resetting the current decision window.

## Implemented Milestone Baseline

Completed:

1. Documentation and tooling bootstrap.
2. Core domain model and board topology.
3. Legal movement, capture, blocks, bonus rolls, timers, Triple Six, and ranking.
4. Application/SDK facade with immutable public snapshots and command results.
5. Pygame shell, screen flow, board geometry, rendering, input, and HUD.
6. Stack/hover UX, legal-move UX, animations, audio, no-legal feedback, pause, restart, and final
   results.
7. Automated test and Ruff verification above the configured coverage threshold.

Still not completed:

- Screenshots/GIFs and release media.
- License and third-party attribution.
- Release packaging/tagging.
- Online, networking, external services, and experimental gameplay expansions.
