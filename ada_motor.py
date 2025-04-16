import time
from adafruit_platformdetect import Detector

detector= Detector()

print ("chip id: ", detector.chip.id)
print ("board id:", detector.board.id)

from adafruit_servokit import ServoKit


motor = ServoKit(channels = 16)

lm = motor.servo[0]
bm = motor.servo[4]
um = motor.servo[8]
rm = motor.servo[14]

def move_continous(servos,speed):
    for s,speed in zip(servos,speed):
        s.angle = speed
    time.sleep(0.1)

def move(m, angle):
    m.angle = angle

def base():
    move(rm,180) # decrease angle -> rotates up
    move(lm,120) # increase angle -> rotates up
    move(um,90) #decrease angle -> go left
    move(bm,90)

def action_1():
    base()
    time.sleep(0.1)
    move(rm,120)
    move(um,120)
    time.sleep(8)
    base()

def action_2():
    start_time = time.time()  # Get the start time
    duration = 10  

    base()
    while time.time() - start_time < duration:
        move(rm, 120)
        move(lm, 180)
        move(um, 180)
        move(um, 120)
        time.sleep(0.2)
        base()
        time.sleep(1)

    base()

def action_3():
    start_time = time.time()  # Get the start time
    duration = 12  # Run for exactly 12 seconds
    move(lm, 180)
    move(rm, 120)

    while time.time() - start_time < duration:
        time.sleep(0.3)
        move(bm, 180)
        time.sleep(0.3)
        move(bm, 120)

    time.sleep(0.3)
    base()
 
def action_4():
    start_time = time.time() 
    duration = 8  
    half_duration = duration / 2  # 4 seconds for each direction

    # Move head right for the first half
    while time.time() - start_time < half_duration:
        move(um, 180)  

    # Move head left for the second half
    while time.time() - start_time < duration:
        move(um, 120)  

    base()

def action_5(duration):
    base()
    time.sleep(0.1)
    move(rm,150)
    time.sleep(duration)
    base()

def action_6(duration):
    base()
    for i in range(4):
        move(rm,120)
        move(lm,180)
    
        time.sleep(0.3)   

        base()

        time.sleep(0.3) 


base()
move(um,45)
time.sleep(1)
move(um,135)
time.sleep(1)
move(um,45)
time.sleep(1)
move(um,135)
time.sleep(1)
move(um,45)
time.sleep(1)
move(um,135)
time.sleep(1)
move(um,45)
time.sleep(1)
move(um,135)
time.sleep(1)
move(um,45)
time.sleep(1)
move(um,135)
time.sleep(1)
base()
# base()
# time.sleep(1)
# action_6()
# time.sleep(1)

# def move(m, target_angle, speed):
#     current_angle = m.angle

#     step = 1 if target_angle > current_angle else -1
#     for angle in range(int(current_angle), int(target_angle),step):
#         m.angle = angle
#         time.sleep(1/speed)


# # action_1()
# # motor.continuous_servo[4].throttle = 0
# # time.sleep(2)
# # motor.continuous_servo[4].throttle = 1
# # time.sleep(2)
# # motor.continuous_servo[4].throttle = -1
# # time.sleep(2)
# # motor.continuous_servo[4].throttle = 0
# time.sleep(1)
# motor.servo[4].angle = 90
# time.sleep(1)
# motor.servo[4].angle = 180
# time.sleep(1)
# motor.servo[4].angle = 90
# myKit = ServoKit(channels = 16)
# myKit.servo[0].angle = 180
# time.sleep(1)
# myKit.servo[0].angle = 0
