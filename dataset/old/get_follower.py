import json
import csv
from Code.data_extraction.old.threads_interface import ThreadsInterface


def process_json_data(user_json):
    """
    Processa il JSON fornito per estrarre user_id, username e full_name.
    """
    # print(user_json)
    if user_json.get("data") == None:
        return []
    followers = (
        user_json.get("data", {}).get("user", {}).get("followers", {}).get("edges", [])
    )
    result = []

    for follower in followers:
        node = follower.get("node", {})
        result.append(
            {
                "user_id": node.get("pk"),
                "username": node.get("username"),
                "full_name": node.get("full_name"),
            }
        )
    return result


def create_user_followers_map(csv_file, output_file):
    """
    Legge gli user_id dal file CSV, processa il JSON associato e crea un nuovo JSON.
    Se l'utente è già presente nell'output_file, lo salta.
    """
    # Carica l'output esistente, se presente
    ti = ThreadsInterface()
    try:
        with open(output_file, "r", encoding="utf-8") as outfile:
            user_followers_map = json.load(outfile)
    except (FileNotFoundError, json.JSONDecodeError):
        user_followers_map = {}

    with open(csv_file, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        iter = 0
        for row in reader:
            if iter == 30:
                with open(output_file, "w", encoding="utf-8") as outfile:
                    json.dump(user_followers_map, outfile, indent=4, ensure_ascii=False)
                return
            user_id = row["user_id"]
            username = row["username"]

            # Salta se l'utente è già presente nell'output
            if user_id in user_followers_map:
                # print(f"Utente {user_id} già processato, salto.")
                continue
            iter = iter + 1
            # Processa l'utente
            print(f"Processando utente {user_id} ({username})...")
            out = ti.retrieve_follower_by_id(user_id)
            followers_list = process_json_data(out)
            user_followers_map[user_id] = {
                "username": username,
                "followers": followers_list,
            }

    # Scrive l'output aggiornato
    with open(output_file, "w", encoding="utf-8") as outfile:
        json.dump(user_followers_map, outfile, indent=4, ensure_ascii=False)


if __name__ == "__main__":

    csv_file = (
        "../data/data.csv"  # Il file CSV che contiene le colonne user_id e username
    )
    output_file = "../data/output.json"  # Il file JSON generato
    for i in range(100):
        create_user_followers_map(csv_file, output_file)
