from machine import Pin, PWM
from time import sleep
servo=PWM(Pin(27))
servo.freq(50)
def set_angle(angle):
    if angle<0:
        angle=0
    elif angle>180:
        angle = 180
    min_duty=int((0.5/20)*1023)+1
    max_duty=int((2.5/20)*1023)-1 
    duty=int(min_duty+(angle/180)*(max_duty-min_duty))
    servo.duty(duty)
while True:

    for angle1 in range(0,181,20):
        set_angle(angle1)
        sleep(0.5)
    for angle2 in range(180,-1,-20):
        set_angle(angle2)
        sleep(0.5)
