# Gameplay Rules Specification

This document is the authoritative gameplay-rules specification for the currently implemented Ludo
game. If a traditional Ludo variant differs from this document, this document wins.

## Terminology

- **Color**: One of Red, Green, Yellow, or Blue.
- **Player**: A human participant assigned one active color.
- **Inactive color**: A board color not used in the current match.
- **Piece**: One of 4 pieces owned by an active player.
- **Yard**: A player's starting holding area.
- **Outer Path**: The shared 52-square circular path.
- **Home Path**: A color-specific private path of 5 squares.
- **Finished**: The final destination after the 5 Home-Path squares.
- **Safe square**: A non-capturing outer-path square.
- **Ordinary square**: An outer-path square that is not safe.
- **Protected block**: Any legal occupancy of 2 or more pieces on an ordinary square.

## Board Topology

- The shared outer path contains exactly 52 logical positions.
- The board uses four colors: Red, Green, Yellow, and Blue.
- Each color has a start position on the shared 52-square path.
- Implemented start positions are Red 0, Green 13, Yellow 26, and Blue 39.
- Pieces move clockwise.
- A piece must complete the full 52-position outer journey relative to its own start before entering
  its private Home Path.
- Each Home Path contains exactly 5 squares.
- Finished is separate from the 5 Home-Path squares.
- The physical/global 52-square board never changes based on player count.
- The authoritative game model must not depend on screen coordinates or a 2D matrix.

Conceptual route:

```text
Yard -> 52 outer-path positions -> 5 private Home-Path positions -> Finished
```

## Player Count and Color Assignment

- The start screen supports 2, 3, or 4 players.
- Players do not manually select colors.
- Colors are assigned randomly when the match starts.
- Inactive colors have no pieces, turns, dice interaction, timers, or progress.

Two-player games:

- Players must occupy opposite corners.
- Valid pairs are Red/Yellow and Green/Blue.
- The game randomly chooses one valid pair and randomly assigns those colors to the players.

Three-player games:

- Three of four colors are randomly assigned.
- The remaining color is inactive.

Four-player games:

- All four colors are used.

## Player Names

- Each player chooses a name after selecting player count.
- Maximum name length is 10 characters.
- Invalid names prevent the match from starting.
- The UI should clearly associate the player name with the randomly assigned color.

## Piece States

Each active player owns exactly 4 pieces. Each piece is in one of four major states:

```text
IN_YARD
ON_OUTER_PATH
ON_HOME_PATH
FINISHED
```

Finished pieces can never move again.

## Dice and Yard Rules

- Each turn begins in a roll phase.
- The dice result is an integer from 1 through 6.
- A piece in the Yard can leave only on an exact roll of 6.
- A piece leaving the Yard moves to that player's starting square.
- If no legal move exists for a roll, the roll is forfeited after no-legal-move feedback.
- Even when one legal move exists, the player must explicitly select the piece.

## Movement and Exact Finish

- The game engine calculates all legal pieces for the current dice result.
- The UI exposes only legal choices.
- A move may traverse ordinary squares, safe squares, and protected blocks unless the exact-finish
  rule prevents the move.
- A piece transitions from outer path to Home Path only after completing its full 52-position outer
  journey relative to its own start.
- A piece reaches Finished only with an exact roll.
- If a dice result would move beyond Finished, the move is illegal and the piece does not move.

## Safe Squares

There are exactly 8 safe squares on the outer path:

- the four player starting squares;
- four additional star-marked safe squares.

Implemented safe-square indexes are:

```text
0, 8, 13, 21, 26, 34, 39, 47
```

Safe-square rules:

- No capture can occur on a safe square.
- Pieces from different players may coexist.
- Multiple pieces from the same player may coexist.
- There is no stacking limit beyond the total pieces in the match.

## Capture Rules

Capture applies only on ordinary, non-safe outer-path squares.

If the moving piece lands on an ordinary square containing exactly one vulnerable opponent piece:

- that opponent piece is captured;
- the captured piece returns to its Yard;
- its state becomes `IN_YARD`;
- the capturing player receives one bonus roll.

If the destination square is safe, no capture occurs. If the destination ordinary square contains a
protected block, no capture occurs.

## Dynamic Protection and Block Rules

This project intentionally uses a custom protection system.

### Same-Player Block

When two or more pieces belonging to one player occupy the same ordinary square, they form a
protected block.

Example:

```text
Red + Red
```

An opponent cannot capture those protected pieces. The block is not a physical barrier: opponents
may pass through it, land on it, and continue moving around the board.

### Joining a Protected Square

If Red + Red already occupy an ordinary square and Blue lands there, Blue does not capture either
Red piece because the Red pieces were protected. The square becomes:

```text
Red + Red + Blue
```

This coexistence is legal.

### Mixed-Player Block

If one Red later leaves, the square becomes:

```text
Red + Blue
```

