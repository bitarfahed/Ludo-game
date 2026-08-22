# UX Design

This document describes the planned desktop user experience. Screenshots, gameplay GIFs, and visual
captures are future documentation artifacts and must not be fabricated before the game exists.

## UX Principles

- Modern, polished, clean, and readable.
- Inspired by traditional Ludo geometry without simply copying a paper board.
- Restrained depth, shadows, highlights, and animation.
- Immediately recognizable Red, Green, Yellow, and Blue player colors.
- Multiple feedback cues instead of relying only on color.
- Desktop mouse and keyboard first; mobile/touch is out of scope for V1.

## Start Screen

The start screen provides:

- 2 Players;
- 3 Players;
- 4 Players;
- a clear transition to name entry;
- invalid-input prevention before match start.

After player count selection, show one name input per player. Names are limited to 10 characters.
Color assignment happens randomly when the match starts, not during manual selection.

## Color Assignment Feedback

When the match begins, the UI should clearly associate each player name with its assigned color and
Yard.

- 2-player matches use a randomly selected opposite pair: Red/Yellow or Green/Blue.
- 3-player matches use three random colors.
- 4-player matches use all colors.
- Inactive corners remain visually present as part of the board but clearly non-participating.

## Board Presentation

The board should preserve classic Ludo readability:

- clear shared path;
- four recognizable Yards;
- colored Home Paths;
- clearly marked safe/star squares;
- visually distinct Finish regions;
- center dice location;
- clean spacing for labels, timers, and stack summaries.

The board rendering layer maps logical positions to screen coordinates. Screen geometry must not
define game state.

## Player and Yard Labels

Each Yard displays:

- player name;
- assigned color;
- progress such as `3 / 4 finished`;
- rank once achieved;
- active-player indication when relevant.

The active player's name and Yard should receive restrained visual emphasis.

## Current Turn Feedback

The active player must be obvious through multiple cues:

- active name highlight;
- subtle Yard highlight;
- dice border or glow using current player color;
- timer near the relevant player area;
- phase-specific affordance, such as clickable dice or selectable pieces.

## Dice UX

The dice sits in the center of the board between the final colored Finish regions. It is clickable
during the roll phase. Avoid requiring a separate distant Roll button.

Planned dice states:

- inactive/disabled;
- rollable for current player;
- rolling animation;
- result displayed;
- highlighted by current player's color.

## Timer Presentation

The timer appears near the player whose decision is required and remains visible to all players.
Display both:

- numeric seconds;
- a small progress indicator or bar.

The roll phase and move phase each use a 10-second decision window. Pause stops the timer and resume
continues with the remaining time.

## Piece Representation

Pieces are small circular game pieces identified by both color and letter:

```text
Red    -> r
Green  -> g
Blue   -> b
Yellow -> y
```

The letter should appear inside a piece shape rather than as a raw board character.

## Stack Presentation

When exactly one piece occupies a square, render it normally. When multiple pieces occupy a square,
use a compact summary such as:

```text
2r
3y
2r 1b
```

Each color component should visually use its corresponding player color. Large stacks should not be
drawn as overlapping full-size pieces.

## Hover Inspection

Hovering a board square should show an enlarged inspection popup or panel. For stacked squares, show
readable details such as:

```text
Red   x 2
Blue  x 1
Green x 1
```

For ordinary protected occupancy, indicate `PROTECTED BLOCK`. For a safe square, indicate
`SAFE SQUARE`. Hover inspection must never modify game state.

## Legal-Move Presentation

After a roll:

- only legal pieces are selectable;
- legal pieces receive a restrained ring, pulse, or highlight;
- illegal pieces remain non-selectable;
- hovering a legal piece may show a hint such as `Move 4 spaces`;
- hovering a legal piece may preview the destination square.

Legal-move calculation comes from the domain/application layer, not from Pygame UI code.

## Movement Animation

Pieces should animate square-by-square along the logical route:

```text
A -> square -> square -> square -> destination
```

The animation layer visualizes a move already resolved by the game engine. It must not contain
business/game-rule logic.

## Capture Animation

Capture should use a short sequence:

1. moving piece reaches destination;
2. captured piece receives brief visual feedback;
3. captured piece returns visually to its Yard.

The sequence should be short enough that gameplay remains responsive.

## Finish and Ranking Feedback

When a piece reaches `FINISHED`, move it visually into the player's Finish area and update progress.
Finished pieces are permanently non-interactive.

When a player finishes all four pieces, briefly display non-disruptive feedback such as:

```text
PLAYER NAME FINISHED!
1st PLACE
```

The player's board status then shows the achieved rank.

## No-Legal-Move Feedback

If a roll has no legal moves, show visible feedback similar to:

```text
NO LEGAL MOVE
Turn will pass...
```

The message lasts 5 seconds and should not unnecessarily obscure the board.

## Pause UX

`ESC` pauses the game.

While paused:

- turn timers stop;
- game input is suspended;
- gameplay animations pause consistently.

Pause menu:

```text
Resume
Restart Match
Main Menu
Quit
```

Resuming restores the same game state and remaining timer rather than resetting the decision window.

## Final Results Screen

At match completion, show final rankings:

```text
FINAL RESULTS

1st  Player A
2nd  Player B
3rd  Player C
4th  Player D
```

Provide:

- Play Again;
- Main Menu;
- Quit.

## Accessibility and Readability

- Do not rely exclusively on color.
- Use labels, letters, highlights, and placement together.
- Keep timer text readable from typical desktop viewing distance.
- Avoid tiny stack details by using hover inspection.
- Maintain sufficient contrast on colored pieces and board regions.
- Keep animation restrained and avoid effects that interfere with decision-making.

## Important UI States

- player-count selection;
- name entry;
- color assignment reveal/match start;
- roll phase;
- dice rolling;
- move selection phase;
- no-legal-move notification;
- move animation;
- capture animation;
- finished-piece update;
- player ranked;
- paused;
- final results.
