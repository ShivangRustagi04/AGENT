import streamlit as st
import requests

# Streamlit app
def main():
    st.title("AI Coding Assistant (Powered by GPT-NeoX)")
    
    # Sidebar for navigation
    menu = st.sidebar.selectbox("Menu", ["Solve Problem", "View Progress"])
    
    if menu == "Solve Problem":
        st.header("Solve a Coding Problem")
        problem_id = st.number_input("Problem ID", min_value=1, step=1)
        problem_description = st.text_area("Problem Description", "Enter the problem here...")
        
        if st.button("Get Hints"):
            response = requests.post(
                "http://127.0.0.1:8000/api/get_hints",
                json={"description": problem_description}
            )
            if response.status_code == 200:
                hints = response.json()["hints"]
                st.subheader("Hints:")
                for hint in hints:
                    st.write(hint)
            else:
                st.error("Failed to fetch hints from the API.")
        
        code = st.text_area("Write your solution here...")
        if st.button("Submit Solution"):
            response = requests.post(
                "http://127.0.0.1:8000/api/evaluate_solution",
                json={"problem_description": problem_description, "solution_code": code}
            )
            if response.status_code == 200:
                evaluation = response.json()["evaluation"]
                st.subheader("Evaluation:")
                st.write(evaluation)
            else:
                st.error("Failed to evaluate the solution.")

    elif menu == "View Progress":
        st.header("Your Progress")
        user_id = st.text_input("User ID")
        if st.button("Fetch Progress"):
            response = requests.post(
                "http://127.0.0.1:8000/api/user_progress",
                json={"user_id": user_id}
            )
            if response.status_code == 200:
                progress = response.json()["progress"]
                st.subheader("Solved Problems:")
                for item in progress:
                    st.write(f"Problem ID: {item['problem_id']}, Status: {item['status']}")
            else:
                st.error("Failed to fetch progress.")

if __name__ == "__main__":
    main()
