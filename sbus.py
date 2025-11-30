from machine import UART, Pin
import time

class SBUSReceiver:
    def __init__(self, uart_id, rx_pin=16):
        # Initialize UART for ESP32
        # Baud: 100000, 8 bits, Even Parity (0), 2 Stop bits
        # RX Pin: 16 (Connect XM+ SBUS here)
        # invert=UART.INV_RX is REQUIRED for XM+ receiver to handle the inverted signal
        try:
            # Attempt to use hardware inversion (standard in newer MicroPython)
            self.sbus = UART(uart_id, baudrate=100000, bits=8, parity=0, stop=2, rx=Pin(rx_pin), invert=UART.INV_RX)
        except AttributeError:
            # Fallback if specific invert constant isn't found (rare)
            print("Warning: UART.INV_RX not found. Signal inversion might fail.")
            self.sbus = UART(uart_id, baudrate=100000, bits=8, parity=0, stop=2, rx=Pin(rx_pin))

        # Constants
        self.SBUS_FRAME_LEN = 25
        self.SBUS_NUM_CHANNELS = 18
        self.OUT_OF_SYNC_THD = 10
        self.SBUS_SIGNAL_OK = 0
        self.SBUS_SIGNAL_LOST = 1
        self.SBUS_SIGNAL_FAILSAFE = 2

        # State Variables
        self.sbusFrame = bytearray(25)
        self.sbusChannels = [0] * 18
        self.isSync = False
        self.validSbusFrame = 0
        self.lostSbusFrame = 0
        self.resyncEvent = 0
        self.outOfSyncCounter = 0
        
    def get_rx_channels(self):
        """Returns the list of channel values"""
        return self.sbusChannels

    def decode_frame(self):
        # Decode the 25-byte frame into 16 channels + 2 digital
        # Bytes 1-22 are the analog channels
        
        # Reset channels
        # Note: We construct the channels integer by shifting bits
        input_data = self.sbusFrame
        
        # SBUS channel data is packed. We must unpack 11 bits per channel.
        # This is a standard decoding routine.
        self.sbusChannels[0]  = ((input_data[1]    |input_data[2]<<8)                 & 0x07FF)
        self.sbusChannels[1]  = ((input_data[2]>>3 |input_data[3]<<5)                 & 0x07FF)
        self.sbusChannels[2]  = ((input_data[3]>>6 |input_data[4]<<2 |input_data[5]<<10)  & 0x07FF)
        self.sbusChannels[3]  = ((input_data[5]>>1 |input_data[6]<<7)                 & 0x07FF)
        self.sbusChannels[4]  = ((input_data[6]>>4 |input_data[7]<<4)                 & 0x07FF)
        self.sbusChannels[5]  = ((input_data[7]>>7 |input_data[8]<<1 |input_data[9]<<9)   & 0x07FF)
        self.sbusChannels[6]  = ((input_data[9]>>2 |input_data[10]<<6)                & 0x07FF)
        self.sbusChannels[7]  = ((input_data[10]>>5|input_data[11]<<3)                & 0x07FF)
        self.sbusChannels[8]  = ((input_data[12]   |input_data[13]<<8)                & 0x07FF)
        self.sbusChannels[9]  = ((input_data[13]>>3|input_data[14]<<5)                & 0x07FF)
        self.sbusChannels[10] = ((input_data[14]>>6|input_data[15]<<2|input_data[16]<<10) & 0x07FF)
        self.sbusChannels[11] = ((input_data[16]>>1|input_data[17]<<7)                & 0x07FF)
        self.sbusChannels[12] = ((input_data[17]>>4|input_data[18]<<4)                & 0x07FF)
        self.sbusChannels[13] = ((input_data[18]>>7|input_data[19]<<1|input_data[20]<<9)  & 0x07FF)
        self.sbusChannels[14] = ((input_data[20]>>2|input_data[21]<<6)                & 0x07FF)
        self.sbusChannels[15] = ((input_data[21]>>5|input_data[22]<<3)                & 0x07FF)

        # Digital Channel 17 & 18
        if (input_data[23] & 0x80): self.sbusChannels[16] = 2047
        else: self.sbusChannels[16] = 0
            
        if (input_data[23] & 0x40): self.sbusChannels[17] = 2047
        else: self.sbusChannels[17] = 0

        # Failsafe detection (Bit 3 of byte 23)
        if (input_data[23] & 0x08):
            self.failSafeStatus = self.SBUS_SIGNAL_FAILSAFE
        elif (input_data[23] & 0x04):
            self.failSafeStatus = self.SBUS_SIGNAL_LOST
        else:
            self.failSafeStatus = self.SBUS_SIGNAL_OK

    def get_new_data(self):
        """Read data from UART and check for sync"""
        # Read whatever is available
        if self.sbus.any():
            # If we are not synced, look for Start Byte (0x0F)
            if not self.isSync:
                data = self.sbus.read(1)
                if data and data[0] == 0x0F:
                    self.isSync = True
                    self.sbusFrame[0] = 0x0F # Store start byte
                    # Try to read the rest immediately if available
                    remaining = self.sbus.readinto(self.sbusFrame, 24) # Need to read into index 1? simpler to just wait next loop
                    # For simplicity in this loop, we just wait for sync.
            else:
                # We are synced, try to read the full frame
                # Note: This is a simplified approach. 
                # Ideally we read exactly 25 bytes starting with 0x0F
                if self.sbus.any() >= 25:
                    self.sbus.readinto(self.sbusFrame, 25)
                    
                    # Check Start Byte (0x0F) and End Byte (0x00)
                    if self.sbusFrame[0] == 0x0F and self.sbusFrame[24] == 0x00:
                        self.validSbusFrame += 1
                        self.decode_frame()
                        self.outOfSyncCounter = 0
                    else:
                        self.lostSbusFrame += 1
                        self.outOfSyncCounter += 1
                        if self.outOfSyncCounter > self.OUT_OF_SYNC_THD:
                            self.isSync = False