from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Problem(Base):
    __tablename__ = "problems"
    
    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(String(20), nullable=False)
    topics = Column(JSON, nullable=True)
    hint = Column(Text, nullable=True)
    constraints = Column(JSON, nullable=True)
    starter_code = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    examples = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "difficulty": self.difficulty,
            "topics": self.topics,
            "hint": self.hint,
            "constraints": self.constraints,
            "starterCode": self.starter_code,
            "examples": [example.to_dict() for example in self.examples]
        }

class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    problem_id = Column(String(36), ForeignKey("problems.id"), nullable=False)
    input_data = Column(Text, nullable=False)
    output_data = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    is_hidden = Column(Boolean, default=False)
    
    # Relationships
    problem = relationship("Problem", back_populates="examples")
    
    def to_dict(self):
        return {
            "input": self.input_data,
            "output": self.output_data,
            "explanation": self.explanation,
            "is_hidden": self.is_hidden
        } 