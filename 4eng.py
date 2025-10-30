from machine import Pin, PWM
from time import sleep
from machine import Pin, PWM
from time import sleep

# === MOTOR DRIVER 1 ===
# Motor 1
IN1 = Pin(12, Pin.OUT)
IN2 = Pin(13, Pin.OUT)
ENA = PWM(Pin(5), freq=300)

# Motor 2
IN3 = Pin(18, Pin.OUT)
IN4 = Pin(19, Pin.OUT)
ENB = PWM(Pin(22), freq=300)

# === MOTOR DRIVER 2 ===
# Motor 3
IN5 = Pin(25, Pin.OUT)
IN6 = Pin(26, Pin.OUT)
ENC = PWM(Pin(21), freq=300)

# Motor 4
IN7 = Pin(4, Pin.OUT)
IN8 = Pin(2, Pin.OUT)
END = PWM(Pin(23), freq=300)

def motor_forward(INA, INB, EN, speed=1023):
    EN.duty(speed)
    INA.value(1)
    INB.value(0)

def motor_backward(INA, INB, EN, speed=1023):
    EN.duty(speed)
    INA.value(0)
    INB.value(1)

def motor_stop(INA, INB, EN):
    EN.duty(0)
    INA.value(0)
    INB.value(0)

# Example usage:
while True:
    print("All motors forward")
    motor_forward(IN1, IN2, ENA)
    motor_forward(IN3, IN4, ENB)
    motor_forward(IN5, IN6, ENC)
    motor_forward(IN7, IN8, END)
    sleep(2)

    print("All stop")
    motor_stop(IN1, IN2, ENA)
    motor_stop(IN3, IN4, ENB)
    motor_stop(IN5, IN6, ENC)
    motor_stop(IN7, IN8, END)
    sleep(2)

