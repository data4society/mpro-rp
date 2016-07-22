"""models which describing database structure"""
from sqlalchemy_utils import UUIDType
from sqlalchemy import Column, ForeignKey, String, Text, Integer, TIMESTAMP, Float, PrimaryKeyConstraint, Boolean
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text, functions

from mprorp.db.dbDriver import Base


class SourceType(Base):
    """source types, for example: website, vk, yandex..."""
    __tablename__ = 'sourcetypes'

    source_type_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # human-readable name
    name = Column(String(255), nullable=False)


class Source(Base):
    """sources for crawler and other"""
    __tablename__ = 'sources'

    source_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # url of source
    url = Column(String(1023))
    # reference to source type
    source_type_id = Column(UUIDType(binary=False), ForeignKey('sourcetypes.source_type_id'))
    sourceType = relationship(SourceType)
    # human-readable name
    name = Column(String(255), nullable=False)
    # period in seconds for parsing. -1 if source is off now
    parse_period = Column(Integer())
    # time for next crawling the source
    next_crawling_time = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # Is it waits or in work now
    wait = Column(Boolean(), server_default="False")


class User(Base):
    __tablename__ = 'users'

    user_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # user email
    email = Column(String(255), unique=True)
    # user name
    name = Column(String(255))
    # when user was created
    created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # key to login
    login_key = Column(String(40), unique=True)
    # encrypted password
    password = Column(String(255))


class Document(Base):
    """main document object"""
    __tablename__ = 'documents'

    doc_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # unic identificator
    guid = Column(String(1023), unique=True)
    # reference to source
    source_id = Column(UUIDType(binary=False), ForeignKey('sources.source_id'))
    source = relationship(Source)
    # document source (for example HTML of full text for site pages)
    doc_source = Column(Text())
    # text for analyzator - without HTML tags
    stripped = Column(Text())
    # result of morphologia
    morpho = Column(JSONB())
    # result of lemmification
    lemmas = Column(JSONB())
    # number of lemmas
    lemma_count = Column(Integer())
    # status of this doc: 0 - initial isert, 1 - complete crawler work, 2 - morho analysis is done,
    #                     3 - lemmas frequency is computed, 4 - rubrics is marked...
    status = Column(Integer())
    # title of document
    title = Column(String(511))
    # timestamp for material publishing date
    published_date = Column(TIMESTAMP())
    # timestamp for adding to database
    created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # document metadata
    meta = Column(JSONB())
    # ids of referenced
    rubric_ids = Column(ARRAY(UUIDType(binary=False), ForeignKey('rubrics.rubric_id')))
    # model type: vk/article
    type = Column(String(255), nullable=False)
    # markup with entities
    markup = Column(JSONB())
    # entities of markup
    entity_ids = Column(ARRAY(UUIDType(binary=False), ForeignKey('entities.entity_id')))


class Record(Base):
    __tablename__ = 'records'

    # document id
    document_id = Column(UUIDType(binary=False),
                         server_default=text("uuid_generate_v4()"), primary_key=True, unique=True)
    # unic identificator
    guid = Column(String(255), unique=True)
    # document title
    title = Column(String(255))
    # document schema
    schema_name = Column(String(40))
    # schema version
    schema_version = Column(String(40))
    # document version
    version = Column(Integer())
    # date of original document publishing 
    published_date = Column(TIMESTAMP())
    # date of document creation
    created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # date of last edition
    edited = Column(TIMESTAMP())
    # last editor, e.g. user who made latest change
    edited_by = Column(UUIDType(binary=False), ForeignKey('users.user_id'))
    # whatever this document training set
    training = Column(Boolean())
    # document rubrics
    rubrics = Column(ARRAY(UUIDType(binary=False), ForeignKey('rubrics.rubric_id')))
    # refrence to source document table record
    source = Column(UUIDType(binary=False), ForeignKey('documents.doc_id'))
    # substnace document
    content = Column(JSONB())
    # node with metadata
    meta = Column(JSONB())
    # some data coming from every change (WIP)
    info = Column(JSONB())
    # vector with the lexemes for fulltext searching
    tsv = Column(TSVECTOR())


class TrainingSet(Base):
    """sets of document for train and test models"""
    __tablename__ = 'trainingsets'

    set_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # human-readable name
    name = Column(String(511))
    # creating date
    set_created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # number of documents in set
    doc_num = Column(Integer())
    # id of all documents in set
    doc_ids = Column(ARRAY(UUIDType(binary=False), ForeignKey('documents.doc_id')))
    # inverse doument frequency for all lemmas of set
    idf = Column(JSONB())
    # index of documents in object_features: key - doc_id, value - row number
    doc_index = Column(JSONB())
    # index of lemmas in object_features: key - lemma, value - column number
    lemma_index = Column(JSONB())
    # object-features matrix
    object_features = Column(ARRAY(item_type=Float, dimensions=2))


