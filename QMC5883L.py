from machine import I2C, Pin
import time
import math

# ================= SETTINGS =================
QMC_ADDR = 0x0D               # I2C address of the QMC5883L magnetometer
LSB_TO_TESLA = 1e-4 / 12000   # Conversion from raw LSB to Tesla (1 LSB ≈ 8.333e-9 T)
HEADING_OFFSET = 0             # Manual heading offset (degrees) to correct compass alignment
SMOOTHING = 5                  # Number of readings to average for smoothing (reduces jitter)

# ================= HELPERS =================
def to_signed(val):
    """
    Converts 16-bit unsigned value from sensor to signed integer.
    QMC5883L outputs 16-bit values; if > 32767, it is negative.
    """
    return val - 65536 if val > 32767 else val

# ================= QMC5883L CLASS =================
class QMC5883L:
    def __init__(self, i2c):
        """
        Initialize QMC5883L sensor in continuous mode.
        """
        self.i2c = i2c

        # Configure sensor: 200Hz output rate, full scale, continuous measurement
        self.i2c.writeto_mem(QMC_ADDR, 0x09, bytes([0b00011101]))

        # Soft reset (resets registers to default)
        self.i2c.writeto_mem(QMC_ADDR, 0x0B, b'\x01')

        # Buffers for moving average smoothing
        self.buffer_x = []
        self.buffer_y = []
        self.buffer_z = []

    def read_raw(self):
        """
        Reads raw 16-bit X, Y, Z values from the sensor.
        Returns signed integers.
        """
        data = self.i2c.readfrom_mem(QMC_ADDR, 0x00, 6)  # Read 6 bytes: X_L, X_H, Y_L, Y_H, Z_L, Z_H
        x = to_signed(int.from_bytes(data[0:2], 'little'))  # Combine bytes and convert to signed
        y = to_signed(int.from_bytes(data[2:4], 'little'))
        z = to_signed(int.from_bytes(data[4:6], 'little'))
        return x, y, z

    def read_tesla(self):
        """
        Reads the raw data, converts to Tesla, and applies moving average smoothing.
        Returns smoothed X, Y, Z values in Tesla.
        """
        x, y, z = self.read_raw()
        # Convert raw counts to Tesla
        X = x * LSB_TO_TESLA
        Y = y * LSB_TO_TESLA
        Z = z * LSB_TO_TESLA

        # Append to buffers for smoothing
        self.buffer_x.append(X)
        self.buffer_y.append(Y)
        self.buffer_z.append(Z)

        # Keep only the last SMOOTHING samples
        if len(self.buffer_x) > SMOOTHING:
            self.buffer_x.pop(0)
            self.buffer_y.pop(0)
            self.buffer_z.pop(0)

        # Compute average (moving average) for smoother readings
        X_avg = sum(self.buffer_x)/len(self.buffer_x)
        Y_avg = sum(self.buffer_y)/len(self.buffer_y)
        Z_avg = sum(self.buffer_z)/len(self.buffer_z)
        return X_avg, Y_avg, Z_avg

    def heading(self):
        """
        Calculates compass heading (degrees) from X and Y components.
        Uses atan2 to handle full 360° range.
        Applies optional HEADING_OFFSET for manual correction.
        """
        X, Y, Z = self.read_tesla()
        angle = math.atan2(Y, X) * (180 / math.pi)  # atan2(Y, X) gives heading in degrees
        if angle < 0:
            angle += 360  # Ensure heading is 0-360°
        angle = (angle + HEADING_OFFSET) % 360  # Apply manual offset
        return angle

    def magnitude(self):
        """
        Calculates the magnitude of the magnetic field vector.
        sqrt(X^2 + Y^2 + Z^2)
        """
        X, Y, Z = self.read_tesla()
        return math.sqrt(X*X + Y*Y + Z*Z)

    def read_list(self):
        """
        Returns a clean list with values and units:
        [('X', value, 'uT'), ... , ('Heading', value, 'deg')]
        """
        X, Y, Z = self.read_tesla()
        # Convert Tesla to microTesla for easier reading
        X_uT, Y_uT, Z_uT = X*1e6, Y*1e6, Z*1e6
        mag_uT = self.magnitude() * 1e6
        heading = self.heading()
        return [
            ("X", round(X_uT, 2), "uT"),
            ("Y", round(Y_uT, 2), "uT"),
            ("Z", round(Z_uT, 2), "uT"),
            ("Magnitude", round(mag_uT, 2), "uT"),
            ("Heading", round(heading, 1), "deg")
        ]

# ================= MAIN =================
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=200000)  # Setup I2C pins and frequency
sensor = QMC5883L(i2c)  # Initialize sensor

print("QMC5883L Magnetometer Ready (Smoothed Output)...\n")

# Continuous loop to read and print data
while True:
    data = sensor.read_list()  # Get smoothed data in a nice list
    print(data)
    time.sleep(0.2)  # Wait 0.2 seconds between readings

