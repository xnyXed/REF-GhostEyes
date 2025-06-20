# === missions.py ===

from machine import Pin, PWM
from time import sleep, ticks_ms, ticks_diff
from suiveur import SuiveurLigne
from moteur import Moteur
from servo import Servo
from ultrason import Ultrason

# === PARAMÈTRES DE VITESSE (OPTIMISÉS) ===
VITESSE_SUIVI_LIGNE = 59
VITESSE_CORRECTION = 55
VITESSE_ROTATION_CUBE = 55
VITESSE_AVANCE_CUBE = 55
VITESSE_DEPOT = 55
VITESSE_RETOUR = 55
VITESSE_DEMI_TOUR = 55
vitesse_actuelle = 0  # en mm/s, ou simplement une copie des valeurs de vitesse PWM

# === INIT ===
ultra = Ultrason(27, 26)
moteur_g = Moteur(21, 22, 23)
moteur_d = Moteur(18, 19, 5)
suiveur = SuiveurLigne(32, 33)
pince = Servo(25)

ligne_actuelle = 1
sens_horaire = True
statut_deplacement = "stop"
pince_ouverte = True

def stop():
    global statut_deplacement
    moteur_g.stop()
    moteur_d.stop()
    statut_deplacement = "stop"

def avancer(vitesse=VITESSE_AVANCE_CUBE):
    global statut_deplacement, vitesse_actuelle
    moteur_g.forward(vitesse)
    moteur_d.forward(vitesse)
    statut_deplacement = "avance"
    vitesse_actuelle = vitesse

def tourner_demi_tour():
    global sens_horaire, statut_deplacement, vitesse_actuelle
    moteur_g.forward(VITESSE_DEMI_TOUR)
    moteur_d.backward(VITESSE_DEMI_TOUR)
    statut_deplacement = "rotation"
    sleep(1.4)
    stop()
    sens_horaire = not sens_horaire
    vitesse_actuelle = VITESSE_DEMI_TOUR


def suivre_ligne(ligne_cible):
    global ligne_actuelle, sens_horaire, statut_deplacement, vitesse_actuelle

    compteur = ligne_actuelle
    last_etat = ""
    last_switch_time = ticks_ms()
    last_ligne_time = ticks_ms()
    min_interval = 600  # délai minimal entre deux lignes pour éviter le surcomptage

    while compteur != ligne_cible:
        etat = suiveur.etat()
        now = ticks_ms()

        # Détection ligne uniquement si suffisamment de temps s’est écoulé
        if etat == "LIGNE" and ticks_diff(now, last_ligne_time) > min_interval:
            compteur = (compteur % 10) + 1 if sens_horaire else (compteur - 2) % 10 + 1
            print("🟩 Ligne détectée. Ligne:", compteur)
            last_ligne_time = now
            ligne_actuelle = compteur
            stop()
            sleep(0.15)  # petite pause pour stabilité

        last_etat = etat

        # Mouvement selon l'état détecté
        if etat == "AVANCER":
            moteur_g.forward(VITESSE_SUIVI_LIGNE)
            moteur_d.forward(VITESSE_SUIVI_LIGNE)
            statut_deplacement = "avance"
            vitesse_actuelle = VITESSE_SUIVI_LIGNE
        elif etat == "GAUCHE":
            moteur_g.backward(VITESSE_CORRECTION)
            sleep(0.05)
            moteur_d.forward(VITESSE_SUIVI_LIGNE)
            statut_deplacement = "gauche"
            vitesse_actuelle = VITESSE_SUIVI_LIGNE
        elif etat == "DROITE":
            moteur_g.forward(VITESSE_SUIVI_LIGNE)
            sleep(0.05)
            moteur_d.backward(VITESSE_CORRECTION)
            statut_deplacement = "droite"
            vitesse_actuelle = VITESSE_SUIVI_LIGNE
        else:
            moteur_g.forward(VITESSE_SUIVI_LIGNE)
            moteur_d.forward(VITESSE_SUIVI_LIGNE)
            statut_deplacement = "avance"
            vitesse_actuelle = VITESSE_SUIVI_LIGNE

        sleep(0.01)

    stop()


