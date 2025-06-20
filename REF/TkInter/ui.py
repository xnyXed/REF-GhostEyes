import tkinter as tk
from tkinter import messagebox
import requests
import uuid

# Valeurs valides à envoyer
COLOR_VALUES = {
    "Jaune": 2,
    "Rouge": 3,
    "Rose": 6,
    "Violet": 7,
    "Vert": 10
}

# Liste des robots (nom : uuid)
ROBOTS = {
    "GHOSTEYES": "24dcc3a8-3de8-0000-0000-000000000000",
    "O.S.R.": "efe16b56-45fa-47a3-8f05-04200828eea9",
    "MAXENCE LA FOURMIS": "72a1834d-98ef-4b46-87f5-5e4c4e82e39a",
    "PATHFINDER": "255f30bc-46f7-41d4-ba1d-db76a0afd7f7",
    "MR KRABS": "53d67923-704f-4b97-b6d4-64a0a04ca5de",
    "PASTA BOT":"7f377006-cba5-5d50f-a058d-45c5ce970f10",
}

API_URL = "http://10.7.4.225:8000/mission"  # adapte à ton API

def run_app():
    root = tk.Tk()
    root.title("Mission Robot – Sélection de blocs")
    root.geometry("500x580")
    root.configure(bg="#f5f5f5")
    root.resizable(False, False)

    # Choix robot
    tk.Label(root, text="Robot", font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(pady=(10, 2))
    selected_robot = tk.StringVar(value=list(ROBOTS.keys())[0])
    tk.OptionMenu(root, selected_robot, *ROBOTS.keys()).pack(pady=5)

    # Choix du nombre de blocs
    tk.Label(root, text="Investir de grandes missions", font=("Helvetica", 12, "bold"), bg="#f5f5f5").pack(pady=(15, 2))
    num_blocks_var = tk.IntVar(value=1)
    spin = tk.Spinbox(root, from_=1, to=len(COLOR_VALUES), textvariable=num_blocks_var, width=5, font=("Helvetica", 11), command=lambda: update_bloc_selectors())
    spin.pack(pady=5)

    # Conteneur dynamique
    bloc_frame = tk.Frame(root, bg="#f5f5f5")
    bloc_frame.pack(pady=10)

    # Stocke les variables et menus
    bloc_vars = []
    bloc_menus = []

    def update_bloc_selectors():
        for widget in bloc_frame.winfo_children():
            widget.destroy()
        bloc_vars.clear()
        bloc_menus.clear()

        for i in range(num_blocks_var.get()):
            row = tk.Frame(bloc_frame, bg="#f5f5f5")
            row.pack(pady=5)

            label = tk.Label(row, text=f"Bloc {i+1}", font=("Helvetica", 11), bg="#f5f5f5")
            label.pack(side=tk.LEFT, padx=5)

            var = tk.StringVar(value="")
            menu = tk.OptionMenu(row, var, *COLOR_VALUES.keys())
            menu.pack(side=tk.LEFT)
            bloc_vars.append(var)
            bloc_menus.append(menu)

            def make_callback(index):
                def callback(*_):
                    refresh_menus(index)
                return callback

            var.trace_add("write", make_callback(i))

        refresh_menus()

    def refresh_menus(changed_index=None):
        selected_colors = [var.get() for var in bloc_vars if var.get()]

        for i, var in enumerate(bloc_vars):
            current = var.get()
            menu = bloc_menus[i]["menu"]
            menu.delete(0, "end")

            available = [color for color in COLOR_VALUES.keys() if color == current or color not in selected_colors]
            for color in available:
                menu.add_command(label=color, command=lambda c=color, v=var: v.set(c))

            if current not in available:
                var.set("")

    update_bloc_selectors()

    status = tk.Label(root, text="", font=("Helvetica", 11), bg="#f5f5f5")
    status.pack(pady=10)

    def send():
        robot_name = selected_robot.get()
        robot_id = ROBOTS[robot_name]

        try:
            uuid.UUID(robot_id)
        except ValueError:
            messagebox.showerror("Erreur UUID", "UUID du robot invalide.")
            return

        try:
            blocs = [COLOR_VALUES[var.get()] for var in bloc_vars if var.get()]
        except KeyError:
            messagebox.showerror("Erreur", "Une sélection de couleur est vide ou invalide.")
            return

        if len(blocs) != num_blocks_var.get():
            messagebox.showerror("Erreur", "Tous les blocs doivent être sélectionnés sans doublons.")
            return

        payload = {
            "robot_id": robot_id,
            "blocs": blocs
        }

        try:
            response = requests.post(API_URL, json=payload)
            if response.status_code == 200:
                status.config(text=f"{len(blocs)} blocs envoyés pour {robot_name}", fg="green")
            else:
                messagebox.showerror("Erreur API", f"{response.status_code} – {response.text}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Requête échouée :\n{e}")

    tk.Button(root, text="Envoyer mission", font=("Helvetica", 12), bg="#4CAF50", fg="white", command=send).pack(pady=20)

    root.mainloop()