class Rubric(Base):
    """rubrics for document rubrication"""
    __tablename__ = 'rubrics'

    rubric_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # name jf rubric
    name = Column(String(255), nullable=False)
    # creation date
    created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # parent reference
    parent_id = Column(UUIDType(binary=False), ForeignKey('rubrics.rubric_id'))
    # rubric description
    description = Column(Text())


class DocumentRubric(Base):
    """result of rubrication by users"""
    __tablename__ = 'documentrubrics'

    # document identificator
    doc_id = Column(UUIDType(binary=False), ForeignKey('documents.doc_id'))
    # document identifier
    rubric_id = Column(UUIDType(binary=False), ForeignKey('rubrics.rubric_id'))
    # rubric identifier
    __table_args__ = (PrimaryKeyConstraint(doc_id, rubric_id),)


class RubricationModel(Base):
    """models for rubrication"""
    __tablename__ = 'rubricationmodels'

    model_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # Model was used for rubric
    rubric_id = Column(UUIDType(binary=False), ForeignKey('rubrics.rubric_id'))
    # Training set used for model
    set_id = Column(UUIDType(binary=False), ForeignKey('trainingsets.set_id'))
    # model = vector
    model = Column(ARRAY(item_type=Float, dimensions=1))
    # Array with length equal number features in training set.
    # Values: -1 - not used, otherwise - feature index in the model
    features = Column(ARRAY(item_type=Integer, dimensions=1))
    # Number of features in the model oppose number of features in training set, which is bidder (or equal)
    features_num = Column(Integer())
    # Date of model learning
    learning_date = Column(TIMESTAMP(), server_default=functions.current_timestamp())


class RubricationResult(Base):
    """result of rubrication  (rubric_id) for document (doc_id) was compute with model (model_id)"""
    __tablename__ = 'rubricationresults'
    # model
    model_id = Column(UUIDType(binary=False), ForeignKey('rubricationmodels.model_id'))
    # rubric
    rubric_id = Column(UUIDType(binary=False), ForeignKey('rubrics.rubric_id'))
    # document
    doc_id = Column(UUIDType(binary=False), ForeignKey('documents.doc_id'))
    # 1 - document associated with rubric, 0 - document not associated with rubric
    result = Column(Integer())
    # Probability
    probability = Column(Float())
    # date of compute
    learning_date = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    __table_args__ = (PrimaryKeyConstraint(model_id, rubric_id, doc_id),)


class ObjectFeatures(Base):
    """object-features matrix for training set of documents. One record is one  row corresponding document doc_id"""
    __tablename__ = 'objectfeatures'

    # Training set id
    set_id = Column(UUIDType(binary=False), ForeignKey('trainingsets.set_id'))
    # Document id
    doc_id = Column(UUIDType(binary=False), ForeignKey('documents.doc_id'))
    # Features vector - compressed or no
    features = Column(ARRAY(item_type=Float, dimensions=1))
    # Is features compressed
    compressed = Column(Boolean())
    # Idexes of non-zero values (filled if compressed)
    indexes = Column(ARRAY(item_type=Integer, dimensions=1))

    __table_args__ = (PrimaryKeyConstraint(set_id, doc_id),)


class EntityClass(Base):
    """Classes of ontology"""
    __tablename__ = 'entity_classes'

    class_id = Column(String(40), primary_key=True)
    name = Column(String(255))


class Entity(Base):
    """ examples of class of ontology """
    __tablename__ = 'entities'

    entity_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # name of entity
    name = Column(String(255))
    # date of entity creation
    created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # date of last edition
    edited = Column(TIMESTAMP())
    # user, creator of entity record
    author = Column(UUIDType(binary=False), ForeignKey('users.user_id'))
    # class of entity - entityclasses
    entity_class = Column(String(40))
    # entity data
    data = Column(JSONB())
    # tsv vector for indexing
    tsv = Column(TSVECTOR())


class Markup(Base):
    """ markups for document: symbol coordinates"""
    __tablename__ = 'markups'

    markup_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    # document
    document = Column(UUIDType(binary=False), ForeignKey('documents.doc_id'))
    name = Column(String(255))
    # data
    data = Column(JSONB())
    # class of ontology
    entity_classes = Column(ARRAY(String(40), dimensions=1))
    # type: "10", "20", ...
    type = Column(String(255))


