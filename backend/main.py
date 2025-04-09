from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Union
import uuid
import time
import psutil
import json
import random
from llama_cpp import Llama

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Llama model
try:
    model = Llama(
        model_path="models/llama-2-7b-chat.gguf",
        n_ctx=2048,
        n_threads=4
    )
except Exception as e:
    print(f"Error loading Llama model: {e}")
    print("Using mock responses instead")
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
    starter_code: Dict[str, str]
    difficulty: str
    topics: Optional[List[str]] = None
    companies: Optional[List[str]] = None

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

class TopicRequest(BaseModel):
    topic: str = "arrays"
    difficulty: str = "medium"

# In-memory storage for problems
problems = {
    "3375": {
        "id": "3375",
        "title": "Minimum Operations to Make Array Values Equal to K",
        "description": "You are given an integer array nums and an integer k. An integer h is called valid for the current array if all values in the array are strictly greater than h. You are allowed to perform the following operation on nums: Select an integer h that is valid for the current array. For each index i where nums[i] > h, set nums[i] to h. Return the minimum number of operations required to make every element in nums equal to k. If it is impossible to make all elements equal to k, return -1.",
        "examples": [
            {
                "input": "nums = [5,2,5,4,5], k = 2",
                "output": "2",
                "explanation": "The operations can be performed in order using valid integers 4 and then 2."
            },
            {
                "input": "nums = [2,1,2], k = 2",
                "output": "-1",
                "explanation": "It is impossible to make all the values equal to 2."
            }
        ],
        "constraints": [
            "2 <= nums.length <= 10^4",
            "1 <= nums[i] <= 10^9",
            "1 <= k <= 10^9"
        ],
        "starter_code": {
            "cpp": "class Solution {\npublic:\n    int minOperations(vector<int>& nums, int k) {\n        // Write your code here\n        return 0;\n    }\n};",
            "java": "class Solution {\n    public int minOperations(int[] nums, int k) {\n        // Write your code here\n        return 0;\n    }\n}",
            "python": "class Solution:\n    def minOperations(self, nums: List[int], k: int) -> int:\n        # Write your code here\n        pass",
            "c": "int minOperations(int* nums, int numsSize, int k) {\n    // Write your code here\n    return 0;\n}"
        },
        "difficulty": "easy",
        "topics": ["Arrays", "Greedy"],
        "companies": ["Google", "Amazon"]
    }
}

@app.get("/api/problems/{problem_id}")
async def get_problem(problem_id: str):
    """Get a specific problem by ID"""
    if problem_id not in problems:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problems[problem_id]

