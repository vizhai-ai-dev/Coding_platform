from sqlalchemy.orm import Session
from .models import Problem, TestCase
import uuid

def create_problem(db: Session, problem_data: dict):
    """Create a new problem in the database"""
    # Generate a UUID for the problem
    problem_id = str(uuid.uuid4())
    
    # Create the problem
    db_problem = Problem(
        id=problem_id,
        title=problem_data.get("title", ""),
        description=problem_data.get("description", ""),
        difficulty=problem_data.get("difficulty", "medium"),
        topics=problem_data.get("topics", []),
        hint=problem_data.get("hint", ""),
        constraints=problem_data.get("constraints", []),
        starter_code=problem_data.get("starterCode", "")
    )
    
    # Add the problem to the database
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    
    # Add test cases if provided
    if "examples" in problem_data:
        for example in problem_data["examples"]:
            test_case = TestCase(
                problem_id=problem_id,
                input_data=example.get("input", ""),
                output_data=example.get("output", ""),
                explanation=example.get("explanation", ""),
                is_hidden=example.get("is_hidden", False)
            )
            db.add(test_case)
        
        db.commit()
    
    return db_problem

def get_problem(db: Session, problem_id: str):
    """Get a problem by ID"""
    return db.query(Problem).filter(Problem.id == problem_id).first()

def get_all_problems(db: Session, skip: int = 0, limit: int = 100):
    """Get all problems with pagination"""
    return db.query(Problem).offset(skip).limit(limit).all()

def get_problems_by_topic(db: Session, topic: str, skip: int = 0, limit: int = 100):
    """Get problems by topic"""
    return db.query(Problem).filter(Problem.topics.contains([topic])).offset(skip).limit(limit).all()

def get_problems_by_difficulty(db: Session, difficulty: str, skip: int = 0, limit: int = 100):
    """Get problems by difficulty"""
    return db.query(Problem).filter(Problem.difficulty == difficulty).offset(skip).limit(limit).all()

def update_problem(db: Session, problem_id: str, problem_data: dict):
    """Update a problem"""
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        return None
    
    # Update problem fields
    for key, value in problem_data.items():
        if key != "examples" and hasattr(db_problem, key):
            setattr(db_problem, key, value)
    
    # Update test cases if provided
    if "examples" in problem_data:
        # Delete existing test cases
        db.query(TestCase).filter(TestCase.problem_id == problem_id).delete()
        
        # Add new test cases
        for example in problem_data["examples"]:
            test_case = TestCase(
                problem_id=problem_id,
                input_data=example.get("input", ""),
                output_data=example.get("output", ""),
                explanation=example.get("explanation", ""),
                is_hidden=example.get("is_hidden", False)
            )
            db.add(test_case)
    
    db.commit()
    db.refresh(db_problem)
    return db_problem

def delete_problem(db: Session, problem_id: str):
    """Delete a problem"""
    db_problem = db.query(Problem).filter(Problem.id == problem_id).first()
    if not db_problem:
        return False
    
    db.delete(db_problem)
    db.commit()
    return True 