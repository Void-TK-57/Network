# import libraries
import select
import socket
import sys

# main FTPServer class
class FTPServer:

    # constructor
    def __init__(self):
        # host
        self.host = '127.0.0.1'
        # ports
        self.data_port = 50001
        self.command_pot = 50002
        self.data_port = 50003
        self.size = 1024
        # socket for the comunication
        self.commad_socket = None
        self.data_port = None

    # function to open socket
    def open_socket(self, port):
        # try to open socket
        try:
            # create socket
            socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bind to host and port
            socket.bind((self.host,port))
            # listen to socket
            socket.listen(1)
        except Exception as error:
            # if socket is open, close
            if socket:
                socket.close()
            print("[Error] " + str(error))
            sys.exit(1)
        # then, return socket created
        return socket

    # run FTPServer
    def run(self):
        # open socket for command
        self.commad_socket = self.open_socket(self.command_pot)
        self.data_socket = self.open_socket(self.data_port)
        # enter loop to accept client
        while True:
            # accept connect
            connection, address = self.socket.accept()

            data = connection.recv(16)

            while data:
                print(data)
                data = connection.recv(16)

            connection.close()
            
if __name__ == "__main__":
    # create FTPServer
    ftp = FTPServer()
    # run FTPServer
    ftp.run()
