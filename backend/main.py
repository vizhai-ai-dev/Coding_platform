from fastapi import FastAPI, HTTPException, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uuid
import time
import psutil
import json
import random
from llama_cpp import Llama
from sqlalchemy.orm import Session

# Import database modules
from database.db import get_db, engine
from database.models import Base
from database.operations import (
    create_problem, 
    get_problem, 
    get_all_problems, 
    get_problems_by_topic, 
    get_problems_by_difficulty,
    update_problem,
    delete_problem
)

# Initialize the database
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Llama model
try:
    print("Loading Llama model...")
    model = Llama(
        model_path="models/llama-2-7b-chat.gguf",
        n_ctx=2048,
        n_threads=4
    )
    print("Llama model loaded successfully!")
except Exception as e:
    print(f"Error loading Llama model: {e}")
    model = None

class CodeSubmission(BaseModel):
    code: str
    language: str
    problem_id: str

class TestCase(BaseModel):
    input: str
    output: str
    is_hidden: bool = False
    explanation: Optional[str] = None

class Problem(BaseModel):
    id: str
    title: str
    description: str
    examples: List[TestCase]
    constraints: List[str]
    difficulty: str
    topics: Optional[List[str]] = None

class TestResult(BaseModel):
    passed: bool
    input: str
    expected_output: str
    actual_output: str
    execution_time: float
    memory_usage: int

class EvaluationResult(BaseModel):
    test_results: List[TestResult]
    feedback: str
    overall_metrics: Dict[str, Union[int, float]]

