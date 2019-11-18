# import libraries
import socket
import sys

import os,socket,threading,time
import traceback

# current working directory
currdir=os.path.abspath('.')

class FTPServerThread(threading.Thread):
    def __init__(self,conn,addr):
        self.conn=conn
        self.addr=addr
        self.basewd=currdir
        self.cwd=self.basewd
        threading.Thread.__init__(self)

    def run(self):
        self.conn.send('220 Welcome!\r\n')
        while True:
            cmd=self.conn.recv(256)
            if not cmd: break
            else:
                print 'Recieved:',cmd
                try:
                    func=getattr(self,cmd[:4].strip().upper())
                    func(cmd)
                except Exception,e:
                    print e
                    #traceback.print_exc()
                    self.conn.send('500 Sorry.\r\n')

    def LoadCwd(self):
        os.chdir(self.cwd)
    def SaveCwd(self):
        self.cwd=os.getcwd()
    def USER(self,cmd):
        self.conn.send('331 OK.\r\n')
    def PASS(self,cmd):
        self.conn.send('230 OK.\r\n')
    def QUIT(self,cmd):
        self.conn.send('221 Goodbye.\r\n')
    def NOOP(self,cmd):
        self.conn.send('200 OK.\r\n')
    def TYPE(self,cmd):
        self.mode=cmd[5]
        self.conn.send('200 Binary mode.\r\n')

    def CDUP(self,cmd):
        self.LoadCwd()
        os.chdir('..')
        self.SaveCwd()
        self.conn.send('200 OK.\r\n')
    def PWD(self,cmd):
        cwd=os.path.relpath(self.cwd,self.basewd)
        if cwd=='.':
            cwd='/'
        else:
            cwd='/'+cwd
        self.conn.send('257 \"%s\"\r\n' % cwd)
    def CWD(self,cmd):
        self.LoadCwd()
        print 'NOW:',os.getcwd()
        chwd=cmd[4:-2]
        if chwd=='/':
            chwd=self.basewd
        elif chwd[0]=='/':
            chwd=self.basewd+chwd
        os.chdir(chwd)
        print 'NOW:',os.getcwd()
        self.SaveCwd()
        self.conn.send('250 OK.\r\n')

    def PORT(self,cmd):
        l=cmd[5:].split(',')
        self.dataAddr='.'.join(l[:4])
        self.dataPort=(int(l[4])<<8)+int(l[5])
        print(self.dataPort)
        self.conn.send('200 I know.\r\n')

    def LIST(self,cmd):
        self.LoadCwd()
        self.conn.send('150 Here comes the directory listing.\r\n')
        self.datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasock.connect((self.dataAddr,self.dataPort))
        l=os.listdir('.')
        for t in l:
            k=self.toListItem(t)
            #print k,
            self.datasock.send(k)
        self.datasock.close()
        self.conn.send('226 Directory send OK.\r\n')

    def toListItem(self,fn):
        st=os.stat(fn)
        fullmode='rwxrwxrwx'
        mode=''
        for i in range(9):
            mode+=((st.st_mode>>(8-i))&1) and fullmode[i] or '-'
        d=(os.path.isdir(fn)) and 'd' or '-'
        ftime=time.strftime(' %b %d %H:%M ', time.gmtime(st.st_mtime))
        return d+mode+' 1 user group '+str(st.st_size)+ftime+os.path.basename(fn)+'\r\n'

    def RETR(self,cmd):
        self.LoadCwd()
        print 'NOW:',os.getcwd()
        fn=cmd[5:-2]
        #fn=self.cwd+'/'+fn
        print 'Down:',fn
        if self.mode=='I':
            fi=open(fn,'rb')
        else:
            fi=open(fn,'r')
        self.conn.send('150 Opening data connection.\r\n')
        self.datasock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.datasock.connect((self.dataAddr,self.dataPort))
        data= fi.read(1024)
        while data:
            self.datasock.send(data)
            data=fi.read(1024)
        self.datasock.close()
        self.conn.send('226 Transfer complete.\r\n')


# main FTP Server based on Threading
class FTPServer(threading.Thread):

    # constructor
    def __init__(self):
        # set socket to None
        self.socket = None
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
    raw_input("Press Enter to end...\n")
    # then stop
    ftp.stop()
