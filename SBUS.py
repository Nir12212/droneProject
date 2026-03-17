from machine import UART, Pin
class SBUSReceiver:
    SBUS_FRAME_LEN = 25
    SBUS_BAUD = 100000
    def __init__(self, uart_id=1, rx_pin=16):
        self.uart = UART(
            uart_id,
            baudrate=self.SBUS_BAUD,
            bits=8,
            parity=0,
            stop=2,
            rx=Pin(rx_pin),
            invert=UART.INV_RX
        )
        self.buf = bytearray(self.SBUS_FRAME_LEN)
        self.channels = [0] * 16

    def _decode_frame(self, data):
        if data[0] != 0x0F:
            return False
        ch = [0] * 16
        ch[0]= ((data[1] | data[2] << 8) & 0x07FF)
        ch[1]= ((data[2] >> 3 | data[3] << 5) & 0x07FF)
        ch[2]= ((data[3] >> 6 | data[4] << 2 | data[5] << 10) & 0x07FF)
        ch[3]= ((data[5] >> 1 | data[6] << 7) & 0x07FF)
        ch[4]= ((data[6] >> 4 | data[7] << 4) & 0x07FF)
        ch[5]= ((data[7] >> 7 | data[8] << 1 | data[9] << 9) & 0x07FF)
        ch[6]= ((data[9] >> 2 | data[10] << 6) & 0x07FF)
        ch[7]= ((data[10] >> 5 | data[11] << 3) & 0x07FF)
        ch[8]= ((data[12] | data[13] << 8) & 0x07FF)
        ch[9]= ((data[13] >> 3 | data[14] << 5) & 0x07FF)
        ch[10]= ((data[14] >> 6 | data[15] << 2 | data[16] << 10) & 0x07FF)
        ch[11]= ((data[16] >> 1 | data[17] << 7) & 0x07FF)
        ch[12]= ((data[17] >> 4 | data[18] << 4) & 0x07FF)
        ch[13]= ((data[18] >> 7 | data[19] << 1 | data[20] << 9) & 0x07FF)
        ch[14]= ((data[20] >> 2 | data[21] << 6) & 0x07FF)
        ch[15]= ((data[21] >> 5 | data[22] << 3) & 0x07FF)
        self.channels = ch
        return True
    def read(self):
        while self.uart.any() >= self.SBUS_FRAME_LEN:
            self.uart.readinto(self.buf)
            if self.buf[0] == 0x0F and self.buf[24] == 0x00:
                if self._decode_frame(self.buf):
                    return True
            self.uart.read(1)

    def get_channel(self, ch_idx):
        if 1 <= ch_idx <= 16:
            return self.channels[ch_idx - 1]
