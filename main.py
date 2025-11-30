import machine
import time
from sbus import SBUSReceiver

ENA_PIN = 14
IN1_PIN = 26
IN2_PIN = 27
SBUS_PIN = 16

class ControllerChannels:
    def __init__(self, channels):
        self.raw = channels
        self.ch1 = channels[0]  # Left:172 Right:1811 Idle:992
        self.ch2 = channels[1]  # Fwd:1811 Back:172 Idle:984  
        self.ch3 = channels[2]  # Throttle:172(stop)-1811(max)
        self.ch4 = channels[3]  # Spin L:172 R:1811 Idle:968
        self.ch5 = channels[4]  # Car:992 Drone:1237
    
    def normalized(self, ch_value, min_val=172, max_val=1811):
        """Normalize to [-1,1] using your exact ranges"""
        center = (min_val + max_val) / 2
        span = (max_val - min_val) / 2
        norm = (ch_value - center) / span
        return max(-1, min(1, norm))
    
    def get_xyz(self):
        """Stick position using your real ranges"""
        x = self.normalized(self.ch1, 172, 1811)  # Left/Right
        y = self.normalized(self.ch2, 172, 1811)  # Fwd/Back
        z = (x*x + y*y) ** 0.5
        return x, y, z
    
    def is_car_mode(self):
        """CH5: 992=CAR, 1237=DRONE"""
        return self.ch5 <= 1100  # Perfect between 992 & 1237
    
    def throttle_norm(self):
        """CH3: 172=0%, 1811=100%"""
        return max(0, min(1, (self.ch3 - 172) / (1811 - 172)))
    
    def is_valid_signal(self):
        """All channels in valid SBUS range"""
        return all(172 <= ch <= 1811 for ch in self.raw[:5])

# Hardware
pwm = machine.PWM(machine.Pin(ENA_PIN), freq=2000)
in1 = machine.Pin(IN1_PIN, machine.Pin.OUT)
in2 = machine.Pin(IN2_PIN, machine.Pin.OUT)
sbus = SBUSReceiver(2, rx_pin=SBUS_PIN)

def set_motor(speed, direction):
    if speed > 1023: speed = 1023
    if speed < 0: speed = 0
    pwm.duty(int(speed))
    if direction == 1:
        in1.value(1); in2.value(0)
    elif direction == -1:
        in1.value(0); in2.value(1)
    else:
        in1.value(0); in2.value(0)

print("PERFECT RANGES: CH1-4=172-1811, CH5=992(CAR)/1237(DRONE)")
print_counter = 0

while True:
    sbus.get_new_data()
    channels = sbus.get_rx_channels()
    ctrl = ControllerChannels(channels)
    
    # Failsafe
    if not ctrl.is_valid_signal():
        set_motor(0, 0)
        if print_counter >= 10:
            print("*** NO SIGNAL - STOP ***")
        continue
    
    # Motor control
    if ctrl.is_car_mode():
        speed = int(ctrl.throttle_norm() * 1023)
        set_motor(speed, 1)
    else:
        set_motor(0, 0)
    
    # Print every 10 loops
    print_counter += 1
    if print_counter >= 10:
        print_counter = 0
        x, y, z = ctrl.get_xyz()
        mode = "CAR" if ctrl.is_car_mode() else "DRONE"
        speed = int(ctrl.throttle_norm() * 1023)
        print(f"CH1:{ctrl.ch1:4} CH2:{ctrl.ch2:4} CH3:{ctrl.ch3:4} CH4:{ctrl.ch4:4} CH5:{ctrl.ch5:4} | {mode} | SPD:{speed:3} XYZ({x:.2f},{y:.2f},{z:.2f})")
    
    time.sleep_ms(10)
