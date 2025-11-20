from machine import Pin,I2C
from time import sleep
import hmc5883l
i2c=I2C(0,scl=Pin(23),sda=Pin(22),freq=400000)
print("I2C devices found:",i2c.scan())
sensor=hmc5883l.HMC5883L(i2c,0x1E)
while True:
    x,y,z=sensor.read()
    heading=sensor.heading()
    print("Magnetic field:")
    print("Axis X:",x)
    print("Axis Y:",y)
    print("Axis Z:",z)
    print("Heading:",heading)
    sleep(0.1)