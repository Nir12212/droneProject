import machine
import time
from sbus import SBUSReceiver

# ---------------- 4 MOTOR L298N PINS ----------------
# Motor A (Left Front)
ENA1_PIN = 14   # PWM
IN1A_PIN = 26   # Direction
IN2A_PIN = 27   

# Motor B (Left Rear) 
ENB1_PIN = 13   # PWM
IN3A_PIN = 25   # Direction
IN4A_PIN = 33   

# Motor C (Right Front)
ENA2_PIN = 12   # PWM
IN1B_PIN = 32   # Direction
IN2B_PIN = 15   

# Motor D (Right Rear)
ENB2_PIN = 2    # PWM
IN3B_PIN = 4    # Direction
IN4B_PIN = 5    

SBUS_PIN = 16

class ControllerChannels:
    def __init__(self, channels):
        self.raw = channels
        self.ch1 = channels[0]  # Left:172 Right:1811 Idle:992 (Steering)
        self.ch2 = channels[1]  # Fwd:1811 Back:172 Idle:984 (Forward/Back)
        self.ch3 = channels[2]  # Throttle:172(stop)-1811(max)
        self.ch4 = channels[3]  # Spin L:172 R:1811 Idle:968 (Tank Spin)
        self.ch5 = channels[4]  # Car:992 Drone:1237
    
    def ch1_steer(self):
        """CH1: 172=left(-1), 992=straight(0), 1811=right(+1)"""
        return max(-1, min(1, (self.ch1 - 992) / (1811 - 992)))
    
    def ch2_drive(self):
        """CH2: 172=back(-1), 984=stop(0), 1811=forward(+1)"""
        return max(-1, min(1, (self.ch2 - 984) / (1811 - 984)))
    
    def ch3_throttle(self):
        """CH3: 172=0%, 1811=100%"""
        return max(0, min(1, (self.ch3 - 172) / (1811 - 172)))
    
    def ch4_spin(self):
        """CH4: 172=spin left(-1), 968=idle(0), 1811=spin right(+1)"""
        return max(-1, min(1, (self.ch4 - 968) / (1811 - 968)))
    
    def ch5_mode(self):
        return "CAR" if self.ch5 <= 1100 else "DRONE"
    
    def is_valid_signal(self):
        return all(172 <= ch <= 1811 for ch in self.raw[:5])

class Motor:
    """Single L298N motor control"""
    def __init__(self, ena_pin, in1_pin, in2_pin):
        self.pwm = machine.PWM(machine.Pin(ena_pin), freq=2000)
        self.in1 = machine.Pin(in1_pin, machine.Pin.OUT)
        self.in2 = machine.Pin(in2_pin, machine.Pin.OUT)
    
    def set_speed_dir(self, speed, direction):
        """speed: 0-1023, direction: -1=reverse, 0=stop, 1=forward"""
        speed = max(0, min(1023, abs(int(speed))))
        self.pwm.duty(speed)
        
        if direction > 0:        # Forward
            self.in1.value(1)
            self.in2.value(0)
        elif direction < 0:      # Reverse
            self.in1.value(0)
            self.in2.value(1)
        else:                    # Stop
            self.in1.value(0)
            self.in2.value(0)

# ---------------- HARDWARE SETUP ----------------
# 4 Motors
motor_lf = Motor(ENA1_PIN, IN1A_PIN, IN2A_PIN)  # Left Front
motor_lr = Motor(ENB1_PIN, IN3A_PIN, IN4A_PIN)  # Left Rear
motor_rf = Motor(ENA2_PIN, IN1B_PIN, IN2B_PIN)  # Right Front
motor_rr = Motor(ENB2_PIN, IN3B_PIN, IN4B_PIN)  # Right Rear

sbus = SBUSReceiver(2, rx_pin=SBUS_PIN)

def tank_drive(left_speed, right_speed):
    """Drive 4 motors tank-style"""
    motor_lf.set_speed_dir(left_speed, 1 if left_speed > 0 else -1 if left_speed < 0 else 0)
    motor_lr.set_speed_dir(left_speed, 1 if left_speed > 0 else -1 if left_speed < 0 else 0)
    motor_rf.set_speed_dir(right_speed, 1 if right_speed > 0 else -1 if right_speed < 0 else 0)
    motor_rr.set_speed_dir(right_speed, 1 if right_speed > 0 else -1 if right_speed < 0 else 0)

print("4-MOTOR TANK DRIVE + QX7 READY!")
print("CH2=Drive, CH1=Steer, CH3=Speed, CH4=Spin, CH5=CAR/DRONE")
print_counter = 0

while True:
    sbus.get_new_data()
    channels = sbus.get_rx_channels()
    ctrl = ControllerChannels(channels)
    
    # Failsafe
    if not ctrl.is_valid_signal() or ctrl.ch5_mode() == "DRONE":
        tank_drive(0, 0)
        if print_counter >= 10:
            print("*** STOPPED (No Signal/DRONE) ***")
        continue
    
    # TANK DRIVE CONTROL
    drive = ctrl.ch2_drive()      # Forward/back (-1 to +1)
    steer = ctrl.ch1_steer()      # Left/right (-1 to +1)
    throttle = ctrl.ch3_throttle() # Overall speed boost (0-1)
    
    # Mix drive + steer → differential speeds
    left_speed = drive * throttle * 1023
    right_speed = drive * throttle * 1023
    
    # Apply steering (tank turn)
    turn_amount = steer * 512  # Max 50% speed difference
    left_speed -= turn_amount
    right_speed += turn_amount
    
    tank_drive(left_speed, right_speed)
    
    # Status
    print_counter += 1
    if print_counter >= 10:
        print_counter = 0
        spin = ctrl.ch4_spin()
        x, y, z = ctrl.ch1_steer(), ctrl.ch2_drive(), abs(drive)
        print(f"CH1:{ctrl.ch1:4} CH2:{ctrl.ch2:4} CH3:{ctrl.ch3:4} | "
              f"L:{left_speed:5.0f} R:{right_speed:5.0f} | "
              f"Steer:{x:.2f} Drive:{y:.2f} Thr:{throttle:.2f}")
    
    time.sleep_ms(10)
