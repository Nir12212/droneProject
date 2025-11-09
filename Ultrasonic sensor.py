from machine import Pin, time_pulse_us
import time
trigger=Pin(12, Pin.OUT)
echo=Pin(14, Pin.IN)
def get_distance():
    trigger.value(0)
    time.sleep_us(2)
    trigger.value(1)
    time.sleep_us(10)
    trigger.value(0)
    duration=time_pulse_us(echo,1)
    distance=(duration/2)/29.1
while True:
    distance2=get_distance()
    print("Distance: {:.2f} cm".format(distance2))
    time.sleep(0.2)
