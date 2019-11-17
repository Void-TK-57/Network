# import libraries
import select
import socket
import sys
"""
host = '127.0.0.1'
port = 9855
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
s.send('PING')
data = s.recv(size)
s.close()
print 'Received:', data
"""

# main client class
class Client:

    # constructor
    def __init__(self, host = "127.0.0.1", port = 50000):
        # host
        self.host = host
        # port
        self.port = port
        self.size = 1024
        # socket for the comunication
        self.socket = None

    # function to open socket
    def open_socket(self):
        # try to open socket
        try:
            # create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # connect
            self.socket.connect((self.host,self.port))
        except Exception as error:
            # if socket is open, close
            if self.socket:
                self.socket.close()
                self.socket = None
            print("[Error] " + str(error))
            sys.exit(1)

    # function to send data
    def send(self, message):
        # check if socket is None
        if self.socket is None:
            self.open_socket()
        self.socket.sendall(message.encode())
        
            
if __name__ == "__main__":
    # create server
    client = Client(port=50001)
    # run server
    client.send("Hello")