@app.get("/api/problems/{problem_id}")
async def get_problem_by_id(problem_id: str, db: Session = Depends(get_db)):
    """Get a specific problem by ID"""
    problem = get_problem(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem.to_dict()

@app.get("/api/problems")
async def list_problems(
    skip: int = 0, 
    limit: int = 100, 
    topic: Optional[str] = None, 
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all problems with optional filtering"""
    if topic:
        problems = get_problems_by_topic(db, topic, skip, limit)
    elif difficulty:
        problems = get_problems_by_difficulty(db, difficulty, skip, limit)
    else:
        problems = get_all_problems(db, skip, limit)
    
    return [problem.to_dict() for problem in problems]

@app.post("/api/problems/generate")
async def generate_problem(
    topic: str = "arrays",
    difficulty: str = "medium",
    db: Session = Depends(get_db)
):
    """Generate a new coding problem using Llama"""
    # Check if model is available
    if model is None:
        raise HTTPException(status_code=500, detail="Llama model not available. Please make sure the model file exists.")
    
    print(f"Generating problem with topic: {topic}, difficulty: {difficulty}")
    
    # Create a prompt for Llama to generate a problem in LeetCode format
    prompt = f"""<s>[INST] You are a coding interview question generator.
I want you to generate a unique coding question about {topic} with {difficulty} difficulty.

The question should be in this exact format:
1. [Title of the Problem]
{difficulty}
Topics: {topic}

Hint:
A concise hint to guide solving strategy

Description:
A thorough and detailed problem statement including:
- Precise definitions of terms and rules
- Detailed explanation of allowed operations
- Clear statement of the problem's goal
- Explicit return conditions and expected format
- Any edge cases to consider
- Minimum length of 4-5 sentences

Examples:
Example 1:
Input: (describe example input in detail)
Output: (expected output with explanation)
Explanation: (thorough explanation of how the output was derived)

Example 2:
Input: (describe another input in detail)
Output: (expected output with explanation)
Explanation: (thorough explanation of how the output was derived)

Constraints:
- List constraint 1 with specific numeric bounds
- List constraint 2 with specific requirements
- Include at least 3 constraints

Python Starter Code:
```python
def solution(input_params):
    # Starter code with proper function signature
    pass
```

Please create a completely original coding question that is directly related to {topic} and appropriate for {difficulty} difficulty level. Make sure all examples are consistent with your description, and that the description is comprehensive and clear. [/INST]</s>
"""
    
    try:
        print("Sending prompt to Llama model...")
        # Generate response using Llama
        response = model.create_completion(
            prompt,
            max_tokens=2048,
            temperature=0.8,
            top_p=0.95,
            top_k=40,
            repeat_penalty=1.1
        )
        
        print("Received response from Llama")
        problem_text = response["choices"][0]["text"]
        print(f"Generated problem text: {problem_text[:100]}...")
        
        # Parse the generated problem
        parsed_problem = parse_llama_problem_response(problem_text, topic)
        
        if parsed_problem:
            print("Successfully parsed problem")
            # Store the problem in the database
            db_problem = create_problem(db, parsed_problem)
            return db_problem.to_dict()
        else:
            print("Failed to parse problem")
            raise HTTPException(status_code=500, detail="Failed to parse generated problem")
    except Exception as e:
        print(f"Error generating problem with Llama: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating problem: {str(e)}")

def execute_code_sandbox(code: str, language: str, test_input: str):
    """
    Execute code with the given input in a sandboxed environment.
    This is a simplified implementation for Python code only.
    In a production environment, use Docker or similar for better isolation.
    """
    import subprocess
    import tempfile
    import os
    
    if language.lower() != "python":
        return {
            "output": f"Language {language} is not supported. Only Python is supported at this time.",
            "execution_time": 0,
            "memory_usage": 0
        }
    
    try:
        # Create a temporary file to store the code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            # Write the code to the file
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name
        
        # Set up command to run with input piped in
        cmd = ['python3', temp_file_path]
        
        # Start measuring time and memory
        start_time = time.time()
        current_process = psutil.Process()
        start_memory = current_process.memory_info().rss
        
        # Run the process with a timeout to prevent infinite loops
        try:
            completed_process = subprocess.run(
                cmd,
                input=test_input.encode('utf-8'),
                capture_output=True,
                timeout=5  # 5 second timeout
            )
            
            # Measure time and memory after execution
            end_time = time.time()
            end_memory = current_process.memory_info().rss
            
            output = completed_process.stdout.decode('utf-8')
            error = completed_process.stderr.decode('utf-8')
            
            # If there was an error, return it
            if error:
                return {
                    "output": f"Error: {error}",
                    "execution_time": 0,
                    "memory_usage": 0
                }
            
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            memory_used = (end_memory - start_memory) / 1024  # Convert to KB
            
            return {
                "output": output.strip(),
                "execution_time": execution_time,
                "memory_usage": memory_used
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "Execution timed out (limit: 5 seconds)",
                "execution_time": 5000,  # 5 seconds in ms
                "memory_usage": 0
            }
    except Exception as e:
        return {
            "output": f"Error executing code: {str(e)}",
            "execution_time": 0,
            "memory_usage": 0
        }
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.post("/api/code/run")
async def run_code(submission: CodeSubmission, db: Session = Depends(get_db)):
    """Run the submitted code against test cases"""
    try:
        # Get the problem from the database
        problem = get_problem(db, submission.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Get all test cases for testing
        if not problem.examples:
            raise HTTPException(status_code=400, detail="No test cases available")
        
        # Prepare results for all test cases
        test_results = []
        total_time = 0
        total_memory = 0
        passed_count = 0
        
        # Process all test cases
        for test_case in problem.examples:
            # Execute code in sandbox
            result = execute_code_sandbox(
                submission.code, 
                submission.language, 
                test_case.input_data
            )
            
            # Get actual output
            actual_output = result["output"].strip()
            expected_output = test_case.output_data.strip()
            
            # Compare outputs (ignoring whitespace)
            passed = actual_output == expected_output
            if passed:
                passed_count += 1
            
            execution_time = result["execution_time"]
            memory_used = result["memory_usage"]
            
            total_time += execution_time
            total_memory += memory_used
            
            # Add result to list
            test_results.append({
                "passed": passed,
                "input": test_case.input_data,
                "expected_output": expected_output,
                "actual_output": actual_output,
                "execution_time": execution_time,
                "memory_usage": memory_used,
                "is_hidden": test_case.is_hidden
            })
        
        # Calculate overall metrics
        total_tests = len(test_results)
        
        return {
            "test_results": test_results,
            "overall_metrics": {
                "total_tests": total_tests,
                "passed_tests": passed_count,
                "success_rate": passed_count / total_tests if total_tests > 0 else 0,
                "average_time": total_time / total_tests if total_tests > 0 else 0,
                "average_memory": total_memory / total_tests if total_tests > 0 else 0,
                "status": "Accepted" if passed_count == total_tests else "Wrong Answer",
            },
            "output": test_results[0]["actual_output"] if test_results else ""
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {
            "test_results": [],
            "overall_metrics": {
                "total_tests": 0,
                "passed_tests": 0,
                "success_rate": 0,
                "average_time": 0,
                "average_memory": 0,
                "status": "Error"
            },
            "output": f"Error: {str(e)}"
        }

def parse_llama_problem_response(text, topic="arrays"):
    """Parse the Llama generated response into a structured problem"""
    try:
        print(f"Parsing response text length: {len(text)}")
        print(f"First 300 chars: {text[:300]}")
        lines = text.split('\n')
        problem = {}
        
        # Initialize with default values
        problem["id"] = str(uuid.uuid4())
        problem["title"] = "Untitled Problem"
        problem["difficulty"] = "medium"
        problem["description"] = "No description provided."
        problem["examples"] = []
        problem["constraints"] = ["No constraints provided"]
        problem["topics"] = [topic.capitalize()]
        problem["hint"] = ""
        problem["starterCode"] = ""
        
        current_section = None
        current_example = {}
        starter_code_lines = []
        collect_starter_code = False
        description_text = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            print(f"Processing line {i}: {line[:50]}...")
                
            # Parse title and difficulty
            if ". " in line and not current_section:
                parts = line.split(". ", 1)
                if len(parts) == 2:
                    problem["title"] = parts[1]
                    print(f"Found title: {problem['title']}")
                    continue
            
            # Also handle format "1. Title"
            if line.startswith("1. ") and not current_section:
                problem["title"] = line.replace("1. ", "").strip()
                print(f"Found title: {problem['title']}")
                continue
            
            # Parse difficulty
            if line.lower() in ["easy", "medium", "hard"]:
                problem["difficulty"] = line.lower()
                print(f"Found difficulty: {problem['difficulty']}")
                continue
                
            # Parse topics
            if line.startswith("Topics:") or line.startswith("Topic:"):
                topics = line.replace("Topics:", "").replace("Topic:", "").strip()
                problem["topics"] = [t.strip() for t in topics.split(",")]
                print(f"Found topics: {problem['topics']}")
                continue
                
            # Parse hint
            if line.startswith("Hint:"):
                problem["hint"] = line.replace("Hint:", "").strip()
                print(f"Found hint: {problem['hint']}")
                continue
                
            # Parse description
            if line == "Description:":
                current_section = "description"
                description_text = []
                print("Found description section")
                continue
                
            # Parse examples
            if line.startswith("Example"):
                if current_section == "description":
                    problem["description"] = "\n".join(description_text).strip()
                    print(f"Set description with {len(description_text)} lines")
                
                if current_example and "input" in current_example and "output" in current_example:
                    problem["examples"].append(current_example)
                    print(f"Added example: {current_example}")
                current_example = {}
                current_section = "example"
                print("Found example section")
                continue
                
            # Parse constraints
            if line == "Constraints:":
                if current_section == "description":
                    problem["description"] = "\n".join(description_text).strip()
                    print(f"Set description with {len(description_text)} lines")
                
                current_section = "constraints"
                problem["constraints"] = []
                print("Found constraints section")
                continue
                
            # Look for Python Starter Code
            if line == "Python Starter Code:" or line.startswith("```python"):
                if current_section == "description":
                    problem["description"] = "\n".join(description_text).strip()
                    print(f"Set description with {len(description_text)} lines")
                
                current_section = "starter_code"
                collect_starter_code = True
                starter_code_lines = []
                print("Found starter code section")
                continue
                
            if line == "```" and collect_starter_code:
                collect_starter_code = False
                continue
                
            # Handle content based on current section
            if current_section == "description":
                description_text.append(line)
            elif current_section == "example":
                if line.startswith("Input:"):
                    current_example["input"] = line.replace("Input:", "").strip()
                elif line.startswith("Output:"):
                    current_example["output"] = line.replace("Output:", "").strip()
                elif line.startswith("Explanation:"):
                    current_example["explanation"] = line.replace("Explanation:", "").strip()
            elif current_section == "constraints":
                if line.startswith("-") or line.startswith("*") or line.startswith("•"):
                    problem["constraints"].append(line.lstrip("-*• ").strip())
                else:
                    problem["constraints"].append(line.strip())
            elif current_section == "starter_code" and collect_starter_code:
                if not line.startswith("```"):
                    starter_code_lines.append(line)
            # Also detect if any line is starter code (def or class)
            elif line.startswith("def ") or line.startswith("class "):
                if current_section != "starter_code":
                    current_section = "starter_code"
                    starter_code_lines = [line]
                else:
                    starter_code_lines.append(line)
        
        # Finalize description if we're still in that section
        if current_section == "description":
            problem["description"] = "\n".join(description_text).strip()
            print(f"Set description with {len(description_text)} lines at the end")
        
        # Add the last example if exists
        if current_example and "input" in current_example and "output" in current_example:
            problem["examples"].append(current_example)
            print(f"Added final example: {current_example}")
            
        # Ensure we have at least one example
        if not problem["examples"]:
            problem["examples"].append({
                "input": "sample input",
                "output": "sample output"
            })
            print("Added default example")
            
        # Set the starter code
        if starter_code_lines:
            problem["starterCode"] = "\n".join(starter_code_lines)
            print(f"Set starter code with {len(starter_code_lines)} lines")
        else:
            # Create a generic starter code if none was generated
            function_name = "solve_problem"
            if problem["title"]:
                function_name = problem["title"].lower().replace(" ", "_").replace("-", "_")
                function_name = ''.join(c for c in function_name if c.isalnum() or c == '_')
            
            problem["starterCode"] = f"""def {function_name}(input_data):
    # TODO: Implement your solution here
    pass"""
            print(f"Created default starter code with function name: {function_name}")
        
        print(f"Final parsed problem: {problem['title']}")
        print(f"Description length: {len(problem['description'])}")
        print(f"Description preview: {problem['description'][:100]}...")
        return problem
                
    except Exception as e:
        print(f"Error parsing problem: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 