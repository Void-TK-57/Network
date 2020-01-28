# import libraries
import socket
import sys

import os,socket,threading,time
import traceback


# FTP Server class for a Thread
class FTPServerThread(threading.Thread):

    # constructor
    def __init__(self, connection, address):
        # set connection and address of the control port
        self.connection = connection
        self.address = address
        # data host and port and socket
        self.data_host = None
        self.data_port = None
        self.data_socket = None
        # mode (binary or ascii)
        self.mode = 'ascii'
        # set initial working directory
        self.base_cwd = os.path.abspath('.')
        # current directory
        self.cwd = self.base_cwd
        # call parent constructor
        threading.Thread.__init__(self)

    # run method
    def run(self):
        # send 220 to the control connection
        self.connection.send('220 Welcome.\r\n')
        while True:
            # receive command
            cmd = self.connection.recv(256)
            if not cmd:
                break
            else:
                # Log
                print("Received: " + str(cmd) + '\n')
                # get paramters
                parameter = cmd[:-2].split(' ')
                # check command
                if parameter[0] == "USER":
                    self.cmd_user(parameter)
                elif parameter[0] == "PASS":
                    self.cmd_pass(parameter)
                elif parameter[0] == "LIST":
                    self.cmd_list(parameter)
                elif parameter[0] == "PORT":
                    self.cmd_port(parameter)
                elif parameter[0] == "QUIT":
                    self.cmd_quit(parameter)
                elif parameter[0] == "CWD":
                    self.cmd_cwd(parameter)
                elif parameter[0] == "RETR":
                    self.cmd_retr(parameter)
                elif parameter[0] == "STOR":
                    self.cmd_stor(parameter)
                else:
                    self.not_implemented(cmd)

    # user command
    def cmd_user(self, arg):
        # send code back to connection
        self.connection.send('331 OK.\r\n')

    # pass command
    def cmd_pass(self, arg):
        self.connection.send('230 OK.\r\n')

    # quit command
    def cmd_quit(self, arg):
        self.connection.send('221 Goodbye.\r\n')

    # port command
    def cmd_port(self, arg):
        # get host and port
        parameters = arg[1].split(',')
        port = ( int(parameters[-2])<<8 ) + int(parameters[-1])
        host = '.'.join( parameters[:-2] )
        # set port and host
        self.data_host = host
        self.data_port = port
        # print port received
        print("[Data Port] " + str(self.data_port))
        # send back ok code
        self.connection.send('200 Port Received.\r\n')

    # list command
    def cmd_list(self, arg):
        # set current directory
        self.load_cwd()
        # send to client data port will be opened
        self.connection.send('150 Data Socket Opening.\r\n')
        # open socket
        success_status = self.open_socket(self.data_host, self.data_port)
        # if status is False, then data connection could not be opened, then notificates client
        if not success_status:
            self.connection.send('425 Could Not Open Data.\r\n')
        else:
            # get directory list
            l = os.listdir('.')
            # for each value
            for t in l:
                print('[LS] ' + str(t))
                self.data_socket.send(str(t)+'\r\n')
            # close socket
            self.close_socket()
            # notificate client
            self.connection.send('226 Directory Sent.\r\n')

    # stor command
    def cmd_stor(self, arg):
        # load cwd
        self.load_cwd()
        # file to create
        file = arg[1]
        try:
            # check mode
            try:
                file_desc = open(file, 'w')
            except:
                file_desc = open(file, 'x')
            print("Creating file: " + file)
        except:
            self.connection.send('450 Cant open new file.\r\n')
            return
         # send to client data port will be opened
        self.connection.send('150 Data Socket Opening.\r\n')
        # open socket
        success_status = self.open_socket(self.data_host, self.data_port)
        # if status is False, then data connection could not be opened, then notificates client
        if not success_status:
            self.connection.send('425 Could Not Open Data.\r\n')
        else:
            # read data
            data = self.data_socket.recv(256)
            # while there is still data
            while data:
                # write data to file
                file_desc.write(data)
                # read again
                data = self.data_socket.recv(256)

            # close data socket
            self.close_socket()
            # notificate client
            self.connection.send('226 Transfer Complete.\r\n')
    
    # retr command
    def cmd_retr(self, arg):
        # load current working directory
        self.load_cwd()
        # get file
        file = arg[1]
        # try to open it
        try:
            # check mode
            if self.mode == 'ascii':
                file_desc = open(file, 'r')
            else:
                file_desc = open(file, 'rb')
        except:
            self.connection.send('550 File not Found.\r\n')
            return
         # send to client data port will be opened
        self.connection.send('150 Data Socket Opening.\r\n')
        # open socket
        success_status = self.open_socket(self.data_host, self.data_port)
        # if status is False, then data connection could not be opened, then notificates client
        if not success_status:
            self.connection.send('425 Could Not Open Data.\r\n')
        else:
            # read data
            data = file_desc.read(1024)
            # while there is still data
            while data:
                # send data to socket
                self.data_socket.send(data)
                # read again
                data = file_desc.read(1024)
            # close data socket
            self.close_socket()
            # notificate client
            self.connection.send('226 Transfer Complete.\r\n')

    # cwd command
    def cmd_cwd(self,arg):
        # load curret working directory
        self.load_cwd()
        # get directory argument passed
        chwd=arg[1]
        # if starts with /
        if chwd=='/':
            # change to base working directory
            chwd=self.basewd
        elif chwd[0]=='/':
            # if only starts with /, then add it base working directory
            chwd=self.basewd+chwd
        # change working directory
        try:
            os.chdir(chwd)
            # save working directory
            self.save_cwd()
            # send it was ok
            self.connection.send('250 OK.\r\n')
        except:
            self.connection.send('550 Folder not Found.\r\n')

    
    # method to show other commands not implemented
    def not_implemented(self, arg):
        self.connection.send('500 Not Implemented.\r\n')

    # method to open socket
    def open_socket(self, host, port):
        # if either host or port is None then return false
        if (host is None or port is None):
            return False

        # try to open socket
        try:
            # create socket
            self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bind to localhost at port 21
            self.data_socket.connect( (host,port) )
            # return True
            return True
        except Exception as error:
            # close socket
            self.close_socket()
            # print error
            print("[Error] " + str(error))
            # then return False
            return False

    # method to close socket
    def close_socket(self):
        # if socket is opened
        if self.data_socket:
            # close
            self.data_socket.close()
        # set socket, port and host to None
        self.data_socket = self.data_port = self.data_host = None

    # method to change current working directory to current directory saved
    def load_cwd(self):
        # change directory to current directory saved
        os.chdir(self.cwd)

    # method to save current working directory
    def save_cwd(self):
        # set cwd
        self.cwd = os.getcwd()



