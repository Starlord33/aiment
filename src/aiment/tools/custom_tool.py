# tools/student_tools.py
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Union
from datetime import datetime
import json
import re
import os

# Input Schemas
class EmotionAnalysisInput(BaseModel):
    text: str = Field(..., description="Text content to analyze for emotions")
    context: Optional[Dict] = Field(default=None, description="Previous interaction context")

class StudentDataInput(BaseModel):
    student_id: str = Field(..., description="Student's unique identifier")
    action: str = Field(..., description="Action to perform: read/write/update")
    data: Optional[Dict] = Field(default=None, description="Data to write or update")

class AcademicProgressInput(BaseModel):
    student_id: str = Field(..., description="Student's unique identifier")
    timeframe: str = Field(..., description="Time period to analyze: 'week', 'month', 'semester'")
    metrics: List[str] = Field(..., description="Metrics to analyze: grades, attendance, participation, etc.")

class SafetyAssessmentInput(BaseModel):
    student_id: str = Field(..., description="Student's unique identifier")
    interaction_text: str = Field(..., description="Current interaction text to analyze")
    historical_data: Optional[Dict] = Field(default=None, description="Previous interactions and assessments")

class CareerGuidanceInput(BaseModel):
    student_id: str = Field(..., description="Student's unique identifier")
    interests: List[str] = Field(..., description="Student's areas of interest")
    skills: List[str] = Field(..., description="Student's current skills")
    academic_performance: Dict = Field(..., description="Academic performance metrics")

class StudyPatternInput(BaseModel):
    student_id: str = Field(..., description="Student's unique identifier")
    timeframe: str = Field(..., description="Period to analyze: 'day', 'week', 'month'")
    activities: List[Dict] = Field(..., description="Study activities to analyze")

class ResourceRecommendationInput(BaseModel):
    student_id: str = Field(..., description="Student's unique identifier")
    topic: str = Field(..., description="Topic or subject area")
    difficulty_level: str = Field(..., description="Preferred difficulty level")
    learning_style: str = Field(..., description="Student's learning style")

# Tool Implementations
class EmotionAnalysisTool(BaseTool):
    name: str = "Emotion Analysis Tool"
    description: str = "Analyzes text for emotional content, sentiment, and potential concerns"
    args_schema: type[BaseModel] = EmotionAnalysisInput

    def _run(self, text: str, context: Optional[Dict] = None) -> Dict:
        """Analyze emotional content in text using sentiment analysis"""
        try:
            # Implement emotion analysis logic here
            # This would typically use a sentiment analysis model
            emotions = {
                'primary_emotion': 'focused',
                'sentiment_score': 0.75,
                'emotional_state': {
                    'stress_level': 'moderate',
                    'engagement': 'high',
                    'motivation': 'positive'
                },
                'concern_flags': [],
                'confidence': 0.85,
                'context': context
            }
            return emotions
        except Exception as e:
            return {
                'error': f"Error analyzing emotions: {str(e)}",
                'success': False
            }

class StudentDataTool(BaseTool):
    name: str = "Student Data Management Tool"
    description: str = "Manages student data including academic records, interaction history, and performance metrics"
    args_schema: type[BaseModel] = StudentDataInput

    def _run(self, student_id: str, action: str, data: Optional[Dict] = None) -> Dict:
        """Handle student data operations"""
        try:
            file_path = f"student_data/{student_id}/profile.json"
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            if action == "read":
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        return json.load(f)
                return {"message": "No data found", "success": False}

            elif action in ["write", "update"]:
                existing_data = {}
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        existing_data = json.load(f)
                
                if action == "update":
                    existing_data.update(data)
                else:
                    existing_data = data

                with open(file_path, 'w') as f:
                    json.dump(existing_data, f, indent=4)
                return {"message": "Data saved successfully", "success": True}

        except Exception as e:
            return {"error": str(e), "success": False}

