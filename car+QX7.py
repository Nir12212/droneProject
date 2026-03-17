from machine import Pin, PWM, ADC
from time import sleep, sleep_ms
import DCMOTOR
from SBUS import SBUSReceiver

def step_motor(steps,direction):
    seq_len=len(sequence)
    step_index=0
    for i in range(steps):
        for pin,value in zip(pins,sequence[step_index]):
            pin.value(value)
        sleep(delay)
        step_index=(step_index+direction)%seq_len
    for pin in pins:
        pin.value(0)
#--------FrSKY------------------
sbus = SBUSReceiver(uart_id=1, rx_pin=16)
def get_controls():
    ch1 = sbus.get_channel(1)
    ch2 = sbus.get_channel(2) 
    ch3 = sbus.get_channel(3)
    ch5 = sbus.get_channel(5)
    ch6 = sbus.get_channel(6)
    return ch1, ch2, ch3, ch5, ch6
#------------motor-----------------
in1=Pin(19,Pin.OUT)
in2=Pin(18,Pin.OUT)
ena=PWM(Pin(5))
in3=Pin(32,Pin.OUT)
in4=Pin(33,Pin.OUT)
enb=PWM(Pin(25))
in5=Pin(23,Pin.OUT)
in6=Pin(22,Pin.OUT)
enc=PWM(Pin(21))
in7=Pin(2,Pin.OUT)
in8=Pin(4,Pin.OUT)
end=PWM(Pin(15))
ena.freq(1000)
enb.freq(1000)
enc.freq(1000)
end.freq(1000)
motor_f=DCMOTOR.motor(in1,in2,ena,in5,in6,enc)
motor_b=DCMOTOR.motor(in3,in4,enb,in7,in8,end)
#--------------stepper------------------
in1s=Pin(12,Pin.OUT)
in2s=Pin(14,Pin.OUT)
in3s=Pin(26,Pin.OUT)
in4s=Pin(27,Pin.OUT)
pins=[in1s,in2s,in3s,in4s]
sequence=[
    [1,0,0,0],
    [1,1,0,0],
    [0,1,0,0],
    [0,1,1,0],
    [0,0,1,0],
    [0,0,1,1],
    [0,0,0,1],
    [1,0,0,1]
]
steps=4110
delay=0.001
step_dir=1
step_armed=True

while True:
#---get channels------------
    sbus.read()
    ch1, ch2, ch3, ch5, ch6 = get_controls()
#----------stepper--------------------
    if 1750 < ch6 and ch6 < 1830:
        if step_armed:
            step_motor(steps, step_dir)
            sleep(0.5)
            step_dir = -step_dir 
            step_armed = False
    else:
        step_armed = True
        
#------speed controll-----------
    ch3=ch3-172
    if ch3>1639:
        ch3=1639
        print(1)
    elif ch3<0:
        ch3=0
    velocity=int((ch3/1639)*100)
    
#-------left/right--------------
    if ch1>1020:
        turn=1
    elif ch1<965:
        turn=0
    else:
        turn=10
#------forward/backward------------
    if ch2>1020:
        direction1=0
    elif ch2<965:
        direction1=1
    else:
        direction1=10
        
    if ch5>1800 and ch5<1863:
        motor_f.turn_to(turn,velocity)
        motor_b.direction(direction1)
        motor_b.turn_to(turn,velocity)
        motor_f.direction(direction1)
        sleep_ms(20)
    else:
        motor_f.turn_to(10,0)
        motor_b.direction(10)
        motor_b.turn_to(10,0)
        motor_f.direction(10)
