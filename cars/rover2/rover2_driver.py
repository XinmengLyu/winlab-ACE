"""
Control the car by controller in the same way of rover2_controller.py.
Access video from PiCamera and send the image frame by frame in the form of binary string
"""
from picar import front_wheels, back_wheels, camera
from picar.SunFounder_PCA9685 import Servo
import picar
import struct
from time import sleep

import io
import socket 
import struct
import time
import datetime
import picamera
import threading

#Current angle and current speed
fw_current = 90
pan_current = 90
tilt_current = 90
motor_speed = 0

#Scaling factor for each controller command
FW_SCALE = 32767/45.0
BW_SCALE = 32767/100.0
PAN_SCALE = 32767/60.0
TILT_SCALE = 32767/20.0

#Initialize corresponding objects
bw = back_wheels.Back_Wheels()
fw = front_wheels.Front_Wheels()
cm = camera.Camera()
picar.setup()

#Ready position
bw.speed = motor_speed
fw.turn(fw_current)
cm.to_position(pan_current,tilt_current)

time_format='%Y-%m-%d_%H-%M-%S'

#Initialize a streaming socket
stream_server = socket.socket()
stream_server.bind(('',8000))
stream_server.listen(0)
(out_streamer, address) = stream_server.accept()

stream = io.BytesIO()

stop_event = threading.Event()
commands_lock = threading.Lock()

car_command = (0,0,0)

#wrapper for socket send and receive method
def send(sock, stuff):
    stufflen = len(stuff)
    totalsent = 0
    while totalsent < stufflen:
        sent = sock.send(stuff[totalsent:])
        if sent == 0:
            return -1
        totalsent = totalsent + sent
    return totalsent

def read(sock, stufflen):
    chunks = io.BytesIO()
    bytes_recd = 0
    while bytesrecd < stufflen:
        chunk = sock.recv(8)
        if chunck == '':
            return -1
        chunks.write(chunk)
        bytes_recd = bytes_recd + len(chunck)
    return chunck

#function for streaming thread
def server_process(stop_event, sock, stream):
    try:
        while not stop_event.isSet():
            if stream.tell() != 0:
                imsize = stream.tell()
                commands_lock.acquire()
                V, E, T = car_command
                commands_lock.release()
                send(sock, struct.pack('<Lhbb', imsize, V, E, T))
                stream.seek(0)
                nsent = send(sock, stream.read())
                if nsent == -1:
                    print("Client closed connection, stopping thread")
                    stop_event.set()
                stream.seek(0)
                stream.truncate()
            time.sleep(0.0001)
    except socket.error:
        print("Connection broken, client no longer recieving")
        print(datetime.datetime.now.strftime(time_format))
        stop_event.set()

#Generator for generating controller byte commands from the controller
def follow(file):
    while True:
        line = file.read(8)
        if not line:
            sleep(0.05)
            continue
        yield line

def main():
    #print('begin:')
    global fw_current
    global pan_current
    global tilt_current
    global motor_speed
    
    #start server thread
    server_thread=threading.Thread(target=server_process, args=[stop_event, out_streamer, stream])
    
    #Config the picamera and start streaming
    try:
        camera = picamera.PiCamera()
        camera.resolution = (128,96)
        camera.framerate = 20
        server_thread.setDaemon(True)
        server_thread.start()
        time.sleep(2)
        print('Starting camera...')
        camera.start_recording(stream, format='mjpeg')

        with open('/dev/input/js0', 'rb') as f:
            for line in follow(f):
                if stop_event.isSet():
                    print('Stop reading from controller')
                    break
                #Decode byte stream
                message = struct.unpack('<hbb',line[-4:])
                print(message)
                commands_lock.acquire()
                car_command = message
                commands_lock.release()
                #02 represent analog joystick
                if message[1] == 02:
                    if message[2] == 0:
                        #Turning front wheels
                        fw_current = round(message[0]/FW_SCALE + 90)
                        fw.turn(fw_current)
                    elif message[2] == 1:
                        #Activating back wheels
                        speed = round(message[0]/BW_SCALE)
                        if speed >= 0:
                            motor_speed = int(speed)
                            bw.backward()
                            bw.speed = motor_speed
                        else:
                            motor_speed = int(abs(speed))
                            bw.forward()
                            bw.speed = motor_speed
                    elif message[2] == 2:
                        #Turning pan servo
                        pan_current = round(-message[0]/PAN_SCALE + 90)
                        cm.to_position(pan_current, tilt_current)
                    elif message[2] == 3:
                        #Turning tilt servo
                        tilt_current = round(message[0]/TILT_SCALE + 90)
                        cm.to_position(pan_current, tilt_current)
                    elif message[2] == 4:
                        #Turning front wheels
                        fw_current = round(message[0]/FW_SCALE + 90)
                        fw.turn(fw_current)
    except KeyboardInterrupt:
        print('Stopping camera and terminating server thread')
        camera.stop_recording()
        server_thread.join()
        destroy()

def destroy():
    print('Terminating program')
    fw.turn_straight()
    bw.stop()
    cm.ready()
    stream_server.close()
    out_streamer.close()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()
        print('Keyboard Interruption')
