# src/aiment/crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from aiment.tools.custom_tool import *

# Create a function that returns an instance of your tool
def create_emotion_analysis_tool():
    return EmotionAnalysisTool()

# This is the critical part - add this dictionary
tool_functions = {
    'EmotionAnalysisTool': create_emotion_analysis_tool
}



@CrewBase
class Aiment():
    """Student Mentoring AI System"""
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def mentor(self) -> Agent:
        return Agent(
        config=self.agents_config['mentor'],
        tools=[
            EmotionAnalysisTool(),
            StudentDataTool(),
            SafetyAssessmentTool(),
            AcademicProgressTool(),
            CareerGuidanceTool(),
            StudyPatternAnalysisTool(),
            ResourceRecommendationTool()
        ],
        llm=os.getenv("MODEL", "ollama/llama3.2"),  # Add this line
    )
    @agent 
    def academic_advisor(self) -> Agent:
        return Agent(
            config=self.agents_config['academic_advisor'],
            tools=[
                AcademicProgressTool(),
                StudentDataTool(),
                CareerGuidanceTool(),
                ResourceRecommendationTool()
            ]
        )

    @agent
    def counselor(self) -> Agent:
        return Agent(
            config=self.agents_config['counselor'],
            tools=[
                EmotionAnalysisTool(),
                SafetyAssessmentTool(),
                StudentDataTool(),
                StudyPatternAnalysisTool()
            ]
        )

    @task
    def initial_assessment(self) -> Task:
        return Task(config=self.tasks_config['initial_assessment'])

    @task
    def academic_planning(self) -> Task:
        return Task(config=self.tasks_config['academic_planning'])
        
    @task
    def well_being_assessment(self) -> Task:
        return Task(config=self.tasks_config['well_being_assessment'])

    @task
    def progress_monitoring(self) -> Task:
        return Task(config=self.tasks_config['progress_monitoring'])

    @task
    def emergency_response(self) -> Task:
        return Task(config=self.tasks_config['emergency_response'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )