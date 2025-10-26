from machine import Pin, I2C
import time
import dht
from ustruct import unpack

# ===== BMP280 DRIVER =====
class BMP280:
    def __init__(self, i2c, addr=0x76):
        self.i2c = i2c
        self.addr = addr
        calib = self.i2c.readfrom_mem(addr, 0x88, 24)
        self.dig_T1, self.dig_T2, self.dig_T3, \
        self.dig_P1, self.dig_P2, self.dig_P3, self.dig_P4, \
        self.dig_P5, self.dig_P6, self.dig_P7, self.dig_P8, \
        self.dig_P9 = unpack("<HhhHhhhhhhhh", calib)

        # Initialize sensor (normal mode)
        self.i2c.writeto_mem(addr, 0xF4, b'\x27')
        self.i2c.writeto_mem(addr, 0xF5, b'\xA0')

    def read_raw_data(self):
        data = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
        pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
        return temp_raw, pres_raw

    def read_compensated_data(self):
        adc_T, adc_P = self.read_raw_data()

        var1 = (((adc_T / 16384.0) - (self.dig_T1 / 1024.0)) * self.dig_T2)
        var2 = ((((adc_T / 131072.0) - (self.dig_T1 / 8192.0)) ** 2) * self.dig_T3)
        t_fine = int(var1 + var2)
        temperature = (var1 + var2) / 5120.0

        var1 = (t_fine / 2.0) - 64000.0
        var2 = var1 * var1 * self.dig_P6 / 32768.0
        var2 = var2 + var1 * self.dig_P5 * 2.0
        var2 = (var2 / 4.0) + (self.dig_P4 * 65536.0)
        var1 = (self.dig_P3 * var1 * var1 / 524288.0 + self.dig_P2 * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * self.dig_P1
        if var1 == 0:
            pressure = 0
        else:
            pressure = 1048576.0 - adc_P
            pressure = ((pressure - (var2 / 4096.0)) * 6250.0) / var1
            var1 = self.dig_P9 * pressure * pressure / 2147483648.0
            var2 = pressure * self.dig_P8 / 32768.0
            pressure = pressure + (var1 + var2 + self.dig_P7) / 16.0

        return temperature, pressure / 100

    @property
    def values(self):
        t, p = self.read_compensated_data()
        return t, p  # return as float for averaging

# ===== SETUP =====
i2c = I2C(0, sda=Pin(18), scl=Pin(21))
bmp = BMP280(i2c=i2c, addr=0x76)

dht_pin = Pin(22)
dht_sensor = dht.DHT22(dht_pin)  # Use DHT11(dht_pin) if needed

# ===== LOOP =====
while True:
    # Read BMP280
    bmp_temp, bmp_pres = bmp.values

    # Read DHT
    try:
        dht_sensor.measure()
        dht_temp = dht_sensor.temperature()
        dht_hum = dht_sensor.humidity()
    except OSError as e:
        dht_temp = None
        dht_hum = None

    # Calculate average temperature if both readings are available
    if dht_temp is not None:
        avg_temp = (bmp_temp + dht_temp) / 2
    else:
        avg_temp = bmp_temp  # fallback if DHT fails

    # Print values
    print("----------------------------")
    print("BMP280 Temperature: %.2fC" % bmp_temp)
    print("BMP280 Pressure:    %.2fhPa" % bmp_pres)
    if dht_temp is not None:
        print("DHT Temperature:    %.2fC" % dht_temp)
        print("DHT Humidity:       %.2f%%" % dht_hum)
    else:
        print("DHT Read Failed")
    print("Average Temperature: %.2fC" % avg_temp)

    time.sleep(2)

