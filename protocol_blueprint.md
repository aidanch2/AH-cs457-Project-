# Application Protocol BluePrint

* Transport Protocol:
  - TCP
* Serialization Format:
  - JSON
* Framing Rule Chosen:
  - Option A: Newline-Delimited JSON (\n Framing)
  - the reciever will read bytes until it finds a '\n' which denotes that it is the end of the message.
  - Ex: {"msg_type":"CONNECT","player_id":"Alice"}\n{"msg_type":"MOVE","player_id":"Alice","payload":{"row":0,"col":2}}\n

# Application Message Types

* CONNECT
  - Client -> Server
  - This is a Client requesting to join the server with a chosen username
  - {
  "msg_type": "CONNECT",
  "player_id": "Alice"
    }
* GAME_START
  -
* MOVE
  -
* STATE_UPDATE
  -
* ERROR
  -
* DISCONNECT
  -
* GAME_OVER
