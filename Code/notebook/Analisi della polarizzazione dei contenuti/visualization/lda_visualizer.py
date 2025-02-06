import logging
import pyLDAvis
import pyLDAvis.gensim_models
import os

class LDAViz:
    @staticmethod
    def visualize(lda_model, corpus, dictionary, output_dir):
        logging.info("Creazione della visualizzazione dei temi con pyLDAvis.")
        vis = pyLDAvis.gensim_models.prepare(lda_model, corpus, dictionary)
        pyLDAvis.save_html(vis, os.path.join(output_dir, "lda_visualization.html"))
        logging.info("Visualizzazione dei temi con pyLDAvis completata e salvata.")
