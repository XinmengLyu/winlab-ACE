"""
Client for video stream from PiCar.
Receive and decode video feed as binary string.
Receive corresponding controller signal as label for future data collection.
"""
import sys
import io
import socket
import struct
import threading
import datetime
import time
import numpy as np
import cv2 as cv

global image_frame
global lock
global client_socket_stream
global client_thread 
global stop_ev
global command

if len(sys.argv)!=3:
    print("must include ip address of car as command line argument + save image 1, do not save 0")
    sys.exit(1)

car_ip=sys.argv[1]
saveIma=sys.argv[2]


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

#processing input data
def client_process(stop_ev, sock):
    global lock
    global image_frame
    global command
    try:
        while not stop_ev.isSet(): 
            image_data=struct.unpack('<Lhbb', read_stuff(sock, struct.calcsize('<Lhbb')).getbuffer())
            #print commands
            print("command ：(%d, %d, %d) " %(image_data[1], image_data[2], image_data[3]))
            lock.acquire()
            
            command=list()
            
            command.append(image_data[1])           
            command.append(image_data[2])
            command.append(image_data[3])
            print("imagesize"+str(image_data[0]))
            image_frame=read_stuff(sock, image_data[0])
            image_frame.seek(0)
            lock.release()
        print("process shutting down now")
        sock.shutdown(socket.SHUT_RDWR)

    except BrokenPipeError:
        print("connection broken, server no longer sending")
        
        stop_ev.set()



def cleanup():
    print('Closing client streaming socket')
    global client_socket_stream
    client_socket_stream.close()

def main():
    global client_socket_stream
    global client_thread
    global commands_out_thread
    global lock
    global image_frame

    try:
        lock=threading.Lock() #lock for using image_frame buffer
        image_frame=io.BytesIO() #buffer for image data
        stop_ev=threading.Event()
        client_socket_stream=socket.socket()
        client_socket_stream.connect((car_ip, 8000))
        client_thread=threading.Thread(target=client_process, args=[stop_ev, client_socket_stream])
        client_thread.setDaemon(True)
        client_thread.start()
        c=1;
        while not stop_ev.isSet():
            lock.acquire()
            bytes = np.fromstring(image_frame.getvalue(), dtype = np.uint8)
            lock.release()
            if len(bytes) != 0:
                image = cv.imdecode(bytes, cv.IMREAD_UNCHANGED)
                flipped=cv.flip(image,-1)
                cv.imshow("img", flipped) #show image stream in a pop up window
                if int(saveIma)==1:
                    print(c)
                    ts=time.time()
                    ts=int(ts)
                    #cv.imwrite("/Users/rongfeng/Downloads/images/image"+str(c)+"_"+str(command[0])+"_"+str(command[1])+"_"+str(command[2])+".jpeg",flipped)
                    cv.imwrite("/Users/rongfeng/Downloads/images/"+str(ts)+"_"+str(command[0])+"_"+str(command[1])+"_"+str(command[2])+".jpeg",flipped)
                    c=c+1
                cv.waitKey(1)
    except KeyboardInterrupt:
        print('Terminating client thread')
        client_thread.join()
        cleanup()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        cleanup()
        print("KeyboardInterrupted!")
