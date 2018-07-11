"""
script for controlling the car based on signal received from '/dev/input/js0'
"""
from picar import front_wheels, back_wheels, camera
from picar.SunFounder_PCA9685 import Servo
import picar
import struct
from time import sleep

#Enables for wheels and camera
rear_wheels_enable  = True
front_wheels_enable = True
camera_enable     = True

# Filter setting, DONOT CHANGE
hmn = 12
hmx = 37
smn = 96
smx = 255
vmn = 186
vmx = 255

#Turning range for each servo
MIDDLE_TOLERANT = 5
PAN_ANGLE_MAX   = 150
PAN_ANGLE_MIN   = 30
TILT_ANGLE_MAX  = 110
TILT_ANGLE_MIN  = 70
FW_ANGLE_MAX    = 90+45
FW_ANGLE_MIN    = 90-45

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
    with open('/dev/input/js0', 'rb') as f:
        for line in follow(f):
            #Decode byte stream
            message = struct.unpack('<hbb',line[-4:])
            print(message)
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

def destroy():
    fw.turn_straight()
    bw.stop()
    cm.ready()
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()
        print('Keyboard Interruption')
