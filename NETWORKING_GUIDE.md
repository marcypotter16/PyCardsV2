# Networking Guide for PyCardsV2

## Overview

Your GameState implementation is ready for client-server networking! Here's how to use it.

## Architecture

```
Server (Python)                     Client (Pygame)
├─ OmniGameState                   ├─ GameState
│  ├─ Full game state              │  ├─ Player's hand
│  ├─ Both players' hands          │  ├─ Visible board
│  └─ Both players' decks          │  └─ Public info only
```

## Usage Examples

### 1. Server Side - Export Full State

```python
# In your server code
game_manager = GameManager(game)

# Get complete game state (includes both players' hidden info)
omni_state = game_manager.get_omni_game_state()

# Send to server as JSON
json_data = omni_state.model_dump_json()
# or use: game_manager.export_state_json(omni=True)

# Send via websocket/HTTP
await websocket.send(json_data)
```

### 2. Server Side - Filter State for Players

```python
# Server filters state before sending to each player
omni_state = game_manager.get_omni_game_state()

# For Player 1 (ME)
player1_state = GameState(
    turn_count=omni_state.turn_count,
    cards_in_hand_me=omni_state.cards_in_hand_me,
    cards_in_board=omni_state.cards_in_board,
    cards_in_gy_me=omni_state.cards_in_gy_me,
    cards_in_gy_op=omni_state.cards_in_gy_op,
    cards_in_deck_me=omni_state.cards_in_deck_me,
)

# For Player 2 (OP) - swap perspective
player2_state = GameState(
    turn_count=omni_state.turn_count,
    cards_in_hand_me=omni_state.cards_in_hand_op,  # OP's hand becomes "my" hand
    cards_in_board=omni_state.cards_in_board,
    cards_in_gy_me=omni_state.cards_in_gy_op,
    cards_in_gy_op=omni_state.cards_in_gy_me,
    cards_in_deck_me=omni_state.cards_in_deck_op,
)

# Send filtered states
await player1_ws.send(player1_state.model_dump_json())
await player2_ws.send(player2_state.model_dump_json())
```

### 3. Client Side - Receive and Apply State

```python
# In your Pygame client
async def receive_state(websocket):
    json_data = await websocket.recv()

    # Parse JSON into GameState
    state = GameState.model_validate_json(json_data)

    # Apply to game
    game_manager.load_game_state(state)
```

### 4. Debugging - Print State

```python
# Print current state for debugging
state = game_manager.get_game_state()
print(state.model_dump_json(indent=2))

# Example output:
# {
#   "turn_count": 0,
#   "cards_in_hand_me": [
#     {
#       "uid": "a1b2c3d4-...",
#       "name": "goth_girl",
#       "base_power": 5,
#       "current_power": 5,
#       "owner": 0,
#       "dead": false,
#       "banished": false
#     }
#   ],
#   "cards_in_board": [
#     [
#       {
#         "uid": "e5f6g7h8-...",
#         "name": "goth_girl",
#         "base_power": 5,
#         "current_power": 7,
#         "owner": 0,
#         "dead": false,
#         "banished": false
#       },
#       [2, 5]
#     ]
#   ]
# }
```

## Network Protocol Recommendations

### WebSocket Messages

```python
# Client -> Server: Player action
{
    "type": "play_card",
    "card_uid": "a1b2c3d4-...",
    "position": [2, 5]
}

# Server -> Clients: State update
{
    "type": "state_update",
    "state": { ...GameState... }
}

# Server -> Clients: Single action (for animations)
{
    "type": "card_played",
    "card_uid": "a1b2c3d4-...",
    "from": "hand",
    "to": [2, 5],
    "player": 0
}
```

### Delta Updates (Optimization)

Instead of sending the full state every time, send deltas:

```python
{
    "type": "delta",
    "changes": {
        "card_played": {
            "uid": "a1b2c3d4-...",
            "from": "hand",
            "to": [2, 5]
        }
    }
}
```

## TODO

- [ ] Implement `load_game_state()` in GameManager
- [ ] Add graveyard controllers
- [ ] Add deck serialization
- [ ] Add turn counter
- [ ] Add card descriptions
- [ ] Test full state export/import cycle

## Integration with Your Server

In your separate server project:

1. Import the GameState models (copy or share the file)
2. Server maintains an `OmniGameState` for each game room
3. On player action:
   - Validate the action
   - Update the OmniGameState
   - Filter and send GameState to each client
4. Clients receive GameState and update their visuals

## Security Notes

⚠️ **Never send OmniGameState to clients!** It contains hidden information (opponent's hand/deck).
✅ Always filter through GameState before sending to players.
✅ Server is the source of truth - validate all client actions.
✅ Use UUIDs to prevent card spoofing.