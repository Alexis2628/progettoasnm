import json
import logging
from Code.data_extraction.old.threads_interface import ThreadsInterface


def setup_logging():
    """Configura il logging."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )


def process_json_data(user_json):
    """
    Processa il JSON fornito per estrarre user_id, username e full_name.
    """
    if user_json.get("data") is None:
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


def allusers(original_data):
    """Crea un insieme contenente tutti gli user_id nel dataset originale."""
    all_users = set(original_data.keys())
    for user_id, user_info in original_data.items():
        followers = user_info.get("followers", [])
        for follower in followers:
            follower_id = follower.get("user_id")
            all_users.add(follower_id)

    return all_users


def find_followers_of_followers(original_json_path, output_json_path, session):
    """
    Trova i follower dei follower solo se sono già presenti nel dataset originale.
    """
    # Carica il JSON originale
    with open(original_json_path, "rb") as file:
        original_data = json.load(file)

    alldata = len(original_data)
    for user_id, user_info in original_data.items():
        if "followers" in user_info:
            alldata = alldata + len(user_info["followers"])

    logging.info(f"Total number of user and follower : {alldata}")

    # Prepara un insieme di user_id per un rapido controllo
    existing_user_ids = allusers(original_data)

    ti = ThreadsInterface()

    request_count = 0
    max_requests = 30
    user_done = 0
    # Itera sui follower di ogni utente e trova i loro follower
    for user_id, user_info in original_data.items():
        if request_count >= max_requests:
            logging.warning(
                "Raggiunto il limite massimo di richieste (%d). Interrompendo ulteriori richieste.",
                max_requests,
            )
            break
        followers = user_info.get("followers", [])

        for follower in followers:
            follower_id = follower.get("user_id")
            if "followers" in follower:
                # logging.info(f"Follower {follower_id} ha già il campo 'followers'. Salto il recupero.")
                user_done = user_done + 1
                continue
            # Solo se il follower è già presente nei nodi esistenti
            if "a" == "a":
                # Controlla il limite di richieste
                if request_count >= max_requests:
                    logging.warning(
                        "Raggiunto il limite massimo di richieste (%d). Interrompendo ulteriori richieste.",
                        max_requests,
                    )
                    break

                # Recupera i follower del follower
                try:
                    out = ti.retrieve_follower_by_id(follower_id, session)
                    if "error" in out:
                        logging.error(
                            "Errore durante il recupero dei follower per follower_id %s",
                            follower_id,
                        )
                        raise Exception
                    request_count += 1
                except Exception as e:
                    logging.info(f"utenti analizzati = {user_done}")
                    with open(output_json_path + "err.json", "w") as output_file:
                        json.dump(original_data, output_file, indent=4)
                    logging.error(
                        "Errore durante il recupero dei follower per follower_id %s: %s",
                        follower_id,
                        e,
                    )
                    raise Exception
                follower_followers = process_json_data(out)

                # Filtra solo i follower già presenti nel dataset originale
                follower["followers"] = [
                    f for f in follower_followers if f["user_id"] in existing_user_ids
                ]
                leng = len(follower["followers"])
                logging.info(
                    f"Recupero follower per follower_id: {follower_id} con n°{leng}"
                )
    logging.info(f"utenti analizzati = {user_done+30}")
    # Salva il nuovo JSON con i follower dei follower
    with open(output_json_path, "w") as output_file:
        json.dump(original_data, output_file, indent=4)

    logging.info("Dataset aggiornato salvato in '%s'.", output_json_path)


if __name__ == "__main__":
    setup_logging()
    sessions = [
        "65955050144%3AS1xuKkl6W1kKqB%3A23%3AAYcjBamMFOs7TY1uYVsrP-gAou7-TriJJsp8l1NgLA",
        "71441509544%3AbPWmQfLc5vQhzF%3A7%3AAYfgsFzvtyS88WCjLlPNxUHfxAyfSs-PMk0cunbBMA",
        "1653774166%3A9uDdOCkxtjfjYr%3A25%3AAYf2jGK4vIx5W_dkE5m8a7PpoN4LA2D5CxUpR4C7BA",  # , # cat
        # "65955050144%3AkwLtyptmN1PWpx%3A3%3AAYfBeEJmc5PyFaNnzsG5Rr-3WVdWmufDi9nBvF94eg" # Fradsa Pasquasdsa
    ]
    for session in sessions:
        for i in range(1, 2):
            try:
                find_followers_of_followers(
                    r"dataset\dataset_cleaned.json",
                    r"dataset\dataset_cleaned.json",
                    session,
                )
            except Exception as e:
                logging.critical("Errore critico: %s", e)
                break
