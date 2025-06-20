from machine import Pin, PWM
from time import sleep

class Servo:
    def __init__(self, pin):
        self.pin_number = pin  # ✅ stocke le numéro du pin pour réactivation
        self.pwm = PWM(Pin(pin), freq=50)
        sleep(0.1)
        self.angle(2)  # Par défaut : fermé à 2°

    def angle(self, degrees):
        # Convertit l'angle (0 à 180) en duty entre 1 et 128
        duty = int((degrees / 180) * 102 + 26)
        duty = min(max(duty, 1), 128)
        self.pwm.duty(duty)

    def ouvrir(self):
        self._reactiver_pwm()
        self.angle(15)  # ✅ Ouvrir à 15°
        sleep(1)
        self.off()

    def fermer(self):
        self._reactiver_pwm()
        self.angle(2)  # ✅ Fermer à 2°
        sleep(1)
        self.off()

    def off(self):
        self.pwm.deinit()

    def _reactiver_pwm(self):
        self.pwm = PWM(Pin(self.pin_number), freq=50)  # ✅ Corrigé avec self.pin_number
