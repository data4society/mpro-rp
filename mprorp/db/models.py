#models which describing database structure
from sqlalchemy_utils import UUIDType
from sqlalchemy import Column, ForeignKey, String,Text,Integer, TIMESTAMP, Float, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text,functions

from mprorp.db.dbDriver import Base

class SourceType(Base):
    """source types, for example: website, vk, yandex..."""
    __tablename__ = 'sourcetype'

    source_type_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    #human-readable name
    name = Column(String(255), nullable=False)

class Source(Base):
    """sources for crawler and other"""
    __tablename__ = 'source'

    source_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    #url of source
    url = Column(String(1023))
    #reference to source type
    source_type_ref = Column(UUIDType(binary=False), ForeignKey('sourcetype.source_type_id'))#reference to source_type
    sourceType = relationship(SourceType)
    #human-readable name
    name = Column(String(255), nullable=False)
    #period in seconds for parsing. -1 if source is off now
    parse_period = Column(Integer())

class User(Base):
    __tablename__ = 'user'

    user_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)

class Document(Base):
    __tablename__ = 'document'

    doc_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    guid = Column(String(1023))
    source_ref = Column(UUIDType(binary=False), ForeignKey('source.source_id'))
    source = relationship(Source)
    doc_source = Column(Text())
    stripped = Column(Text())
    morpho = Column(JSON())
    lemmas = Column(JSON())
    lemma_count = Column(Integer())
    status = Column(Integer())
    title = Column(String(511))
    #type
    issue_date = Column(TIMESTAMP(),server_default=functions.current_timestamp())
    created = Column(TIMESTAMP())
    validated = Column(TIMESTAMP())
    validated_by_ref = Column(UUIDType(binary=False), ForeignKey('user.user_id'))
    validated_by = relationship(User)
    user = relationship(User)
    meta = Column(JSON())
    tsv = Column(TSVECTOR())


class TrainingSet(Base):
    __tablename__ = 'trainingset'

    set_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    #human-readable name
    set_name = Column(String(511))
    set_created = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    doc_num = Column(Integer())
    doc_refs = Column(ARRAY(UUIDType(binary=False), ForeignKey('document.doc_id')))
    idf = Column(JSON())
    doc_index = Column(JSON())
    lemma_index = Column(JSON())
    object_features = Column(ARRAY(item_type= Float ,dimensions=2))

    #docs = relationship(Document)

class Rubric(Base):
    __tablename__ = 'rubric'

    rubric_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    #name jf rubric
    name = Column(String(255), nullable=False)


class DocumentRubric(Base):
    __tablename__ = 'documentrubric'

    doc_id = Column(UUIDType(binary=False), ForeignKey('document.doc_id'))
    rubric_id = Column(UUIDType(binary=False), ForeignKey('rubric.rubric_id'))
    __table_args__ = (PrimaryKeyConstraint(doc_id, rubric_id),)

class RubricationModel(Base):
    __tablename__ = 'rubricationmodel'

    model_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    rubric_id = Column(UUIDType(binary=False), ForeignKey('rubric.rubric_id'))
    set_id = Column(UUIDType(binary=False), ForeignKey('trainingset.set_id'))
    model = Column(ARRAY(item_type= Float, dimensions=1))
    # Array with length equal number features in training set.
    # Values: -1 - not used, otherwise - feature index in the model
    features = Column(ARRAY(item_type= Integer ,dimensions=1))
    # Number of features in the model oppose number of features in training set, which is bidder (or equal)
    features_num = Column(Integer())
    learning_date = Column(TIMESTAMP(), server_default=functions.current_timestamp())

class RubricationResult(Base):
    __tablename__ = 'rubricationresult'

    model_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"))
    rubric_id = Column(UUIDType(binary=False), ForeignKey('rubric.rubric_id'))
    doc_id = Column(UUIDType(binary=False), ForeignKey('document.doc_id'))
    result = Column(Integer())
    learning_date = Column(TIMESTAMP(), server_default=functions.current_timestamp())
    __table_args__ = (PrimaryKeyConstraint(model_id, rubric_id, doc_id),)