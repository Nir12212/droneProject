from machine import Pin, I2C
import dht
from ustruct import unpack
import QMC5883L
class BMP280:
    def __init__(self, i2c, addr=0x76):
        self.i2c = i2c
        self.addr = addr

        # Read calibration data
        calib = i2c.readfrom_mem(addr, 0x88, 24)
        (self.dig_T1, self.dig_T2, self.dig_T3,
         self.dig_P1, self.dig_P2, self.dig_P3,
         self.dig_P4, self.dig_P5, self.dig_P6,
         self.dig_P7, self.dig_P8, self.dig_P9) = unpack("<HhhHhhhhhhhh", calib)

        # Sensor config
        i2c.writeto_mem(addr, 0xF4, b'\x27')
        i2c.writeto_mem(addr, 0xF5, b'\xA0')

    def read(self):
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)

        # Temperature calculations
        var1 = ((temp_raw / 16384.0) - (self.dig_T1 / 1024.0)) * self.dig_T2
        var2 = ((((temp_raw / 131072.0) - (self.dig_T1 / 8192.0)) ** 2) * self.dig_T3)
        t_fine = var1 + var2
        temp = t_fine / 5120.0

        # Pressure calculations
        var1 = (t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = (var2 / 4.0) + (self.dig_P4 * 65536.0)
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1

        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - pres_raw
            pressure = ((pressure - (var2 / 4096.0)) * 6250.0) / var1
            pressure = pressure + (self.dig_P7 +
                                   (self.dig_P8 * pressure / 32768.0) +
                                   (self.dig_P9 * pressure * pressure / 2147483648.0)) / 16.0

        return temp, pressure / 100


# ---- PUBLIC FUNCTION YOU WILL IMPORT ----
def read_all():
    i2c = I2C(0, sda=Pin(18), scl=Pin(21))
    bmp = BMP280(i2c, addr=0x76)
    dht_sensor = dht.DHT22(Pin(19))
    i2c1=I2C(0,scl=Pin(23),sda=Pin(22),freq=400000)
    sensor=hmc5883l.HMC5883L(i2c1,0x1E)
    
    bmp_temp, bmp_pres = bmp.read()
    x,y,z=sensor.read()
    heading=sensor.heading()


    try:
        dht_sensor.measure()
        dht_temp = dht_sensor.temperature()
        dht_hum = dht_sensor.humidity()
    except:
        dht_temp = None
        dht_hum = None
        
    # Average temperature
    if dht_temp is not None:
        avg = (bmp_temp + dht_temp) / 2
    else:
        avg = bmp_temp

    return [
        round(avg, 2),
        round(dht_hum, 2) if dht_hum is not None else None,
        round(bmp_pres, 2),
        round(x, 2),
        round(y, 2),
        round(z, 2)
    ]
