import json
import sys
import struct
import socket
import io
import copy

RECEIVE_BUFFER = 4096

class MessageHandler:

    """
    This class is responsible for a single message exchange with a client. Send then receive."""

    def __init__(self, sock:socket.socket, request_content:str):
        self.sock = sock
        self.address = sock.getpeername()

        self._send_buffer = self._construct_message(request_content)
        self._recv_buffer = b""

        # Receive Flags
        self._content_header_length = None
        self._content_header = None
        self._content = None


    def read(self):
        self._read_socket_to_buffer()
        if not self._recv_buffer:
            # There is nothing to read
            return None
        if self._content_header_length is None:
            self._content_header_length = self._process_message_header()
        if self._content_header is None:
            self._content_header = self._process_content_header()
        if self._content is None:
            self._content = self._process_content()
        if self._content is not None:
            # print(f"Message content unpacked.")
            content = copy.deepcopy(self._content)
            self._reset_incoming()
            return content
        # TODO: Unregister socket once response recieved


    def write(self):
        n_bytes_sent = self.sock.send(self._send_buffer)
        self._send_buffer = self._send_buffer[n_bytes_sent:]
        if not self._send_buffer:
            return True
        else: 
            return False


    def _construct_message(self, message_content:str):
        CONTENT_ENCODING = 'utf-8'
        # print(f"Sending message to {self.address}")
        content_bytes = json.dumps(message_content, ensure_ascii=False).encode(CONTENT_ENCODING)
        # construct the message header
        content_header = {
            "byteorder": sys.byteorder,
            "content-length": len(content_bytes),
            "content-type": "text/json",
            "content-encoding": "utf-8",
        }
        content_header_bytes = json.dumps(content_header, ensure_ascii=False).encode('utf-8')
        message_header = struct.pack(">H", len(content_header_bytes))
        message = message_header + content_header_bytes + content_bytes

        return message

    def _read_socket_to_buffer(self):
        try:
            # Should be ready to read
            data = self.sock.recv(RECEIVE_BUFFER)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            self._recv_buffer += data
     


    def _reset_incoming(self):
        # print(f"Resetting MessageHandler incoming flags.")
        
        # Receive Flags
        self._content_header_length = None
        self._content_header = None
        self._content = None


    def _process_message_header(self):

        # the length of the fixed-length header,hdrlen is a 2-byte integer in
        # network, or big-endian, byte order.
        hdrlen = 2
        if len(self._recv_buffer) >= hdrlen:
            content_header_length = struct.unpack(
                # '>' - big-endian
                # 'H' - unsigned short (c), integer (Python)
                ">H", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]
            return content_header_length
        else:
            return None
        

    def _process_content_header(self):
        hdrlen = self._content_header_length
        if hdrlen is None:
            raise ValueError(f"hdrlen is None: {hdrlen=}")
        if len(self._recv_buffer) >= hdrlen:
            content_header = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in content_header:
                    raise ValueError(f"Missing required header '{reqhdr}'.")   
            return content_header
        else:
            return None

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj 

    def _process_content(self):
        if self._content_header is None:
            return None
        content_len = self._content_header["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self._content_header["content-type"] == "text/json":
            encoding = self._content_header["content-encoding"]
            return self._json_decode(data, encoding)
        else:
            print(f'No handling logic for content-type:{self._content_header["content-type"]}')
            return data
  