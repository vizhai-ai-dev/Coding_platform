# AI-Powered Coding Platform

A LeetCode-style coding platform that uses Llama 3 for problem generation, code evaluation, and feedback.

## Features

- 🎯 LeetCode-style interface with problem statement, code editor, and output console
- 🤖 AI-powered problem generation using Llama 3
- 📝 Real-time code execution and evaluation
- 📊 Performance metrics (time and memory usage)
- 💡 AI-generated feedback on code quality and efficiency
- 🔍 Multiple programming language support (C++, Java, Python, C)
- 📚 Various problem topics and difficulty levels

## User Flow

1. **Select preferences**: Choose programming language, question topic, and difficulty level
2. **Solve the problem**: View the problem description and write your solution in the editor
3. **Test your solution**: Run code to test against sample inputs
4. **Submit for evaluation**: Get comprehensive feedback on your solution

## UI Components

- **Landing Page**: Select language, topic, and difficulty
- **Problem Statement Panel**: Problem description with examples and constraints
- **Code Editor**: Write and edit code with language selection
- **Output Console**: View test results and performance metrics

## Tech Stack

- Frontend: React + TypeScript + Material-UI
- Backend: FastAPI + Python
- AI: Llama 3 (via llama-cpp-python)
- Code Editor: Monaco Editor

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8 or higher
- Llama 3 model file (llama-2-7b-chat.gguf)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd coding-platform
```

2. Set up the frontend:
```bash
cd frontend
npm install
```

3. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Download the Llama 3 model:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python download_model.py
```
This will download the llama-2-7b-chat.gguf model file to the `backend/models` directory.

## Running the Application

1. Start the backend server:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload
```

2. Start the frontend development server:
```bash
cd frontend
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## API Endpoints

- `GET /api/problems/{problem_id}`: Get a specific problem by ID
- `POST /api/problems/generate`: Generate a new coding problem
- `POST /api/code/run`: Run code against test cases
- `POST /api/code/evaluate`: Evaluate code and get AI feedback

## Example Problem Format

```json
{
  "id": "3375",
  "title": "Minimum Operations to Make Array Values Equal to K",
  "description": "Problem description text...",
  "examples": [
    {
      "input": "nums = [5,2,5,4,5], k = 2",
      "output": "2",
      "explanation": "The operations can be performed in order using valid integers 4 and then 2."
    }
  ],
  "constraints": [
    "2 <= nums.length <= 10^4",
    "1 <= nums[i] <= 10^9"
  ],
  "starter_code": {
    "cpp": "class Solution { ... }",
    "java": "class Solution { ... }",
    "python": "class Solution: ..."
  },
  "difficulty": "easy",
  "topics": ["Arrays", "Greedy"]
}
```

## Screenshots

- Landing Page: User selects preferences
- Problem View: LeetCode-style interface with problem statement, code editor, and output console

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 