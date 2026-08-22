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

## Future Entries

Future prompt entries should be added only after the work is actually requested and performed. Do
not claim future implementation has happened before it exists.
