from machine import Pin, PWM
from time import sleep, ticks_ms, ticks_diff
from suiveur import SuiveurLigne
from moteur import Moteur
from servo import Servo

# === INIT ===

# Moteur gauche
mg_in1 = Pin(21, Pin.OUT)
mg_in2 = Pin(22, Pin.OUT)
mg_pwm = PWM(Pin(23))
mg_pwm.freq(1000)

# Moteur droit
md_in1 = Pin(18, Pin.OUT)
md_in2 = Pin(19, Pin.OUT)
md_pwm = PWM(Pin(5))
md_pwm.freq(1000)

moteur_g = Moteur(mg_in1, mg_in2, mg_pwm)
moteur_d = Moteur(md_in1, md_in2, md_pwm)

pince = Servo(25)
suiveur = SuiveurLigne(32, 33)

# === VARIABLES ===
compteur = 0
ligne_detectee = False
last_etat = ""
last_switch_time = ticks_ms()

# === Fonction pince séquence ===
def sequence_pince():
    print("🔓 Ouverture pince")
    pince.ouvrir()
    sleep(1)
    print("🔐 Fermeture pince")
    pince.fermer()

# === LOOP ===
while compteur < 11:
    etat = suiveur.etat()
    print("Capteurs:", etat, "| Compteur:", compteur)

    # Détection de passage rapide gauche ↔ droite
    now = ticks_ms()
    delay = ticks_diff(now, last_switch_time)

    if (etat == "GAUCHE" and last_etat == "DROITE") or (etat == "DROITE" and last_etat == "GAUCHE"):
        if delay < 300:
            if not ligne_detectee:
                compteur += 1
                ligne_detectee = True
                print("⚡ Ligne détectée par oscillation rapide GAUCHE ↔ DROITE | Total:", compteur)
                moteur_g.stop()
                moteur_d.stop()
                sleep(0.3)
    last_etat = etat
    last_switch_time = now

    # Comportement normal de suivi
    if etat == "AVANCER":
        moteur_g.forward(80)
        moteur_d.forward(80)
    elif etat == "GAUCHE":
        moteur_g.backward(20)
        sleep(0.05)  # pause rapide pour éviter conflit
        moteur_d.forward(80)
    elif etat == "DROITE":
        moteur_g.forward(80)
        sleep(0.05)
        moteur_d.backward(20)
    elif etat == "LIGNE":
        if not ligne_detectee:
            compteur += 1
            ligne_detectee = True
            print("🟩 Ligne verticale détectée | Total:", compteur)

            if compteur == 5 or compteur == 10:
                moteur_g.stop()
                moteur_d.stop()
                sequence_pince()
    else:
        moteur_g.forward(80)
        moteur_d.forward(80)

    # Réinit détection de ligne
    if etat != "LIGNE":
        ligne_detectee = False

    sleep(0.01)

# === FIN ===
print("✅ Fin du tour. Total lignes:", compteur)
moteur_g.stop()
moteur_d.stop()