@app.post("/api/problems/generate")
async def generate_problem(
    topic: str = "arrays",
    difficulty: str = "medium"
):
    """Generate a new coding problem using Llama 3"""
    # Create a prompt for Llama to generate a problem in LeetCode format
    prompt = f"""
    Generate a {difficulty} level coding problem about {topic} in LeetCode format.
    
    The problem should include:
    1. A problem number (e.g., 3375)
    2. A clear title
    3. A detailed description with the problem statement
    4. 2-3 examples with inputs, outputs, and explanations
    5. Constraints on input sizes and values
    6. Starter code for C++, Java, Python, and C
    
    Follow this format:
    
    Problem ID: [number]
    Title: [title]
    Difficulty: {difficulty}
    
    Description:
    [detailed problem description]
    
    Examples:
    Example 1:
    Input: [format exactly as it would appear in LeetCode]
    Output: [expected output]
    Explanation: [explain the solution]
    
    Example 2:
    Input: [another example input]
    Output: [expected output]
    Explanation: [explanation]
    
    Constraints:
    - [constraint 1]
    - [constraint 2]
    - [constraint 3]
    
    Provide starter code templates for the following languages:
    
    C++:
    ```cpp
    [starter code]
    ```
    
    Java:
    ```java
    [starter code]
    ```
    
    Python:
    ```python
    [starter code]
    ```
    
    C:
    ```c
    [starter code]
    ```
    """
    
    # Generate response using Llama if available, otherwise use mock data
    if model:
        try:
            response = model.create_completion(
                prompt,
                max_tokens=2048,
                temperature=0.7,
                stop=["```", "Problem ID:"]
            )
            # In a real implementation, you would parse the response
            problem_text = response["choices"][0]["text"]
            
            # Parse the generated problem (simplified)
            # In a real app, you'd implement more robust parsing
            parsed_problem = parse_llama_problem_response(problem_text)
            
            if parsed_problem:
                problem_id = str(uuid.uuid4())
                problems[problem_id] = parsed_problem
                problems[problem_id]["id"] = problem_id
                
                # Generate additional test cases with Llama
                test_cases_prompt = f"""
                Generate 10 additional test cases for the following coding problem:
                
                Problem: {parsed_problem['title']}
                Description: {parsed_problem['description']}
                
                Current examples:
                {json.dumps(parsed_problem['examples'], indent=2)}
                
                Generate 10 more test cases in the same format. Each test case should have:
                1. Input in the exact same format as the examples
                2. Expected output
                3. Brief explanation if necessary
                
                Make sure the test cases cover edge cases, large inputs, and special scenarios.
                """
                
                try:
                    test_cases_response = model.create_completion(
                        test_cases_prompt,
                        max_tokens=2048,
                        temperature=0.7
                    )
                    test_cases_text = test_cases_response["choices"][0]["text"]
                    
                    # Parse the additional test cases
                    additional_test_cases = parse_llama_test_cases(test_cases_text, parsed_problem['examples'][0] if parsed_problem['examples'] else None)
                    
                    # Add hidden test cases
                    for tc in additional_test_cases:
                        tc["is_hidden"] = True
                        parsed_problem['examples'].append(tc)
                        
                    # Ensure we have at least 10 test cases total
                    while len(parsed_problem['examples']) < 10:
                        new_test = generate_hidden_test_case(parsed_problem)
                        new_test["is_hidden"] = True
                        parsed_problem['examples'].append(new_test)
                        
                except Exception as e:
                    print(f"Error generating additional test cases with Llama: {e}")
                    # Add some generated test cases as fallback
                    for _ in range(8):  # Add 8 more to the existing 2
                        new_test = generate_hidden_test_case(parsed_problem)
                        new_test["is_hidden"] = True
                        parsed_problem['examples'].append(new_test)
                
                return problems[problem_id]
        except Exception as e:
            print(f"Error generating problem with Llama: {e}")
    
    # Fallback to pre-defined problems if Llama fails or is not available
    problem_id = str(uuid.uuid4())
    
    # Select problem based on topic and difficulty
    if topic.lower() == "arrays" and difficulty.lower() == "easy":
        problems[problem_id] = get_array_easy_problem(problem_id)
    elif topic.lower() == "arrays" and difficulty.lower() == "medium":
        problems[problem_id] = get_array_medium_problem(problem_id)
    elif topic.lower() == "dynamic programming" or topic.lower() == "dp":
        problems[problem_id] = get_dp_problem(problem_id)
    else:
        # Default problem
        problems[problem_id] = get_array_medium_problem(problem_id)
    
    # Add 8 more test cases to reach 10 total
    for _ in range(8):
        new_test = generate_hidden_test_case(problems[problem_id])
        new_test["is_hidden"] = True
        problems[problem_id]["examples"].append(new_test)
    
    return problems[problem_id]

