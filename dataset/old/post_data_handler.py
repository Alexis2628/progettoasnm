import os
import pandas as pd
from Code.data_extraction.old.threads_interface import ThreadsInterface
import json
import logging

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,  # Livello di logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s - %(levelname)s - %(message)s",  # Formato del messaggio di log
    handlers=[logging.StreamHandler()],  # Mostra i log su console
)


class PostDataHandler:
    def __init__(self, post_data_csv: str, replies_data_csv: str):
        self.post_data_csv = post_data_csv
        self.replies_data_csv = replies_data_csv
        self.existing_posts = self._load_existing_data(post_data_csv)
        self.existing_replies = self._load_existing_data(replies_data_csv)
        self.threads_interface = ThreadsInterface()

        logging.info(
            "PostDataHandler initialized with post_data_csv: %s and replies_data_csv: %s",
            post_data_csv,
            replies_data_csv,
        )

    def _load_existing_data(self, filename):
        if os.path.exists(filename):
            logging.info("Loading existing data from %s", filename)
            return pd.read_csv(filename).to_dict(orient="records")
        logging.info("No existing data found at %s", filename)
        return []

    def get_existing_ids(self, existing_data):
        ids = {post["Post ID"] for post in existing_data}
        logging.debug("Existing IDs loaded: %s", ids)
        return ids

    def collect_posts_by_queries(self, queries: list, iterations_per_query: int = 1):

        filename = self.post_data_csv
        seen_post_ids = self.get_existing_ids(self.existing_posts.copy())
        all_posts = self.existing_posts.copy()

        logging.info("Starting to collect posts for queries: %s", queries)

        for query in queries:
            logging.info("Collecting posts for query: %s", query)
            for i in range(iterations_per_query):
                logging.debug("Iteration %d for query: %s", i + 1, query)
                response = self.threads_interface.retrieve_thread_by_query(query)
                if not response or not response.get("data"):
                    logging.warning(
                        "No data found for query: %s on iteration %d", query, i + 1
                    )
                    continue

                for edges in response["data"]["searchResults"]["edges"]:
                    thread_type = edges["node"]["thread"]["thread_type"]
                    for threads_item in edges["node"]["thread"]["thread_items"]:
                        post_data = threads_item["post"]
                        post_id = post_data.get("pk")

                        if post_id in seen_post_ids:
                            logging.debug(
                                "Post ID %s already processed, skipping", post_id
                            )
                            continue

                        seen_post_ids.add(post_id)
                        user_data = self._extract_post_data(post_data, thread_type)

                        logging.info("Collected post ID: %s", post_id)
                        if user_data is not None:
                            all_posts.append(user_data)

        self._save_data_to_csv(all_posts, filename)
        logging.info("Post collection completed, saved data to %s", filename)
        return all_posts

    def _extract_post_data(self, post_data, thread_type):
        try:
            post_id = post_data.get("pk")
            user_id = post_data["user"].get("id")
            username = post_data["user"].get("username")
            profile_pic_url = post_data["user"].get("profile_pic_url")
            text_fragments = post_data["text_post_app_info"]["text_fragments"].get(
                "fragments", []
            )
            text_post = text_fragments[0]["plaintext"] if text_fragments else ""
            like_count = post_data.get("like_count")
            quote_count = post_data["text_post_app_info"].get("quote_count")
            caption_text = post_data.get("caption").get("text", "")
            direct_reply_count = post_data.get("direct_reply_count")
            repost_count = post_data["text_post_app_info"].get("repost_count")

            logging.debug("Extracted post data for post ID: %s", post_id)

            return {
                "Post ID": post_id,
                "User ID": user_id,
                "Thread Type": thread_type,
                "Username": username,
                "Profile Picture URL": profile_pic_url,
                "Text Post": text_post,
                "Like Count": like_count,
                "Quote Count": quote_count,
                "Caption Text": caption_text,
                "Direct Reply Count": direct_reply_count,
                "Repost Count": repost_count,
            }
        except:
            return None

    def collect_replies_by_post_id(self, post_ids: list):
        filename = self.replies_data_csv
        seen_reply_ids = self.get_existing_ids(self.existing_replies.copy())
        all_replies = self.existing_replies.copy()

        logging.info("Starting to collect replies for post IDs: %s", post_ids)

        for post_id in post_ids:
            logging.info("Collecting replies for post ID: %s", post_id)
            try:
                response = json.loads(
                    self.threads_interface.retrieve_replies_by_post_id(int(post_id))
                )
            except:
                response = ""
            if not response or not response.get("data"):
                logging.warning("No data found for post ID: %s", post_id)
                continue

            for edges in response["data"]["data"]["edges"]:
                for threads_item in edges["node"]["thread_items"]:
                    post_data = threads_item["post"]
                    reply_id = post_data.get("pk")

                    if reply_id in seen_reply_ids:
                        logging.debug(
                            "Reply ID %s already processed, skipping", reply_id
                        )
                        continue  # Salta se la risposta è già stata processata

                    seen_reply_ids.add(reply_id)
                    reply_data = self._extract_post_data(post_data, thread_type="reply")
                    if reply_data is not None:
                        reply_data = self._update_post_data_with_json(
                            post_data, reply_data
                        )
                        reply_data["Parent Post ID"] = post_id

                        logging.info(
                            "Collected reply ID: %s for post ID: %s", reply_id, post_id
                        )
                        all_replies.append(reply_data)

        self._save_data_to_csv(all_replies, filename)
        logging.info("Reply collection completed, saved data to %s", filename)
        return all_replies

    def _update_post_data_with_json(self, post_data, post_dict):
        json_data = post_data
        if json_data:
            post_dict.update(
                {
                    "Following": json_data["user"]["friendship_status"].get(
                        "following", False
                    ),
                    "Followed By": json_data["user"]["friendship_status"].get(
                        "followed_by", False
                    ),
                    "Can Reply": json_data["text_post_app_info"].get(
                        "can_reply", False
                    ),
                    "Reply Control": json_data["text_post_app_info"].get(
                        "reply_control", "everyone"
                    ),
                    "Reshare Count": json_data.get("reshare_count", 0),
                    "Is Verified": json_data["user"].get("is_verified", False),
                }
            )
        return post_dict

    def _save_data_to_csv(self, data, filename):
        logging.info("Saving data to CSV: %s", filename)
        df = pd.DataFrame(data)
        df.drop_duplicates(inplace=True)
        df.to_csv(filename, index=False)
        logging.info("Data successfully saved to %s", filename)
