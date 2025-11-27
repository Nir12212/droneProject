from machine import PWM
class motor:
    def __init__(self,in1,in2,ena,in3,in4,enb):
        self.in1=in1
        self.in2=in2
        self.ena=ena
        self.in3=in3
        self.in4=in4
        self.enb=enb
    def turn_to(self,speed):
        self.ena.duty(int(1023*speed/100))
        self.enb.duty(int(1023*speed/100))
    def direction(self):
        self.in1.value(1)
        self.in2.value(0)
        self.in3.value(0)
        self.in4.value(1)
