
"""
A simple echo client
"""

import socket

host = '127.0.0.1'
port = 9855
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
s.send('PING')
data = s.recv(size)
s.close()
print 'Received:', data
