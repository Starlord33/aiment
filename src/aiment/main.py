# src/aiment/main.py
import os
from .crew import Aiment

def ensure_student_directory(student_id):
    """Create a directory for the student if it doesn't exist"""
    os.makedirs(f"student_reports/{student_id}", exist_ok=True)

def run_aiment_crew(inputs):
    """Run a specific Aiment task based on session type"""
    # Create directories
    os.makedirs("student_reports", exist_ok=True)
    ensure_student_directory(inputs['student_id'])
    
    # Initialize Aiment
    aiment = Aiment()
    
    # Map session type to task
    session_type = inputs.get('session_type', 'initial_assessment')
    
    # Get the crew
    crew = aiment.crew()
    
    # Get the specific task
    if session_type == 'initial_assessment':
        task = aiment.initial_assessment()
    elif session_type == 'academic_planning':
        task = aiment.academic_planning()
    elif session_type == 'well_being_check':
        task = aiment.well_being_assessment()
    elif session_type == 'follow_up':
        task = aiment.progress_monitoring()
    elif session_type == 'emergency':
        task = aiment.emergency_response()
    else:
        task = aiment.initial_assessment()
    
    # Execute the task with the crew
    result = crew.execute_task(task, inputs=inputs)
    
    return result

if __name__ == "__main__":
    # Example usage
    inputs = {
        'student_id': 'S12345',
        'year': 'Freshman',
        'major': 'Computer Science',
        'gpa': '3.5',
        'input': 'I am feeling overwhelmed with my coursework and struggling to balance academics with extracurricular activities.',
        'session_type': 'initial_assessment'
    }
    
    result = run_aiment_crew(inputs)
    print(result)