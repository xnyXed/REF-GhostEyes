from machine import Pin

class SuiveurLigne:
    def __init__(self, pin_gauche, pin_droite):
        self.ir_gauche = Pin(pin_gauche, Pin.IN)
        self.ir_droite = Pin(pin_droite, Pin.IN)

    def lire(self):
        return (self.ir_gauche.value(), self.ir_droite.value())

    def etat(self):
        g, d = self.lire()
        if g == 0 and d == 0:
            return "AVANCER"
        elif g == 0 and d == 1:
            return "DROITE"
        elif g == 1 and d == 0:
            return "GAUCHE"
        elif g == 1 and d == 1:
            return "LIGNE"
        else:
            return "ERREUR"