def parse_llama_problem_response(text):
    """Parse the Llama generated response into a structured problem"""
    try:
        lines = text.split('\n')
        problem = {}
        
        # Find key sections using simple parsing
        # This is a simplified version; a real implementation would be more robust
        title_line = next((l for l in lines if l.startswith("Title:")), "")
        difficulty_line = next((l for l in lines if l.startswith("Difficulty:")), "")
        
        # Parse title and difficulty
        problem["title"] = title_line.replace("Title:", "").strip() if title_line else "Untitled Problem"
        problem["difficulty"] = difficulty_line.replace("Difficulty:", "").strip().lower() if difficulty_line else "medium"
        
        # Find description section
        description_start = None
        examples_start = None
        constraints_start = None
        
        for i, line in enumerate(lines):
            if line.strip() == "Description:" or line.strip().startswith("Description:"):
                description_start = i + 1
            elif line.strip() == "Examples:" or line.strip().startswith("Examples:") or line.strip().startswith("Example 1:"):
                examples_start = i
                if description_start:
                    break
        
        # Find constraints section
        for i, line in enumerate(lines):
            if line.strip() == "Constraints:" or line.strip().startswith("Constraints:"):
                constraints_start = i + 1
                break
        
        # Extract description
        if description_start and examples_start:
            problem["description"] = "\n".join(lines[description_start:examples_start]).strip()
        else:
            problem["description"] = "No description provided."
        
        # Extract examples
        examples = []
        if examples_start and constraints_start:
            example_text = "\n".join(lines[examples_start:constraints_start])
            
            # Split by "Example" markers
            example_sections = []
            current_section = []
            
            for line in lines[examples_start:constraints_start]:
                if line.strip().startswith("Example") and ":" in line and current_section:
                    example_sections.append(current_section)
                    current_section = [line]
                else:
                    current_section.append(line)
            
            if current_section:
                example_sections.append(current_section)
            
            # Process each example
            for section in example_sections:
                if not section:
                    continue
                
                example = {}
                input_line = next((l for l in section if "Input:" in l), "")
                output_line = next((l for l in section if "Output:" in l), "")
                explanation_lines = []
                
                explanation_start = False
                for line in section:
                    if "Explanation:" in line:
                        explanation_start = True
                        explanation_lines.append(line.replace("Explanation:", "").strip())
                    elif explanation_start:
                        explanation_lines.append(line.strip())
                
                example["input"] = input_line.replace("Input:", "").strip() if input_line else ""
                example["output"] = output_line.replace("Output:", "").strip() if output_line else ""
                
                if explanation_lines:
                    example["explanation"] = " ".join(explanation_lines).strip()
                
                if example["input"] or example["output"]:
                    examples.append(example)
        
        problem["examples"] = examples if examples else [{"input": "sample input", "output": "sample output"}]
        
        # Extract constraints
        constraints = []
        if constraints_start:
            for line in lines[constraints_start:]:
                if line.strip() and line.strip().startswith("-"):
                    constraints.append(line.strip().replace("-", "", 1).strip())
                elif line.strip() and not line.strip().startswith("```"):
                    # Stop if we hit code blocks or other sections
                    if "```" in line or "C++:" in line or "Java:" in line:
                        break
                    constraints.append(line.strip())
        
        problem["constraints"] = constraints if constraints else ["No constraints provided"]
        
        # Extract starter code
        problem["starter_code"] = {}
        
        # Find code blocks for each language
        cpp_code = extract_code_block(text, "cpp")
        java_code = extract_code_block(text, "java")
        python_code = extract_code_block(text, "python")
        c_code = extract_code_block(text, "c")
        
        if cpp_code:
            problem["starter_code"]["cpp"] = cpp_code
        else:
            problem["starter_code"]["cpp"] = "class Solution {\npublic:\n    // TODO: Implement solution\n};"
            
        if java_code:
            problem["starter_code"]["java"] = java_code
        else:
            problem["starter_code"]["java"] = "class Solution {\n    // TODO: Implement solution\n}"
            
        if python_code:
            problem["starter_code"]["python"] = python_code
        else:
            problem["starter_code"]["python"] = "class Solution:\n    # TODO: Implement solution\n    pass"
            
        if c_code:
            problem["starter_code"]["c"] = c_code
        else:
            problem["starter_code"]["c"] = "// TODO: Implement solution"
        
        # Add topic based on the problem content
        if topic.lower() in problem["description"].lower():
            problem["topics"] = [topic.capitalize()]
        else:
            problem["topics"] = ["Algorithm"]
        
        return problem
    
    except Exception as e:
        print(f"Error parsing problem: {e}")
        return None

