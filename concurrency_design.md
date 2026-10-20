# Chosen Architecture: Multi Threading

* I'd rather do multi threading because from what I've seen the code is easier to wright. When I was looking at the pros and cons of each choice it seems like the biggest cons is dealing with the critical section and that its not very scalable (the code is easy but the concept is a little harder). Whilst the cons for Non-blocking I/O is that its harder to code easy to understand. Id rather deal with a critical section because I learned all about it in cs370 and im hoping I havent forgot everything.

## How it works:

* The server will have one server thread two working threads constantly listening to player A's socket and player B's socket. both threads will have access to the same 3x3 board, and the turn variable in the servers memory.

# Thread Safety Strategy: One Global Lock

# Connection Lifecycle

## Listening Socket Accept

* the main server thread will create a TCP socket and bind it to a designated port. There will be a constantly running while loop that accepts incoming client connections
  
## Thread Spawning for Clients

* when a client connects, the accept() command on the server side returns a new client socket and the main server will take it and append it to a shared list of all connected clients. then it will create a new thread for that specific client, starts said thread. and goes back to listening for new connections.
  
## Game Loop
* in each client's thread there will be an infinite loop listening for incoming messages (like a MOVE command)... when a message is recieved the thread will try to aquire the global game lock... once it has aquired, the code will enter the critical section and validate the move (eg: the current_turn variable or the board variables)... if its a valid move it will broadcast STATE_UPDATE to all other sockets in the list of connected cleints... and then realease the lock so other clients can have it

## Client Connection Teardown
* if a client loses connection, quits, or the game ends. the recv() command will throw an. error or return an empty string... when that happens that thread will break out of the infinite loop... then it aquires the game lock... and removes itself from the connected clients list... then closes its socket and releases the lock
