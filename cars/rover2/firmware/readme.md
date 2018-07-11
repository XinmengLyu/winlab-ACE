This is a firmware update for a PiCar. Camera.py will add a new camera class in the PiCar module. This camera class packed both pan and tilt servos and coordiants them through its methods. It also enables a easy to calibrate the servos by simply changing the offset value for both servos.


How to update:
1. Copy camera.py to directory /home/pi/SunFounder_PiCar/picar in the RaspberryPi. 
2. Open sheel and go to directory /home/pi/SunFounder_PiCar/. Then run -sudo python setup.py install.
3. When you wirte a python script for the car import the camera class by the line "from PiCar import camera"
