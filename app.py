import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

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

# Streamlit app
def main():
    st.title("AI Coding Assistant")
    
    # Sidebar for navigation
    menu = st.sidebar.selectbox("Menu", ["Solve Problem"])
    
    if menu == "Solve Problem":
        st.header("Solve a Coding Problem")
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

if __name__ == "__main__":
    main()