class SafetyAssessmentTool(BaseTool):
    name: str = "Safety Assessment Tool"
    description: str = "Monitors and assesses student safety and well-being concerns"
    args_schema: type[BaseModel] = SafetyAssessmentInput

    def _run(self, student_id: str, interaction_text: str, historical_data: Optional[Dict] = None) -> Dict:
        """Assess safety concerns from interaction text"""
        try:
            # Define risk indicators and their patterns
            risk_patterns = {
                'self_harm': r'\b(hurt|harm|suicide|die)\b',
                'abuse': r'\b(abuse|hurt|scared|threatened)\b',
                'crisis': r'\b(emergency|crisis|urgent|help)\b',
                'academic_stress': r'\b(overwhelmed|stress|anxiety|panic)\b'
            }

            # Check for risk indicators
            risk_levels = {}
            for risk_type, pattern in risk_patterns.items():
                matches = len(re.findall(pattern, interaction_text.lower()))
                risk_levels[risk_type] = 'high' if matches > 2 else 'medium' if matches > 0 else 'low'

            # Overall risk assessment
            overall_risk = 'high' if 'high' in risk_levels.values() else 'medium' if 'medium' in risk_levels.values() else 'low'

            return {
                'risk_assessment': {
                    'overall_risk_level': overall_risk,
                    'specific_risks': risk_levels,
                    'timestamp': datetime.now().isoformat(),
                    'requires_immediate_action': overall_risk == 'high'
                },
                'recommendations': self._generate_safety_recommendations(overall_risk),
                'success': True
            }
        except Exception as e:
            return {"error": str(e), "success": False}

    def _generate_safety_recommendations(self, risk_level: str) -> List[str]:
        """Generate safety recommendations based on risk level"""
        recommendations = {
            'high': [
                "Immediate supervisor notification required",
                "Schedule urgent counseling session",
                "Contact emergency contacts if necessary",
                "Document all interactions and concerns"
            ],
            'medium': [
                "Schedule follow-up counseling session",
                "Increase monitoring frequency",
                "Document concerns and maintain observation"
            ],
            'low': [
                "Continue regular monitoring",
                "Document any changes in behavior",
                "Maintain regular check-ins"
            ]
        }
        return recommendations.get(risk_level, ["Continue regular monitoring"])

class AcademicProgressTool(BaseTool):
    name: str = "Academic Progress Tool"
    description: str = "Tracks and analyzes student academic progress and performance"
    args_schema: type[BaseModel] = AcademicProgressInput

    def _run(self, student_id: str, timeframe: str, metrics: List[str]) -> Dict:
        """Analyze academic progress based on specified metrics"""
        try:
            # This would typically connect to your academic database
            # Simulated progress tracking
            progress_data = {
                'academic_performance': {
                    'grades': {
                        'current_gpa': 3.5,
                        'trend': 'improving',
                        'subjects': {
                            'math': 'A-',
                            'science': 'B+',
                            'english': 'A'
                        }
                    },
                    'attendance': {
                        'rate': 95,
                        'trend': 'stable'
                    },
                    'participation': {
                        'level': 'active',
                        'trend': 'improving'
                    }
                },
                'skill_development': {
                    'technical_skills': ['python', 'data analysis'],
                    'soft_skills': ['communication', 'teamwork'],
                    'areas_for_improvement': ['public speaking']
                },
                'goals_progress': {
                    'completed': ['Complete Python course'],
                    'in_progress': ['Develop portfolio'],
                    'pending': ['Internship application']
                },
                'timeframe': timeframe,
                'timestamp': datetime.now().isoformat()
            }
            return progress_data
        except Exception as e:
            return {"error": str(e), "success": False}

