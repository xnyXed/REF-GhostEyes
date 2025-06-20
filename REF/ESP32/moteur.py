from machine import Pin, PWM
from time import sleep

class Moteur:
    def __init__(self, in1, in2, en_pwm, min_duty=200, max_duty=1023):
        self.in1 = Pin(in1, Pin.OUT)
        self.in2 = Pin(in2, Pin.OUT)
        self.pwm = PWM(Pin(en_pwm), freq=1000)
        self.min_duty = min_duty
        self.max_duty = max_duty

    def forward(self, speed):
    # Impulsion de démarrage si speed est bas
        if speed < 50:
            self.pwm.duty(self._duty_cycle(100))
            self.in1.value(1)
            self.in2.value(0)
            sleep(0.05)  # courte impulsion à pleine puissance

        self.pwm.duty(self._duty_cycle(speed))
        self.in1.value(1)
        self.in2.value(0)

    def backward(self, speed):
        if speed < 50:
            self.pwm.duty(self._duty_cycle(100))
            self.in1.value(0)
            self.in2.value(1)
            sleep(0.05)

        self.pwm.duty(self._duty_cycle(speed))
        self.in1.value(0)
        self.in2.value(1)

    def stop(self):
        self.pwm.duty(0)
        self.in1.value(0)
        self.in2.value(0)

    def _duty_cycle(self, speed):
        speed = max(1, min(speed, 100))  # clamp
        return int(self.min_duty + (self.max_duty - self.min_duty) * ((speed - 1) / 99))
