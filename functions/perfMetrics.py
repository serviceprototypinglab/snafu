import psutil
import os
import sys
import socket

def waste_cpu():
    for x in range(0,999999):
        pass

def connect_tcp():
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5006
    BUFFER_SIZE = 1024
    MESSAGE = b'Hello, World!'
    #--
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))
    s.send(MESSAGE)
    data = s.recv(BUFFER_SIZE)
    s.close()
    #--

def open_file():
    code = open('localfib.py','r')
    content = code.read()
