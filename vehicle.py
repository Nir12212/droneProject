from machine import Pin, PWM, ADC
from time import sleep
import DCMOTOR

in1=Pin(18,Pin.OUT)
in2=Pin(19,Pin.OUT)
ena=PWM(Pin(5))
in3=Pin(32,Pin.OUT)
in4=Pin(33,Pin.OUT)
enb=PWM(Pin(25))
in5=Pin(23,Pin.OUT)
in6=Pin(22,Pin.OUT)
enc=PWM(Pin(21))
in7=Pin(4,Pin.OUT)
in8=Pin(2,Pin.OUT)
end=PWM(Pin(15))
ena.freq(1000)
enb.freq(1000)
enc.freq(1000)
end.freq(1000)

motor_f=DCMOTOR.motor(in1,in2,ena,in5,in6,enc)
motor_b=DCMOTOR.motor(in3,in4,enb,in7,in8,end)

while True:
#speed controll
    ch3=
    if ch3>4095:
        ch3=4095
    elif ch3<300:
        ch3=0
    velocity=int((ch3/4095)*100)
#backward/forward
    ch2=
    if ch2>1845:
        turn=0
    elif ch2<1835:
        turn=1
    else:
        turn=10
#left/right    
    ch1=
    if ch1>1820:
        dirction1=0
    elif ch1<1790:
        direction1=1
    else:
        if not(turn==10):
            direction1=0
        else:
            dirction=10
    
    motor_f.turn_to(turn,velocity)
    motor_b.direction(direction1)
    sleep(0.15)