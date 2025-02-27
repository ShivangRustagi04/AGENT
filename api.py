from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Initialize FastAPI app
app = FastAPI()

# Load GPT-NeoX model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-2.7B")
model = AutoModelForCausalLM.from_pretrained("EleutherAI/gpt-neo-2.7B")

# Initialize SQLite3 database
def init_db():
    conn = sqlite3.connect('coding_assistant.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            name TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_progress (
            user_id TEXT,
            problem_id INTEGER,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(user_id)
        )
    ''')
    conn.commit()
    conn.close()

# Call init_db to ensure the database is initialized
init_db()

# Pydantic models for request/response
class Problem(BaseModel):
    description: str

class Solution(BaseModel):
    problem_description: str
    solution_code: str

class UserProgress(BaseModel):
    user_id: str

# Generate hints using GPT-NeoX
@app.post("/api/get_hints")
async def get_hints(problem: Problem):
    prompt = f"Provide hints for solving this coding problem: {problem.description}"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    outputs = model.generate(inputs.input_ids, max_length=100, num_return_sequences=1)
    hint = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"hints": hint.split("\n")}

# Evaluate a solution using GPT-NeoX
@app.post("/api/evaluate_solution")
async def evaluate_solution(solution: Solution):
    prompt = f"Evaluate this solution for the problem: {solution.problem_description}\nSolution:\n{solution.solution_code}"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
    outputs = model.generate(inputs.input_ids, max_length=100, num_return_sequences=1)
    evaluation = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"evaluation": evaluation}

# Fetch user progress from the database
@app.post("/api/user_progress")
async def user_progress(user_progress: UserProgress):
    conn = sqlite3.connect('coding_assistant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT problem_id, status FROM user_progress WHERE user_id = ?", (user_progress.user_id,))
    progress = cursor.fetchall()
    conn.close()
    if progress:
        return {"progress": [{"problem_id": row[0], "status": row[1]} for row in progress]}
    else:
        raise HTTPException(status_code=404, detail="User not found")