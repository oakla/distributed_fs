import struct
import socket
import config
import sys
import json

import client_model
import client_message_handling


RECEIVE_BUFFER = 4096

class Client:

    def __init__(self, fs_root) -> None:
        self.fs_root = fs_root
        self.node_fs = client_model.NodeFS(fs_root)
        self.response_queued = False

        self.server_address = (config.SERVER_HOST, config.SERVER_PORT)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.connect_to_server()
        self._start_event_loop()


    def connect_to_server(self):
        print(f"Attempting to connect with server ({self.server_address})")
        try:
            self.sock.connect(self.server_address)
        except ConnectionRefusedError:
            print(f"Connection refused by server at {self.server_address}. Exiting.")
            exit()
        else:
            print(f"Connected to {self.server_address}")


    def _start_event_loop(self):
        message_handler = client_message_handling.MessageHandler(self.sock)
        try:
            while True:
                if not self.response_queued:
                    message_content = message_handler.read()
                if message_content is None:
                    continue
                if isinstance(message_content, str):
                    print(f"Received message: {message_content}")
                    self.sock.sendall(self.create_response_message(message_content))
                else:
                    print(
                        f"WARNING: No handling logice for message content type: {type(message_content)}"
                    )
        except KeyboardInterrupt:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()

    def create_response_message(self, path="/"):
        # TODO: This code should be shared with the server's construct message logic (DRY)
        CONTENT_ENCODING = "utf-8"

        directory_info = self.get_response_content(path=path)

        content_bytes = json.dumps(directory_info, ensure_ascii=False).encode(
            CONTENT_ENCODING
        )
        content_header = {
            "byteorder": sys.byteorder,
            "content-type": "text/json",
            "content-encoding": CONTENT_ENCODING,
            "content-length": len(content_bytes),
        }
        content_header_bytes = json.dumps(content_header, ensure_ascii=False).encode(
            "utf-8"
        )
        message_header = struct.pack(">H", len(content_header_bytes))
        message = message_header + content_header_bytes + content_bytes
        return message

    def get_response_content(self, path="/") -> dict[str, dict] | str:
        try:
            response_content = self.node_fs.get_directory_info(path)
        except ValueError as e:
            response_content = f"error: str(e)"
        finally:
            return response_content
