import argparse
import socket
import sys
import threading
import json
import random


game_lock = threading.Lock()
board = ["-"] * 9
connected_clients = {}
current_turn = None
scores = {}
guessing_data = {}
target_number = 0

# makes sure the port a to-be-connected client enters is a valid one
def CheckPort(port_str):
    try:
        port = int(port_str)
    except ValueError:
        raise argparse.ArgumentTypeError("Port must be an integer.")
    if not (1024 <= port <= 65535):
        raise argparse.ArgumentTypeError(f"Port must be between 1024 and 65535. Got: {port}")
    return port

# sticks '\n' to messages to keep track of when one message ends and it sends it over the TCP stream
def send(sock, msg_dict):
    try:
        payload = json.dumps(msg_dict) + "\n"
        sock.sendall(payload.encode('utf-8'))
    except Exception as e:
        print(f"Error sending message: {e}")

# this sends a json message to all of the connected clients
def broadcast(msg_dict):
    for client_sock in list(connected_clients.keys()):
        send(client_sock, msg_dict)

def checkWinConditions():
    win_cond = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in win_cond:
        if board[a] != "-" and board[a] == board[b] == board[c]:
            return board[a]
    if "-" not in board:
        return 'Draw'
    return None

def gameReset():
    global board, current_turn, guessing_data
    board = ["-"] * 9
    current_turn = None
    guessing_data = {}

def clientHandler(client_sock, client_addr):
    global current_turn, target_number
    
    buffer = ""
    try:
        while True:
            # Read from socket until a newline is found
            while "\n" not in buffer:
                data = client_sock.recv(1024)
                if not data:
                    break
                buffer += data.decode('utf-8')
            
            if not buffer:
                break
                
            # Extract the first full JSON message up to the newline
            line, buffer = buffer.split("\n", 1)
            msg = json.loads(line)
            msg_type = msg.get("msg_type")
            
            # CRITICAL SECTION
            with game_lock:
                if msg_type == "CONNECT":
                    player_id = msg.get("player_id", "Unknown")
                    connected_clients[client_sock] = {"player_id": player_id, "role": None}
                    print(f"Player {player_id} connected from {client_addr}")
                    
                    if len(connected_clients) == 1:
                        send(client_sock, {"msg_type": "LOBBY_WAIT", "message": "Waiting for Player 2..."})
                    elif len(connected_clients) == 2:
                        # Start the guessing game to figure who goes first
                        target_number = random.randint(1, 10)
                        broadcast({"msg_type": "PROMPT_GUESS", "message": "Guess a number 1-10 to see who goes first!"})

                elif msg_type == "GUESS":
                    player_id = msg.get("player_id")
                    guess = int(msg.get("guess", 0))
                    guessing_data[client_sock] = guess
                    
                    if len(guessing_data) == 2:
                        clients = list(guessing_data.keys())
                        c1, c2 = clients[0], clients[1]
                        dist1 = abs(target_number - guessing_data[c1])
                        dist2 = abs(target_number - guessing_data[c2])
                        
                        if dist1 < dist2:
                            winner, loser = c1, c2
                        elif dist2 < dist1:
                            winner, loser = c2, c1
                        else:
                            # Tie
                            guessing_data.clear()
                            target_number = random.randint(1, 10)
                            broadcast({"msg_type": "ERROR", "error_code": "TIE", "message": f"Both guessed equally! Number was {target_number}. Re-rolling..."})
                            broadcast({"msg_type": "PROMPT_GUESS", "message": "Guess a new number 1-10!"})
                            continue
                        
                        # Assign roles
                        connected_clients[winner]["role"] = "X"
                        connected_clients[loser]["role"] = "O"
                        current_turn = connected_clients[winner]["player_id"]
                        
                        # Send GAME_START to both
                        send(winner, {"msg_type": "GAME_START", "assigned_role": "X", "opponent_id": connected_clients[loser]["player_id"]})
                        send(loser, {"msg_type": "GAME_START", "assigned_role": "O", "opponent_id": connected_clients[winner]["player_id"]})
                        
                        # Broadcast initial board state
                        broadcast({"msg_type": "STATE_UPDATE", "board": board, "active_turn": current_turn})

                elif msg_type == "MOVE":
                    player_id = msg.get("player_id")
                    if player_id != current_turn:
                        send(client_sock, {"msg_type": "ERROR", "error_code": "NOT_YOUR_TURN", "message": "Please wait for your turn."})
                        continue
                    
                    payload = msg.get("payload", {})
                    row = payload.get("row")
                    col = payload.get("col")
                    index = (row * 3) + col
                    
                    if 0 <= index <= 8 and board[index] == "-":
                        role = connected_clients[client_sock]["role"]
                        board[index] = role
                        
                        # Check win condition
                        outcome = checkWinConditions()
                        if outcome:
                            # Send final state before game over
                            broadcast({"msg_type": "STATE_UPDATE", "board": board, "active_turn": None})
                            winner_name = player_id if outcome != "Draw" else "Nobody"
                            broadcast({"msg_type": "GAME_OVER", "outcome": outcome, "winner": winner_name})
                            gameReset()
                        else:
                            # Swap turns
                            for sock, info in connected_clients.items():
                                if sock != client_sock:
                                    current_turn = info["player_id"]
                                    break
                            broadcast({"msg_type": "STATE_UPDATE", "board": board, "active_turn": current_turn})
                    else:
                        send(client_sock, {"msg_type": "ERROR", "error_code": "INVALID_MOVE", "message": "That cell is already occupied or out of bounds."})
                        send(client_sock, {"msg_type": "STATE_UPDATE", "board": board, "active_turn": current_turn})

                elif msg_type == "DISCONNECT":
                    break
            # CRITICAL SECTION ENDS

    except (ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        print(f"Error handling client: {e}")
    finally:
        # Client Connection Teardown
        with game_lock:
            if client_sock in connected_clients:
                player_id = connected_clients[client_sock]["player_id"]
                print(f"Player {player_id} disconnected.")
                del connected_clients[client_sock]
                # If someone drops mid-game, forfeit the match
                if current_turn is not None:
                    broadcast({"msg_type": "GAME_OVER", "outcome": "FORFEIT", "winner": "Remaining Player"})
                    gameReset()
        client_sock.close()

def main():
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe Game Server")
    parser.add_argument('-p', '--port', required=True, type=CheckPort, help='Listening port (1024-65535)')
    args = parser.parse_args()

    host = '0.0.0.0'
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server_socket.bind((host, args.port))
    server_socket.listen(5)
    
    print(f"Server initialized on {host}:{args.port}. Waiting for connections...")
    
    try:
        while True:
            client_conn, client_addr = server_socket.accept()
            client_thread = threading.Thread(target=clientHandler, args=(client_conn, client_addr))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()