def chercher_et_prendre_cube():
    global pince_ouverte, statut_deplacement, vitesse_actuelle
    rotation_sens = sens_horaire
    moteur_g.backward(VITESSE_ROTATION_CUBE) if rotation_sens else moteur_g.forward(VITESSE_ROTATION_CUBE)
    moteur_d.forward(VITESSE_ROTATION_CUBE) if rotation_sens else moteur_d.backward(VITESSE_ROTATION_CUBE)
    statut_deplacement = "rotation"
    vitesse_actuelle = VITESSE_ROTATION_CUBE

    t_rotation_start = ticks_ms()
    while True:
        dist = ultra.distance_cm()
        if dist and 1 < dist < 20:
            stop()
            sleep(0.2)
            if rotation_sens:
                moteur_g.backward(15)
                moteur_d.forward(15)
            else:
                moteur_g.forward(15)
                moteur_d.backward(15)
            sleep(0.15)
            stop()
            break
        sleep(0.05)

    t_rotation_end = ticks_ms()
    rotation_duration = ticks_diff(t_rotation_end, t_rotation_start)

    t_avance_start = ticks_ms()
    while True:
        dist = ultra.distance_cm()
        if dist and 2 <= dist <= 8:
            stop()
            sleep(0.2)
            break
        avancer(VITESSE_AVANCE_CUBE)
        vitesse_actuelle = VITESSE_AVANCE_CUBE
        sleep(0.05)

    avance_duration = ticks_diff(ticks_ms(), t_avance_start)

    pince.fermer()
    pince_ouverte = False
    sleep(0.4)

    moteur_g.backward(VITESSE_AVANCE_CUBE)
    moteur_d.backward(VITESSE_AVANCE_CUBE)
    statut_deplacement = "recule"
    vitesse_actuelle = VITESSE_AVANCE_CUBE
    sleep(avance_duration / 1200)
    stop()
    sleep(0.2)

    if rotation_sens:
        moteur_g.forward(VITESSE_ROTATION_CUBE)
        moteur_d.backward(VITESSE_ROTATION_CUBE)
    else:
        moteur_g.backward(VITESSE_ROTATION_CUBE)
        moteur_d.forward(VITESSE_ROTATION_CUBE)
    sleep(rotation_duration / 1000)
    vitesse_actuelle = VITESSE_ROTATION_CUBE
    stop()
    sleep(0.2)


def mission_couleur(ligne_cube, ligne_depot):
    global pince_ouverte, vitesse_actuelle
    pince.ouvrir()
    pince_ouverte = True
    sleep(0.5)

    suivre_ligne(ligne_cube)
    sleep(0.2)

    chercher_et_prendre_cube()
    sleep(0.2)

    suivre_ligne(ligne_depot)
    sleep(0.2)

    moteur_g.backward(VITESSE_DEPOT) if sens_horaire else moteur_g.forward(VITESSE_DEPOT)
    moteur_d.forward(VITESSE_DEPOT) if sens_horaire else moteur_d.backward(VITESSE_DEPOT)
    vitesse_actuelle = VITESSE_DEPOT
    sleep(0.7)
    stop()

    avancer(VITESSE_DEPOT)
    vitesse_actuelle = VITESSE_DEPOT
    sleep(0.5)
    stop()

    pince.ouvrir()
    pince_ouverte = True
    sleep(0.5)

    moteur_g.backward(VITESSE_RETOUR)
    moteur_d.backward(VITESSE_RETOUR)
    vitesse_actuelle = VITESSE_RETOUR
    sleep(0.5)
    stop()
    
    moteur_g.forward(VITESSE_DEPOT) if sens_horaire else moteur_g.backward(VITESSE_DEPOT)
    moteur_d.backward(VITESSE_DEPOT) if sens_horaire else moteur_d.forward(VITESSE_DEPOT)
    vitesse_actuelle = VITESSE_DEPOT
    sleep(0.7)
    stop()

    return True  # ✅ FIN de la mission

def executer_mission(numero_ligne):
    if numero_ligne == 2:
        return mission_couleur(2, 5)
    elif numero_ligne == 3:
        return mission_couleur(3, 5)
    elif numero_ligne == 6:
        return mission_couleur(6, 5)
    elif numero_ligne == 7:
        return mission_couleur(7, 9)
    elif numero_ligne == 10:
        return mission_couleur(10, 9)
    return False
