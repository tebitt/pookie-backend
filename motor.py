from adafruit_servokit import ServoKit
import time
motor = ServoKit(channels = 16)

lm = motor.servo[0]
bm = motor.servo[4]
um = motor.servo[8]
rm = motor.servo[12]

# SLOW_SPEED = 100
# MODERATE_SPEED = 150
# FAST_SPEED = 200

# lm.set_pulse_width_range(500,2400)
# rm.set_pulse_width_range(500,2400)

def move(m, angle):
    m.angle = angle

def base():
    move(rm,180) # decrease angle -> rotates up
    move(lm,120) # increase angle -> rotates up
    move(um,180) #decrease angle -> go left
    move(bm,90)

def action_1():
    base()
    time.sleep(0.2)
    move(rm,120)
    move(um,120)
    time.sleep(3)
    base()

def action_2():
    base()
    for i in range(2):
        move(rm,120)
        move(lm,180)
        # move(um,180)
        # move(um,120)
        time.sleep(0.2)
        base()
        time.sleep(0.2)
    base()

def action_3():
    base()
    for i in range(2):
        move(bm,180)
        move(lm,180)
        move(rm,120)

        time.sleep(0.3)

        move(lm,120)
        move(rm,180)

        time.sleep(0.3)   

        move(bm,60)


        time.sleep(0.3) 

    base()

 

def action_6():
    base()
    for i in range(4):
        move(rm,120)
        move(lm,180)
    
        time.sleep(0.3)   

        base()

        time.sleep(0.3)   
    
def test():
    move(um,180)

action_1()
time.sleep(1)
action_2()
time.sleep(1)
action_3()
time.sleep(1)
action_6()
time.sleep(1)

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