# Chosen Architecture: Multi Threading
* I'd rather do multi threading because from what I've seen the code is easier to wright. When I was looking at the pros and cons of each choice it seems like the biggest cons is dealing with the critical section and that its not very scalable (the code is easy but the concept is a little harder). Whilst the cons for Non-blocking I/O is that its harder to code easy to understand. Id rather deal with a critical section because I learned all about it in cs370 and im hoping I havent forgot everything.
###How it works:
* The server will have one server thread two working threads constantly listening to player A's socket and player B's socket. both threads will have access to the same 3x3 board, and the turn variable in the servers memory.
# Thread Safety Strategy: One Global Lock
# Connection Lifecycle
* 
