from time import sleep
import reseau
import missions
import ubinascii
import network
import _thread

def get_robot_uuid():
    mac = ubinascii.hexlify(network.WLAN().config('mac')).decode()
    return f"{mac[:8]}-{mac[8:12]}-0000-0000-000000000000"

mac = get_robot_uuid()

def main():
    reseau.connecter_wifi("IMERIR Fablab", "imerir66")
    print(" Robot ID:", mac)
    
    mission_index = 0
    blocks = []

    while True:
        if mission_index >= len(blocks):
            print("🔄 Recherche d'instructions...")
            instruction = reseau.recuperer_instruction(mac)
            if instruction and "blocks" in instruction and len(instruction["blocks"]) > 0:
                blocks = instruction["blocks"]
                mission_index = 0
                print("📋 Nouvelles missions reçues :", blocks)
            else:
                print("✅ Aucune nouvelle mission")
                sleep(5)
                continue

        numero = blocks[mission_index]
        print("🚀 Exécution mission", numero)
        missions.executer_mission(numero)

        # ✅ ENVOYER SUMMARY SEULEMENT après la DERNIÈRE mission
        if mission_index == len(blocks) - 1:
            print("📬 Toutes les missions sont effectuées, envoi du SUMMARY...")
            reseau.envoyer_summary()

        mission_index += 1
        sleep(2)
        
def boucle_telemetrie():
    while True:
        try:
            distance = missions.ultra.distance_cm()
            distance_mm = float(distance * 10) if distance else 0

            reseau.envoyer_telemetrie(
                robot_id=mac,
                vitesse=float(missions.vitesse_actuelle),
                distance_ultrasons=distance_mm,
                statut=missions.statut_deplacement,
                ligne=missions.ligne_actuelle,
                pince_active=missions.pince_ouverte
            )
        except Exception as e:
            print("Erreur télémetrie périodique :", e)

        sleep(1)

_thread.start_new_thread(boucle_telemetrie, ())
main()
