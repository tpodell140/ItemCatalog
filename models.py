import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(250), nullable = False)
    email = Column(String(250), nullable = False)
    picture = Column(String(250))
    id = Column(Integer, primary_key = True)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name'      : self.name,
            'email'     : self.email,
            'picture'   : self.picture,
            'id'        : self.id
        }

class Dealership(Base):
    __tablename__ = 'dealership'

    name = Column(String(100), nullable = False)
    location = Column(String(250), nullable = False)
    logo = Column(String(250))
    make = Column(String(50), nullable = False)
    id = Column(Integer, primary_key = True)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name'      : self.name,
            'location'  : self.location,
            'logo'      : self.logo,
            'make'      : self.make,
            'id'        : self.id
        }

class Car(Base):
    __tablename__ = 'car'

    make = Column(String(50), nullable = False)
    model = Column(String(50), nullable = False)
    year = Column(Integer, nullable = False)
    status = Column(String(10), nullable = False)
    price = Column(Integer, nullable = False)
    image = Column(String(250), nullable = False)
    mileage = Column(Integer)
    color = Column(String(50), nullable = False)
    id = Column(Integer, primary_key= True)
    dealer_id = Column(Integer, ForeignKey('dealership.id'))
    dealership = relationship(Dealership)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'make'      : self.make,
            'model'     : self.model,
            'year'      : self.year,
            'status'    : self.status,
            'price'     : self.price,
            'image'     : self.image,
            'mileage'   : self.mileage,
            'color'     : self.color,
            'id'        : self.id,
            'dealer_id' : self.dealer_id
        }

engine = create_engine('sqlite:///dealerinventory.db')

Base.metadata.create_all(engine)
