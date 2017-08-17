import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Dealership(Base):
    __tablename__ = 'dealership'

    name = Column(String(100), nullable = False)
    location = Column(String(250), nullable = False)
    logo = Column(String(250))
    make = Column(String(50), nullable = False)
    id = Column(Integer, primary_key = True)

class Car(Base):
    __tablename__ = 'car'

    make = Column(String(50), nullable = False)
    model = Column(String(50), nullable = False)
    year = Column(Integer, nullable = False)
    price = Column(Integer, nullable = False)
    image = Column(String(250), nullable = False)
    mileage = Column(Integer)
    id = Column(Integer, primary_key= True)
    dealer_id = Column(Integer, ForeignKey('dealership.id'))
    dealership = relationship(Dealership)

engine = create_engine('sqlite:///dealerinventory.db')

Base.metadata.create_all(engine)
