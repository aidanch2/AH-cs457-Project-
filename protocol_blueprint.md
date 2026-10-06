# Application Protocol BluePrint

* Transport Protocol:
  - TCP
* Serialization Format:
  - JSON
* Framing Rule Chosen:
  - Option A: Newline-Delimited JSON (\n Framing)
  - the reciever will read bytes until it finds a '\n' which denotes that it is the end of the message.
  - Ex: {"msg_type":"CONNECT","player_id":"aidan"}\n{"msg_type":"MOVE","player_id":"aidan","payload":{"row":0,"col":2}}\n

# Application Message Types

* CONNECT
  - Client -> Server
  - This is a Client requesting to join the server with a chosen username
  - {"msg_type": "CONNECT", "player_id": "aidan"}
* GAME_START
  - Server -> Client
  - Telling the clients the game will start
  - {"msg_type": "GAME_START", "assigned_role": "X", "opponent_id": "Bob"}
* MOVE
  - Client -> Server
  - Telling the server a where they are placing their piece for their turn
  - {"msg_type": "MOVE", "player_id": "aidan", "payload": {"row": 0, "col": 2}}
* STATE_UPDATE
  - Server -> Client
  - server updates the board and sends it back to clients
  - {"msg_type": "STATE_UPDATE", "board": ["X", "-", "O", "-", "-", "-", "-", "-", "-"], "active_turn": "Bob"}
* ERROR
  - Server -> Client
  - Server tells client that somethings wrong or they cant do that move
  - {"msg_type": "ERROR", "error_code": "INVALID_MOVE", "message": "That cell is already occupied."}
* DISCONNECT
  - Client -> Server
  - client tells server its gonna disconnect
  - {"msg_type": "DISCONNECT", "player_id": "aidan"}
* GAME_OVER
  - Server -> Client
  - Server tells people who won / ends game
  - {"msg_type": "GAME_OVER", "outcome": "WIN", "winner": "aidan"}

# Connection Termination & Socket Lifecycle Management

## Application-Layer Disconnect (DISCONNECT Message)
* Application-Layer Disconnect (DISCONNECT Message)
  - in this circumstance the client will send a DISCONNECT message to the server
* Transport-Layer Teardown (TCP FIN / Clean Closure)
  - this will trigger the 0-byte EOF condition that my server will be looking for
* Abrupt Termination (TCP RST / Hard Drops)
  - ubn this situation the server will catch a ConnectionResetError so the lobby wont crash

## The TCP EOF (0-Byte) Rule in Socket Programming
* 
 