The remaining pair is still a protected block. This legally evolved mixed-player block can include
more colors, such as:

```text
Red + Blue + Green
```

or pieces from all four active colors. The block is still not a movement barrier. Each player may
move their own pieces out on later legal turns.

### Loss of Protection

If departures reduce an ordinary square to exactly one piece, protection disappears. The remaining
single piece becomes vulnerable again.

### Important Creation Rule

Mixed-player coexistence on an ordinary square cannot be created merely by declining a capture. If
Red is alone on an ordinary square and Blue lands there, Blue must capture Red. The result is not
Red + Blue.

Mixed-player blocks arise only through legal interaction with a previously protected occupancy.

## Bonus Rolls

A player receives one additional roll when at least one of these occurs:

1. the dice result is 6;
2. the resolved move captures an opponent piece;
3. the resolved move causes a piece to reach `FINISHED`.

Bonus reasons do not stack for a single resolved roll/move. A roll of 6 that also captures, or a
roll of 6 that also finishes, still grants only one bonus roll.

A bonus roll is a new roll and may itself create another bonus. There is no stored queue of multiple
bonuses produced by one move.

If a roll has no legal move, that roll is forfeited and does not generate a bonus roll, even if the
unusable result was 6.

## Triple-Six Rule

Track consecutive sixes.

- For `6, 6, 6`, the first two rolls and their resolved moves remain valid.
- The third consecutive six is cancelled.
- On the cancelled third six, no piece moves, no capture is processed, no finish is processed, no
  bonus is awarded, and the turn ends immediately.
- Do not undo the first two moves.
- A non-six resets the consecutive-six counter.
- For `6, 6, 4`, the `4` resets the sequence. If the `4` creates a bonus through capture or finish,
  the next bonus roll starts with the consecutive-six counter reset.

## Timers and No-Legal-Move Feedback

Roll phase:

- At the beginning of a player's turn, they have 10 seconds to roll.
- If the timer expires, the turn is forfeited and play advances to the next active player.

Move phase:

- After a valid dice roll with legal moves, the timer resets to 10 seconds.
- If no legal piece is selected before expiration, the move is forfeited, the turn ends, and play
  advances.
- The game must not automatically choose a move.

No legal moves:

- If a roll produces zero legal moves, show a visible message similar to `NO LEGAL MOVE` and
  `Turn will pass...` for 5 seconds.
- The message does not unnecessarily obscure the board.
- After 5 seconds, the turn ends.
- The unusable roll is forfeited.

## Turn Order

- Active players take turns clockwise according to assigned board positions.
- Inactive colors are skipped.
- Players who have received a final rank are skipped.
- Turn logic should operate on active/eligible players rather than special-casing player counts.

## Ranking and Match Completion

- A player finishes when all 4 of their pieces reach `FINISHED`.
- Finished players receive the next available rank and leave turn rotation.
- The match continues until only one unranked player remains.
- The last unranked player is automatically assigned the final remaining rank.
- Do not force the last remaining player to continue alone.

Rank sets:

- 2 players: 1st, 2nd.
- 3 players: 1st, 2nd, 3rd.
- 4 players: 1st, 2nd, 3rd, 4th.

## Invariants

- Outer path length is always 52.
- Each Home Path length is always 5.
- Finished is separate from Home Path squares.
- Safe-square count is always 8.
- Active players each have 4 pieces.
- Finished pieces never move.
- Inactive colors never participate in gameplay.
- Legal moves are calculated by the domain/application layer, not by Pygame.
- Screen coordinates never define game state.

## Acceptance and Test Scenarios

Required rule-test scenarios:

- leaving Yard with 6;
- failure to leave Yard without 6;
- complete outer-loop progression;
- transition to Home Path;
- exact finish;
- overshooting finish;
- capture of one vulnerable opponent;
- no capture on safe square;
- same-player block creation;
- inability to capture a protected block;
- opponent joining a protected block;
- evolution into mixed-player block;
- mixed block losing protection when reduced to one piece;
- unrestricted passing through blocks;
- safe-square stacking;
- multiple bonus reasons producing only one bonus;
- bonus roll generating another bonus;
- unusable roll producing no bonus;
- consecutive `6,6,6`;
- sequence `6,6,4`;
- roll timeout;
- move timeout;
- zero legal moves;
- active-player rotation;
- inactive colors being skipped;
- finished players being skipped;
- 2-player opposite-corner constraint;
- random color assignment;
- 10-character name limit;
- ranking for 2, 3, and 4 players;
- automatic assignment of final remaining rank.

Additional useful edge cases:

- a Yard exit onto an occupied safe starting square;
- a piece already on Home Path moving exactly to Finished;
- a piece on Home Path overshooting Finished;
- multiple pieces of the same color on a safe square;
- all active colors represented on one safe square;
- a captured piece losing all path progress and returning to Yard;
- a player finishing on a move that also rolled 6 receiving only one bonus before being removed if
  all pieces are finished.