class Reference(Base):
    """symbol coordinates of spans linked with entity class and, possible, entity"""
    __tablename__ = 'references'

    reference_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    markup = Column(UUIDType(binary=False), ForeignKey('markups.markup_id'))
    markup_rel = relationship(Markup)
    # class of ontology
    entity_class = Column(String(40))
    # example of class of ontology
    entity = Column(UUIDType(binary=False), ForeignKey('entities.entity_id'))
    # symbol coordinates
    start_offset = Column(Integer())
    end_offset = Column(Integer())
    length_offset = Column(Integer())
    # ???
    outer_id = Column(Integer())


class Mention(Base):
    __tablename__ = 'mentions'

    mention_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    markup = Column(UUIDType(binary=False), ForeignKey('markups.markup_id'))
    entity_class = Column(String(40))
    reference_ids = Column(ARRAY(UUIDType(binary=False), ForeignKey('references.reference_id')))
    outer_id = Column(Integer())


class Change(Base):
    __tablename__ = 'changes'

    # id of document
    document_id = Column(UUIDType(binary=False), ForeignKey('records.document_id'))
    # version of document
    version = Column(Integer())
    # change data
    data = Column(JSONB())
    # date of change creation
    created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    # user who made a change
    owner = Column(UUIDType(binary=False), ForeignKey('users.user_id'))

    __table_args__ = (PrimaryKeyConstraint(document_id, version),)


class SessionData(Base):
    __tablename__ = 'sessions'

    # session token
    session_token = Column(UUIDType(binary=False),
                           server_default=text("uuid_generate_v4()"), primary_key=True, unique=True)
    # user who owns a session
    owner = Column(UUIDType(binary=False), ForeignKey('users.user_id'))
    # date of session creation
    created = Column(TIMESTAMP(), server_default=functions.current_timestamp())


class Embedding(Base):
    """ embedding for words of language"""
    __tablename__ = 'embeddings'

    emb_id = Column(String(40), primary_key=True)
    # name of Embeddings: russian news, russian wikipedia
    name = Column(String(255))


class WordEmbedding(Base):
    """embedding vector for lemma"""
    __tablename__ = 'word_embeddings'

    lemma = Column(String(100))
    # Embedding:
    embedding = Column(String(40))
    # vector for lemma
    vector = Column(ARRAY(item_type=Float, dimensions=1))
    __table_args__ = (PrimaryKeyConstraint(lemma, embedding),)


class Gazetteer(Base):
    """gazetteer"""
    __tablename__ = 'gazetteers'

    gaz_id = Column(String(40), primary_key=True)
    # name of gazetteer
    name = Column(String(255))
    # words in gazetteer
    lemmas = Column(ARRAY(item_type=String, dimensions=1))


class TomitaResult(Base):
    """tomita result for document: symbol coordinates"""
    __tablename__ = 'tomita_results'

    doc_id = Column(UUIDType(binary=False), ForeignKey('documents.doc_id'))
    # grammar identifier
    grammar = Column(String(40))
    # symbol coordinates of tomita results
    result = Column(JSONB())

    __table_args__ = (PrimaryKeyConstraint(doc_id, grammar),)


class NERFeature(Base):
    """features, using for NER: lemmas coordinates"""
    __tablename__ = 'ner_features'

    doc_id = Column(UUIDType(binary=False), ForeignKey('documents.doc_id'))
    # 1 - embedding, 2 - gazetteer, 3 - tomita fact, 4 - syntactic feature: case, 5 - syntactic feature: plural/singular
    feature_type = Column(Integer())
    # fact_id, gaz_id, emb_id, ...
    feature = Column(String(40))
    # lemma coordinates
    word_index = Column(Integer)
    sentence_index = Column(Integer)
    # value = Column(ARRAY(item_type=Float, dimensions=1))
    value = Column(JSONB())

    __table_args__ = (PrimaryKeyConstraint(doc_id, feature_type, feature, word_index, sentence_index),)


# NO USED


class TomitaGrammar(Base):
    __tablename__ = 'tomita_grammars'

    gram_id = Column(String(40), primary_key=True)
    name = Column(String(255))


class TomitaFact(Base):
    __tablename__ = 'tomita_facts'

    fact_id = Column(String(40), primary_key=True)
    # name of fact
    name = Column(String(255))
    # grammar
    grammar = Column(String(40))


class NERModel(Base):
    __tablename__ = 'ner_models'

    ner_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    embedding = Column(String(40))
    gazetteers = Column(ARRAY(String(40)))
    tomita_facts = Column(ARRAY(String(40)))
    morpho_features = Column(ARRAY(String(40)))
    hyper_parameters = Column(JSONB())
    parameters = Column(JSONB())


