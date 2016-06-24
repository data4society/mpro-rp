import mprorp.analyzer.db as db


def ner_model(model_id, training_set_id):
    model = db.get_ner_model(model_id)
    # get doc_id
    # get all features and embeddings for all sentense_index and word_index
    # collect initialization vectors for each word
    # run nn