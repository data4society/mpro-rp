from analyzer.pymystem3_w import Mystem
import db.dbDriver
from db.models import *
import numpy as np
import math

session = db.dbDriver.dbDriver.DBSession()
my_doc_id = "7a721274-151a-4250-bb01-4a4772557d09"

def getDoc(id):
    return session.query(Document).filter(Document.doc_id == id).one().doc_source

def putMorpho(id,morpho):
    some_doc = session.query(Document).filter(Document.doc_id == id).one()
    some_doc.morpho = morpho
    session.commit()

def morpho(id):
    m = Mystem(disambiguation=False)
    text = getDoc(id)
    new_morpho = m.analyze(text)
    putMorpho(id,new_morpho)

def getMorpho(id):
    return session.query(Document).filter(Document.doc_id == id).one().morpho

def putLemmas(id,lemmas):
    some_doc = session.query(Document).filter(Document.doc_id == id).one()
    some_doc.lemmas = lemmas
    session.commit()

def lemmas_freq(id):
    lemmas = {}
    morpho = getMorpho(id)
    for i in morpho:
        for l in i.get('analysis',[]):
            if l.get('lex',False):
                lemmas[l['lex']] = lemmas.get(l['lex'], 0) + l.get('wt', 1)
    putLemmas(id,lemmas)

morpho(my_doc_id)
lemmas_freq(my_doc_id)

def idf_learn(set_id = ''):
    #get lemmas of all docs in set
    docs = {'id1':{'тип':1,'становиться':3},'id2':{'тип':1,'есть':2}}

    #document frequency - number of documents with lemma
    doc_freq = {}
    #number of lemmas in document
    doc_size = {}
    #index of lemma in overall list
    lemma_index = {}
    #lemma counter in overall list
    lemma_counter = 0
    # document index
    doc_index = {}
    # document counter in overall list
    doc_counter = 0


    for doc_id in docs:
        #initialize doc_size
        doc_size[doc_id] = 0
        # add lemma in overall list by giving index
        doc_index[doc_id] = doc_counter
        doc_counter = doc_counter + 1
        for lemma in docs[doc_id]:
            #increase number of docs with lemma
            doc_freq[lemma] = doc_freq.get(lemma,0) + 1
            #increase number of lemmas in document
            doc_size[doc_id] = doc_size[doc_id] + docs[doc_id][lemma]
            # add lemma in overall list by giving index
            if lemma_index.get(lemma,-1) == -1:
                lemma_index[lemma] = lemma_counter
                lemma_counter = lemma_counter + 1

    #eval idf
    idf = {}
    for lemma in doc_freq:
        idf[lemma] = - math.log(doc_freq[lemma]/num_docs)

    print(lemma_index)
    #objects-features
    main_table = np.zeros((num_docs,lemma_counter))
    doc_counter = 0
    #fill table objects-features
    for doc_lemmas in docs:
        for lemma in doc_lemmas:
            main_table[doc_counter,lemma_index[lemma]] = doc_lemmas[lemma]
        doc_counter = doc_counter + 1

    # eval sum of frequency lemmas in docs
    doc_freq = main_table.sum(axis=1)

    #eval idf
    idf = {}
    for lemma in doc_freq:
        idf[lemma] = - math.log(doc_freq[lemma]/num_docs)

    #eval objects-features: product tf and idf:
    for i_doc in range(num_docs):
        for lemma in lemma_index:
            main_table

    print(main_table)


    print(idf)


lemmas_db = session.query(Document).filter(Document.doc_id == my_doc_id).one().lemmas

print(lemmas_db)

idf_learn()