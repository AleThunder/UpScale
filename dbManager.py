from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///database.db"
Base = declarative_base()


class Source(Base):
    __tablename__ = 'sources'
    id = Column(Integer, primary_key=True, autoincrement=True)  #3
    domain = Column(String, nullable=False)  #velmi.ua
    graphql = Column(Boolean, default=False)  #true
    selectors_id = Column(Integer, ForeignKey('selectors.id'))  #1


class Selector(Base):
    __tablename__ = 'selectors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    element_type = Column(String, nullable=False)  # 'name', 'sku', etc.
    css = Column(String, nullable=False)


class Input(Base):
    __tablename__ = 'inputs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, nullable=False)
    p_id = Column(String, nullable=False)
    brand = Column(String, nullable=False)
    raw_name = Column(String, nullable=True)
    raw_desc = Column(String, nullable=True)
    raw_spec = Column(String, nullable=True)
    status = Column(Boolean, default=False)
    source_id = Column(Integer, ForeignKey('sources.id'), nullable=False)
    result_id = Column(Integer, ForeignKey('results.id'), nullable=True)


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    sku = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    images = Column(Text, nullable=True)  # Consider storing JSON as string
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    short_description = Column(String, nullable=True)
    meta_data = Column(String, nullable=True)
    attributes = Column(String, nullable=True)
    input_id = Column(Integer, ForeignKey('input.id'), nullable=False)

def initialize_database():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

def get_session():
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

def get_selectors_for_domain(session, domain_id):
    selectors = session.query(Selector).filter_by(domain_id=domain_id).all()
    return {selector.element_type: selector.selector for selector in selectors}

def get_image_strategy_for_domain(session, source_id):
    source = session.query(Source).filter_by(id=source_id).first()
    if source and source.graphql:
        return GraphQLImageParsingStrategy()
    else:
        return CssImageParsingStrategy()
    