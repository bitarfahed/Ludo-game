# UX Design

This document describes the currently implemented desktop user experience. Screenshots, gameplay
GIFs, and release media have not been added and must not be fabricated.

## UX Principles

- Modern, clean, readable desktop presentation.
- Classic Ludo structure with a restrained digital treatment.
- Clear Red, Green, Yellow, and Blue player identity.
- Multiple feedback cues instead of relying only on color.
- Desktop mouse and keyboard first; mobile/touch is out of scope.
- UI consumes facade-provided state and never owns authoritative game rules.

## Implemented Screens

The Pygame application includes:

- main menu;
- player setup;
- game board;
- pause overlay;
- final results.

Entry point:

```bash
uv run python -m ludo.pygame_ui.main
```

Smoke launch:

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

## Board Presentation

The board renderer displays:

- the shared 52-square Outer Path;
- all four Yard areas;
- active and inactive player corners;
- colored 5-square Home Paths;
- Finish regions;
- Start/Safe markers;
- star Safe Squares;
- non-traversable dark center cells around Finish/Dice areas;
- center normal-die and Special Die controls;
- player name and timer areas;
- Hazard markers;
- Boost `+2` markers;
- Shield Square markers.

Logical board positions are mapped to screen coordinates by `BoardGeometry`. Screen geometry does
not define game state.

## Player Areas And Turn Feedback

Each active player area shows:

- player name;
- active-player indication;
- finished-piece count or achieved rank;
- timer when that player is active.

Current-player feedback combines:

- highlighted player text;
- active Yard emphasis;
- dice accent associated with the current color;
- timer near the active player area;
- legal-piece rings during move phase.

Inactive corners are visible but subdued and do not behave as gameplay participants.

## Dice UX

The center board area contains separate controls for:

- normal/base die;
- Special Die.

Implemented flow:

1. During roll phase, the normal die is clickable.
2. After a valid base roll, the Special Die becomes clickable.
3. After the Special Die result, legal movement actions are shown.

The dice displays authoritative values returned by `GameFacade`. The UI does not generate dice
values or decide whether `+2` applies.

## Legal Destination `V` Markers

After dice resolution:

- legal destinations are shown with compact `V` markers;
- marker color corresponds to the active player;
- markers are derived from facade legal actions, not UI-side movement calculation;
- base and base-plus-2 destinations may both appear when both are legal;
- Backward Capture destinations may appear;
- clicking a marker submits the exact action id represented by that marker;
- markers disappear once an action is selected;
- markers are hidden while movement animation locks input;
- no markers appear when no legal move exists.

Players may also click a legal piece directly when the piece has only one legal action.

## Piece Representation

Pieces render as small circles with color and compact letter identity:

```text
Red    -> r
Green  -> g
Yellow -> y
Blue   -> b
```

Placement always goes through board geometry:

- `IN_YARD` pieces use Yard slots;
- `ON_OUTER_PATH` pieces use global outer squares;
- `ON_HOME_PATH` pieces use private Home Path squares;
- `FINISHED` pieces use the player's Finish region.

Shielded pieces display an additional visual ring/indicator.

## Special-Square Presentation

- Hazards render with a distinct warning marker.
- Boost Squares render with a visible `+2`.
- Shield Squares render with a distinct Shield marker.
- Existing Start/Safe and star Safe Square markers remain visible.
- Legal destination `V` markers are not added to forced Hazard or Boost destinations unless those
  destinations are independently legal actions.

## Stack Presentation

Single pieces render normally. Multiple pieces occupying the same logical outer square render as a
compact stack summary such as:

```text
2r
3y
2r 1b
```

Each summary component uses the corresponding player color. This covers same-color stacks, mixed
protected blocks, safe-square stacks, and multi-color occupancy.

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

Popup placement stays within representative window bounds where practical. Hover inspection is
visual-only and does not change game state.

## Movement, Capture, And Finish Animation

Resolved moves animate through facade-provided route steps. The renderer interpolates from the
piece's source square to each authoritative route step.

- A dice result of `N` displays exactly `N` movement progressions for the selected movement value.
- Special Die `+2`, Hazard penalty, and Boost displacement route additions are produced by facade
  state.
- Outer Path to Home Path and Finish transitions are represented by route snapshots.
- Capture feedback is non-blocking and presentation-only.
- Finish feedback uses a brief pulse.

The domain/facade resolves all move effects before animation begins.

## Timer And No-Legal Feedback

The active player's timer shows:

- numeric seconds remaining;
- a progress bar.

Roll, Special Die, and move phases each use a 10-second decision window. Pause freezes the
UI-created clock and resume continues with the remaining time.

If a roll has no legal actions after the Special Die step, the game shows a `NO LEGAL MOVE`
feedback message with a countdown. Input is blocked for the notice window, and the turn passes
automatically after 5 seconds.

## Pause And Results

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

At match completion, final rankings are shown in rank order. The final results screen provides:

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
- Hazard;
- Boost;
- Shield acquired;
- Shield broken;
- ranking.

Audio uses configurable volumes and includes a no-op fallback path. No copyrighted audio assets are
included.

## Accessibility And Readability

- UI does not rely exclusively on color.
- Pieces use letters as well as color.
- Active player is communicated through text, highlight, dice accent, and timer placement.
- Legal pieces and legal destinations are visually distinguished.
- Stack summaries remain compact, with hover inspection for details.
- Animations are restrained and non-blocking.

## Important UI States

- main menu;
- player-count selection;
- name entry;
- match start with assigned colors;
- roll phase;
- normal die rolling;
- Special Die phase;
- move selection phase;
- legal-piece and legal-destination hover preview;
- no-legal-move notification;
- move animation;
- Hazard/Boost/Shield feedback;
- capture animation;
- finish feedback;
- player ranked;
- paused;
- final results.

## Not Implemented

- online/networked play;
- Bot/AI players;
- mobile/touch-specific UI;
- screenshots/GIFs in documentation;
- curated licensed audio assets;
- Portal, Double-or-Nothing, Coins/Shop, Time Crystal/Undo, or Split Dice systems.
