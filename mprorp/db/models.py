#models which describing database structure
from sqlalchemy_utils import UUIDType
from sqlalchemy import Column, ForeignKey, String,Text,Integer, TIMESTAMP, Float
from sqlalchemy.dialects.postgresql import JSON, TSVECTOR, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text

from mprorp.db.dbDriver import Base

#source types, for example: website, vk, yandex...
class SourceType(Base):
    __tablename__ = 'sourcetype'

    source_type_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    name = Column(String(255), nullable=False)

class Source(Base):
    __tablename__ = 'source'

    source_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
    url = Column(String(1023))
    source_type_ref = Column(UUIDType(binary=False), ForeignKey('sourcetype.source_type_id'))#reference to source_type
    sourceType = relationship(SourceType)

class User(Base):
    __tablename__ = 'user'

    user_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)

class Document(Base):
    __tablename__ = 'document'

    doc_id = Column(UUIDType(binary=False), server_default=text("uuid_generate_v4()"), primary_key=True)
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
    issue_date = Column(TIMESTAMP())
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
    doc_ref = Column(ARRAY(UUIDType(binary=False), ForeignKey('document.doc_id')))
    #idf = Column(JSON())
    #doc_index = Column(JSON())
    #lemma_index = Column(JSON())
    #object_features = Column(ARRAY(item_type= Float ,dimensions=2))

    #docs = relationship(Document)
