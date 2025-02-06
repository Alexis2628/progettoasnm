from Code.data_extraction.old.post_data_handler import PostDataHandler


def main():
    # File CSV dove salvare i post raccolti
    post_data_csv = "../data/post_data.csv"
    replies_data_csv = "../data/replies_data.csv"

    # Query da cercare
    queries = [
        "#IntelligenzaArtificiale",
        "AI",
        "#ArtificialIntelligence",
        "Machine Learning",
        "Deep Learning",
        "#MachineLearning",
        "#DeepLearning",
        "#ChatGPT",
        "#AIImpact",
        "AI e privacy",
    ]

    # Inizializza il gestore di post
    post_data_handler = PostDataHandler(post_data_csv, replies_data_csv)

    # Raccoglie i post usando le query definite
    all_posts = post_data_handler.collect_posts_by_queries(queries)

    ids = post_data_handler.get_existing_ids(all_posts)

    all_replies = post_data_handler.collect_replies_by_post_id(ids)

    print(f"Totale post raccolti: {len(all_posts)}")
    print(f"Totale replies raccolti: {len(all_replies)}")


if __name__ == "__main__":
    main()
