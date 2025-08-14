import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-pro')

# Function to generate hints using Gemini API
def generate_hint(problem_description):
    prompt = f"Provide hints for solving this coding problem: {problem_description}"
    response = model.generate_content(prompt)
    hints = response.text.split("\n")  # Split hints into a list
    return hints

# Function to evaluate a solution using Gemini API
def evaluate_solution(problem_description, solution_code):
    # Check if the solution is empty or too short to be considered complete
    if not solution_code.strip() or len(solution_code.strip()) < 20:
        return (
            "Your solution seems incomplete, but don't worry! You're on the right track. "
            "Take your time to think through the problem and try again. I believe in you!"
        )

    # Generate feedback for the solution without providing direct answers
    prompt = (
        f"Evaluate this solution for the problem: {problem_description}\n"
        f"Solution:\n{solution_code}\n\n"
        "Provide constructive feedback that encourages the candidate without giving away the solution. "
        "If the solution is incomplete or incorrect, motivate the candidate to keep trying."
    )
    response = model.generate_content(prompt)
    evaluation = response.text

    # Add motivational messages based on the evaluation
    if "correct" in evaluation.lower() or "well done" in evaluation.lower():
        evaluation += "\n\nGreat job! You've cracked it! Keep up the excellent work!"
    else:
        evaluation += (
            "\n\nYou're moving in the right direction! I believe in you and know that you can crack it. "
            "Take a moment to review the feedback and refine your solution."
        )

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
