# AI Prompting & Constraint Strategy
* The prompts below are what i will use to make sure ai follows my schema

## Prompt 1: TCP Framing & Socket Lifecycle Loop
> "Write a Python TCP server receive loop for a Tic Tac Toe game. You MUST strictly adhere to the following constraints:
> 1. **Framing:** Use Newline-Delimited JSON (`\n`). Accumulate incoming bytes into a buffer and extract complete strings only when a `\n` is encountered.
> 2. **TCP EOF:** Explicitly check `if not data: break` to handle the 0-byte EOF condition for graceful disconnects.
> 3. **Socket Exceptions:** Wrap the `recv()` call in a `try/except` block that catches `ConnectionResetError` and `BrokenPipeError` to handle abrupt network drops without crashing the server."

## Prompt 2: Message Serialization & Schema Validation
> "Write a Python message parser function for the server. It must handle an incoming JSON string representing a player's move. 
> 
> The incoming message will strictly follow this schema:
> `{"msg_type": "MOVE", "player_id": "<alias>", "payload": {"row": <int>, "col": <int>}}`
>
> 1. Decode the JSON and validate the coordinates (must be 0-2).
> 2. If the move is out-of-turn or the cell is occupied, serialize and return this exact ERROR schema:
> `{"msg_type": "ERROR", "error_code": "INVALID_MOVE", "message": "<reason>"}`
> 3. Do not generate generic game logic; only write the parsing, validation, and JSON serialization functions."
