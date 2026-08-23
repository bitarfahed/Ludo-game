# UX Design

This document describes the currently implemented desktop user experience. Screenshots, gameplay
GIFs, and release media have not been added and must not be fabricated.

## UX Principles

- Modern, clean, and readable desktop presentation.
- Classic Ludo structure with a restrained digital treatment.
- Clear Red, Green, Yellow, and Blue player identity.
- Multiple feedback cues instead of relying only on color.
- Desktop mouse and keyboard first; mobile/touch is out of scope.
- UI displays facade-provided state and never owns authoritative game rules.

## Implemented Screens

The Pygame application includes:

- main menu;
- player setup;
- game board;
- pause overlay;
- final results.

The application entry point is:

```bash
uv run python -m ludo.pygame_ui.main
```

A smoke-launch mode also exists:

```bash
uv run python -m ludo.pygame_ui.main --smoke
```

## Main Menu And Setup

The main menu provides Start Game and Quit. Start Game opens player setup.

Player setup provides:

- 2-, 3-, and 4-player count selection;
- one name field per active player;
- 10-character name limiting;
- disabled Start Game behavior until names are valid;
- Back and Start Game actions.

Color assignment happens when the match starts. Players do not manually choose colors.

## Color Assignment Feedback

When the match begins, each active player name is shown near the assigned Yard. Inactive colors
remain visible as subdued board corners.

- 2-player matches use a randomly selected opposite pair: Red/Yellow or Green/Blue.
- 3-player matches use three random active colors.
- 4-player matches use all colors.

## Board Presentation

The board renderer displays:

- the shared 52-square outer path;
- four Yards;
- colored 5-square Home Paths;
- safe/start markers;
- star safe squares;
- Finish regions;
- a center dice area;
- player label and timer areas.

Logical board positions are mapped to screen coordinates by `BoardGeometry`. Screen geometry does
not define game state.

## Player And Yard Labels

Each active player area shows:

- player name;
- active-player indication;
- status such as finished-piece count or achieved rank;
- timer when that player is active.

Inactive corners are visually present but do not behave as gameplay participants.

## Current Turn Feedback

The current player is indicated through:

- highlighted/current player text;
- active Yard emphasis;
- dice accent associated with the current color;
- timer near the active player area;
- legal-piece rings during move phase.

## Dice UX

The dice is displayed in the center board area.

Implemented states:

- rollable during roll phase;
- disabled outside roll phase;
- short dice-roll animation;
- final authoritative dice value displayed after roll;
- current-player accent when rollable.

Dice clicks are routed through `GameFacade`. The UI does not generate or decide dice values.

## Timer Presentation

The active player's timer shows:

- numeric seconds remaining;
- a small progress bar.

Roll and move phases each use a 10-second decision window. Pause freezes the active timer and resume
continues with the remaining time.

## Piece Representation

Pieces are rendered as small circles with a color and compact letter identity:

```text
Red    -> r
Green  -> g
Yellow -> y
Blue   -> b
```

Pieces are positioned through board geometry according to facade snapshots:

- `IN_YARD` pieces use Yard slots;
- `ON_OUTER_PATH` pieces use global outer squares;
- `ON_HOME_PATH` pieces use private Home Path squares;
- `FINISHED` pieces use the player's Finish region.

## Stack Presentation

Single pieces render normally. Multiple pieces occupying the same logical outer square render as a
compact stack summary such as:

```text
2r
3y
2r 1b
```

Each summary component uses the corresponding player color. This covers same-color stacks, mixed
protected blocks, large safe-square stacks, and multi-color occupancy.

## Hover Inspection

Hovering an occupied outer square shows a popup with per-color counts, for example:

```text
Red x 2
Blue x 1
Green x 1
```

The popup also indicates:

- `SAFE SQUARE` for safe-square occupancy;
- `PROTECTED BLOCK` for ordinary protected occupancy.

Hover inspection is visual-only and does not change game state.

## Legal-Move Presentation

After a roll with legal moves:

- only legal pieces are selectable;
- legal pieces receive a visible ring;
- illegal pieces do not submit moves;
- hovering a legal piece previews the facade-provided destination;
- selecting a legal piece submits the move through `GameFacade`.

The UI does not recalculate legal movement.

## Movement Animation

Resolved moves animate through facade-provided route steps. The renderer interpolates from the
piece's current source square to each authoritative route step, so a dice result of `N` displays
exactly `N` visible movement progressions.

Outer Path to Home Path and finish transitions are represented by route snapshots from the facade.

## Capture Animation

Capture feedback is non-blocking and presentation-only:

1. the moving piece reaches the destination;
2. the captured piece receives brief feedback;
3. the captured piece returns visually to Yard.

The domain/facade already resolved the capture before animation begins.

## Finish And Ranking Feedback

Finished pieces appear in the player's Finish region and are no longer selectable.

When a player finishes all four pieces, the UI displays brief ranking feedback. Ranked players are
skipped by the turn engine. When only one unranked player remains, final ranking is assigned
automatically and the UI transitions to results.

## No-Legal-Move Feedback

If a roll has no legal moves, the game shows a `NO LEGAL MOVE` feedback message with a countdown.
Input is blocked for the notice window, and the turn passes automatically after 5 seconds.

## Pause UX

`ESC` toggles pause.

While paused:

- turn timers stop;
- gameplay input is suspended;
- animations pause;
- facade-created UI clocks preserve remaining time.

Pause menu:

```text
Resume
Restart Match
Main Menu
Quit
```

Restart Match, Main Menu, and Play Again reset presentation state so stale animations, hover state,
and prior facade results do not leak into the next flow.

## Final Results Screen

At match completion, final rankings are shown in rank order. The screen provides:

- Play Again;
- Main Menu;
- Quit.

Play Again starts a fresh match from the previous setup.

## Audio

The audio layer provides generated placeholder tones for:

- UI clicks;
- dice roll;
- move;
- capture;
- finish;
- ranking.

Audio uses configurable volumes and includes a no-op fallback path.

## Accessibility And Readability

- UI does not rely exclusively on color.
- Pieces use letters as well as color.
- Active player is communicated through text, highlight, dice accent, and timer placement.
- Stack summaries remain compact, with hover inspection for details.
- Animations are restrained and non-blocking.

## Important UI States

- main menu;
- player-count selection;
- name entry;
- match start with assigned colors;
- roll phase;
- dice rolling;
- move selection phase;
- legal-piece hover preview;
- no-legal-move notification;
- move animation;
- capture animation;
- finish feedback;
- player ranked;
- paused;
- final results.

## Not Implemented

- online/networked play;
- mobile/touch-specific UI;
- screenshots/GIFs in documentation;
- curated licensed audio assets;
- experimental gameplay expansions outside the current rules baseline.
