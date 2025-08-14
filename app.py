import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

# Load environment variables
load_dotenv()

# Configure Gemini API
try:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    if not GOOGLE_API_KEY:
        st.error("❌ Google API key not found. Please check your .env file.")
        st.stop()
    
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-pro')  # Use stable model
except Exception as e:
    st.error(f"Failed to configure Gemini: {e}")
    st.stop()

def generate_hint(problem_description):
    """Generate hints for coding problems."""
    if not problem_description.strip():
        return ["Please provide a problem description to get hints."]

    prompt = f"""
    Provide 3-5 concise hints for solving this coding problem, formatted as bullet points:
    Problem: {problem_description}
    Hints:
    """

    for attempt in range(3):  # Retry up to 3 times
        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": 0.7}
            )
            text_output = response.text.strip()
            # Clean bullet points
            hints = [line.strip("-• ").strip() for line in text_output.split("\n") if line.strip()]
            return hints
        except Exception as e:
            time.sleep(1)
            if attempt == 2:
                return [f"Failed to generate hints: {e}"]

def evaluate_solution(problem_description, solution_code):
    """Evaluate a coding solution and provide feedback."""
    if not problem_description.strip():
        return "Please provide a problem description for evaluation."
    if not solution_code.strip():
        return "Your solution is empty. Please write some code first!"
    if len(solution_code.strip()) < 20:
        return "Your solution seems too short. Try expanding on your approach."

    prompt = f"""
    Act as a coding mentor. Provide constructive feedback on this solution:
    
    Problem: {problem_description}
    
    Solution:
    {solution_code}
    
    Evaluation Guidelines:
    1. Identify what's working well
    2. Point out areas for improvement
    3. Suggest next steps without giving direct answers
    4. Keep feedback encouraging and growth-oriented
    5. Format your response in clear paragraphs
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.3}
        )
        evaluation = response.text.strip()

        # Add motivational closing
        if any(word in evaluation.lower() for word in ["correct", "good", "well done", "great"]):
            evaluation += "\n\n🌟 Excellent progress! You're demonstrating great problem-solving skills!"
        else:
            evaluation += "\n\n💪 Keep going! Every attempt makes you a better programmer. You've got this!"
        return evaluation
    except Exception as e:
        return f"Couldn't evaluate your solution due to an error: {e}"

def main():
    st.title("🎯 AI Coding Assistant")
    st.caption("Get hints and feedback on your coding solutions")

    with st.sidebar:
        st.header("Settings")
        if st.button("Check API Connection"):
            try:
                model.generate_content("Test connection")
                st.success("✅ Connected to Gemini API")
            except Exception as e:
                st.error(f"API Connection Failed: {e}")

    tab1, tab2 = st.tabs(["Solve Problem", "About"])

    with tab1:
        problem = st.text_area(
            "Problem Description",
            placeholder="Paste the coding problem here...",
            height=150
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Get Hints"):
                if not problem.strip():
                    st.warning("Please enter a problem first")
                else:
                    with st.spinner("Generating hints..."):
                        hints = generate_hint(problem)
                        st.subheader("💡 Hints")
                        for hint in hints:
                            st.write(f"- {hint}")
        
        with col2:
            if st.button("Clear All"):
                st.experimental_rerun()

        solution = st.text_area(
            "Your Solution",
            placeholder="Write your code solution here...",
            height=300
        )

        if st.button("Submit Solution"):
            with st.spinner("Evaluating your solution..."):
                feedback = evaluate_solution(problem, solution)
                st.subheader("📝 Evaluation")
                st.write(feedback)

    with tab2:
        st.markdown("""
        ## About This Assistant
        This tool helps you practice coding by:
        - Providing hints when you're stuck
        - Giving constructive feedback on your solutions
        - Encouraging learning through iteration
        
        Powered by Google's Gemini AI.
        """)

if __name__ == "__main__":
    main()
