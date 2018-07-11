"""
A testing script for a PiCar
Hard code the instructions for front wheels, back wheels and camera servo into RaspberryPi
"""
from picar import front_wheels, back_wheels, camera
from picar.SunFounder_PCA9685 import Servo
import picar
from time import sleep

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

MIDDLE_TOLERANT = 5
PAN_ANGLE_MAX   = 170
PAN_ANGLE_MIN   = 10
TILT_ANGLE_MAX  = 150
TILT_ANGLE_MIN  = 70
FW_ANGLE_MAX    = 90+30
FW_ANGLE_MIN    = 90-30

bw = back_wheels.Back_Wheels(debug = True)
fw = front_wheels.Front_Wheels(debug = True)
cm = camera.Camera(debug = True)
picar.setup()

#fw.offset = 0
#pan_servo.offset = 10
#tilt_servo.offset = 0

bw.speed = 0
fw.turn(90)
cm.to_position(90,90)

motor_speed = 90

def main():
    pan_angle = 90              # initial angle for pan
    tilt_angle = 90             # initial angle for tilt
    fw_angle = 90

    print "Begin!"
    sleep(3)
    cm.to_position(60,90)
    cm.to_position(110,90)
    cm.to_position(90,90)
    sleep(1)
    cm.to_position(90,70)
    cm.to_position(90,110)
    cm.to_position(90,90)
    sleep(3)
    bw.speed = motor_speed
    bw.forward()
    print("going forward")
    sleep(3)
    bw.backward()
    print("going backward")
    sleep(3)

    bw.stop()
    sleep(3)
    
    bw.speed = motor_speed - 10
    fw.turn_left()
    print("turn left")
    bw.forward()
    print("going forward")
    sleep(3)
    bw.backward()
    print("going backward")
    sleep(3)

    fw.turn_right()
    print("turn right")
    bw.forward()
    print("going forward")
    sleep(3)
    bw.backward()
    print("going backward")
    sleep(3)

    bw.stop()
    fw.turn_straight()

def destroy():
    fw.turn_straight()
    bw.stop()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        destroy()
