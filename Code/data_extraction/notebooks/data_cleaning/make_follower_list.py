import pandas as pd


def make_follower_list(followers_csv, followers_of_followers_csv, output_csv):
    # Carica e pulisci followers
    df_f = pd.read_csv(followers_csv).drop_duplicates().dropna().astype(str)
    df_f = df_f.rename(
        columns={
            "user_threads_userpk": "thread_user_pk",
            "username": "thread_username",
            "user_threads_follower_pk": "thread_follower_pk",  # se presente, altrimenti usa follower_pk
            "follower_pk": (
                "thread_follower_pk"
                if "user_threads_follower_pk" not in df_f.columns
                else None
            ),
            "follower_username": "thread_follower_username",
        }
    )

    # Se 'user_threads_follower_pk' non c'è, usa follower_pk
    if "thread_follower_pk" not in df_f.columns:
        df_f["thread_follower_pk"] = df_f["follower_pk"]

    df_f = df_f[
        [
            "thread_user_pk",
            "thread_username",
            "thread_follower_pk",
            "thread_follower_username",
        ]
    ]

    # Carica e pulisci followers of followers
    df_ff = (
        pd.read_csv(followers_of_followers_csv).drop_duplicates().dropna().astype(str)
    )
    df_ff = df_ff.rename(
        columns={
            "user_threads_userpk": "thread_user_pk",
            "user_username": "thread_username",
            "follower_pk": "thread_follower_pk",
            "follower_username": "thread_follower_username",
        }
    )

    df_ff = df_ff[
        [
            "thread_user_pk",
            "thread_username",
            "thread_follower_pk",
            "thread_follower_username",
        ]
    ]

    # Unisci, deduplica, salva
    df_final = pd.concat([df_f, df_ff]).drop_duplicates().reset_index(drop=True)
    df_final.to_csv(output_csv, index=False)


if __name__ == "__main__":
    # Esempio di utilizzo
    path = r"Code\data_extraction\data\raw\AI/"
    output_path = r"Code\data_extraction\data\processed/"
    # make_follower_list(
    #     path + "followers.csv",
    #     path + "followers_of_followers.csv",
    #     output_path + "all_followers.csv",
    # )
    path = r"Code\data_extraction\data\raw\ML/"
    make_follower_list(
        path + "followers.csv",
        path + "followers_of_followers.csv",
        output_path + "ml_all_followers.csv",
    )
    path = r"Code\data_extraction\data\raw\ChatGPT/"
    make_follower_list(
        path + "followers.csv",
        path + "followers_of_followers.csv",
        output_path + "gpt_all_followers.csv",
    )