def extract_code_block(text, language):
    """Extract a code block for a specific language from text"""
    language_markers = {
        "cpp": ["```cpp", "```c++", "C++:"],
        "java": ["```java", "Java:"],
        "python": ["```python", "Python:"],
        "c": ["```c", "C:"]
    }
    
    markers = language_markers.get(language.lower(), [])
    
    for marker in markers:
        try:
            start_idx = text.find(marker)
            if start_idx != -1:
                start_idx = text.find("\n", start_idx) + 1
                end_idx = text.find("```", start_idx)
                
                if end_idx == -1:  # If closing ``` not found
                    # Try to find the next language marker
                    for next_lang in ["C++:", "Java:", "Python:", "C:"]:
                        next_marker = text.find(next_lang, start_idx)
                        if next_marker != -1:
                            end_idx = text.rfind("\n", start_idx, next_marker)
                            break
                
                if end_idx == -1:  # If still not found
                    end_idx = len(text)
                
                code = text[start_idx:end_idx].strip()
                return code
        except:
            continue
    
    return ""

def get_array_easy_problem(problem_id):
    """Return a pre-defined array easy problem in LeetCode format"""
    return {
        "id": problem_id,
        "title": "Two Sum",
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nYou can return the answer in any order.",
        "examples": [
            {
                "input": "nums = [2,7,11,15], target = 9",
                "output": "[0,1]",
                "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
            },
            {
                "input": "nums = [3,2,4], target = 6",
                "output": "[1,2]"
            },
            {
                "input": "nums = [3,3], target = 6",
                "output": "[0,1]"
            }
        ],
        "constraints": [
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists."
        ],
        "starter_code": {
            "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your code here\n        return {};\n    }\n};",
            "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your code here\n        return new int[0];\n    }\n}",
            "python": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        # Write your code here\n        pass",
            "c": "int* twoSum(int* nums, int numsSize, int target, int* returnSize) {\n    // Write your code here\n    *returnSize = 2;\n    int* result = (int*)malloc(2 * sizeof(int));\n    return result;\n}"
        },
        "difficulty": "easy",
        "topics": ["Arrays", "Hash Table"],
        "companies": ["Google", "Amazon", "Facebook", "Apple"]
    }

def get_array_medium_problem(problem_id):
    """Return a pre-defined array medium problem in LeetCode format"""
    return {
        "id": problem_id,
        "title": "3Sum",
        "description": "Given an integer array nums, return all the triplets [nums[i], nums[j], nums[k]] such that i != j, i != k, and j != k, and nums[i] + nums[j] + nums[k] == 0.\n\nNotice that the solution set must not contain duplicate triplets.",
        "examples": [
            {
                "input": "nums = [-1,0,1,2,-1,-4]",
                "output": "[[-1,-1,2],[-1,0,1]]",
                "explanation": "The unique triplets that sum to zero are [-1,-1,2] and [-1,0,1]."
            },
            {
                "input": "nums = [0,1,1]",
                "output": "[]",
                "explanation": "There are no three numbers that sum to zero."
            },
            {
                "input": "nums = [0,0,0]",
                "output": "[[0,0,0]]",
                "explanation": "The only triplet that sums to zero is [0,0,0]."
            }
        ],
        "constraints": [
            "3 <= nums.length <= 3000",
            "-10^5 <= nums[i] <= 10^5"
        ],
        "starter_code": {
            "cpp": "class Solution {\npublic:\n    vector<vector<int>> threeSum(vector<int>& nums) {\n        // Write your code here\n        return {};\n    }\n};",
            "java": "class Solution {\n    public List<List<Integer>> threeSum(int[] nums) {\n        // Write your code here\n        return new ArrayList<>();\n    }\n}",
            "python": "class Solution:\n    def threeSum(self, nums: List[int]) -> List[List[int]]:\n        # Write your code here\n        pass",
            "c": "int** threeSum(int* nums, int numsSize, int* returnSize, int** returnColumnSizes) {\n    // Write your code here\n    *returnSize = 0;\n    *returnColumnSizes = NULL;\n    return NULL;\n}"
        },
        "difficulty": "medium",
        "topics": ["Arrays", "Two Pointers", "Sorting"],
        "companies": ["Amazon", "Microsoft", "Facebook", "Google"]
    }

