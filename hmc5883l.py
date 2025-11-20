import math
class HMC5883L:
    address=0x1E
    def __init__(self,i2c,address):
        self.i2c=i2c
        self.address=address
        self.i2c.writeto_mem(self.address,0x00,b'\x70')
        self.i2c.writeto_mem(self.address,0x01,b'\xA0')
        self.i2c.writeto_mem(self.address,0x02,b'\x00')
    def read(self):
        data = self.i2c.readfrom_mem(self.address, 0x03, 6)
        x = (data[0] << 8 | data[1])
        z = (data[2] << 8 | data[3])
        y = (data[4] << 8 | data[5])
        if x > 32767: x -= 65536
        if y > 32767: y -= 65536
        if z > 32767: z -= 65536
        return x, y, z
    def heading(self):
        x, y, _ = self.read()
        heading_rad = math.atan2(y, x)
        heading_deg = math.degrees(heading_rad)
        if heading_deg < 0:
            heading_deg += 360
        return heading_deg