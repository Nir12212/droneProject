from ustruct import unpack

class BMP280:
    def __init__(self, i2c, addr=0x76):
        self.i2c, self.addr = i2c, addr
        c = i2c.readfrom_mem(addr, 0x88, 24)
        self.t1, self.t2, self.t3, self.p1, self.p2, self.p3, self.p4, self.p5,
self.p6, self.p7, self.p8, self.p9 = unpack("<HhhHhhhhhhhh", c)
        i2c.writeto_mem(addr, 0xF4, b'\x27')
        i2c.writeto_mem(addr, 0xF5, b'\xA0')

    def values(self):
        d = self.i2c.readfrom_mem(self.addr, 0xF7, 6)
        p = (d[0] << 12) | (d[1] << 4) | (d[2] >> 4)
        t = (d[3] << 12) | (d[4] << 4) | (d[5] >> 4)

        v1 = (((t >> 3) - (self.t1 << 1)) * self.t2) >> 11
        v2 = (((((t >> 4) - self.t1) * ((t >> 4) - self.t1)) >> 12) * self.t3) >> 14
        tf = v1 + v2
        temp = ((tf * 5 + 128) >> 8) / 100

        v1 = tf - 128000
        v2 = v1 * v1 * self.p6
        v2 += (v1 * self.p5) << 17
        v2 += self.p4 << 35
        v1 = ((v1 * v1 * self.p3) >> 8) + ((v1 * self.p2) << 12)
        v1 = (((1 << 47) + v1) * self.p1) >> 33
        if v1 == 0:
            return temp, 0

        p = 1048576 - p
        p = int((((p << 31) - v2) * 3125) / v1)
        v1 = (self.p9 * (p >> 13) * (p >> 13)) >> 25
        v2 = (self.p8 * p) >> 19
        pres = ((p + v1 + v2) >> 8) + (self.p7 << 4)

        return temp, pres