import network
import urequests
import json
from time import sleep

def connecter_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("🔌 Connexion Wi-Fi...")
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            print(".", end="")
            sleep(0.5)
    print("\n Connecté avec IP :", wlan.ifconfig()[0])

def envoyer_telemetrie(robot_id, vitesse, distance_ultrasons, statut, ligne, pince_active):
    url = "http://10.7.4.225:8000/telemetry"
    data = {
        "robot_id": robot_id,
        "vitesse": vitesse,
        "distance_ultrasons": distance_ultrasons,
        "statut_deplacement": statut,
        "ligne": ligne,
        "statut_pince": pince_active
    }
    try:
        res = urequests.post(url, json=data)
        print("📡 Télémetrie envoyée :", res.status_code)
        res.close()
    except Exception as e:
        print("❌ Erreur télémetrie :", e)

def recuperer_instruction(robot_id):
    url = f"http://10.7.4.225:8000/instructions?robot_id={robot_id}"
    try:
        res = urequests.get(url)
        if res.status_code == 200:
            data = res.json()
            print(" Instruction reçue :", data)
            res.close()
            return data
        else:
            print(" Mauvaise réponse :", res.status_code)
    except Exception as e:
        print(" Erreur GET :", e)
    return None


def envoyer_summary(robot_id = "24dcc3a8-3de8-0000-0000-000000000000"):
    url = "http://10.7.4.225:8000/summary"
    data = {
        "robot_id": robot_id
    }
    try:
        res = urequests.post(url, json=data)
        print(" ✅ Résumé de mission envoyé :", res.status_code)
        res.close()
    except Exception as e:
        print(" ❌ Erreur envoi résumé :", e)