def get_dp_problem(problem_id):
    """Return a pre-defined dynamic programming problem in LeetCode format"""
    return {
        "id": problem_id,
        "title": "Climbing Stairs",
        "description": "You are climbing a staircase. It takes n steps to reach the top.\n\nEach time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "examples": [
            {
                "input": "n = 2",
                "output": "2",
                "explanation": "There are two ways to climb to the top.\n1. 1 step + 1 step\n2. 2 steps"
            },
            {
                "input": "n = 3",
                "output": "3",
                "explanation": "There are three ways to climb to the top.\n1. 1 step + 1 step + 1 step\n2. 1 step + 2 steps\n3. 2 steps + 1 step"
            }
        ],
        "constraints": [
            "1 <= n <= 45"
        ],
        "starter_code": {
            "cpp": "class Solution {\npublic:\n    int climbStairs(int n) {\n        // Write your code here\n        return 0;\n    }\n};",
            "java": "class Solution {\n    public int climbStairs(int n) {\n        // Write your code here\n        return 0;\n    }\n}",
            "python": "class Solution:\n    def climbStairs(self, n: int) -> int:\n        # Write your code here\n        pass",
            "c": "int climbStairs(int n) {\n    // Write your code here\n    return 0;\n}"
        },
        "difficulty": "easy",
        "topics": ["Dynamic Programming", "Math", "Memoization"],
        "companies": ["Amazon", "Apple", "Adobe"]
    }

def execute_code_sandbox(code: str, language: str, test_input: str):
    """
    Simulates executing code in a sandbox environment.
    In a real implementation, you would use Docker or similar to safely execute code.
    """
    # This is just a simulation - in a real app, you'd actually execute the code
    return {
        "output": f"Simulated output for input: {test_input}",
        "execution_time": random.uniform(5, 100),  # Random time between 5-100ms
        "memory_usage": random.randint(1000, 5000)  # Random memory usage between 1-5MB
    }

