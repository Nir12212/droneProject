from machine import Pin, PWM, ADC
from time import sleep
import DCMOTORS

in1=Pin(18,Pin.OUT)
in2=Pin(19,Pin.OUT)
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

motor_f=DCMOTORS.motor(in1,in2,ena,in5,in6,enc)
motor_b=DCMOTORS.motor(in3,in4,enb,in7,in8,end)

while True:
    motor_f.turn_to(100)
    motor_f.direction()
    motor_b.direction()
    motor_b.turn_to(100)
    sleep(0.15)