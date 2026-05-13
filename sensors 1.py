from machine import I2C, Pin
from math import sqrt
import dht
# from bmp280 import BMP280
from qmc5883l import QMC5883L

i2c1=I2C(0, scl=Pin(23), sda=Pin(22))
#i2c1=I2C(1, scl=Pin(18), sda=Pin(21))
mag= QMC5883L(i2c1)
#bmp=BM280(i2c2)
dht_sensor=dht.DHT22(Pin(19))

def read_all():
    dht_sensor.measure()
    dht_temp=dht_sensor.temperature()
    dht_hum=dht_sensor.humidity()
    x, y, z=mag.read_uT()
    vector=sqrt(x**2 + y**2 + z**2)
    #temp, press=bmp.values()
    #avg_temp=(temp+dht_temp)/2
    avg_temp=dht_temp
    return [
        round(avg_temp, 2),
        round(dht_hum, 2),
        "The sensor isn't working now, try again later",
        round(x, 2),
        round(y, 2),
        round(z, 2),
        round(vector, 2)
    ]

