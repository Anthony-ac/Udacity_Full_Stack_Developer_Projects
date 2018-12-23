from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

# Creates parent class to be inherited by the below functions

Base = declarative_base()

# Creates user table with 4 fields


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

# Creates body_part table with 4 fields


class BodyPart(Base):
    __tablename__ = 'body_part'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

# Converts object to bytes for storage

    @property
    def serialize(self):
        # Converts back and returns the following fields
        return {
            'name': self.name,
            'id': self.id,
        }

# Creates work_out table with 8 fields


class Workout(Base):
    __tablename__ = 'work_out'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    difficulty = Column(String(8))
    body_part_id = Column(Integer, ForeignKey('body_part.id'))
    bodypartrel = relationship(BodyPart)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

# Converts object to bytes for storage

    @property
    def serialize(self):
        # Converts back and returns the following fields
        return {
            'name': self.name,
            'description': self.description,
            'id': self.id,
            'difficulty': self.difficulty,
        }


engine = create_engine('sqlite:///weightlifting.db')

# Creates database weightlifting by passing variable: engine as argument.


Base.metadata.create_all(engine)
