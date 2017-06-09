"""program configuration"""
# base settings config
maindb_connection = ''
testdb_connection = 'postgres://postgres:@localhost:5432/mprorp'  # for travis db
google_private_key_id = ''
google_private_key = ''
google_client_email = ''
google_client_id = ''
google_spreadsheet_id = ''

tomita_log_path = ''

learning_parameters = {
    'rubricator':{
        'feature_selection': 2, # 1 - entropy_difference, 2 - mutual_information
        'optimal_features_number': 250,
        'tf_steps': 4000,
        'lr': 10,
        'l2': 0.005,
        'probab_limit': 0.5,
        'coef_for_tf_idf': 100,  # Коэффициент, который используется для вектора tf_idf,когда он присоединяется к эмбеддингу
        'coef_for_embed': 0.1,
        'run_stop_lemmas': False, # Использование файла для чтения стоп-лемм
        'stop_lemmas_filename': '/lex_count', # Имя файла, содержащего стоп-леммы
        'stop_lemmas_count': 1000, # Порог, при превышении которго лемма считается не интересной и попадает в стоп-леммы
        'eliminate_once_found_lemma': True,
        'num_docs_in_step': 100,
        'lemma_frequency_limit': 20,
        'rubric_num': 'pp',
    },
    'paragraph embeddings':{
        'embedding_for_word_count' : 5,
        'learning_steps': 4001,
        'calc_steps': 2001,
        'verbose' : True,

        'consistent_words' : True,
        'use_par_embed' : True,
        'use_NN' : True,
        'learning_rate' : 1,

        'batch_size' : 100,
        'embedding_size' : 128, # 128  # Dimension of the embedding vector.
        # embed_par_size : 400
        'skip_window' : 1,  # How many words to consider left and right (if not consistent_words)
        'num_skips' : 3,  # Size of the window with consistent or random order words
        'l1_size' : 512,  # 256

        'reg_l1' : 0.0001,
        'reg_emded' : 0.00005,
        'dropout' : 0.7,

        # if use_NN:
        'filename_NN' : 'ModelEP_0406_128_NonCons_6_3.pic',
        # else:
        'filename_no_NN' : 'ModelEP_0406_128_NonCons_6_3.pic',

        # parameters for rubrication
        'reg_coef': 0.000005,
        'lr':0.0025,
        'tf_steps': 100000,
        'valid_size' : 10,
        'valid_window' : 100,
        'num_sampled': 64
    },
    'models and sets':{
        'rubric_num': 'pp',
        'train_set_name': 'train_set_10',
        'test_set_name': 'test_set_10',
        'embedding_id': 'ModelEP_0506_128_NonCons_6_3.pic'
    }
}



try:
    # trying override base settings with custom
    from mprorp.config.local_settings import *
    for big_key in ['rubricator', 'paragraph embeddings', 'models and sets']:
        if big_key in local_learning_parameters.keys():
            params = local_learning_parameters[big_key]
            for key in params.keys():
                learning_parameters[big_key][key] = params[key]

except ImportError:
    pass

