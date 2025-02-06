import logging
from gensim.corpora.dictionary import Dictionary
from gensim.models.ldamodel import LdaModel

class TopicModeling:
    @staticmethod
    def perform_topic_modeling(user_opinions, num_topics=5):
        logging.info("Esecuzione del topic modeling con LDA.")
        texts = [opinion.split() for opinion in user_opinions.values()]
        dictionary = Dictionary(texts)
        corpus = [dictionary.doc2bow(text) for text in texts]
        lda_model = LdaModel(corpus=corpus, num_topics=num_topics, id2word=dictionary, random_state=42)
        logging.info("Topic modeling completato.")
        return lda_model, dictionary, corpus
