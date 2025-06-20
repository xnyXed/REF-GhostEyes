from machine import Pin, time_pulse_us
from time import sleep_us

class Ultrason:
    def __init__(self, trig_pin, echo_pin):
        self.trig = Pin(trig_pin, Pin.OUT)
        self.echo = Pin(echo_pin, Pin.IN)
        self.trig.value(0)
        sleep_us(2)

    def distance_cm(self):
        # Envoi d'une impulsion de 10µs
        self.trig.value(1)
        sleep_us(10)
        self.trig.value(0)

        # Mesure du temps pour l'écho
        try:
            duration = time_pulse_us(self.echo, 1, 30000)  # timeout 30ms
            distance = (duration / 2) / 29.1  # conversion en cm
            return round(distance, 1)
        except OSError:
            return -1  # pas de signal reçu
