import streamlit as st
import sqlite3
import os
import google.generativeai as genai
from dotenv import load_dotenv

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

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')

# Function to generate hints using Gemini API
def generate_hint(problem_description):
    prompt = f"Provide hints for solving this coding problem: {problem_description}"
    response = model.generate_content(prompt)
    hints = response.text.split("\n")  # Split hints into a list
    return hints

# Function to evaluate a solution using Gemini API
def evaluate_solution(problem_description, solution_code):
    prompt = f"Evaluate this solution for the problem: {problem_description}\nSolution:\n{solution_code}"
    response = model.generate_content(prompt)
    evaluation = response.text
    return evaluation

# Function to add or update user progress
def update_progress(user_id, problem_id, status):
    conn = sqlite3.connect('coding_assistant.db')
    cursor = conn.cursor()
    try:
        # Check if user exists
        cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        if not cursor.fetchone():
            st.error("User ID not found. Please register first.")
            conn.close()
            return
        
        # Insert or replace progress
        cursor.execute('''
            INSERT OR REPLACE INTO user_progress (user_id, problem_id, status)
            VALUES (?, ?, ?)
        ''', (user_id, problem_id, status))
        conn.commit()
        st.success(f"Progress saved for user_id: {user_id}, problem_id: {problem_id}")
    except Exception as e:
        st.error(f"Error saving progress: {e}")
    finally:
        conn.close()

# Function to fetch user details
def get_user_details(user_id):
    conn = sqlite3.connect('coding_assistant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, email FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user

# Streamlit app
def main():
    st.title("AI Coding Assistant (Powered by Gemini API)")
    
    # Initialize database
    init_db()
    
    # Sidebar for navigation
    menu = st.sidebar.selectbox("Menu", ["Solve Problem", "View Progress", "Register User"])
    
    if menu == "Solve Problem":
        st.header("Solve a Coding Problem")
        problem_id = st.number_input("Problem ID", min_value=1, step=1)
        problem_description = st.text_area("Problem Description", "Enter the problem here...")
        
        if st.button("Get Hints"):
            hints = generate_hint(problem_description)
            st.subheader("Hints:")
            for hint in hints:
                st.write(hint)
        
        code = st.text_area("Write your solution here...")
        if st.button("Submit Solution"):
            evaluation = evaluate_solution(problem_description, code)
            st.subheader("Evaluation:")
            st.write(evaluation)
            
            # Save progress
            user_id = st.text_input("Enter your User ID to save progress")
            if user_id.strip() == "":
                st.error("User ID cannot be empty.")
                return
            
            update_progress(user_id, problem_id, "Completed")
    
    elif menu == "View Progress":
        st.header("Your Progress")
        user_id = st.text_input("User ID")
        if st.button("Fetch Progress"):
            user_details = get_user_details(user_id)
            if not user_details:
                st.error("User ID not found. Please register first.")
                return
            
            st.subheader(f"User Details:")
            st.write(f"Name: {user_details[0]}")
            st.write(f"Email: {user_details[1]}")
            
            conn = sqlite3.connect('coding_assistant.db')
            cursor = conn.cursor()
            cursor.execute("SELECT problem_id, status FROM user_progress WHERE user_id = ?", (user_id,))
            progress = cursor.fetchall()
            conn.close()
            
            if progress:
                st.subheader("Solved Problems:")
                for row in progress:
                    st.write(f"Problem ID: {row[0]}, Status: {row[1]}")
            else:
                st.write("No progress found for this user.")
    
    elif menu == "Register User":
        st.header("Register New User")
        user_id = st.text_input("User ID")
        name = st.text_input("Name")
        email = st.text_input("Email")
        
        if st.button("Register"):
            conn = sqlite3.connect('coding_assistant.db')
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO users (user_id, name, email)
                    VALUES (?, ?, ?)
                ''', (user_id, name, email))
                conn.commit()
                st.success("User registered successfully!")
            except sqlite3.IntegrityError:
                st.error("User ID already exists. Please choose a different User ID.")
            finally:
                conn.close()

if __name__ == "__main__":
    main()