# main FTP Server based on Threading
class FTPServer(threading.Thread):

    # constructor
    def __init__(self):
        # set socket to None
        self.socket = self.open_socket('127.0.0.1')
        # call parents constructor
        threading.Thread.__init__(self)

    # run FTP Server
    def run(self):
        # if socket is None, open socket
        if self.socket is None:
            self.open_socket('127.0.0.1')
        # listen to at most 5
        self.socket.listen(5)
        while True:
            # accept conncetion
            connection, address = self.socket.accept()
            # create a Server Thread Objcet
            thread_server = FTPServerThread(connection, address)
            # set daemon to True
            thread_server.daemon = True
            # start server thread
            thread_server.start()

        
    # method to open socket
    def open_socket(self, host, port = 21):
        # try to open socket
        try:
            # create socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # bind to localhost at port 21
            self.socket.bind( (host,port) )
        except Exception as error:
            # close socket
            self.close_socket()
            # print error
            print("[Error] " + str(error))

    # method to close socket
    def close_socket(self):
        # check if socket was opened
        if self.socket:
            # then closed
            self.socket.close()
        # set socket to None
        self.socket = None

    # method to stop the server
    def stop(self):
        # close socket
        self.close_socket()


        
            
if __name__ == "__main__":
    # create FTPServer
    ftp = FTPServer()
    # set daemon to True
    ftp.daemon = True
    # run FTPServer
    ftp.start()
    # enter blocking state
    raw_input("Press Enter to end...\n\n")
    # then stop
    ftp.stop()
