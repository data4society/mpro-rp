from mprorp.db.models import *
import mprorp.analyzer.db as db
import mprorp.db.dbDriver as Driver
import numpy as np
import mprorp.analyzer.rubricator as rb
import mprorp.ner.feature as feature
import mprorp.ner.identification as id


session = Driver.db_session()
rubricator = [
      {
        "rubric":"интернет",
        "rubric_minus":"интернет (-)",
        "set_name":"internet_tr_id_pnc_0"
      },
      {
        "rubric":"ЛГБТ",
        "rubric_minus":"ЛГБТ (-)",
        "set_name":"lgbt_tr_id_pnc_0"
      },
      {
        "rubric":"искусство",
        "rubric_minus":"искусство (-)",
        "set_name":"iskustvo_tr_id_pnc"
      },
      {
        "rubric":"насилие",
        "rubric_minus":"насилие (-)",
        "set_name":"nasilie_tr_id_pnc"
      },
      {
        "rubric":"угрозы",
        "rubric_minus":"угрозы (-)",
        "set_name":"ugrozy_tr_id_pnc"
      },
      {
        "rubric":"отчисление и увольнение",
        "rubric_minus":"отчисление и увольнение (-)",
        "set_name":"uvolnenie_tr_id_pnc"
      }
    ]

rubrics = session.query(Rubric).all()
rubric_ids_by_names = {}
for rubric in rubrics:
    rubric_ids_by_names[rubric.name] = str(rubric.rubric_id)

for rubr_obj in rubricator:
    rubr_obj["rubric_id"] = rubric_ids_by_names[rubr_obj["rubric"]]
    rubr_obj["rubric_minus_id"] = rubric_ids_by_names[rubr_obj["rubric_minus"]]


def print_lemmas_from_ribric_models(rubrics):
    models = {}
    train_set = {}
    print(rubrics)
    rubrics_names = {}
    for rubric_dict in rubrics:
        rubric_id = rubric_dict['rubric_id']
        rubrics_names[rubric_id] = rubric_dict['rubric']
        train_set_id = db.get_set_id_by_name(rubric_dict['set_name'])
        if train_set_id is None or train_set_id == '':
            continue
        train_set[rubric_id] = train_set_id
        # correct_answers[rubric_id] = db.get_rubric_answer_doc(doc_id, rubric_id)
        models[rubric_id] = db.get_model(rubric_id, train_set_id, session)
    sets = db.get_idf_lemma_index_by_set_id(train_set.values(), session)
    for rubric_id in train_set:
        set_id = train_set[rubric_id]
        mif_number = models[rubric_id]['features_num']
        lemma_index = sets[set_id]['lemma_index']
        model = models[rubric_id]['model']
        # print(lemma_index)
        # print(mif_number)
        # print(sets[set_id]['idf'])
        # print(models[rubric_id]['features'])
        # print(model)
        # print(len(models[rubric_id]['features']))
        main_words = []
        coef_p = np.zeros(len(lemma_index))
        coef_m = np.zeros(len(lemma_index))
        i=0
        for lemma in lemma_index:
            if lemma_index[lemma] in models[rubric_id]['features']:
                main_words.append(lemma)
                coef = model[models[rubric_id]['features'].index(lemma_index[lemma])]
                if coef > 0:
                    coef_p[i] = coef
                else:
                    coef_m[i] = coef
                i+=1

        good_numbers_p = np.argsort(coef_p)
        good_numbers_m = np.argsort(coef_m)
        print(rubrics_names[rubric_id])
        wp = []
        wm = []
        for i in range(len(lemma_index)):
            if coef_p[good_numbers_p[len(lemma_index) - i - 1]] > 0:
                wp.append(main_words[good_numbers_p[len(lemma_index) - i - 1]])
            if coef_m[good_numbers_m[i]] < 0:
                wm.append(main_words[good_numbers_m[i]])




        print('positive')
        print(wp)
        print('negative')
        print(wm)


print_lemmas_from_ribric_models(rubricator)