#!/usr/bin/python           # This is client.py file

import socket               # Import socket module

myinput = raw_input()

s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 12346                # Reserve a port for your service.

s.connect((host, port))
s.send(myinput)
fromserver = s.recv(1024)
s.close()
print(fromserver)
fromserver = fromserver + "\n"
myfile = open("outputtest.txt", "a+")
myfile.write(fromserver)
myfile.close()



