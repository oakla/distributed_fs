# Distributed File System Explorer


## Usage

### Setup your Virtual Environment
On  linux, run
```bash
$ python3 -m venv .venv
```
to create a virtual environment named `.venv` in the current directory.

Then, activate the virtual environment by running
```bash
$ source .venv/bin/activate
```

### Configuration
A small number of server settings can be configured in src/config.py:
- `HOST` - the host address the server will bind to.
- `PORT` - the port the server will bind to.


### Demo
1. Launch the server by running `src/app_server.py` with Python 3.10
2. Launch demo clients by running the following files with Python:
    - `src/launch_test_client_1.py`
    - `src/launch_test_client_2.py`
    - `src/launch_test_client_3.py`

3. The server console with display instructions on how to query the connected clients.


### Normal usage
1. Launch the server by running `src/app_server.py` with Python
2. Launch the clients by running `python src/client_main.py <path_to_virtual_root>`

## Design
### The server:
- uses TCP/IP sockets to communicate with clients.
- The starts by creating a listening socket.
- The server handles multiple connections by using multiplexing with the `select` module.
- For each client connection, the server creates a MessageHandler object to:
    - read variable length messages.
    - control the registration of the associated socket with the server's selector.

It was thought to be beneficial to allow the user to continue to input commands while the server waits on the client. This was achieved by using a non-blocking call to `select.select()` with a timeout of 1 second. After events from the selector have been handled, or the timeout has elapsed, the flow of the server returns to the user input dialog.

In all tests, the clients responded very quickly, so it would have looked nicer if the input halted until the client responded. 

### Clients:
Clients provide information of the virtual root folder that they point to. This virtual root folder is path that is pass to the client script when it is launched.

After a client connects, the client 
1. creates a `MessageHandler` object which handles the reading of variable length messages. 
2. then waits for a request from the server using a blocking call to `.recv()`.
3. responds to the server by sending information on the contents of a folder.

The server host and port can be configured in the `src/config.py` file.


## Cavets

- The server has not been tested with more than 5 simultaneous clients.
- The client has not been designed to handle requests that match a file path. It handles directory paths only.


## Assumptions
each client only connects to one server at a time
