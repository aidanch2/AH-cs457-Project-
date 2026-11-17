import argparse
import socket
import sys
import json

def checkPort(port_str):
    try:
        port = int(port_str)
    except ValueError:
        raise argparse.ArgumentTypeError("Port must be an integer.")
    if not (1024 <= port <= 65535):
        raise argparse.ArgumentTypeError(f"Port must be between 1024 and 65535. Got: {port}")
    return port

def send(sock, msg_dict):
    payload = json.dumps(msg_dict) + "\n"
    sock.sendall(payload.encode('utf-8'))

def printBoard(board_array):
    print(f"\n {board_array[0]} | {board_array[1]} | {board_array[2]} ")
    print("---+---+---")
    print(f" {board_array[3]} | {board_array[4]} | {board_array[5]} ")
    print("---+---+---")
    print(f" {board_array[6]} | {board_array[7]} | {board_array[8]} \n")

def main():
    parser = argparse.ArgumentParser(description="Tic-Tac-Toe Game Client")
    parser.add_argument('-i', '--hostname', required=True, help='Server DNS hostname')
    parser.add_argument('-p', '--port', required=True, type=checkPort, help='Server port (1024-65535)')
    args = parser.parse_args()
    
    # Step 2: DNS Resolution Requirement
    try:
        server_ip = socket.gethostbyname(args.hostname)
    except socket.gaierror:
        print(f"[ERROR] Unable to resolve DNS hostname '{args.hostname}'.")
        print("Please check your Cisco router DNS configuration ('ip dns server' / 'ip host') or verify domain spelling.")
        sys.exit(1)
        
    # Ask for username
    player_id = input("Enter your Player Name: ").strip()
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, args.port))
        print("Connected to server successfully!\n")
        
        # Send initial CONNECT JSON payload
        send(client_socket, {"msg_type": "CONNECT", "player_id": player_id})
        
        buffer = ""
        while True:
            # Read network stream until newline
            while "\n" not in buffer:
                data = client_socket.recv(1024)
                if not data:
                    print("Server closed connection.")
                    sys.exit(0)
                buffer += data.decode('utf-8')
            
            line, buffer = buffer.split("\n", 1)
            msg = json.loads(line)
            msg_type = msg.get("msg_type")
            
            if msg_type == "LOBBY_WAIT":
                print(msg.get("message"))
                
            elif msg_type == "PROMPT_GUESS":
                print(f"\n[SERVER]: {msg.get('message')}")
                while True:
                    guess = input("Your guess (1-10): ")
                    if guess.isdigit() and 1 <= int(guess) <= 10:
                        send(client_socket, {"msg_type": "GUESS", "player_id": player_id, "guess": guess})
                        print("Waiting for opponent...")
                        break
                    print("Invalid input. Try again.")
                    
            elif msg_type == "GAME_START":
                role = msg.get("assigned_role")
                opp = msg.get("opponent_id")
                print(f"\nGame Starting! You are {role}. Your opponent is {opp}.")
                
            elif msg_type == "STATE_UPDATE":
                printBoard(msg.get("board"))
                active_turn = msg.get("active_turn")
                
                if active_turn == player_id:
                    print("It is YOUR turn!")
                    while True:
                        move = input("Enter cell number (1-9) or 'q' to quit: ")
                        if move.lower() == 'q':
                            send(client_socket, {"msg_type": "DISCONNECT", "player_id": player_id})
                            sys.exit(0)
                        if move.isdigit() and 1 <= int(move) <= 9:
                            idx = int(move) - 1
                            row, col = divmod(idx, 3)
                            send(client_socket, {"msg_type": "MOVE", "player_id": player_id, "payload": {"row": row, "col": col}})
                            break
                        print("Invalid input.")
                elif active_turn is not None:
                    print(f"Waiting for {active_turn} to make a move...")
                    
            elif msg_type == "ERROR":
                print(f"\n[!] ERROR: {msg.get('message')}")
                
            elif msg_type == "GAME_OVER":
                print(f"\n*** GAME OVER! Outcome: {msg.get('outcome')} | Winner: {msg.get('winner')} ***\n")
                # Game is over, client exit time
                break

    except ConnectionRefusedError:
        print(f"[ERROR] Connection refused. Is the server running on {server_ip}:{args.port}?")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDisconnecting...")
        send(client_socket, {"msg_type": "DISCONNECT", "player_id": player_id})
    finally:
        client_socket.close()

if __name__ == "__main__":
    main()