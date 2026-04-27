"""
Database models for the Mergington High School Activities API
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# Association table for many-to-many relationship between students and activities
student_activity_association = Table(
    'student_activity',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activity.id'), primary_key=True),
    Column('enrolled_at', DateTime, default=datetime.utcnow)
)


class Activity(Base):
    """Model for extracurricular activities"""
    __tablename__ = "activity"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text)
    schedule = Column(String)
    max_participants = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to students
    participants = relationship(
        "Student",
        secondary=student_activity_association,
        back_populates="activities"
    )
    
    def __repr__(self):
        return f"<Activity(name='{self.name}', max_participants={self.max_participants})>"


class Student(Base):
    """Model for student users"""
    __tablename__ = "student"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to activities
    activities = relationship(
        "Activity",
        secondary=student_activity_association,
        back_populates="participants"
    )
    
    def __repr__(self):
        return f"<Student(email='{self.email}', name='{self.name}')>"
