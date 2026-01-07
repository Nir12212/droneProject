from machine import PWM
class motor:
    def __init__(self,in1,in2,ena,in3,in4,enb):
        self.in1=in1
        self.in2=in2
        self.ena=ena
        self.in3=in3
        self.in4=in4
        self.enb=enb
    def turn_to(self,turn,speed):
        if turn==0:
            self.ena.duty(int(1023*speed/100))
            self.enb.duty(int(1023*speed/300))
        elif turn==1:
            self.ena.duty(int(1023*speed/300))
            self.enb.duty(int(1023*speed/100))
        else:
            self.ena.duty(int(1023*speed/100))
            self.enb.duty(int(1023*speed/100))
    def direction(self,direction):
        if direction==0:
            in1.value(1)
            in2.value(0)
            in3.value(0)
            in4.value(1)
        elif direction==1:
            in1.value(0)
            in2.value(1)
            in3.value(1)
            in4.value(0)
        else:
            in1.value(0)
            in2.value(0)
            in3.value(0)
            in4.value(0)