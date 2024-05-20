from datetime import datetime
import socket
import selectors
import server_message_handling
import config

client_id = 0
def create_new_client_id():
    global client_id
    client_id += 1
    return client_id


class ConnectedClient:
    """
    Holds
    - the queue of outgoing messages
    - the queue of incoming messages to be displayed to user
    - the client's socket

    Jobs:
    When a outgoing message is queued:
       - register socket with selector for WRITE events
       - pass message to message_handler for sending
    """

    def __init__(self, sock:socket.socket, selector:selectors.DefaultSelector) -> None:
        
        self.sock = sock
        print(f"New client connected: {self.sock.getpeername()}")


        self.selector = selector

        # A new message_handler is created for each new request
        self.message_handler = None

        self.out_message_content = [] 
        self.in_message_content = []
        self.client_id = create_new_client_id()

        self.waiting_for_response = False


    def is_connected(self):
        try:
            # this will try to read bytes without blocking and also without removing them from buffer (peek only)
            data = self.sock.recv(16, socket.MSG_DONTWAIT | socket.MSG_PEEK)
            if len(data) == 0:
                return False
        except BlockingIOError:
            return True  # socket is open and reading from it would block
        except ConnectionResetError:
            return False  # socket was closed for some other reason
        except Exception as e:
            print("unexpected exception when checking if a socket is closed")
            return True
        return True
    

    def close_connection(self):
        print(f"Closing connection with {self.client_id} - {self.sock.getpeername()}")
        try:
            self.selector.unregister(self.sock)
        except KeyError:
            pass
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


    def queue_outgoing_message(self, message_content:str):
        if self.waiting_for_response:
            print(f"Message cannot be sent to {self.client_id}. Already waiting for a response from {self.client_id}.")
            return None
        self.out_message_content = message_content
 
        self.message_handler = server_message_handling.MessageHandler(self.sock, message_content)
        self.selector.register(self.sock, selectors.EVENT_WRITE, data=self)
        self.waiting_for_response = True


    def _save_received_message(self, message_content):
        self.in_message_content.append(message_content)
        self.waiting_for_response = False


    def read(self):
        if self.message_handler is None:
            print(f"Client {self.client_id} - {self.sock.getpeername()} has no message handler")
            return None
        message_content = self.message_handler.read()
        if not message_content:
            return None

        print(f"Client {self.client_id} returned message of type: {type(message_content)}")
        self._save_received_message(message_content)

        self.selector.unregister(self.sock)

    
    def write(self):
        assert self.message_handler is not None, "Outgoing message was not queued before attempting to write."
        full_message_sent = self.message_handler.write()
        if full_message_sent:
            self.selector.modify(self.sock, selectors.EVENT_READ, self)


    def print_responses(self):
        while self.in_message_content:
            message = self.in_message_content.pop(0)
            print(self._dir_info_to_string(message))
            input("Press Enter to continue...")


    def _dir_info_to_string(self, dir_info:dict) -> str:
        try:
            s=f"Path: {dir_info['path']}\nContents:\n\n"
            for item in dir_info["contents"]:
                s+=self._get_fileobject_info_as_string(item) + '\n'
            return s 
        except:
            return str(dir_info)           


    def _get_fileobject_info_as_string(self, info_dict, truncated=False):
        s=f'{info_dict["name"]}\n'
        s+=f'- mtime: {timestampe_to_readable(info_dict["mtime"])}\n'
        
        if info_dict['type'] == "directory":
            s+=f"- Number of Items: {info_dict['n_items']}\n"
        elif info_dict['type'] == "file":
            sha256_hash=f"- sha256 hash: {info_dict['sha256_hash']}\n"
            if truncated:
                sha256_hash = sha256_hash[:config.MAX_DISPLAY_WIDTH]
            s+=sha256_hash
        else:
            print(f"ERROR: a FS object of unexpected type was found: {info_dict['type']}")
        return s
    

class DistributedFS:

    def __init__(self, connected_clients:dict[socket.socket, ConnectedClient]) -> None:
        self.connected_clients = connected_clients


    def get_client_with_id(self, client_id:int):
        for client in self.connected_clients.values():
            if client.client_id == client_id:
                return client
        return None


    def print_conntected_clients(self, ):
        # TODO: Check if they are still connected
        print("________________________")
        print(f"Connected Clients:")
        column_width = 5
        n_columns = int((config.MAX_DISPLAY_WIDTH+1) / column_width)

        clients = [f" {client.client_id:>{column_width-2}}" for  client in self.connected_clients.values()]
        if not clients:
            print("There are no connection clients.")

        while clients:
            print(*clients[:n_columns], sep=',')
            clients = clients[n_columns:]
        print("________________________")

    
def timestampe_to_readable(timestamp):
    return datetime.fromtimestamp(timestamp)
