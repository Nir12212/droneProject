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
    
    def ch1_left_right(self):
        """CH1: 172=left(-1), 992=idle(0), 1811=right(+1)"""
        return max(-1, min(1, (self.ch1 - 992) / (1811 - 992)))
    
    def ch2_forward_back(self):
        """CH2: 172=back(-1), 984=idle(0), 1811=forward(+1)"""
        return max(-1, min(1, (self.ch2 - 984) / (1811 - 984)))
    
    def ch3_throttle(self):
        """CH3: 172=0%, 1811=100%"""
        return max(0, min(1, (self.ch3 - 172) / (1811 - 172)))
    
    def ch4_spin(self):
        """CH4: 172=spin left(-1), 968=idle(0), 1811=spin right(+1)"""
        return max(-1, min(1, (self.ch4 - 968) / (1811 - 968)))
    
    def ch5_mode(self):
        """CH5: 992=car, 1237=drone → returns 'CAR' or 'DRONE'"""
        return "CAR" if self.ch5 <= 1100 else "DRONE"
    
    def get_xyz(self):
        """Stick position: x=ch1 left/right, y=ch2 fwd/bk, z=magnitude"""
        x = self.ch1_left_right()
        y = self.ch2_forward_back()
        z = (x*x + y*y) ** 0.5
        return x, y, z
    
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

print("CHANNEL FUNCTIONS ACTIVE!")
print("ch1_left_right()  ch2_forward_back()  ch3_throttle()  ch4_spin()  ch5_mode()")
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
    
    # Motor control using ch3_throttle() and ch5_mode()
    if ctrl.ch5_mode() == "CAR":
        speed = int(ctrl.ch3_throttle() * 1023)
        set_motor(speed, 1)
    else:
        set_motor(0, 0)
    
    # Print using channel functions
    print_counter += 1
    if print_counter >= 10:
        print_counter = 0
        x, y, z = ctrl.get_xyz()
        mode = ctrl.ch5_mode()
        throttle = ctrl.ch3_throttle()
        spin = ctrl.ch4_spin()
        speed = int(throttle * 1023)
        print(f"Raw: {ctrl.ch1:4} {ctrl.ch2:4} {ctrl.ch3:4} {ctrl.ch4:4} {ctrl.ch5:4} | "
              f"LR:{x:.2f} FB:{y:.2f} TH:{throttle:.2f} SP:{spin:.2f} | {mode} SPD:{speed:3}")
    
    time.sleep_ms(10)
