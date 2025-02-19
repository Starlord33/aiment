# crew.py
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.custom_tool import (
    EmotionAnalysisTool,
    StudentDataTool,
    SafetyAssessmentTool,
    AcademicProgressTool,
    CareerGuidanceTool,
    StudyPatternAnalysisTool,
    ResourceRecommendationTool
)

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
                CareerGuidanceTool()
            ],
            verbose=True
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
            ],
            verbose=True
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
            ],
            verbose=True
        )

    @task
    def initial_assessment_task(self) -> Task:
        return Task(
            config=self.tasks_config['initial_assessment_task']
        )

    @task
    def academic_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['academic_planning_task']
        )

    @task
    def well_being_task(self) -> Task:
        return Task(
            config=self.tasks_config['well_being_task']
        )

    @task
    def progress_monitoring_task(self) -> Task:
        return Task(
            config=self.tasks_config['progress_monitoring_task']
        )

    @task
    def continuous_monitoring_task(self) -> Task:
        return Task(
            config=self.tasks_config['continuous_monitoring_task']
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )