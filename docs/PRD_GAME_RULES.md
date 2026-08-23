# Gameplay Rules Specification

This document is the authoritative gameplay-rules specification for the currently implemented Ludo
game. If a traditional Ludo variant differs from this document, this document wins.

## Terminology

- **Color**: Red, Green, Yellow, or Blue.
- **Player**: A local human participant assigned one active color.
- **Inactive color**: A board color not used in the current match.
- **Piece**: One of 4 pieces owned by an active player.
- **Yard**: A player's starting holding area.
- **Outer Path**: The shared 52-square logical path.
- **Start Square**: A color's entry square on the Outer Path.
- **Home Path**: A color-specific private path of 5 squares.
- **Finished**: The final destination after a piece leaves the Home Path.
- **Safe Square**: A non-capturing outer-path square.
- **Ordinary Square**: An outer-path square that is not safe.
- **Protected Block**: Any legal occupancy of 2 or more pieces on an ordinary square.
- **Base Roll**: The normal die result, 1 through 6.
- **Special Roll**: A separate special die roll that may add `+2`.
- **Chosen Movement Value**: The movement amount selected from legal base or base-plus-special
  actions.

## Player Count And Color Assignment

- Matches support exactly 2, 3, or 4 active players.
- Each active player owns exactly 4 pieces.
- Player names are validated and limited to 10 characters.
- Players do not manually choose colors.
- Colors are randomly assigned through injectable randomness.
- Inactive colors have no Player object in turn order, no pieces, no turns, no timers, and no dice
  interaction.

Two-player matches:

- Use one opposite pair only: Red/Yellow or Green/Blue.
- The pair and player-color assignment are random.

Three-player matches:

- Use three distinct random colors.
- The fourth color is inactive.

Four-player matches:

- Use all four colors.

Turn order follows clockwise board color order among active, unranked players.

## Board Topology

- The shared Outer Path contains exactly 52 logical positions.
- Implemented Start positions are Red 0, Green 13, Yellow 26, and Blue 39.
- Each Start Square is also a Safe Square.
- There are exactly 8 Safe Squares: the four starts plus four star safe squares.
- Implemented Safe Square indexes are `0, 8, 13, 21, 26, 34, 39, 47`.
- Each color has a private 5-square Home Path.
- Finished is separate from those five Home Path squares.
- A piece may enter its Home Path only after completing the full 52-position outer journey relative
  to its own Start.
- Being geometrically near the Home entrance is never enough.
- Screen coordinates and the 15x15 visual board do not define game state.

Conceptual route:

```text
Yard -> Outer Path -> Home Path -> Finished
```

## Piece States

Pieces use these authoritative states:

```text
IN_YARD
ON_OUTER_PATH
ON_HOME_PATH
FINISHED
```

Finished pieces can never move. Shields may exist only while a piece is on the Outer Path.

## Normal Die, Special Die, And Movement Choices

Each turn uses an explicit two-step dice flow:

1. The current player rolls the normal die.
2. If the normal roll is not cancelled by Triple Six, the player rolls the Special Die.
3. The game exposes legal actions for the available movement value or values.
4. The player explicitly chooses a legal piece or legal destination.

Normal die:

- Produces a base roll from 1 through 6.
- Base-six rules use this base roll, not a synthetic Special Die result.

Special Die:

- Has a 20% success probability.
- A success produces `+2`.
- A failure produces `0`.
- A successful `+2` can create a second movement value: `base roll + 2`.
- The Special Die does not create a second physical die or a separate piece move.

Movement choices:

- If only the base value has legal actions, only base actions are exposed.
- If only base `+ 2` has legal actions, only those actions are exposed.
- If both values have legal actions, both sets are exposed and the player chooses.
- If neither value has legal actions, the game enters the no-legal-move notice.
- The UI may show multiple legal destinations for one piece; each destination maps to an explicit
  action id.

## Yard Rules And Forced Yard Release

- A piece in Yard can leave only with an exact base roll of 6.
- A successful Special Die `+2` cannot turn a base 4 into a Yard-release 6.
- Leaving Yard places the piece on its owner's Start Square.
- Yard release clears any shield state.

Anti-stall rule:

- At the start of a turn, the engine records whether all of that player's pieces are in Yard.
- If that player starts the turn with all pieces in Yard and ends the turn with all pieces still in
  Yard, that player is marked for a forced base 6 on a later normal turn.
- The forced value is used as the next normal die result for that player.
- The marker is cleared when used, or when the player has any piece outside Yard.
- The forced 6 behaves like a real base 6 for Yard release, bonus-roll, and Triple Six purposes.
- Bonus-roll chains do not incorrectly create the stall marker after a successful Yard release.

## Movement And Exact Finish

- Outer Path movement advances by player-relative progress from the owner's Start.
- Crossing from Outer Path into Home Path is allowed only after the required full outer journey.
- Home Path movement advances through indexes 0 through 4.
- Finished requires an exact roll from Home Path or from the last valid journey progress.
- A move that would overshoot Finished is illegal.
- Legal-move calculation rejects invalid dice or movement values.

## Safe Squares, Start Squares, And Coexistence

The following are always aligned for every color:

```text
Yard release destination
= player Start Square
= Safe Square
= visual Start/Safe marker
```

Safe-square rules:

- No capture can occur on a Safe Square.
- Pieces from any active colors may coexist.
- Same-player pieces may coexist.
- There is no stacking limit beyond the total number of pieces in the match.

## Capture Rules

Capture applies only on ordinary, non-safe Outer Path squares.

If a moving piece lands on an ordinary square containing exactly one vulnerable opponent piece:

- that opponent is captured;
- the captured piece returns to Yard;
- its path progress is cleared;
- its shield, if any, is removed;
- the moving player receives one capture-based bonus roll.

If the destination is safe, or if the destination contains a protected block, no capture occurs.

## Dynamic Protection And Block Rules

This project intentionally uses a custom protection system.

Same-player block:

- Two or more pieces from one player on the same ordinary square are protected.
- Opponents may pass through the square.
- Opponents may land on an already protected square without capturing.

Mixed-player block:

- If an opponent legally joins an already protected ordinary square, the occupancy can become mixed.
- A legally evolved mixed occupancy of 2 or more pieces remains protected.
- Protection is lost when departures reduce the square to one piece.

Creation rule:

- Mixed-player coexistence cannot be created by declining a required capture.
- If Red is alone on an ordinary square and Blue lands there, Blue must capture Red unless Red has
  a Shield.

## Bonus Rolls

A player receives one bonus roll when a resolved move includes at least one of:

1. base roll is 6;
2. an opponent is captured;
3. a piece reaches Finished.

Bonus reasons do not stack for a single move. A move that both rolls 6 and captures still grants
only one bonus roll. A bonus roll can itself create another bonus. An unusable roll grants no bonus,
even if the base roll was 6.

## Triple Six

- Consecutive base rolls of 6 are tracked.
- For `6, 6, 6`, the first two rolls and moves remain valid.
- The third consecutive base 6 is cancelled.
- The cancelled roll does not move a piece, trigger capture, finish, board effects, or bonus.
- The turn ends immediately.
- A non-six resets the counter.

## No Legal Move And Timers

Roll and special-roll phases:

- The player has 10 seconds to act.
- If the timer expires before the required die click, the turn is forfeited.

Move phase:

- After legal actions are available, the timer resets to 10 seconds.
- If no legal action is selected before expiration, the move is forfeited.
- The game does not auto-select a piece.

No legal move:

- If there are zero legal actions after the Special Die step, the game shows a no-legal-move notice.
- The notice lasts 5 seconds.
- The turn then passes automatically.

## Hazard Squares

Hazards are match-fixed special squares on the Outer Path.

- Each match has 8 Hazard Squares.
- There are 2 Hazards in each 13-square sector.
- Hazards are randomly generated at match creation through injectable randomness.
- Hazards do not overlap Safe Squares, Start Squares, Boost Squares, or Shield Squares.
- The layout remains fixed for the whole match.
- Passing over a Hazard does nothing.
- Direct landing on a Hazard forces a 2-step backward displacement.
- If fewer than two backward steps are available before the piece's Start, the penalty clamps at
  Start.
- A Hazard never sends a piece to Yard.
- Collision is resolved after the final penalty destination is determined.
- If the clamped destination is a Start/Safe Square, normal Safe Square coexistence applies and no
  capture occurs.
- Hazard displacement does not trigger another Hazard, Boost, or Shield Square.
- Shield does not protect against Hazard displacement.

Critical invariant:

```text
Forced backward movement cannot move a piece before its own Start progress and cannot allow a
piece to bypass the required outer lap or enter Home early.
```

## Boost Squares

Boosts are match-fixed special squares on the Outer Path.

- Each match has 4 Boost Squares.
- There is 1 Boost in each 13-square sector.
- Boosts are randomly generated at match creation through injectable randomness.
- Boosts do not overlap Safe Squares, Start Squares, Hazards, or Shield Squares.
- Passing over a Boost does nothing.
- Direct landing on a Boost forces an automatic 2-step forward displacement.
- Collision is resolved after the forced destination.
- Boost displacement does not trigger another Hazard, Boost, or Shield Square.

Special Die `+2` and Boost `+2` are different:

- Special Die `+2` is part of movement-value selection before a piece moves.
- Boost `+2` is an automatic board effect after landing on a Boost Square.

## Shield Squares And Shield State

Shield Squares are match-fixed special squares on the Outer Path.

- Each match has 4 Shield Squares.
- There is 1 Shield Square in each 13-square sector.
- Shields do not overlap Safe Squares, Start Squares, Hazards, or Boosts.
- Passing over a Shield Square does nothing.
- Direct landing grants the moving piece one Shield.
- A piece can carry at most one Shield.
- Landing on a Shield Square while already shielded keeps the existing Shield and does not create a
  second Shield-acquired event.
- A piece can acquire another Shield later after the previous Shield is consumed.
- Shield state is visible on the piece.
- Shields are removed when entering Home Path and are not retained by Finished pieces.

Shield protection:

```text
normal opponent Capture against shield
-> Shield consumed
-> defender survives
-> attacker and defender coexist
-> no capture-based Bonus Roll
```

Shield protects against player capture only. It does not protect against Hazard displacement.

Backward Capture does not expose a legal action against a shielded target because no actual capture
would occur.

## Backward Capture

Backward Capture is a tactical capture-only rule.

- It is not general backward movement.
- It exists only when the current legal movement value can move a piece backward to an actual
  capturable opponent.
- It cannot move before the player's Start progress.
- It cannot target Safe Squares.
- It cannot target protected blocks.
- It cannot target shielded pieces.
- A successful Backward Capture returns the opponent to Yard and grants the normal capture bonus.
- If the same piece has multiple legal actions, the UI requires an explicit destination/action.

## Special Squares And Capture Order

For a normal forward move:

1. The selected movement value resolves the direct landing square.
2. If the direct landing square is a Hazard, Boost, or Shield Square, that direct-landing effect is
   applied.
3. Collision is resolved at the final authoritative destination.
4. Forced Hazard/Boost destinations do not chain into more special-square effects.

## Ranking And Match Completion

- A player completes when all 4 owned pieces are Finished.
- Completed players receive the next available rank.
- Ranked players are removed from future turn rotation.
- A player is never ranked twice.
- When only one unranked player remains, that player automatically receives the final rank and the
  match is complete.

Rank sets:

- 2 players: 1st, 2nd.
- 3 players: 1st, 2nd, 3rd.
- 4 players: 1st, 2nd, 3rd, 4th.

## Invariants

- Outer Path length is always 52.
- Each Home Path length is always 5.
- Finished is separate from Home Path squares.
- Safe-square count is always 8.
- Active players each have 4 pieces.
- Finished pieces never move.
- Inactive colors never participate in gameplay.
- Legal moves are calculated by the domain/application layer, not by Pygame.
- Screen coordinates never define game state.
- Backward forced movement cannot create negative or wrapped player-relative journey progress.

## Acceptance And Test Scenarios

The current suite covers:

- player-count validation and color assignment;
- Yard release with base 6 and rejection without 6;
- Special Die success/failure and optional base/base-plus-2 action choices;
- forced Yard-release anti-stall behavior;
- normal outer movement, Home Path entry, exact finish, and overshoot rejection;
- captures, safe-square non-capture, same-player blocks, evolved mixed blocks, and protection loss;
- shielded capture, shield reacquisition, and shield removal at Home/Finished;
- Hazard generation, direct landing, clamping at Start, collision after displacement, and no chains;
- Boost generation, direct landing, collision after displacement, and no chains;
- Backward Capture legality and shielding/safe/protected-block exclusions;
- bonus rolls, unusable rolls, Triple Six, timers, and no-legal notice;
- ranking, final rank assignment, and match completion;
- facade snapshots/events, route generation, UI render state, interaction, animation, and audio.