@app.post("/api/code/run")
async def run_code(submission: CodeSubmission):
    """Run the submitted code against test cases"""
    try:
        # Get the problem
        problem = problems.get(submission.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Get all test cases for testing
        if not problem["examples"]:
            raise HTTPException(status_code=400, detail="No test cases available")
        
        # Prepare results for all test cases
        test_results = []
        total_time = 0
        total_memory = 0
        
        # Process all test cases
        for test_case in problem["examples"]:
            # Simulate code execution (in a real app, you would create a sandbox)
            start_time = time.time()
            process = psutil.Process()
            start_memory = process.memory_info().rss
            
            # Execute code in sandbox (simulated here)
            result = execute_code_sandbox(
                submission.code, 
                submission.language, 
                test_case["input"]
            )
            
            # In a real implementation, we would actually execute the code
            # For simulation, we'll sometimes return the correct answer
            should_pass = random.random() > 0.3  # 70% chance of passing
            
            # Format the output like LeetCode
            actual_output = test_case["output"] if should_pass else generate_wrong_output(test_case["output"])
            
            end_time = time.time()
            end_memory = process.memory_info().rss
            
            # Calculate execution stats
            execution_time = (end_time - start_time) * 1000  # Convert to ms
            memory_used = (end_memory - start_memory) / 1024  # Convert to KB
            
            total_time += execution_time
            total_memory += memory_used
            
            test_results.append({
                "passed": should_pass,
                "input": test_case["input"],
                "expected_output": test_case["output"],
                "actual_output": actual_output,
                "execution_time": execution_time,
                "memory_usage": memory_used,
                "is_hidden": test_case.get("is_hidden", False)
            })
        
        # Calculate overall metrics
        passed_count = sum(1 for r in test_results if r["passed"])
        
        return {
            "test_results": test_results,
            "overall_metrics": {
                "total_tests": len(test_results),
                "passed_tests": passed_count,
                "average_time": total_time / len(test_results) if test_results else 0,
                "average_memory": total_memory / len(test_results) if test_results else 0,
                "status": "Accepted" if passed_count == len(test_results) else "Wrong Answer",
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/code/evaluate", response_model=EvaluationResult)
async def evaluate_code(submission: CodeSubmission):
    """Evaluate the submitted code using Llama 3"""
    try:
        # Get the problem
        problem = problems.get(submission.problem_id)
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        # Run the code against all test cases
        test_results = []
        total_time = 0
        total_memory = 0
        passed_count = 0
        
        for i, test_case in enumerate(problem["examples"]):
            # Simulate code execution
            result = execute_code_sandbox(
                submission.code, 
                submission.language, 
                test_case["input"]
            )
            
            # In a LeetCode-style system, we would judge correctness based on output
            # For simulation, we'll add some variability to make it realistic
            
            # More likely to pass for earlier test cases
            difficulty_factor = 0.9 if i == 0 else (0.7 if i == 1 else 0.5)
            passed = random.random() < difficulty_factor
            
            # For first test case, higher chance of passing if language is Python
            if i == 0 and submission.language == 'python':
                passed = random.random() < 0.95
            
            actual_output = test_case["output"] if passed else generate_wrong_output(test_case["output"])
            execution_time = result["execution_time"]
            memory_usage = result["memory_usage"]
            
            total_time += execution_time
            total_memory += memory_usage
            if passed:
                passed_count += 1
            
            test_results.append({
                "passed": passed,
                "input": test_case["input"],
                "expected_output": test_case["output"],
                "actual_output": actual_output,
                "execution_time": execution_time,
                "memory_usage": memory_usage
            })
        
        # Generate hidden test cases for a more realistic LeetCode experience
        num_hidden_tests = random.randint(1, 3)
        for i in range(num_hidden_tests):
            # Generate a hidden test case based on existing test cases
            hidden_test = generate_hidden_test_case(problem)
            
            result = execute_code_sandbox(
                submission.code, 
                submission.language, 
                hidden_test["input"]
            )
            
            # Hidden tests are often harder to pass
            passed = random.random() < 0.6
            
            actual_output = hidden_test["output"] if passed else generate_wrong_output(hidden_test["output"])
            execution_time = result["execution_time"]
            memory_usage = result["memory_usage"]
            
            total_time += execution_time
            total_memory += memory_usage
            if passed:
                passed_count += 1
            
            test_results.append({
                "passed": passed,
                "input": hidden_test["input"],
                "expected_output": hidden_test["output"],
                "actual_output": actual_output,
                "execution_time": execution_time,
                "memory_usage": memory_usage
            })
            
        # Generate feedback using Llama 3
        if model:
            try:
                feedback_prompt = f"""
                Analyze this {submission.language} code:
                ```
                {submission.code}
                ```
                
                Problem: {problem['title']}
                
                Provide feedback in LeetCode style:
                1. Time complexity
                2. Space complexity
                3. Approach analysis
                4. Potential optimizations
                """
                
                response = model.create_completion(
                    feedback_prompt,
                    max_tokens=512,
                    temperature=0.7,
                    stop=["```"]
                )
                
                feedback = response["choices"][0]["text"]
            except Exception as e:
                print(f"Error generating feedback with Llama: {e}")
                feedback = generate_leetcode_feedback(problem, submission.language, passed_count, len(test_results))
        else:
            # Generate mock LeetCode-style feedback
            feedback = generate_leetcode_feedback(problem, submission.language, passed_count, len(test_results))
        
        # Calculate overall metrics (LeetCode style)
        total_tests = len(test_results)
        avg_time = total_time / total_tests if total_tests > 0 else 0
        avg_memory = total_memory / total_tests if total_tests > 0 else 0
        
        # LeetCode-style percentile rankings
        time_percentile = round(random.uniform(70, 99.5), 1)
        memory_percentile = round(random.uniform(65, 99.5), 1)
        
        overall_metrics = {
            "total_tests": total_tests,
            "passed_tests": passed_count,
            "average_time": avg_time,
            "average_memory": avg_memory,
            "time_percentile": time_percentile,
            "memory_percentile": memory_percentile,
            "status": "Accepted" if passed_count == total_tests else "Wrong Answer",
            "runtime_beats": f"{time_percentile}% of {submission.language} submissions",
            "memory_beats": f"{memory_percentile}% of {submission.language} submissions"
        }
        
        return {
            "test_results": test_results,
            "feedback": feedback,
            "overall_metrics": overall_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

def generate_wrong_output(correct_output: str) -> str:
    """Generate a plausible wrong output based on the correct output"""
    if "[" in correct_output and "]" in correct_output:
        # It's an array or 2D array
        if "[[" in correct_output:
            # It's a 2D array, make a small change
            return correct_output.replace("[", "", 1).replace("]", "", 1)
        else:
            try:
                if "," in correct_output:
                    # Array with multiple elements
                    elements = correct_output.strip("[]").split(",")
                    if elements and len(elements) > 1:
                        # Swap two elements
                        elements[0], elements[1] = elements[1], elements[0]
                        return "[" + ",".join(elements) + "]"
                # Could be a single number
                number = int(correct_output.strip("[]"))
                return f"[{number+1}]"
            except:
                # If parsing fails, just append an element
                return correct_output[:-1] + ",0]"
    elif correct_output.isdigit():
        # It's a number
        number = int(correct_output)
        # Return a slightly different number
        return str(number + (1 if random.random() > 0.5 else -1))
    else:
        # String or other type, append something
        return correct_output + " (incorrect)"

def generate_hidden_test_case(problem):
    """Generate a hidden test case based on the problem examples"""
    if not problem["examples"]:
        return {"input": "sample input", "output": "sample output"}
    
    # Use the first example as a template
    template = problem["examples"][0]
    
    # Modify the input based on the problem type
    input_str = template["input"]
    output_str = template["output"]
    
    # Array problems (most common)
    if "nums = [" in input_str:
        # Extract the array
        array_start = input_str.find("[")
        array_end = input_str.find("]")
        if array_start != -1 and array_end != -1:
            array_str = input_str[array_start:array_end+1]
            try:
                # Parse the array and modify it
                array = json.loads(array_str.replace("=", ":")
                                  .replace("nums", '"nums"')
                                  .replace("target", '"target"'))
                
                # Make a larger array
                new_array = list(array) * 2
                # Shuffle it
                random.shuffle(new_array)
                
                # Replace the array in the input
                new_input = input_str.replace(array_str, str(new_array))
                # Generate a plausible output
                new_output = output_str
                
                return {"input": new_input, "output": new_output}
            except:
                pass
    
    # Number problems
    if "n = " in input_str:
        try:
            n_value = int(input_str.split("=")[1].strip())
            # Increase the value
            new_n = n_value * 10
            new_input = input_str.replace(str(n_value), str(new_n))
            
            # For problems like factorial or Fibonacci, scale the output
            if int(output_str) > 1:
                new_output = str(int(output_str) * 100)
            else:
                new_output = output_str
                
            return {"input": new_input, "output": new_output}
        except:
            pass
    
    # If we couldn't generate a specific hidden test, make a simple modification
    return {
        "input": "Hidden Test: " + input_str,
        "output": output_str
    }

def generate_leetcode_feedback(problem, language, passed_count, total_tests):
    """Generate LeetCode-style feedback for a submission"""
    # Time complexity options by difficulty
    time_complexities = {
        "easy": ["O(n)", "O(n log n)", "O(1)"],
        "medium": ["O(n)", "O(n log n)", "O(n²)"],
        "hard": ["O(n log n)", "O(n²)", "O(2^n)"]
    }
    
    # Space complexity options
    space_complexities = ["O(1)", "O(n)", "O(log n)"]
    
    # Select complexities based on problem difficulty
    difficulty = problem.get("difficulty", "medium")
    time_complexity = random.choice(time_complexities.get(difficulty, time_complexities["medium"]))
    space_complexity = random.choice(space_complexities)
    
    # Generate approach description
    approach_templates = [
        "You approached this problem using a {technique}, which is efficient for this type of problem.",
        "Your solution uses a {technique} approach, which works well here.",
        "The {technique} strategy you implemented is appropriate for this challenge."
    ]
    
    techniques = {
        "arrays": ["two-pointer", "sliding window", "greedy", "divide and conquer"],
        "strings": ["two-pointer", "sliding window", "dynamic programming"],
        "linkedlists": ["fast and slow pointer", "recursive", "iterative"],
        "trees": ["depth-first search", "breadth-first search", "recursive"],
        "dp": ["bottom-up dynamic programming", "top-down memoization", "recursion with memoization"]
    }
    
    # Choose a technique based on problem topic
    technique = "algorithmic"
    for topic in problem.get("topics", []):
        topic_lower = topic.lower()
        for key in techniques:
            if key in topic_lower:
                technique = random.choice(techniques[key])
                break
    
    approach = random.choice(approach_templates).format(technique=technique)
    
    # Generate optimization suggestions
    optimization_templates = [
        "Consider using a hash map to improve lookup time.",
        "You could reduce the space complexity by using an in-place algorithm.",
        "Try using a more efficient data structure for this operation.",
        "Consider edge cases like empty inputs or single elements.",
        "The time complexity could be improved by using binary search in this step."
    ]
    
    optimizations = []
    if passed_count < total_tests:
        # More optimization suggestions for failing solutions
        num_optimizations = random.randint(2, 3)
    else:
        # Fewer suggestions for passing solutions
        num_optimizations = random.randint(0, 2)
    
    for _ in range(num_optimizations):
        optimization = random.choice(optimization_templates)
        if optimization not in optimizations:
            optimizations.append(optimization)
    
    # Language-specific comments
    language_comments = {
        "cpp": [
            "Good use of STL containers.",
            "Consider using references to avoid unnecessary copying.",
            "Using unordered_map instead of map could improve performance here."
        ],
        "java": [
            "Good use of Java collections.",
            "Consider using StringBuilder for string concatenation.",
            "ArrayList operations could be optimized in this context."
        ],
        "python": [
            "Good use of Python's built-in functions.",
            "List comprehensions could make this code more concise.",
            "Consider using defaultdict for this counting operation."
        ],
        "c": [
            "Good memory management.",
            "Consider using a more efficient sorting algorithm.",
            "Array indexing could be optimized to avoid bounds checking."
        ]
    }
    
    lang_comment = ""
    if language in language_comments:
        lang_comment = random.choice(language_comments[language])
    
    # Format the feedback in LeetCode style
    feedback = f"""
# Solution Analysis

## Time Complexity: {time_complexity}
## Space Complexity: {space_complexity}

### Approach:
{approach}

### Optimizations:
{"".join(f"- {opt}\n" for opt in optimizations) if optimizations else "Your solution is well optimized."}

### Language-specific notes:
{lang_comment}
    """
    
    return feedback.strip()

def parse_llama_test_cases(text, example_template):
    """Parse test cases generated by Llama"""
    test_cases = []
    try:
        # Split by "Example" or "Test Case" markers
        lines = text.split('\n')
        
        current_test = {}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.lower().startswith("input:"):
                if current_test and "input" in current_test:
                    # Save previous test case
                    if "input" in current_test and "output" in current_test:
                        test_cases.append(current_test)
                    current_test = {}
                
                current_test["input"] = line.replace("Input:", "").strip()
                current_section = "input"
            elif line.lower().startswith("output:"):
                current_test["output"] = line.replace("Output:", "").strip()
                current_section = "output"
            elif line.lower().startswith("explanation:"):
                current_test["explanation"] = line.replace("Explanation:", "").strip()
                current_section = "explanation"
            elif current_section == "input":
                current_test["input"] += " " + line
            elif current_section == "output":
                current_test["output"] += " " + line
            elif current_section == "explanation":
                current_test["explanation"] += " " + line
            elif line.lower().startswith("example") or line.lower().startswith("test case"):
                # Start a new test case
                if current_test and "input" in current_test and "output" in current_test:
                    test_cases.append(current_test)
                current_test = {}
                current_section = None
        
        # Add the last test case if it exists
        if current_test and "input" in current_test and "output" in current_test:
            test_cases.append(current_test)
            
        # If we couldn't parse any test cases, create some based on the template
        if not test_cases and example_template:
            for i in range(3):
                test_cases.append(generate_hidden_test_case({"examples": [example_template]}))
                
    except Exception as e:
        print(f"Error parsing test cases: {e}")
        if example_template:
            # Generate some test cases based on the template
            for i in range(3):
                test_cases.append(generate_hidden_test_case({"examples": [example_template]}))
    
    return test_cases

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 