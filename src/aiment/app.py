# src/aiment/app.py
import streamlit as st
import os
import threading
import time
import requests
from dotenv import load_dotenv
from aiment.main import run_aiment_crew, ensure_student_directory

# Load environment variables
load_dotenv()

# Change this function to use absolute imports
def get_aiment():
    """Import and return Aiment class"""
    from aiment.crew import Aiment  # Use absolute import
    return Aiment()

        
def check_llm_connection():
    """Check if the LLM API is available"""
    api_base = os.getenv("API_BASE", "http://localhost:11434")
    try:
        response = requests.get(f"{api_base}/api/tags")
        return response.status_code == 200, api_base
    except Exception as e:
        return False, str(e)

def run_aiment_with_ui(inputs):
    """Run Aiment crew with better logging and error handling"""
    
    # Create directories
    os.makedirs("student_reports", exist_ok=True)
    ensure_student_directory(inputs['student_id'])
    
    # Add debug info to the UI
    st.text("🔄 Initializing Aiment system...")
    
    # Check if Ollama is running based on .env settings
    api_base = os.getenv("API_BASE", "http://localhost:11434")
    model = os.getenv("MODEL", "ollama/llama3.2")
    
    is_connected, message = check_llm_connection()
    if not is_connected:
        st.error(f"⚠️ Cannot connect to LLM API at {api_base}: {message}")
        return f"Error connecting to LLM API. Please check if Ollama is running."
    
    st.text(f"✅ Connected to LLM: {api_base} - {model}")
    
    # Try to run the crew with progress updates
    try:
        st.text("🔄 Initializing CrewAI agents...")
        
        st.text(f"🔄 Starting execution with inputs: {inputs}")
        
        # Create a placeholder for progress
        progress_placeholder = st.empty()
        progress_placeholder.text("🔄 AI agents working on your request...")
        
        # Run with timeout protection
        result = {"response": None, "error": None, "completed": False}
        
        
        def run_task():
            try:
                aiment = get_aiment()
                task_result = run_aiment_crew(inputs)
                result["response"] = task_result
                result["completed"] = True
            except Exception as e:
                result["error"] = str(e)
                import traceback
                print(f"Error details: {traceback.format_exc()}") 
        
        # Start thread
        thread = threading.Thread(target=run_task)
        thread.start()
        
        # Wait with progress indicators
        wait_time = 0
        max_wait = 120  # Maximum seconds to wait
        
        while not result["completed"] and result["error"] is None and wait_time < max_wait:
            progress_placeholder.text(f"🔄 AI agents working on your request... ({wait_time}s)")
            time.sleep(1)
            wait_time += 1
        
        if wait_time >= max_wait and not result["completed"]:
            progress_placeholder.text("⚠️ Operation taking longer than expected. The process is still running in the background.")
            return "The operation is taking longer than expected. This might be due to complex processing or an issue with the LLM connection. Please check the terminal for logs."
        
        if result["error"]:
            return f"Error during execution: {result['error']}"
        
        # Determine the report file based on session type
        session_type = inputs.get('session_type', 'initial_assessment')
        student_id = inputs.get('student_id', 'unknown')
        
        report_map = {
            'initial_assessment': f"student_reports/{student_id}/initial_assessment.md",
            'academic_planning': f"student_reports/{student_id}/academic_plan.md",
            'well_being_check': f"student_reports/{student_id}/wellbeing_assessment.md",
            'follow_up': f"student_reports/{student_id}/progress_report.md",
            'emergency': f"student_reports/{student_id}/emergency_response.md"
        }
        
        report_file = report_map.get(session_type, f"student_reports/{student_id}/report.md")
        
        if os.path.exists(report_file):
            with open(report_file, 'r') as rf:
                report_content = rf.read()
                return report_content
        
        return result["response"] or "Processing complete. The AI system has analyzed your input."
    
    except Exception as e:
        st.error(f"⚠️ Error: {str(e)}")
        return f"Error: {str(e)}"

def main():
    st.title("Aiment - AI Student Mentoring System")
    
    # Check LLM connection
    is_connected, message = check_llm_connection()
    if not is_connected:
        st.error(f"⚠️ Cannot connect to LLM API: {message}")
        st.info("Please make sure Ollama is running before using this application.")
    else:
        st.success("✅ Connected to LLM API")
    
    # Student Information Form
    with st.form("student_info"):
        st.subheader("Student Information")
        student_id = st.text_input("Student ID", value="S12345")
        year = st.selectbox("Year", ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"])
        major = st.text_input("Major", value="Computer Science")
        gpa = st.text_input("GPA", value="3.5")
        
        # Session Type
        session_type = st.selectbox(
            "Session Type",
            [
                "initial_assessment",
                "academic_planning",
                "well_being_check",
                "follow_up",
                "emergency"
            ],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        # Student Input
        student_input = st.text_area(
            "What can we help you with today?",
            value="I'm feeling overwhelmed with my coursework and struggling to balance academics with extracurricular activities."
        )
        
        submitted = st.form_submit_button("Submit")
    
    if submitted:
        with st.spinner("Processing your request..."):
            inputs = {
                'student_id': student_id,
                'year': year,
                'major': major,
                'gpa': gpa,
                'input': student_input,
                'session_type': session_type
            }
            
            result = run_aiment_with_ui(inputs)
            st.markdown("## AI Assessment")
            st.markdown(result)

if __name__ == "__main__":
    main()