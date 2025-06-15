import os
import json
import logging


def save_results_to_file(model_results, output_dir):
    """Salva su file i risultati dei modelli.

    Parameters
    ----------
    model_results : dict
        Mappatura nome_modello -> risultato.
    output_dir : str
        Cartella di destinazione.
    """

    os.makedirs(output_dir, exist_ok=True)
    for model_name, result in model_results.items():
        print("model_name: ", model_name)
        result_file_path = os.path.join(
            output_dir,
            (
                f"{model_name}_results.json"
                if isinstance(result, dict)
                else f"{model_name}_results.txt"
            ),
        )
        with open(result_file_path, "w") as f:

            if isinstance(result, set):
                result = list(result)

            if isinstance(result, dict):
                result = convert_sets_in_dict(result)
                json.dump(result, f, indent=4)
            elif isinstance(result, tuple):
                result = convert_sets_in_tuple(result)
                json.dump(result, f, indent=4)
            else:
                f.write(f"{model_name}: {result}\n")

        logging.info(f"Risultati salvati correttamente in {model_name}")


def convert_sets_in_dict(d):
    """Converte ricorsivamente i ``set`` in ``list`` dentro un dict.

    Parameters
    ----------
    d : dict
        Dizionario potenzialmente contenente set.

    Returns
    -------
    dict
        Dizionario con i set convertiti in liste.
    """
    for key, value in d.items():
        if isinstance(value, set):
            d[key] = list(value)
        elif isinstance(value, dict):
            d[key] = convert_sets_in_dict(value)
        elif isinstance(value, tuple):
            d[key] = convert_sets_in_tuple(value)
    return d


def convert_sets_in_tuple(t):
    """Converte eventuali ``set`` presenti in una tupla in ``list``.

    Parameters
    ----------
    t : tuple
        Tupla che può contenere set.

    Returns
    -------
    tuple
        Nuova tupla con i set convertiti in liste.
    """

    return tuple(
        convert_sets_in_list(item) if isinstance(item, (set, tuple)) else item
        for item in t
    )


def convert_sets_in_list(l):
    """Converte eventuali ``set`` presenti in una lista in ``list``.

    Parameters
    ----------
    l : list
        Lista che può contenere set.

    Returns
    -------
    list
        Lista con eventuali set convertiti in liste.
    """

    return [
        convert_sets_in_list(item) if isinstance(item, (set, tuple)) else item
        for item in l
    ]