class CareerGuidanceTool(BaseTool):
    name: str = "Career Guidance Tool"
    description: str = "Provides career guidance and recommendations based on student profile"
    args_schema: type[BaseModel] = CareerGuidanceInput

    def _run(self, student_id: str, interests: List[str], skills: List[str], academic_performance: Dict) -> Dict:
        """Generate career guidance recommendations"""
        try:
            # This would typically connect to career databases and job market data
            career_guidance = {
                'recommended_careers': [
                    {
                        'title': 'Data Scientist',
                        'alignment_score': 0.85,
                        'required_skills': ['python', 'statistics', 'machine learning'],
                        'skill_gaps': ['deep learning', 'big data'],
                        'education_path': ['BS Computer Science', 'MS Data Science'],
                        'market_demand': 'high'
                    }
                ],
                'skill_development': {
                    'recommended_courses': [
                        'Advanced Python Programming',
                        'Introduction to Machine Learning'
                    ],
                    'suggested_projects': [
                        'Data Analysis Portfolio',
                        'Machine Learning Project'
                    ]
                },
                'internship_opportunities': [
                    {
                        'company': 'Tech Corp',
                        'position': 'Data Science Intern',
                        'requirements': ['Python', 'SQL'],
                        'application_deadline': '2024-05-01'
                    }
                ],
                'timestamp': datetime.now().isoformat()
            }
            return career_guidance
        except Exception as e:
            return {"error": str(e), "success": False}

class StudyPatternAnalysisTool(BaseTool):
    name: str = "Study Pattern Analysis Tool"
    description: str = "Analyzes and optimizes student study patterns and habits"
    args_schema: type[BaseModel] = StudyPatternInput

    def _run(self, student_id: str, timeframe: str, activities: List[Dict]) -> Dict:
        """Analyze study patterns and provide recommendations"""
        try:
            analysis = {
                'study_patterns': {
                    'peak_productivity_times': ['9:00-11:00', '15:00-17:00'],
                    'average_session_duration': '45 minutes',
                    'most_effective_methods': ['active recall', 'spaced repetition'],
                    'common_distractions': ['social media', 'phone notifications']
                },
                'recommendations': {
                    'schedule_adjustments': [
                        'Schedule complex tasks during morning peak hours',
                        'Take regular breaks every 45 minutes'
                    ],
                    'method_improvements': [
                        'Implement Pomodoro Technique',
                        'Use concept mapping for complex topics'
                    ],
                    'environment_optimization': [
                        'Create a dedicated study space',
                        'Minimize digital distractions'
                    ]
                },
                'progress_metrics': {
                    'focus_improvement': '+15%',
                    'retention_rate': '75%',
                    'productivity_score': 8.2
                },
                'timestamp': datetime.now().isoformat()
            }
            return analysis
        except Exception as e:
            return {"error": str(e), "success": False}

class ResourceRecommendationTool(BaseTool):
    name: str = "Resource Recommendation Tool"
    description: str = "Recommends learning resources based on student preferences and needs"
    args_schema: type[BaseModel] = ResourceRecommendationInput

    def _run(self, student_id: str, topic: str, difficulty_level: str, learning_style: str) -> Dict:
        """Recommend personalized learning resources"""
        try:
            recommendations = {
                'online_courses': [
                    {
                        'title': 'Advanced Python Programming',
                        'platform': 'Coursera',
                        'difficulty': 'intermediate',
                        'duration': '6 weeks',
                        'learning_style_match': 0.9
                    }
                ],
                'study_materials': [
                    {
                        'type': 'interactive tutorial',
                        'title': 'Python Projects Portfolio',
                        'format': 'hands-on',
                        'difficulty': difficulty_level
                    }
                ],
                'practice_resources': [
                    {
                        'type': 'coding exercises',
                        'platform': 'LeetCode',
                        'difficulty': difficulty_level,
                        'topics': ['algorithms', 'data structures']
                    }
                ],
                'supplementary_materials': [
                    {
                        'type': 'video tutorials',
                        'platform': 'YouTube',
                        'channel': 'Tech Learning',
                        'playlist': 'Python Mastery'
                    }
                ],
                'peer_learning': [
                    {
                        'type': 'study group',
                        'topic': topic,
                        'schedule': 'weekly',
                        'format': 'virtual'
                    }
                ],
                'timestamp': datetime.now().isoformat()
            }
            return recommendations
        except Exception as e:
            return {"error": str(e), "success": False}