import math

class QMC5883L:
    def __init__(self, i2c, addr=0x0D):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x09, b'\x1d')
        self.i2c.writeto_mem(self.addr, 0x0b, b'\x01')

    def read(self):
        d = self.i2c.readfrom_mem(self.addr, 0x00, 6)
        x = int.from_bytes(d[0:2], 'little', True)
        y = int.from_bytes(d[2:4], 'little', True)
        z = int.from_bytes(d[4:6], 'little', True)
        return x, y, z

    def read_uT(self):
        x, y, z = self.read()
        return x * 100, y * 100, z * 100
