from adafruit_servokit import ServoKit
import time
myKit = ServoKit(channels = 16)

myKit.servo[0].angle = 60

time.sleep(1)
myKit.servo[0].angle = 0

