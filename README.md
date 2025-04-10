# AI-Powered Coding Platform

A backend service that uses Llama 3 for problem generation, code evaluation, and feedback.

## Features

- 🤖 AI-powered problem generation using Llama 3
- 📝 Real-time code execution and evaluation
- 📊 Performance metrics (time and memory usage)
- 💡 AI-generated feedback on code quality and efficiency
- 🔍 Multiple programming language support (C++, Java, Python, C)
- 📚 Various problem topics and difficulty levels

## API Endpoints

- `GET /api/problems/{problem_id}`: Get a specific problem by ID
- `POST /api/problems/generate`: Generate a new coding problem
- `POST /api/code/run`: Run code against test cases

## Tech Stack

- Backend: FastAPI + Python
- AI: Llama 3 (via llama-cpp-python)

## Prerequisites

- Python 3.8 or higher
- Llama 3 model file (llama-2-7b-chat.gguf)

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd coding-platform
```

2. Set up the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Download the Llama 3 model:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python download_model.py
```
This will download the llama-2-7b-chat.gguf model file to the `backend/models` directory.

## Running the Application

Start the backend server:
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

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
  "difficulty": "easy",
  "topics": ["Arrays", "Greedy"]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 