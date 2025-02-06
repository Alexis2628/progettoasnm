import os
import json
import logging

def save_results_to_file(model_results, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for model_name, result in model_results.items():
        print("model_name: ", model_name)
        result_file_path = os.path.join(output_dir, f"{model_name}_results.json" if isinstance(result, dict) else f"{model_name}_results.txt")
        with open(result_file_path, "w") as f:
            # Se il risultato è un set, lo converto in una lista prima di salvarlo come JSON
            if isinstance(result, set):
                result = list(result)
            # Se è un dizionario o una tupla, converto i set in liste e salvo come JSON
            if isinstance(result, dict):
                result = convert_sets_in_dict(result)  # Converti i set in liste in un dizionario
                json.dump(result, f, indent=4)  # Salva come JSON
            elif isinstance(result, tuple):
                result = convert_sets_in_tuple(result)  # Converti i set in liste in una tupla
                json.dump(result, f, indent=4)  # Salva come JSON
            else:
                f.write(f"{model_name}: {result}\n")

        logging.info(f"Risultati salvati correttamente in {model_name}")

def convert_sets_in_dict(d):
    # Funzione ricorsiva per convertire tutti i set in liste nel dizionario
    for key, value in d.items():
        if isinstance(value, set):
            d[key] = list(value)
        elif isinstance(value, dict):
            d[key] = convert_sets_in_dict(value)  # Conversione ricorsiva per dizionari annidati
        elif isinstance(value, tuple):
            d[key] = convert_sets_in_tuple(value)  # Gestione delle tuple
    return d

def convert_sets_in_tuple(t):
    # Funzione per convertire i set in liste dentro una tupla
    return tuple(convert_sets_in_list(item) if isinstance(item, (set, tuple)) else item for item in t)

def convert_sets_in_list(l):
    # Funzione per convertire i set in liste dentro una lista
    return [convert_sets_in_list(item) if isinstance(item, (set, tuple)) else item for item in l]
