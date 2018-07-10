import sys
import io
import socket
import struct
import threading
import datetime
import time
import picamera
import numpy as np

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

global stop_event
global commands_out_thread
global client_socket_commands
global socket_lock

if len(sys.argv)!=2:
    print("must include ip address of car as command line argument")
    sys.exit(1)

car_ip=sys.argv[1]

time_format='%Y-%m-%d_%H-%M-%S'

button_names={ 0:'A',
        1:'B',
        2:'X',
        3:'Y',
        4:'LB',
        5:'RB',
        6:'screen',
        7:'menu',
        8:'xbox' }

analog_names={0:'js1-x',
        1:'js1-y',
        2:'LT',
        3:'js2-x',
        4:'js2-y',
        5:'RT',
        6:'DPad-x',
        7:'DPad-y'}

def read_stuff(sock, stufflen):
    chunks=io.BytesIO()
    bytes_recd=0
    while bytes_recd<stufflen:
        chunk=sock.recv(min(stufflen-bytes_recd, 8192))
        if chunk=='':
            return -1
        chunks.write(chunk)
        bytes_recd=bytes_recd+len(chunk)
    return chunks

def send_stuff(sock, stuff):
    stufflen=len(stuff)
    totalsent=0
    while totalsent<stufflen:
        sent=sock.send(stuff[totalsent:])
        if sent==0:
            return -1
        totalsent=totalsent+sent
    return totalsent

class ClientGUI(QMainWindow):

    def __init__(self, parent=None):
        super(ClientGUI, self).__init__(parent)

        start_button=QPushButton("start")
        stop_button=QPushButton("stop")
        calib_button=QPushButton("calibrate")
        dcoll_button=QPushButton("data collect")
        sdcoll_button=QPushButton("stop data collection")
        start_button.clicked.connect(self.start_act)
        stop_button.clicked.connect(self.stop_act)
        dcoll_button.clicked.connect(self.dcoll_act)
        sdcoll_button.clicked.connect(self.sdcoll_act)
        calib_button.clicket.connnect(self.calib_act)
        layout=QGridLayout()
        layout.addWidget(start_button, 0, 0)
        layout.addWidget(stop_button, 0, 1)
        layout.addWidget(dcoll_button, 0, 2)
        layout.addWidget(sdcoll_button, 0, 3)
        layout.addWidget(calib_button, 0, 4)
        centralwidget=QWidget()
        centralwidget.setLayout(layout)
        self.setCentralWidget(centralwidget)

        self.setWindowTitle("Image Player")
        self.show()


    def stop_act(self):
        global stop_event
        global commands_out_thread
        stop_event.set()
        commands_out_thread.join()
        

    def start_act(self):
        global client_socket_commands
        global commands_out_thread
        client_socket_commands.connect((car_ip, 8005))
        commands_out_thread.start()

    def dcoll_act(self):
        global socket_lock
        global client_socket_commands 
        message_buf=struct.pack("IhBB", 0, 0, 3, 6) #data collection start message
        socket_lock.acquire()
        send_stuff(commands_out_sock, message_buf) 
        socket_lock.release()

    def sdcoll_act(self):
        global socket_lock
        global client_socket_commands 
        message_buf=struct.pack("IhBB", 0, 0, 3, 7) #data collection start message
        socket_lock.acquire()
        send_stuff(commands_out_sock, message_buf) 
        socket_lock.release()

    def calib_act(self):
        global socket_lock
        global client_socket_commands 
        message_buf=struct.pack("IhBB", 0, 0, 3, 2) #data collection start message
        socket_lock.acquire()
        send_stuff(commands_out_sock, message_buf) 
        #Call calibration window here
        message_buf=struct.pack("IhBB", 0, 0, 3, 3) #data collection start message
        send_stuff(commands_out_sock, message_buf) 
        socket_lock.release()


socket_lock=threading.Lock()

joystick_file='/dev/input/js0'
js_out=open(joystick_file, 'rb')

def commands_out_process(stop_event, js_out, commands_out_sock):
    #thread for outputting commands
    global socket_lock
    try: 
        while not stop_event.isSet():
            evbuf=js_out.read(8)
            if evbuf and not calib_flag:
                time, value, in_type, in_id=struct.unpack('IhBB', evbuf)
                print(in_type, in_id) 
                socket_lock.acquire()
                send_stuff(commands_out_sock, evbuf) 
                socket_lock.release()
                if in_type==1 and button_names[in_id]=='xbox' and value==1:
                    stop_event.set()
    except BrokenPipeError:
        print("command connection broken, server no longer recieving")
        print(datetime.datetime.now().strftime(time_format))
        stop_event.set()


client_socket_commands=socket.socket() 
commands_out_thread=threading.Thread(target=commands_out_process, args=[stop_event, js_out, client_socket_commands])