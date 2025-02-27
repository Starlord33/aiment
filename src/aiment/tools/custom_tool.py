# src/aiment/tools/custom_tool.py
from typing import Any, Dict, List, Optional, Type
import os
import json
import random
from datetime import datetime, timedelta
from crewai.tools import BaseTool
import logging
from pydantic import BaseModel, Field


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmotionAnalysisInput(BaseModel):
    """Input schema for EmotionAnalysisTool."""
    input_text: str = Field(..., description="The student's text response to analyze for emotional content.")

class EmotionAnalysisTool(BaseTool):
    name: str = "EmotionAnalysisTool"
    description: str = "Analyzes emotional content and sentiment in student responses to determine their emotional state"
    args_schema: Type[BaseModel] = EmotionAnalysisInput

    def _run(self, input_text: str) -> str:
        """Analyze the emotional content of student text input"""
        logger.info(f"EmotionAnalysisTool._run called with input: '{input_text[:50]}...' (truncated)")
        
        try:
            # Define emotion categories
            emotions = {
                "joy": 0.0, "sadness": 0.0, "anxiety": 0.0, "frustration": 0.0,
                "motivation": 0.0, "exhaustion": 0.0, "confidence": 0.0,
                "confusion": 0.0, "hope": 0.0
            }
            
            # Keywords that might indicate different emotions
            emotion_keywords = {
                "joy": ["happy", "excited", "thrilled", "pleased", "delighted", "enjoy", "fun", "great"],
                "sadness": ["sad", "down", "depressed", "unhappy", "miserable", "heartbroken", "upset", "disappointed"],
                "anxiety": ["anxious", "worried", "nervous", "stress", "panic", "overwhelm", "fear", "dread", "concern"],
                "frustration": ["frustrat", "annoyed", "irritated", "angry", "upset", "difficult", "hard", "struggle"],
                "motivation": ["motivated", "inspired", "determined", "driven", "eager", "committed", "enthusiastic"],
                "exhaustion": ["tired", "exhausted", "fatigue", "drain", "burnout", "sleep", "rest", "overworked"],
                "confidence": ["confident", "sure", "certain", "capable", "able", "competent", "mastery"],
                "confusion": ["confused", "unclear", "lost", "uncertain", "puzzled", "don't understand", "complex"],
                "hope": ["hope", "optimistic", "anticipate", "look forward", "better", "improve", "progress"]
            }
            
            # Simple analysis based on keyword presence
            input_lower = input_text.lower()
            
            for emotion, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in input_lower:
                        emotions[emotion] += 0.2  # Increase score for each keyword found
            
            # Normalize to ensure no score exceeds 1.0
            for emotion in emotions:
                emotions[emotion] = min(emotions[emotion], 1.0)
                emotions[emotion] = round(emotions[emotion], 2)
            
            # Determine primary emotion
            primary_emotion = max(emotions, key=emotions.get)
            primary_score = emotions[primary_emotion]
            
            # If no clear emotion is detected, set to neutral
            if primary_score < 0.2:
                primary_emotion = "neutral"
                assessment = "The student's emotional state appears relatively neutral or unclear from the text."
            else:
                # Generate assessment based on primary emotion
                assessments = {
                    "joy": "The student appears to be in a positive emotional state, showing signs of happiness and satisfaction.",
                    "sadness": "The student shows indicators of sadness or disappointment that may need attention.",
                    "anxiety": "The student is displaying signs of anxiety or stress that should be addressed.",
                    "frustration": "The student appears frustrated, possibly with academic challenges or other issues.",
                    "motivation": "The student shows good motivation and drive toward their goals.",
                    "exhaustion": "The student appears to be experiencing fatigue or exhaustion that may impact performance.",
                    "confidence": "The student demonstrates confidence in their abilities and approach.",
                    "confusion": "The student seems confused or uncertain about concepts or expectations.",
                    "hope": "The student maintains a hopeful outlook despite challenges."
                }
                assessment = assessments.get(primary_emotion, "The student's emotional state requires further assessment.")
            
            # Get recommendations
            recommendations = self._get_recommendations(primary_emotion)
            
            # Format the response
            response = {
                "primary_emotion": primary_emotion,
                "emotion_scores": emotions,
                "assessment": assessment,
                "recommendations": recommendations,
                "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return json.dumps(response, indent=2)
            
        except Exception as e:
            logger.error(f"Error in EmotionAnalysisTool._run: {str(e)}", exc_info=True)
            return json.dumps({"error": f"Analysis failed: {str(e)}"})
    
    def _get_recommendations(self, emotion: str) -> list:
        """Generate recommendations based on detected emotion"""
        recommendations = {
            "joy": [
                "Encourage the student to mentor others who may be struggling",
                "Suggest more challenging projects to maintain engagement",
                "Discuss long-term goals to channel positive energy"
            ],
            "sadness": [
                "Schedule a follow-up counseling session",
                "Provide resources for mental health support",
                "Consider workload adjustments if academic pressure is contributing"
            ],
            "anxiety": [
                "Teach stress management techniques",
                "Review time management strategies",
                "Consider exam or assignment accommodations if needed"
            ],
            "frustration": [
                "Identify specific sources of frustration",
                "Connect with tutoring for challenging subjects",
                "Break down complex tasks into manageable steps"
            ],
            "motivation": [
                "Channel motivation into specific goal-setting",
                "Connect with student leadership opportunities",
                "Suggest research or advanced project opportunities"
            ],
            "exhaustion": [
                "Discuss work-life balance strategies",
                "Review sleep habits and self-care",
                "Consider temporary workload adjustments"
            ],
            "confidence": [
                "Encourage peer tutoring or mentoring roles",
                "Suggest participation in academic competitions",
                "Discuss advanced courses or accelerated options"
            ],
            "confusion": [
                "Schedule additional office hours with instructors",
                "Connect with study groups or tutoring",
                "Provide clarification resources and examples"
            ],
            "hope": [
                "Help develop concrete steps toward goals",
                "Connect with mentors in areas of interest",
                "Provide opportunities to build on positive outlook"
            ],
            "neutral": [
                "Continue regular check-ins",
                "Explore interests and motivations more deeply",
                "Monitor for changes in emotional state"
            ]
        }
        
        return recommendations.get(emotion, ["Schedule a follow-up assessment", "Maintain regular check-ins"])


class StudentDataTool(BaseTool):
    name: str = "StudentDataTool"
    description: str = "Accesses and manages student academic and personal data"
    
    def _execute(self, student_id: str) -> str:
        """Retrieve student data based on student ID"""
        # Check if we already have data for this student
        student_file = f"student_reports/{student_id}/student_data.json"
        
        if os.path.exists(student_file):
            with open(student_file, 'r') as f:
                return f.read()
        
        # Generate synthetic student data
        student_data = self._generate_student_data(student_id)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(student_file), exist_ok=True)
        
        # Save the data
        with open(student_file, 'w') as f:
            json.dump(student_data, f, indent=2)
        
        return json.dumps(student_data, indent=2)
    
    def _generate_student_data(self, student_id: str) -> Dict:
        """Generate synthetic student data"""
        # Common majors with corresponding courses
        majors = {
            "Computer Science": [
                "Introduction to Programming", "Data Structures", "Algorithms", 
                "Computer Systems", "Database Management", "Software Engineering",
                "Artificial Intelligence", "Machine Learning", "Web Development"
            ],
            "Psychology": [
                "Introduction to Psychology", "Developmental Psychology", "Cognitive Psychology",
                "Social Psychology", "Abnormal Psychology", "Statistics for Psychology",
                "Research Methods", "Neuroscience", "Clinical Psychology"
            ],
            "Business Administration": [
                "Principles of Management", "Marketing Fundamentals", "Financial Accounting",
                "Business Ethics", "Organizational Behavior", "Business Law",
                "Strategic Management", "Operations Management", "Business Analytics"
            ],
            "Engineering": [
                "Calculus", "Physics", "Engineering Design", "Thermodynamics",
                "Mechanics of Materials", "Electric Circuits", "Fluid Mechanics",
                "Control Systems", "Engineering Ethics"
            ],
            "Biology": [
                "General Biology", "Cell Biology", "Genetics", "Ecology",
                "Microbiology", "Physiology", "Biochemistry", "Molecular Biology",
                "Evolutionary Biology"
            ]
        }
        
        # Randomly select major and year
        major = random.choice(list(majors.keys()))
        years = ["Freshman", "Sophomore", "Junior", "Senior"]
        year = random.choice(years)
        year_num = years.index(year) + 1
        
        # Generate GPA and course data
        overall_gpa = round(random.uniform(2.0, 4.0), 2)
        
        # Select relevant courses based on major and year
        potential_courses = majors[major]
        current_courses = []
        completed_courses = []
        
        # Distribute courses between completed and current based on year
        for i, course in enumerate(potential_courses):
            course_data = {
                "name": course,
                "credits": random.choice([3, 4]),
                "grade": self._generate_grade(overall_gpa)
            }
            
            if i < year_num * 2:  # Completed courses based on year
                completed_courses.append(course_data)
            elif len(current_courses) < 5:  # Current courses (max 5)
                current_courses.append(course_data)
        
        # Generate personal data
        interests = []
        all_interests = [
            "Robotics", "Art", "Music", "Sports", "Literature", "Volunteering",
            "Photography", "Gaming", "Travel", "Cooking", "Dance", "Debate",
            "Entrepreneurship", "Sustainability", "Theater", "Writing"
        ]
        for _ in range(random.randint(2, 5)):
            interest = random.choice(all_interests)
            if interest not in interests:
                interests.append(interest)
        
        # Generate extracurricular activities
        extracurriculars = []
        all_extracurriculars = [
            "Student Government", "Chess Club", "Debate Team", "Music Band",
            "Environmental Club", "Sports Team", "Volunteer Organization",
            "Cultural Club", "Academic Honor Society", "Tech Club",
            "Art Club", "Theater Group", "Student Newspaper"
        ]
        for _ in range(random.randint(1, 3)):
            activity = random.choice(all_extracurriculars)
            if activity not in extracurriculars:
                extracurriculars.append(activity)
        
        # Combine all data
        student_data = {
            "student_id": student_id,
            "personal_info": {
                "major": major,
                "year": year,
                "interests": interests,
                "extracurricular_activities": extracurriculars,
                "career_goals": self._generate_career_goals(major)
            },
            "academic_info": {
                "overall_gpa": overall_gpa,
                "completed_courses": completed_courses,
                "current_courses": current_courses,
                "academic_standing": self._determine_standing(overall_gpa)
            },
            "support_history": {
                "previous_meetings": self._generate_meetings(year_num),
                "academic_accommodations": random.random() < 0.15,  # 15% chance of accommodations
                "flags": self._generate_flags(overall_gpa)
            }
        }
        
        return student_data
    
    def _generate_grade(self, target_gpa: float) -> str:
        """Generate a plausible grade based on overall GPA"""
        grade_options = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F"]
        grade_points = [4.0, 3.7, 3.3, 3.0, 2.7, 2.3, 2.0, 1.7, 1.3, 1.0, 0.0]
        
        # Calculate probabilities based on target GPA
        # Higher probability for grades close to target GPA
        probabilities = []
        for points in grade_points:
            # Inverse of the distance from target, squared for emphasis
            prob = 1 / (1 + abs(target_gpa - points) ** 2)
            probabilities.append(prob)
        
        # Normalize probabilities
        total = sum(probabilities)
        probabilities = [p / total for p in probabilities]
        
        # Select grade based on probability distribution
        return random.choices(grade_options, weights=probabilities, k=1)[0]
    
    def _determine_standing(self, gpa: float) -> str:
        """Determine academic standing based on GPA"""
        if gpa >= 3.5:
            return "Dean's List"
        elif gpa >= 3.0:
            return "Good Standing"
        elif gpa >= 2.0:
            return "Academic Warning"
        else:
            return "Academic Probation"
    
    def _generate_meetings(self, year_num: int) -> List[Dict]:
        """Generate synthetic meeting history"""
        meetings = []
        current_date = datetime.now()
        
        # Generate more meetings for higher year students
        num_meetings = random.randint(year_num - 1, year_num * 2)
        
        for i in range(num_meetings):
            # Generate a date in the past, more recent for later meetings
            days_ago = random.randint(30, 365) - (i * 30)
            meeting_date = current_date - timedelta(days=days_ago)
            
            meeting_types = ["Initial Assessment", "Academic Planning", "Well-being Check", 
                           "Progress Monitoring", "Career Guidance"]
            
            meeting = {
                "date": meeting_date.strftime("%Y-%m-%d"),
                "type": random.choice(meeting_types),
                "summary": "Previous meeting notes would appear here.",
                "follow_up_items": random.choice([True, False])
            }
            
            meetings.append(meeting)
        
        # Sort by date, most recent first
        return sorted(meetings, key=lambda x: x["date"], reverse=True)
    
    def _generate_flags(self, gpa: float) -> List[Dict]:
        """Generate potential flags based on student performance"""
        flags = []
        
        # Academic performance flags
        if gpa < 2.0:
            flags.append({
                "type": "Academic",
                "severity": "High",
                "description": "Student at risk of academic probation",
                "date_flagged": (datetime.now() - timedelta(days=random.randint(10, 30))).strftime("%Y-%m-%d")
            })
        elif gpa < 2.5:
            flags.append({
                "type": "Academic",
                "severity": "Medium",
                "description": "Struggling in multiple courses",
                "date_flagged": (datetime.now() - timedelta(days=random.randint(10, 60))).strftime("%Y-%m-%d")
            })
        
        # Random flags with low probability
        if random.random() < 0.2:  # 20% chance of attendance flag
            flags.append({
                "type": "Attendance",
                "severity": "Medium",
                "description": "Multiple class absences",
                "date_flagged": (datetime.now() - timedelta(days=random.randint(5, 20))).strftime("%Y-%m-%d")
            })
        
        if random.random() < 0.1:  # 10% chance of well-being flag
            flags.append({
                "type": "Well-being",
                "severity": "Medium",
                "description": "Student reported high stress levels",
                "date_flagged": (datetime.now() - timedelta(days=random.randint(3, 15))).strftime("%Y-%m-%d")
            })
        
        return flags
    
    def _generate_career_goals(self, major: str) -> List[str]:
        """Generate plausible career goals based on major"""
        career_goals = {
            "Computer Science": [
                "Software Engineer", "Data Scientist", "AI Researcher",
                "Web Developer", "Cybersecurity Specialist", "Game Developer"
            ],
            "Psychology": [
                "Clinical Psychologist", "Counselor", "Research Psychologist",
                "Human Resources Specialist", "Social Worker", "Psychiatrist"
            ],
            "Business Administration": [
                "Marketing Manager", "Financial Analyst", "Management Consultant",
                "Entrepreneur", "Human Resources Manager", "Business Analyst"
            ],
            "Engineering": [
                "Mechanical Engineer", "Civil Engineer", "Electrical Engineer",
                "Aerospace Engineer", "Project Manager", "Research Scientist"
            ],
            "Biology": [
                "Physician", "Research Scientist", "Pharmacist",
                "Environmental Scientist", "Geneticist", "Biotechnologist"
            ]
        }
        
        # Select 1-3 career goals
        goals = career_goals.get(major, ["Professional in field", "Graduate studies"])
        return random.sample(goals, min(random.randint(1, 3), len(goals)))


class SafetyAssessmentTool(BaseTool):
    name: str = "SafetyAssessmentTool" 
    description: str = "Evaluates student safety concerns and risk levels"
    
    def _execute(self, input_text: str) -> str:
        """Assess potential safety concerns in student input"""
        # Define safety concern categories
        concerns = {
            "self_harm": 0.0,
            "harm_to_others": 0.0,
            "substance_abuse": 0.0,
            "severe_distress": 0.0,
            "basic_needs": 0.0
        }
        
        # Keywords that might indicate safety concerns
        concern_keywords = {
            "self_harm": ["hurt myself", "harm myself", "end my life", "suicide", "kill myself", 
                         "don't want to live", "no point in living", "better off dead"],
            "harm_to_others": ["hurt someone", "harm others", "violent thoughts", "revenge", 
                              "make them pay", "they deserve to suffer", "bring weapon"],
            "substance_abuse": ["drunk", "wasted", "high", "using drugs", "addicted", 
                              "can't stop drinking", "overdose", "blackout"],
            "severe_distress": ["can't handle", "breaking down", "falling apart", "crisis", 
                               "desperate", "hopeless", "unbearable", "trauma"],
            "basic_needs": ["homeless", "nowhere to sleep", "can't afford food", "haven't eaten", 
                           "unsafe housing", "abusive", "kicked out", "no money for"]
        }
        
        # Simple analysis based on keyword presence
        input_lower = input_text.lower()
        for concern, keywords in concern_keywords.items():
            for keyword in keywords:
                if keyword in input_lower:
                    concerns[concern] += 0.3  # Increase score for each keyword found
        
        # Normalize to ensure no score exceeds 1.0
        for concern in concerns:
            concerns[concern] = min(concerns[concern], 1.0)
            concerns[concern] = round(concerns[concern], 2)
        
        # Determine overall risk level
        max_concern = max(concerns.values())
        if max_concern >= 0.6:
            risk_level = "High"
        elif max_concern >= 0.3:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        # Generate response with recommendations
        primary_concerns = [concern for concern, level in concerns.items() if level >= 0.3]
        
        if risk_level == "High":
            action_plan = [
                "Immediate referral to campus mental health services",
                "Consider wellness check if student cannot be reached",
                "Notify appropriate campus emergency services",
                "Document all concerns and actions taken",
                "Schedule follow-up within 24 hours"
            ]
        elif risk_level == "Medium":
            action_plan = [
                "Schedule appointment with counseling services within 48 hours",
                "Provide crisis hotline and emergency resources",
                "Check in with student within 24-48 hours",
                "Document concerns and maintain communication",
                "Consider academic accommodations if needed"
            ]
        else:
            action_plan = [
                "Provide supportive resources appropriate to student needs",
                "Schedule routine follow-up",
                "Monitor for changes in behavior or academic performance",
                "Document any concerns for future reference"
            ]
        
        # Prepare response
        response = {
            "risk_assessment": {
                "overall_risk_level": risk_level,
                "concern_scores": concerns,
                "primary_concerns": primary_concerns,
            },
            "recommended_actions": action_plan,
            "campus_resources": self._get_campus_resources(primary_concerns),
            "assessment_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(response, indent=2)
    
    def _get_campus_resources(self, concerns: List[str]) -> Dict[str, str]:
        """Provide relevant campus resources based on identified concerns"""
        all_resources = {
            "self_harm": {
                "Campus Counseling Center": "555-123-4567 (24/7 Crisis Line)",
                "National Suicide Prevention Lifeline": "988",
                "Student Health Services": "555-123-8900"
            },
            "harm_to_others": {
                "Campus Police": "555-123-9111",
                "Student Conduct Office": "555-123-4444",
                "Violence Prevention Program": "555-123-5555"
            },
            "substance_abuse": {
                "Substance Abuse Services": "555-123-6666",
                "Recovery Support Group": "555-123-7777",
                "Student Health Services": "555-123-8900"
            },
            "severe_distress": {
                "Campus Counseling Center": "555-123-4567",
                "Peer Support Program": "555-123-9999",
                "Student Support Services": "555-123-0000"
            },
            "basic_needs": {
                "Student Emergency Fund": "555-123-1111",
                "Campus Food Pantry": "555-123-2222",
                "Housing Services": "555-123-3333",
                "Financial Aid Office": "555-123-4444"
            }
        }
        
        # If no specific concerns, return general resources
        if not concerns:
            return {
                "Campus Counseling Center": "555-123-4567",
                "Student Support Services": "555-123-0000",
                "Student Health Services": "555-123-8900"
            }
        
        # Compile relevant resources
        resources = {}
        for concern in concerns:
            if concern in all_resources:
                resources.update(all_resources[concern])
        
        return resources


class AcademicProgressTool(BaseTool):
    name: str = "AcademicProgressTool"
    description: str = "Analyzes academic performance trends and progress"
    
    def _execute(self, student_data: str) -> str:
        """Analyze academic performance and provide insights"""
        # Parse student data
        if isinstance(student_data, str):
            try:
                data = json.loads(student_data)
            except json.JSONDecodeError:
                return json.dumps({
                    "error": "Invalid student data format",
                    "details": "The provided data could not be parsed as JSON"
                })
        else:
            data = student_data
        
        # Extract relevant academic information
        academic_info = data.get("academic_info", {})
        overall_gpa = academic_info.get("overall_gpa", 0.0)
        completed_courses = academic_info.get("completed_courses", [])
        current_courses = academic_info.get("current_courses", [])
        academic_standing = academic_info.get("academic_standing", "Unknown")
        
        # Calculate performance metrics
        course_performance = self._analyze_course_performance(completed_courses)
        strengths_weaknesses = self._identify_strengths_weaknesses(completed_courses)
        graduation_progress = self._estimate_graduation_progress(data)
        risk_assessment = self._academic_risk_assessment(data)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(data, risk_assessment)
        
        # Compile analysis
        analysis = {
            "summary": {
                "overall_gpa": overall_gpa,
                "academic_standing": academic_standing,
                "total_credits_completed": sum(course.get("credits", 0) for course in completed_courses),
                "current_course_load": len(current_courses),
                "risk_level": risk_assessment["risk_level"]
            },
            "detailed_analysis": {
                "performance_trends": course_performance,
                "strengths_and_weaknesses": strengths_weaknesses,
                "graduation_progress": graduation_progress,
                "current_semester_projection": self._project_current_semester(current_courses, overall_gpa)
            },
            "risk_assessment": risk_assessment,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(analysis, indent=2)
    
    def _analyze_course_performance(self, completed_courses: List[Dict]) -> Dict:
        """Analyze performance across completed courses"""
        if not completed_courses:
            return {"trend": "Not enough data for trend analysis"}
        
        # Calculate grade distribution
        grade_counts = {}
        for course in completed_courses:
            grade = course.get("grade", "")
            if grade:
                grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        # Determine trend (simplified)
        good_grades = sum(grade_counts.get(g, 0) for g in ["A", "A-", "B+", "B"])
        poor_grades = sum(grade_counts.get(g, 0) for g in ["C-", "D+", "D", "F"])
        
        if good_grades > len(completed_courses) * 0.7:
            trend = "Strong performance across most courses"
        elif good_grades > poor_grades:
            trend = "Mixed performance with more strengths than weaknesses"
        elif poor_grades > good_grades:
            trend = "Struggling in multiple courses, needs academic support"
        else:
            trend = "Consistent average performance"
        
        return {
            "grade_distribution": grade_counts,
            "trend": trend
        }
    
    def _identify_strengths_weaknesses(self, completed_courses: List[Dict]) -> Dict:
        """Identify academic strengths and weaknesses"""
        if not completed_courses:
            return {
                "strengths": ["Not enough data to determine strengths"],
                "weaknesses": ["Not enough data to determine weaknesses"]
            }
        
        # Group courses by performance
        strong_courses = []
        weak_courses = []
        
        for course in completed_courses:
            name = course.get("name", "")
            grade = course.get("grade", "")
            
            if grade in ["A", "A-", "B+"]:
                strong_courses.append(name)
            elif grade in ["C-", "D+", "D", "F"]:
                weak_courses.append(name)
        
        # Determine subject areas from course names
        strength_areas = self._extract_subject_areas(strong_courses)
        weakness_areas = self._extract_subject_areas(weak_courses)
        
        return {
            "strengths": strength_areas if strength_areas else ["No clear strengths identified"],
            "weaknesses": weakness_areas if weakness_areas else ["No clear weaknesses identified"]
        }
    
    def _extract_subject_areas(self, course_names: List[str]) -> List[str]:
        """Extract general subject areas from course names"""
        # Define subject keywords
        subject_mapping = {
            "Math": ["calculus", "algebra", "statistics", "mathematics", "computational"],
            "Programming": ["programming", "coding", "software", "development", "algorithm"],
            "Science": ["physics", "chemistry", "biology", "science", "laboratory"],
            "Writing": ["writing", "composition", "literature", "essay", "communications"],
            "Business": ["business", "management", "marketing", "finance", "accounting"],
            "Social Sciences": ["psychology", "sociology", "anthropology", "economics", "political"],
            "Arts": ["art", "music", "theater", "design", "creative"],
            "Engineering": ["engineering", "mechanical", "electrical", "systems", "materials"]
        }
        
        # Count occurrences of each subject area
        subject_counts = {subject: 0 for subject in subject_mapping}
        
        for course in course_names:
            course_lower = course.lower()
            for subject, keywords in subject_mapping.items():
                for keyword in keywords:
                    if keyword in course_lower:
                        subject_counts[subject] += 1
                        break
        
        # Return subjects with at least one match
        return [subject for subject, count in subject_counts.items() if count > 0]
    
    def _estimate_graduation_progress(self, student_data: Dict) -> Dict:
        """Estimate progress toward graduation requirements"""
        # Extract relevant data
        academic_info = student_data.get("academic_info", {})
        personal_info = student_data.get("personal_info", {})
        
        year = personal_info.get("year", "Unknown")
        major = personal_info.get("major", "Unknown")
        completed_credits = sum(course.get("credits", 0) for course in academic_info.get("completed_courses", []))
        
        # Estimate typical graduation requirements
        total_credits_needed = 120  # Standard for most 4-year degrees
        
        # Estimate progress based on year and credits
        expected_progress = {
            "Freshman": 0.25,
            "Sophomore": 0.5,
            "Junior": 0.75,
            "Senior": 0.9
        }
        
        year_progress = expected_progress.get(year, 0.5)
        credit_progress = completed_credits / total_credits_needed
        
        # Compare actual progress to expected progress
        if credit_progress < year_progress - 0.1:
            status = "Behind expected progress"
        elif credit_progress > year_progress + 0.1:
            status = "Ahead of expected progress"
        else:
            status = "On track with expected progress"
        
        return {
            "completed_credits": completed_credits,
            "total_credits_needed": total_credits_needed,
            "percent_complete": round(credit_progress * 100, 1),
            "status": status,
            "estimated_semesters_remaining": max(1, round((total_credits_needed - completed_credits) / 15))
        }
    
    def _academic_risk_assessment(self, student_data: Dict) -> Dict:
        """Assess academic risk factors"""
        # Extract relevant data
        academic_info = student_data.get("academic_info", {})
        support_history = student_data.get("support_history", {})
        
        gpa = academic_info.get("overall_gpa", 0.0)
        academic_standing = academic_info.get("academic_standing", "")
        completed_courses = academic_info.get("completed_courses", [])
        flags = support_history.get("flags", [])
        
        # Count failing grades
        failing_courses = sum(1 for course in completed_courses if course.get("grade") in ["D", "F"])
        
        # Define risk factors and their weights
        risk_factors = []
        risk_score = 0.0
        
        if gpa < 2.0:
            risk_factors.append("GPA below academic probation threshold")
            risk_score += 0.4
        elif gpa < 2.5:
            risk_factors.append("GPA in warning range")
            risk_score += 0.2
        
        if "Academic Probation" in academic_standing:
            risk_factors.append("Currently on academic probation")
            risk_score += 0.3
        elif "Academic Warning" in academic_standing:
            risk_factors.append("Currently on academic warning")
            risk_score += 0.2
        
        if failing_courses > 0:
            risk_factors.append(f"Failed {failing_courses} course(s) in academic history")
            risk_score += 0.1 * min(failing_courses, 3)
        
        # Check for academic flags
        academic_flags = [flag for flag in flags if flag.get("type") == "Academic"]
        if academic_flags:
            risk_factors.append(f"{len(academic_flags)} academic concern flag(s) in record")
            risk_score += 0.1 * min(len(academic_flags), 3)
        
        # Determine overall risk level
        if risk_score >= 0.5:
            risk_level = "High"
        elif risk_score >= 0.2:
            risk_level = "Medium"
        else:
            risk_level = "Low"
        
        return {
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "risk_factors": risk_factors if risk_factors else ["No significant academic risk factors identified"]
        }
    
    def _project_current_semester(self, current_courses: List[Dict], overall_gpa: float) -> Dict:
        """Project performance in current semester"""
        if not current_courses:
            return {"projection": "No current courses to project"}
        
        # Base projection on overall GPA
        if overall_gpa >= 3.5:
            likely_outcome = "Strong performance expected to continue"
            projected_gpa = round(min(4.0, overall_gpa + random.uniform(-0.2, 0.1)), 2)
        elif overall_gpa >= 3.0:
            likely_outcome = "Solid performance expected to continue"
            projected_gpa = round(min(4.0, overall_gpa + random.uniform(-0.3, 0.2)), 2)
        elif overall_gpa >= 2.5:
            likely_outcome = "Moderate performance with potential for improvement"
            projected_gpa = round(min(4.0, overall_gpa + random.uniform(-0.2, 0.3)), 2)
        else:
            likely_outcome = "At risk for continued academic difficulties"
            projected_gpa = round(min(4.0, overall_gpa + random.uniform(-0.1, 0.4)), 2)
        
        # Identify potential challenging courses
        challenging_courses = []
        for course in current_courses:
            name = course.get("name", "")
            # Simple heuristic: courses with certain keywords might be challenging
            difficult_keywords = ["advanced", "calculus", "physics", "organic", "quantum", "theory"]
            if any(keyword in name.lower() for keyword in difficult_keywords):
                challenging_courses.append(name)
        
        return {
            "likely_outcome": likely_outcome,
            "projected_semester_gpa": projected_gpa,
            "potential_challenging_courses": challenging_courses if challenging_courses else ["No specific courses identified as challenging"]
        }
    
    def _generate_recommendations(self, student_data: Dict, risk_assessment: Dict) -> List[str]:
        """Generate personalized academic recommendations"""
        recommendations = []
        risk_level = risk_assessment.get("risk_level", "Low")
        
        # Add recommendations based on risk level
        if risk_level == "High":
            recommendations.extend([
                "Schedule weekly academic advising appointments",
                "Connect with tutoring services for all challenging courses",
                "Consider reduced course load for next semester",
                "Develop structured study plan with academic support staff",
                "Utilize campus learning center for study skills development"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "Schedule bi-weekly academic advising check-ins",
                "Connect with tutoring for specific challenging courses",
                "Join study groups for collaborative learning",
                "Attend professor office hours regularly",
                "Consider time management workshop or resources"
            ])
        else:
            recommendations.extend([
                "Maintain regular academic advising each semester",
                "Continue current successful study strategies",
                "Consider mentoring other students or becoming a tutor",
                "Explore research or internship opportunities"
            ])
        
        # Add specific recommendations based on student strengths/weaknesses
        academic_info = student_data.get("academic_info", {})
        personal_info = student_data.get("personal_info", {})
        
        # Career alignment recommendations
        career_goals = personal_info.get("career_goals", [])
        if career_goals:
            recommendations.append(f"Explore courses that align with career goals in {', '.join(career_goals)}")
            recommendations.append("Schedule appointment with career services to discuss academic-career alignment")
        
        return recommendations


class CareerGuidanceTool(BaseTool):
    name: str = "CareerGuidanceTool"
    description: str = "Provides career path recommendations and resources"
    
    def _execute(self, student_info: str) -> str:
        """Provide career guidance based on student information"""
        # Parse student information
        if isinstance(student_info, str):
            try:
                data = json.loads(student_info)
            except json.JSONDecodeError:
                return json.dumps({
                    "error": "Invalid student data format",
                    "details": "The provided data could not be parsed as JSON"
                })
        else:
            data = student_info
        
        # Extract relevant information
        personal_info = data.get("personal_info", {})
        academic_info = data.get("academic_info", {})
        
        major = personal_info.get("major", "Unknown")
        interests = personal_info.get("interests", [])
        career_goals = personal_info.get("career_goals", [])
        year = personal_info.get("year", "Unknown")
        
        # Career recommendations
        career_recommendations = self._recommend_careers(major, interests)
        skill_development = self._skill_development_plan(major, year, career_goals)
        experience_recommendations = self._experience_recommendations(major, year, interests)
        resources = self._career_resources(major, career_goals)
        
        # Generate career timeline
        timeline = self._generate_career_timeline(year, major)
        
        # Compile guidance
        guidance = {
            "career_assessment": {
                "major_alignment": self._assess_major_alignment(major, career_goals, interests),
                "current_preparedness": self._assess_preparedness(year, academic_info),
                "recommended_career_paths": career_recommendations
            },
            "action_plan": {
                "skill_development": skill_development,
                "experience_recommendations": experience_recommendations,
                "timeline": timeline
            },
            "resources": resources,
            "guidance_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(guidance, indent=2)
    
    def _recommend_careers(self, major: str, interests: List[str]) -> List[Dict]:
        """Recommend career paths based on major and interests"""
        # Define career paths by major
        career_paths = {
            "Computer Science": [
                {"title": "Software Engineer", "outlook": "Excellent", "median_salary": "$110,000"},
                {"title": "Data Scientist", "outlook": "Excellent", "median_salary": "$122,000"},
                {"title": "Machine Learning Engineer", "outlook": "Excellent", "median_salary": "$135,000"},
                {"title": "Web Developer", "outlook": "Good", "median_salary": "$77,000"},
                {"title": "Cybersecurity Analyst", "outlook": "Excellent", "median_salary": "$103,000"},
                {"title": "DevOps Engineer", "outlook": "Excellent", "median_salary": "$115,000"}
            ],
            "Psychology": [
                {"title": "Clinical Psychologist", "outlook": "Good", "median_salary": "$82,000"},
                {"title": "HR Specialist", "outlook": "Good", "median_salary": "$65,000"},
                {"title": "Market Research Analyst", "outlook": "Good", "median_salary": "$71,000"},
                {"title": "Social Worker", "outlook": "Moderate", "median_salary": "$55,000"},
                {"title": "School Counselor", "outlook": "Moderate", "median_salary": "$58,000"},
                {"title": "UX Researcher", "outlook": "Good", "median_salary": "$90,000"}
            ],
            "Business Administration": [
                {"title": "Financial Analyst", "outlook": "Good", "median_salary": "$83,000"},
                {"title": "Marketing Manager", "outlook": "Good", "median_salary": "$100,000"},
                {"title": "Management Consultant", "outlook": "Good", "median_salary": "$115,000"},
                {"title": "Operations Manager", "outlook": "Moderate", "median_salary": "$95,000"},
                {"title": "Human Resources Manager", "outlook": "Moderate", "median_salary": "$90,000"},
                {"title": "Entrepreneur", "outlook": "Variable", "median_salary": "Variable"}
            ],
            "Engineering": [
                {"title": "Mechanical Engineer", "outlook": "Good", "median_salary": "$95,000"},
                {"title": "Civil Engineer", "outlook": "Good", "median_salary": "$93,000"},
                {"title": "Electrical Engineer", "outlook": "Good", "median_salary": "$100,000"},
                {"title": "Aerospace Engineer", "outlook": "Moderate", "median_salary": "$116,000"},
                {"title": "Biomedical Engineer", "outlook": "Good", "median_salary": "$92,000"},
                {"title": "Environmental Engineer", "outlook": "Good", "median_salary": "$88,000"}
            ],
            "Biology": [
                {"title": "Research Scientist", "outlook": "Moderate", "median_salary": "$85,000"},
                {"title": "Healthcare Administrator", "outlook": "Good", "median_salary": "$75,000"},
                {"title": "Biotechnologist", "outlook": "Good", "median_salary": "$92,000"},
                {"title": "Pharmaceutical Sales", "outlook": "Moderate", "median_salary": "$86,000"},
                {"title": "Environmental Scientist", "outlook": "Moderate", "median_salary": "$71,000"},
                {"title": "Medical Writer", "outlook": "Good", "median_salary": "$78,000"}
            ]
        }
        
        # Default recommendations if major not found
        default_careers = [
            {"title": "Business Analyst", "outlook": "Good", "median_salary": "$85,000"},
            {"title": "Technical Writer", "outlook": "Moderate", "median_salary": "$74,000"},
            {"title": "Project Manager", "outlook": "Good", "median_salary": "$95,000"}
        ]
        
        # Get career paths for the student's major
        recommended_careers = career_paths.get(major, default_careers)
        
        # Add interest-based variations
        interest_careers = self._get_interest_based_careers(interests)
        if interest_careers:
            recommended_careers.extend(interest_careers)
        
        # Limit to 5 recommendations
        return recommended_careers[:5]
    
    def _get_interest_based_careers(self, interests: List[str]) -> List[Dict]:
        """Generate career recommendations based on interests"""
        interest_careers = {
            "Art": [
                {"title": "UX/UI Designer", "outlook": "Good", "median_salary": "$85,000"},
                {"title": "Graphic Designer", "outlook": "Moderate", "median_salary": "$53,000"}
            ],
            "Music": [
                {"title": "Music Producer", "outlook": "Competitive", "median_salary": "$68,000"},
                {"title": "Audio Engineer", "outlook": "Moderate", "median_salary": "$62,000"}
            ],
            "Writing": [
                {"title": "Content Strategist", "outlook": "Good", "median_salary": "$72,000"},
                {"title": "Technical Writer", "outlook": "Moderate", "median_salary": "$74,000"}
            ],
            "Gaming": [
                {"title": "Game Designer", "outlook": "Competitive", "median_salary": "$85,000"},
                {"title": "QA Tester", "outlook": "Moderate", "median_salary": "$55,000"}
            ],
            "Sustainability": [
                {"title": "Sustainability Consultant", "outlook": "Growing", "median_salary": "$78,000"},
                {"title": "Environmental Planner", "outlook": "Moderate", "median_salary": "$75,000"}
            ],
            "Robotics": [
                {"title": "Robotics Engineer", "outlook": "Excellent", "median_salary": "$110,000"},
                {"title": "Automation Specialist", "outlook": "Good", "median_salary": "$92,000"}
            ],
            "Entrepreneurship": [
                {"title": "Startup Founder", "outlook": "Variable", "median_salary": "Variable"},
                {"title": "Business Development", "outlook": "Good", "median_salary": "$85,000"}
            ],
            "Travel": [
                {"title": "International Business", "outlook": "Moderate", "median_salary": "$80,000"},
                {"title": "Tourism Management", "outlook": "Moderate", "median_salary": "$65,000"}
            ],
            "Cooking": [
                {"title": "Food Scientist", "outlook": "Moderate", "median_salary": "$73,000"},
                {"title": "Nutritionist", "outlook": "Good", "median_salary": "$63,000"}
            ],
        }
        
        # Collect careers based on interests
        recommendations = []
        for interest in interests:
            for key, careers in interest_careers.items():
                if interest.lower() in key.lower() or key.lower() in interest.lower():
                    recommendations.extend(careers)
                    break
        
        return recommendations
    
    def _skill_development_plan(self, major: str, year: str, career_goals: List[str]) -> Dict:
        """Generate skill development recommendations"""
        # Core skills by major
        core_skills = {
            "Computer Science": ["Programming", "Algorithms", "Data Structures", "Problem Solving"],
            "Psychology": ["Research Methods", "Critical Thinking", "Communication", "Analytical Skills"],
            "Business Administration": ["Financial Analysis", "Management", "Marketing", "Strategic Planning"],
            "Engineering": ["Technical Design", "Mathematics", "Problem Solving", "Technical Writing"],
            "Biology": ["Lab Techniques", "Research Methods", "Scientific Writing", "Data Analysis"]
        }
        
        # Soft skills for all majors
        soft_skills = ["Communication", "Teamwork", "Time Management", "Leadership", "Adaptability"]
        
        # Technical skills by career field
        technical_skills = {
            "Software Engineer": ["Java", "Python", "JavaScript", "Cloud Services", "Git"],
            "Data Scientist": ["Python", "R", "Machine Learning", "Statistics", "SQL"],
            "Researcher": ["Research Methods", "Statistics", "Data Analysis", "Technical Writing"],
            "Marketing": ["Digital Marketing", "Social Media", "Analytics", "Content Creation"],
            "Finance": ["Financial Modeling", "Excel", "Accounting", "Data Analysis"],
            "Healthcare": ["Medical Terminology", "Patient Care", "Electronic Health Records"]
        }
        
        # Get appropriate skills based on major and career goals
        major_skills = core_skills.get(major, ["Problem Solving", "Critical Thinking", "Communication"])
        
        # Find relevant technical skills from career goals
        career_technical_skills = []
        for goal in career_goals:
            for career, skills in technical_skills.items():
                if career.lower() in goal.lower():
                    career_technical_skills.extend(skills)
        
        # Remove duplicates
        career_technical_skills = list(set(career_technical_skills))
        
        # Organize by priority based on year
        if year in ["Freshman", "Sophomore"]:
            priority_skills = major_skills[:2] + soft_skills[:2]
            secondary_skills = major_skills[2:] + soft_skills[2:]
            future_skills = career_technical_skills
        else:  # Junior or Senior
            priority_skills = career_technical_skills[:3] + major_skills[:1]
            secondary_skills = soft_skills[:3]
            future_skills = [skill for skill in career_technical_skills if skill not in priority_skills]
        
        return {
            "priority_skills": priority_skills,
            "secondary_skills": secondary_skills,
            "future_skills": future_skills,
            "recommended_courses": self._recommend_courses(major, priority_skills),
            "recommended_certifications": self._recommend_certifications(major, career_goals)
        }
    
    def _recommend_courses(self, major: str, priority_skills: List[str]) -> List[str]:
        """Recommend courses based on major and priority skills"""
        # Map skills to general course recommendations
        skill_courses = {
            "Programming": ["Advanced Programming Techniques", "Web Development", "Mobile App Development"],
            "Data Structures": ["Advanced Data Structures", "Algorithm Design"],
            "Machine Learning": ["Introduction to Machine Learning", "Data Mining", "Neural Networks"],
            "Statistics": ["Applied Statistics", "Statistical Methods", "Data Analysis"],
            "Communication": ["Professional Communication", "Technical Writing", "Public Speaking"],
            "Research Methods": ["Research Design", "Qualitative Research Methods", "Quantitative Analysis"],
            "Leadership": ["Leadership Theory", "Organizational Behavior", "Team Management"],
            "Financial Analysis": ["Corporate Finance", "Financial Statement Analysis", "Investment Analysis"],
            "Technical Design": ["Engineering Design", "CAD Fundamentals", "Product Development"],
            "Problem Solving": ["Critical Thinking", "Design Thinking", "Creative Problem Solving"]
        }
        
        # Collect course recommendations based on priority skills
        courses = []
        for skill in priority_skills:
            skill_course_options = skill_courses.get(skill, [])
            if skill_course_options:
                courses.append(random.choice(skill_course_options))
        
        # Add major-specific courses
        major_courses = {
            "Computer Science": ["Software Engineering", "Database Systems", "Computer Networks"],
            "Psychology": ["Cognitive Psychology", "Social Psychology", "Developmental Psychology"],
            "Business Administration": ["Strategic Management", "Marketing Research", "Business Analytics"],
            "Engineering": ["Thermodynamics", "Fluid Mechanics", "Materials Science"],
            "Biology": ["Molecular Biology", "Genetics", "Physiology"]
        }
        
        major_specific = major_courses.get(major, [])
        if major_specific:
            courses.extend(major_specific[:2])
        
        # Remove duplicates and limit to 5
        return list(set(courses))[:5]
    
    def _recommend_certifications(self, major: str, career_goals: List[str]) -> List[str]:
        """Recommend professional certifications"""
        # Map majors to potential certifications
        major_certs = {
            "Computer Science": [
                "AWS Certified Developer", 
                "Google Cloud Professional Developer",
                "Microsoft Certified: Azure Developer",
                "Certified Information Systems Security Professional (CISSP)"
            ],
            "Psychology": [
                "Board Certified Behavior Analyst (BCBA)",
                "Certified Clinical Mental Health Counselor (CCMHC)",
                "National Certified Counselor (NCC)"
            ],
            "Business Administration": [
                "Project Management Professional (PMP)",
                "Certified Public Accountant (CPA)",
                "Certified Business Analysis Professional (CBAP)",
                "Chartered Financial Analyst (CFA)"
            ],
            "Engineering": [
                "Professional Engineer (PE)",
                "Certified SolidWorks Professional (CSWP)",
                "Leadership in Energy and Environmental Design (LEED)"
            ],
            "Biology": [
                "Clinical Laboratory Scientist/Medical Technologist",
                "Medical Laboratory Technician (MLT)",
                "Registered Environmental Health Specialist"
            ]
        }
        
        # Career-specific certifications
        career_certs = {
            "Software Engineer": ["Oracle Certified Professional Java Programmer", "Certified Kubernetes Administrator"],
            "Data Scientist": ["IBM Data Science Professional", "Microsoft Certified: Data Analyst Associate"],
            "Cybersecurity": ["Certified Ethical Hacker (CEH)", "CompTIA Security+"],
            "Marketing": ["Google Analytics Certification", "HubSpot Content Marketing Certification"],
            "Finance": ["Financial Risk Manager (FRM)", "Certified Financial Planner (CFP)"],
            "Healthcare": ["Certified Health Education Specialist (CHES)", "Certified in Public Health (CPH)"]
        }
        
        # Collect certifications
        certifications = []
        
        # Add major-specific certifications
        major_specific = major_certs.get(major, [])
        if major_specific:
            certifications.extend(random.sample(major_specific, min(2, len(major_specific))))
        
        # Add career-goal specific certifications
        for goal in career_goals:
            for career, certs in career_certs.items():
                if career.lower() in goal.lower():
                    certifications.extend(certs)
                    break
        
        # Return unique certifications
        return list(set(certifications))[:3]
    
    def _experience_recommendations(self, major: str, year: str, interests: List[str]) -> Dict:
        """Recommend experiences based on major, year, and interests"""
        # Base recommendations by year
        if year in ["Freshman", "Sophomore"]:
            internships = ["Entry-level internship", "On-campus research assistant"]
            activities = ["Join relevant student organizations", "Volunteer in related field"]
            events = ["Career fair", "Freshman/Sophomore specific networking events"]
        else:  # Junior or Senior
            internships = ["Industry internship", "Research position"]
            activities = ["Leadership role in student organization", "Industry-related projects"]
            events = ["Industry conferences", "Career fair", "Networking events with professionals"]
        
        # Add major-specific recommendations
        major_specific = {
            "Computer Science": {
                "internships": ["Software development internship", "QA testing internship"],
                "activities": ["Hackathons", "Open source contributions", "Coding competitions"],
                "events": ["Tech meetups", "Developer conferences"]
            },
            "Psychology": {
                "internships": ["Research lab assistant", "Mental health organization intern"],
                "activities": ["Psychology club", "Volunteer at counseling center"],
                "events": ["Psychology conferences", "Mental health awareness events"]
            },
            "Business Administration": {
                "internships": ["Business analyst internship", "Marketing assistant"],
                "activities": ["Case competitions", "Entrepreneurship club"],
                "events": ["Business networking events", "Industry panels"]
            },
            "Engineering": {
                "internships": ["Engineering firm internship", "Research and development"],
                "activities": ["Engineering projects", "Design competitions"],
                "events": ["Industry expositions", "Engineering society events"]
            },
            "Biology": {
                "internships": ["Laboratory research assistant", "Field research aide"],
                "activities": ["Biology club", "Conservation volunteer work"],
                "events": ["Research symposiums", "Scientific conferences"]
            }
        }
        
        # Get major-specific experiences
        major_internships = major_specific.get(major, {}).get("internships", [])
        major_activities = major_specific.get(major, {}).get("activities", [])
        major_events = major_specific.get(major, {}).get("events", [])
        
        # Add interest-based experiences
        interest_experiences = self._get_interest_based_experiences(interests)
        
        # Combine recommendations
        return {
            "internships": list(set(internships + major_internships))[:3],
            "activities": list(set(activities + major_activities + interest_experiences.get("activities", [])))[:3],
            "events": list(set(events + major_events + interest_experiences.get("events", [])))[:3],
            "projects": interest_experiences.get("projects", ["Portfolio development", "Independent research"])[:3]
        }
    
    def _get_interest_based_experiences(self, interests: List[str]) -> Dict:
        """Generate experience recommendations based on interests"""
        interest_experiences = {
            "Art": {
                "activities": ["Art club", "Design portfolio development"],
                "events": ["Art exhibitions", "Design workshops"],
                "projects": ["Visual design project", "Digital portfolio creation"]
            },
            "Music": {
                "activities": ["Music ensemble", "Production club"],
                "events": ["Music festivals", "Industry workshops"],
                "projects": ["Music production portfolio", "Recording project"]
            },
            "Writing": {
                "activities": ["Student publication", "Writing workshop"],
                "events": ["Literary events", "Writing competitions"],
                "projects": ["Blog development", "Content creation portfolio"]
            },
            "Gaming": {
                "activities": ["Game development club", "Esports team"],
                "events": ["Gaming conventions", "Game jams"],
                "projects": ["Game mod development", "Simple game creation"]
            },
            "Sustainability": {
                "activities": ["Environmental club", "Sustainability initiatives"],
                "events": ["Environmental conferences", "Sustainability summits"],
                "projects": ["Campus sustainability project", "Environmental impact study"]
            },
            "Robotics": {
                "activities": ["Robotics club", "Engineering competitions"],
                "events": ["Robotics competitions", "Tech showcases"],
                "projects": ["Robotics project", "Automation system development"]
            }
        }
        
        # Collect experiences based on interests
        activities = []
        events = []
        projects = []
        
        for interest in interests:
            for key, experiences in interest_experiences.items():
                if interest.lower() in key.lower() or key.lower() in interest.lower():
                    activities.extend(experiences.get("activities", []))
                    events.extend(experiences.get("events", []))
                    projects.extend(experiences.get("projects", []))
                    break
        
        return {
            "activities": activities,
            "events": events,
            "projects": projects
        }
    
    def _career_resources(self, major: str, career_goals: List[str]) -> Dict:
        """Provide relevant career resources"""
        # General resources
        general_resources = {
            "campus": [
                "Career Services Center - Resume reviews, interview preparation, job search assistance",
                "Academic Advising - Course selection aligned with career goals",
                "Alumni Network - Connect with graduates in your field"
            ],
            "online": [
                "LinkedIn Learning - Skills development courses",
                "Coursera and edX - Specialized certificates and courses",
                "Handshake - Job and internship platform"
            ]
        }
        
        # Major-specific resources
        major_resources = {
            "Computer Science": {
                "organizations": ["Association for Computing Machinery (ACM)", "IEEE Computer Society"],
                "websites": ["GitHub", "Stack Overflow", "LeetCode", "HackerRank"],
                "publications": ["Communications of the ACM", "IEEE Software"]
            },
            "Psychology": {
                "organizations": ["American Psychological Association", "Psi Chi"],
                "websites": ["PsychINFO", "Psychology Today", "APA PsycNet"],
                "publications": ["Journal of Applied Psychology", "Psychological Science"]
            },
            "Business Administration": {
                "organizations": ["American Management Association", "National Business Association"],
                "websites": ["Harvard Business Review", "Wall Street Journal", "Bloomberg"],
                "publications": ["Harvard Business Review", "Forbes", "Business Insider"]
            },
            "Engineering": {
                "organizations": ["National Society of Professional Engineers", "American Society of Civil Engineers"],
                "websites": ["Engineering.com", "IEEE Spectrum", "Engineering Toolbox"],
                "publications": ["Engineering News-Record", "IEEE Spectrum"]
            },
            "Biology": {
                "organizations": ["American Society for Biochemistry and Molecular Biology", "American Institute of Biological Sciences"],
                "websites": ["Nature.com", "PubMed", "Cell Press"],
                "publications": ["Nature", "Science", "Cell"]
            }
        }
        
        # Get resources for student's major
        major_specific = major_resources.get(major, {
            "organizations": ["Professional association in your field"],
            "websites": ["Industry-specific websites and job boards"],
            "publications": ["Field-specific journals and publications"]
        })
        
        # Combine resources
        resources = {
            "campus_resources": general_resources["campus"],
            "online_platforms": general_resources["online"],
            "professional_organizations": major_specific["organizations"],
            "field_specific_resources": major_specific["websites"],
            "publications": major_specific["publications"]
        }
        
        return resources
    
    def _assess_major_alignment(self, major: str, career_goals: List[str], interests: List[str]) -> Dict:
        """Assess alignment between major, career goals, and interests"""
        alignment_score = 0.0
        alignment_factors = []
        
        # Define typical career paths for majors
        major_careers = {
            "Computer Science": ["Software Engineer", "Data Scientist", "IT Specialist", "Web Developer", "Cybersecurity"],
            "Psychology": ["Counselor", "Therapist", "HR Specialist", "Researcher", "Social Worker"],
            "Business Administration": ["Manager", "Analyst", "Consultant", "Marketing", "Finance"],
            "Engineering": ["Engineer", "Designer", "Developer", "Project Manager", "Researcher"],
            "Biology": ["Researcher", "Healthcare", "Scientist", "Environmental", "Pharmaceutical"]
        }
        
        # Check career goal alignment with major
        major_career_paths = major_careers.get(major, [])
        career_alignment = 0
        
        for goal in career_goals:
            for path in major_career_paths:
                if path.lower() in goal.lower():
                    career_alignment += 1
                    alignment_factors.append(f"Career goal '{goal}' aligns well with {major} degree")
                    break
        
        # Calculate career alignment score
        if career_goals:
            career_alignment_score = min(career_alignment / len(career_goals), 1.0)
            alignment_score += career_alignment_score * 0.6  # Weight career alignment at 60%
        else:
            alignment_score += 0.3  # Neutral if no goals specified
            alignment_factors.append(f"No specific career goals provided to assess alignment with {major}")
        
        # Assess interest alignment (more subjective)
        interest_alignment = {
            "Computer Science": ["technology", "programming", "computing", "software", "gaming", "data", "robotics"],
            "Psychology": ["people", "behavior", "mental", "counseling", "social", "research", "development"],
            "Business Administration": ["business", "management", "entrepreneurship", "marketing", "finance", "leadership"],
            "Engineering": ["design", "building", "mechanics", "systems", "robotics", "technology"],
            "Biology": ["science", "health", "environment", "research", "nature", "medicine", "laboratory"]
        }
        
        # Check interest alignment
        interest_keywords = interest_alignment.get(major, [])
        interest_matches = 0
        
        for interest in interests:
            for keyword in interest_keywords:
                if keyword.lower() in interest.lower() or interest.lower() in keyword.lower():
                    interest_matches += 1
                    alignment_factors.append(f"Interest in '{interest}' complements {major} studies")
                    break
        
        # Calculate interest alignment score
        if interests:
            interest_alignment_score = min(interest_matches / len(interests), 1.0)
            alignment_score += interest_alignment_score * 0.4  # Weight interest alignment at 40%
        else:
            alignment_score += 0.2  # Neutral if no interests specified
            alignment_factors.append("No specific interests provided to assess alignment with major")
        
        # Determine overall alignment level
        if alignment_score >= 0.8:
            alignment_level = "Excellent"
            recommendation = f"Current major ({major}) is very well-aligned with career goals and interests"
        elif alignment_score >= 0.6:
            alignment_level = "Good"
            recommendation = f"Current major ({major}) is generally well-aligned with career goals and interests"
        elif alignment_score >= 0.4:
            alignment_level = "Moderate"
            recommendation = f"Current major ({major}) has some alignment with goals and interests, but consider complementary coursework"
        else:
            alignment_level = "Low"
            recommendation = f"Consider exploring whether current major ({major}) is the best fit for stated goals and interests"
        
        if not alignment_factors:
            alignment_factors.append("Insufficient information to identify specific alignment factors")
        
        return {
            "alignment_level": alignment_level,
            "alignment_score": round(alignment_score, 2),
            "alignment_factors": alignment_factors,
            "recommendation": recommendation
        }
    
    def _assess_preparedness(self, year: str, academic_info: Dict) -> Dict:
        """Assess career preparedness based on academic status"""
        # Base preparedness on year
        year_progress = {
            "Freshman": 0.2,
            "Sophomore": 0.4,
            "Junior": 0.6,
            "Senior": 0.8,
            "Graduate": 0.9
        }
        
        base_score = year_progress.get(year, 0.5)
        
        # Adjust for GPA
        gpa = academic_info.get("overall_gpa", 0.0)
        if gpa >= 3.5:
            gpa_modifier = 0.1
        elif gpa >= 3.0:
            gpa_modifier = 0.05
        elif gpa < 2.5:
            gpa_modifier = -0.05
        else:
            gpa_modifier = 0
        
        preparedness_score = base_score + gpa_modifier
        preparedness_score = max(0.1, min(1.0, preparedness_score))  # Ensure between 0.1 and 1.0
        
        # Generate assessment
        if preparedness_score >= 0.8:
            level = "High"
            assessment = "Well-prepared for career entry with current trajectory"
        elif preparedness_score >= 0.6:
            level = "Good"
            assessment = "On track for career readiness with continued progress"
        elif preparedness_score >= 0.4:
            level = "Moderate"
            assessment = "Making progress toward career readiness, with opportunities for improvement"
        else:
            level = "Early Stage"
            assessment = "Beginning career preparation journey with significant development ahead"
        
        # Generate preparedness factors
        preparedness_factors = []
        
        # Year-based factors
        year_factors = {
            "Freshman": ["Early in academic journey with time to explore", "Building foundational knowledge"],
            "Sophomore": ["Developing core academic skills", "Beginning to specialize in major"],
            "Junior": ["Advancing in specialized knowledge", "Time to pursue internships and experience"],
            "Senior": ["Finalizing academic requirements", "Transitioning to job search and career entry"],
            "Graduate": ["Advanced specialized knowledge", "Research or professional focus"]
        }
        
        preparedness_factors.extend(year_factors.get(year, []))
        
        # GPA-based factors
        if gpa >= 3.5:
            preparedness_factors.append("Strong academic performance demonstrates mastery of material")
        elif gpa >= 3.0:
            preparedness_factors.append("Solid academic record shows competence in field")
        elif gpa >= 2.5:
            preparedness_factors.append("Academic performance shows room for strengthening in some areas")
        else:
            preparedness_factors.append("Academic performance suggests need for additional support and improvement")
        
        return {
            "preparedness_level": level,
            "preparedness_score": round(preparedness_score, 2),
            "assessment": assessment,
            "preparedness_factors": preparedness_factors
        }
    
    def _generate_career_timeline(self, year: str, major: str) -> List[Dict]:
        """Generate a career preparation timeline"""
        timeline = []
        
        # Define standard milestones by year
        standard_milestones = {
            "Freshman": [
                {"timeframe": "First Semester", "milestone": "Explore introductory courses and student organizations"},
                {"timeframe": "Second Semester", "milestone": "Meet with academic advisor to discuss major and career interests"},
                {"timeframe": "Summer", "milestone": "Volunteer or part-time job to build basic work experience"}
            ],
            "Sophomore": [
                {"timeframe": "First Semester", "milestone": "Join major-specific student organizations"},
                {"timeframe": "Second Semester", "milestone": "Prepare resume and LinkedIn profile"},
                {"timeframe": "Summer", "milestone": "Seek entry-level internship or research opportunity"}
            ],
            "Junior": [
                {"timeframe": "First Semester", "milestone": "Attend career fairs and networking events"},
                {"timeframe": "Second Semester", "milestone": "Apply for summer internships and research positions"},
                {"timeframe": "Summer", "milestone": "Complete career-focused internship"}
            ],
            "Senior": [
                {"timeframe": "First Semester", "milestone": "Begin job search or graduate school applications"},
                {"timeframe": "Second Semester", "milestone": "Interview for full-time positions or finalize post-graduation plans"},
                {"timeframe": "Post-Graduation", "milestone": "Transition to career or advanced education"}
            ]
        }
        
        # Add major-specific milestones
        major_milestones = {
            "Computer Science": [
                {"year": "Freshman", "timeframe": "Second Semester", "milestone": "Build first programming portfolio project"},
                {"year": "Sophomore", "timeframe": "Summer", "milestone": "Contribute to open source projects"},
                {"year": "Junior", "timeframe": "First Semester", "milestone": "Prepare for technical interviews"},
                {"year": "Senior", "timeframe": "First Semester", "milestone": "Complete capstone project for portfolio"}
            ],
            "Psychology": [
                {"year": "Freshman", "timeframe": "Second Semester", "milestone": "Begin exploring research opportunities"},
                {"year": "Sophomore", "timeframe": "Summer", "milestone": "Volunteer at mental health organization"},
                {"year": "Junior", "timeframe": "Second Semester", "milestone": "Prepare for GRE if considering graduate school"},
                {"year": "Senior", "timeframe": "First Semester", "milestone": "Complete independent research project"}
            ],
            "Business Administration": [
                {"year": "Freshman", "timeframe": "Second Semester", "milestone": "Job shadow a professional in your field"},
                {"year": "Sophomore", "timeframe": "First Semester", "milestone": "Participate in case competition"},
                {"year": "Junior", "timeframe": "Summer", "milestone": "Internship with business in target industry"},
                {"year": "Senior", "timeframe": "Second Semester", "milestone": "Network with alumni in desired field"}
            ],
            "Engineering": [
                {"year": "Freshman", "timeframe": "Summer", "milestone": "Complete relevant certification or workshop"},
                {"year": "Sophomore", "timeframe": "Second Semester", "milestone": "Join engineering project team"},
                {"year": "Junior", "timeframe": "First Semester", "milestone": "Prepare for FE exam if applicable"},
                {"year": "Senior", "timeframe": "First Semester", "milestone": "Complete senior design project"}
            ],
            "Biology": [
                {"year": "Freshman", "timeframe": "Second Semester", "milestone": "Explore research lab opportunities"},
                {"year": "Sophomore", "timeframe": "Summer", "milestone": "Field or laboratory research experience"},
                {"year": "Junior", "timeframe": "Second Semester", "milestone": "Prepare for MCAT/GRE if applicable"},
                {"year": "Senior", "timeframe": "First Semester", "milestone": "Complete thesis or capstone research"}
            ]
        }
        
        # Get standard timeline for student's year
        year_index = ["Freshman", "Sophomore", "Junior", "Senior"].index(year) if year in ["Freshman", "Sophomore", "Junior", "Senior"] else 0
        
        # Add all relevant future milestones
        for current_year in ["Freshman", "Sophomore", "Junior", "Senior"][year_index:]:
            timeline.extend(standard_milestones.get(current_year, []))
        
        # Add major-specific milestones for current and future years
        for milestone in major_milestones.get(major, []):
            milestone_year = milestone.get("year")
            if milestone_year in ["Freshman", "Sophomore", "Junior", "Senior"]:
                milestone_year_index = ["Freshman", "Sophomore", "Junior", "Senior"].index(milestone_year)
                if milestone_year_index >= year_index:
                    timeline.append({
                        "timeframe": f"{milestone_year}: {milestone.get('timeframe')}",
                        "milestone": milestone.get('milestone')
                    })
        
        # Sort timeline (simple approach based on year mention)
        def get_year_index(item):
            timeframe = item.get("timeframe", "")
            if "Freshman" in timeframe:
                return 0
            elif "Sophomore" in timeframe:
                return 1
            elif "Junior" in timeframe:
                return 2
            elif "Senior" in timeframe:
                return 3
            elif "Post-Graduation" in timeframe:
                return 4
            else:
                return 5
        
        timeline.sort(key=get_year_index)
        
        return timeline


class StudyPatternAnalysisTool(BaseTool):
    name: str = "StudyPatternAnalysisTool"
    description: str = "Analyzes student study habits and patterns"
    
    def _execute(self, input_data: str) -> str:
        """Analyze study patterns and habits from student data and input"""
        # Parse input data
        if isinstance(input_data, str):
            try:
                data = json.loads(input_data)
            except json.JSONDecodeError:
                # If not JSON, treat as direct student input
                data = {"input": input_data}
        else:
            data = input_data
        
        # Extract relevant information
        student_input = data.get("input", "")
        academic_info = data.get("academic_info", {})
        personal_info = data.get("personal_info", {})
        
        # Generate synthetic study pattern data if not provided
        study_patterns = data.get("study_patterns", self._generate_study_patterns())
        
        # Analyze study habits from input text
        text_analysis = self._analyze_study_habits_from_text(student_input)
        
        # Infer learning style
        learning_style = self._infer_learning_style(study_patterns, text_analysis)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(learning_style, academic_info, text_analysis)
        
        # Compile analysis
        analysis = {
            "study_pattern_assessment": {
                "current_patterns": study_patterns,
                "text_insights": text_analysis,
                "learning_style": learning_style
            },
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(analysis, indent=2)
    
    def _generate_study_patterns(self) -> Dict:
        """Generate synthetic study pattern data"""
        return {
            "average_study_time": {
                "hours_per_week": random.randint(5, 30),
                "consistency": random.choice(["High", "Medium", "Low"]),
                "session_length": random.randint(30, 180)  # minutes
            },
            "study_environment": {
                "preferred_location": random.choice(["Library", "Dorm/Home", "Cafe", "Study Room", "Outdoors"]),
                "noise_level": random.choice(["Silent", "Quiet", "Moderate", "Background music"]),
                "solo_vs_group": random.choice(["Always solo", "Mainly solo", "Mixed", "Mainly group", "Always group"])
            },
            "study_techniques": {
                "note_taking": random.choice(["Detailed", "Minimal", "Visual", "Sporadic", "None"]),
                "practice_problems": random.choice(["Frequent", "Occasional", "Rare"]),
                "re_reading": random.choice(["Frequent", "Occasional", "Rare"]),
                "flashcards": random.choice(["Frequent", "Occasional", "Rare"]),
                "summarization": random.choice(["Frequent", "Occasional", "Rare"])
            },
            "technology_use": {
                "digital_notes": random.choice(["Frequent", "Occasional", "Rare"]),
                "online_resources": random.choice(["Frequent", "Occasional", "Rare"]),
                "educational_apps": random.choice(["Frequent", "Occasional", "Rare"]),
                "potential_distractions": random.choice(["High", "Medium", "Low"])
            },
            "time_management": {
                "planning": random.choice(["Structured", "Flexible", "Minimal", "None"]),
                "procrastination": random.choice(["High", "Medium", "Low"]),
                "deadline_approach": random.choice(["Well in advance", "Just-in-time", "Last-minute"])
            }
        }
    
    def _analyze_study_habits_from_text(self, input_text: str) -> Dict:
        """Extract study habit information from student input text"""
        # Initialize analysis
        analysis = {
            "time_management_indicators": [],
            "environment_indicators": [],
            "technique_indicators": [],
            "challenge_indicators": [],
            "preference_indicators": []
        }
        
        # Skip if no input
        if not input_text:
            return {
                "insight_confidence": "None",
                "insights": ["No text input provided for analysis"]
            }
        
        # Define indicator keywords
        indicators = {
            "time_management_indicators": {
                "good": ["planner", "schedule", "routine", "organized", "ahead of time", "plan ahead"],
                "poor": ["procrastinate", "last minute", "cram", "rush", "forget to", "run out of time"]
            },
            "environment_indicators": {
                "preferences": ["library", "quiet", "music", "home", "dorm", "cafe", "study room", "group", "alone"]
            },
            "technique_indicators": {
                "active": ["practice problems", "flashcards", "quiz myself", "teach others", "summarize", "discuss"],
                "passive": ["re-read", "highlight", "review notes", "listen to lectures", "watch videos"]
            },
            "challenge_indicators": {
                "common": ["distracted", "focus", "concentrate", "understand", "remember", "confused", "stressed", 
                          "overwhelmed", "bored", "tired", "motivation"]
            },
            "preference_indicators": {
                "visual": ["diagram", "chart", "visual", "see", "picture", "draw", "watch"],
                "auditory": ["listen", "discuss", "hear", "talk", "audio", "sound"],
                "reading/writing": ["write", "read", "note", "text", "words"],
                "kinesthetic": ["practice", "hands-on", "do", "experience", "active", "movement"]
            }
        }
        
        # Simple keyword analysis
        input_lower = input_text.lower()
        
        # Check for time management indicators
        for category, keywords in indicators["time_management_indicators"].items():
            for keyword in keywords:
                if keyword in input_lower:
                    analysis["time_management_indicators"].append(f"{category}: '{keyword}'")
        
        # Check for environment preferences
        for keyword in indicators["environment_indicators"]["preferences"]:
            if keyword in input_lower:
                analysis["environment_indicators"].append(f"Mentioned: '{keyword}'")
        
        # Check for study techniques
        for category, keywords in indicators["technique_indicators"].items():
            for keyword in keywords:
                if keyword in input_lower:
                    analysis["technique_indicators"].append(f"{category}: '{keyword}'")
        
        # Check for challenges
        for keyword in indicators["challenge_indicators"]["common"]:
            if keyword in input_lower:
                analysis["challenge_indicators"].append(f"Mentioned: '{keyword}'")
        
        # Check for learning style preferences
        for style, keywords in indicators["preference_indicators"].items():
            for keyword in keywords:
                if keyword in input_lower:
                    analysis["preference_indicators"].append(f"{style}: '{keyword}'")
        
        # Determine confidence in insights
        total_indicators = sum(len(indicators) for indicators in analysis.values())
        
        if total_indicators >= 10:
            confidence = "High"
        elif total_indicators >= 5:
            confidence = "Medium"
        elif total_indicators > 0:
            confidence = "Low"
        else:
            confidence = "None"
        
        # Generate key insights
        insights = []
        
        if analysis["time_management_indicators"]:
            if any("good" in indicator for indicator in analysis["time_management_indicators"]):
                insights.append("Student appears to have structured time management approach")
            elif any("poor" in indicator for indicator in analysis["time_management_indicators"]):
                insights.append("Student may struggle with time management and procrastination")
        
        if analysis["technique_indicators"]:
            if any("active" in indicator for indicator in analysis["technique_indicators"]):
                insights.append("Student uses active learning techniques")
            elif any("passive" in indicator for indicator in analysis["technique_indicators"]):
                insights.append("Student relies primarily on passive study methods")
        
        if analysis["challenge_indicators"]:
            if len(analysis["challenge_indicators"]) >= 3:
                insights.append("Student mentions multiple study challenges that should be addressed")
            else:
                insights.append("Student mentions some specific study challenges")
        
        # Add default insight if none generated
        if not insights:
            insights.append("Limited study habit information available from text")
        
        return {
            "insight_confidence": confidence,
            "detailed_indicators": analysis,
            "insights": insights
        }
    
    def _infer_learning_style(self, study_patterns: Dict, text_analysis: Dict) -> Dict:
        """Determine likely learning style preferences"""
        # Initialize style scores
        styles = {
            "visual": 0,
            "auditory": 0,
            "reading_writing": 0,
            "kinesthetic": 0
        }
        
        # Analyze study techniques for style indicators
        techniques = study_patterns.get("study_techniques", {})
        if techniques.get("note_taking") in ["Detailed", "Visual"]:
            styles["visual"] += 1
            styles["reading_writing"] += 1
        
        if techniques.get("practice_problems") == "Frequent":
            styles["kinesthetic"] += 2
        
        if techniques.get("flashcards") == "Frequent":
            styles["visual"] += 1
            styles["reading_writing"] += 1
        
        # Analyze environment preferences
        environment = study_patterns.get("study_environment", {})
        if environment.get("solo_vs_group") in ["Mainly group", "Always group"]:
            styles["auditory"] += 1
        
        if environment.get("noise_level") == "Background music":
            styles["auditory"] += 1
        
        # Analyze technology use
        technology = study_patterns.get("technology_use", {})
        if technology.get("digital_notes") == "Frequent":
            styles["visual"] += 1
            styles["reading_writing"] += 1
        
        if technology.get("online_resources") == "Frequent":
            styles["visual"] += 1
        
        # Add insights from text analysis
        preference_indicators = text_analysis.get("detailed_indicators", {}).get("preference_indicators", [])
        for indicator in preference_indicators:
            if "visual" in indicator.lower():
                styles["visual"] += 1
            elif "auditory" in indicator.lower():
                styles["auditory"] += 1
            elif "reading/writing" in indicator.lower():
                styles["reading_writing"] += 1
            elif "kinesthetic" in indicator.lower():
                styles["kinesthetic"] += 1
        
        # Determine primary and secondary styles
        primary_style = max(styles, key=styles.get)
        styles_copy = styles.copy()
        styles_copy.pop(primary_style)
        secondary_style = max(styles_copy, key=styles_copy.get)
        
        # Format style names for readability
        style_names = {
            "visual": "Visual",
            "auditory": "Auditory",
            "reading_writing": "Reading/Writing",
            "kinesthetic": "Kinesthetic"
        }
        
        # Generate style descriptions
        style_descriptions = {
            "visual": "Learns best through visual aids, diagrams, charts, and seeing information",
            "auditory": "Learns best through listening, discussing, and processing information verbally",
            "reading_writing": "Learns best through reading materials and writing notes or summaries",
            "kinesthetic": "Learns best through hands-on activities, practice, and physical engagement"
        }
        
        # Prepare learning style assessment
        learning_style = {
            "primary_style": style_names.get(primary_style),
            "primary_description": style_descriptions.get(primary_style),
            "secondary_style": style_names.get(secondary_style),
            "secondary_description": style_descriptions.get(secondary_style),
            "style_breakdown": {style_names.get(s): score for s, score in styles.items()},
            "assessment_confidence": "Medium"  # Default confidence level
        }
        
        return learning_style
    
    def _generate_recommendations(self, learning_style: Dict, academic_info: Dict, text_analysis: Dict) -> Dict:
        """Generate personalized study recommendations"""
        # Get primary learning style
        primary_style = learning_style.get("primary_style", "")
        secondary_style = learning_style.get("secondary_style", "")
        
        # Base recommendations by learning style
        style_recommendations = {
            "Visual": [
                "Use color-coding in notes to organize information",
                "Create mind maps or diagrams to visualize complex concepts",
                "Watch video tutorials or demonstrations when available",
                "Use flashcards with visual elements or symbols",
                "Draw or sketch concepts to enhance understanding"
            ],
            "Auditory": [
                "Record lectures and listen to them during review",
                "Read notes aloud when studying",
                "Participate in study groups with discussion",
                "Explain concepts verbally to others",
                "Use voice memos for quick notes and ideas"
            ],
            "Reading/Writing": [
                "Take detailed notes during lectures and readings",
                "Rewrite key information in your own words",
                "Create outlines and summaries of content",
                "Use written flashcards for key terms and concepts",
                "Write practice essays or responses to potential questions"
            ],
            "Kinesthetic": [
                "Incorporate movement during study sessions",
                "Use hands-on practice whenever possible",
                "Create physical models or manipulatives",
                "Take short walks between study topics",
                "Apply concepts through labs, projects, or real-world applications"
            ]
        }
        
        # Get recommendations for primary and secondary styles
        primary_style_recs = style_recommendations.get(primary_style, [])
        secondary_style_recs = style_recommendations.get(secondary_style, [])
        
        # Select recommendations (3 primary, 2 secondary)
        selected_style_recs = random.sample(primary_style_recs, min(3, len(primary_style_recs)))
        if secondary_style_recs:
            selected_style_recs.extend(random.sample(secondary_style_recs, min(2, len(secondary_style_recs))))
        
        # Add time management recommendations based on text analysis
        time_management_recs = [
            "Create a weekly study schedule with specific time blocks",
            "Break large assignments into smaller, manageable tasks",
            "Set specific, achievable goals for each study session",
            "Use the Pomodoro Technique (25 min study, 5 min break)",
            "Plan study sessions at times when you're naturally most alert",
            "Schedule buffer time before deadlines to avoid last-minute rushes",
            "Use a digital or physical planner to track assignments and exams"
        ]
        
        # Check text analysis for time management issues
        time_indicators = text_analysis.get("detailed_indicators", {}).get("time_management_indicators", [])
        if any("poor" in indicator for indicator in time_indicators):
            selected_time_recs = random.sample(time_management_recs, min(3, len(time_management_recs)))
        else:
            selected_time_recs = random.sample(time_management_recs, min(1, len(time_management_recs)))
        
        # Add study environment recommendations
        environment_recs = [
            "Find a consistent study location with minimal distractions",
            "Consider if background noise or silence helps your concentration",
            "Ensure proper lighting and comfortable seating",
            "Remove digital distractions during focused study time",
            "Try different study environments to discover what works best",
            "Consider if group or solo studying is more effective for different subjects"
        ]
        
        selected_environment_recs = random.sample(environment_recs, min(2, len(environment_recs)))
        
        # Add technology recommendations
        tech_recs = [
            "Use apps like Forest or Focus To-Do to manage study sessions",
            "Try digital flashcard tools like Anki or Quizlet",
            "Consider note-taking apps with organization features",
            "Use website blockers during focused study time",
            "Explore subject-specific learning tools and simulations"
        ]
        
        selected_tech_recs = random.sample(tech_recs, min(2, len(tech_recs)))
        
        # Compile all recommendations
        all_recommendations = {
            "learning_style_based": selected_style_recs,
            "time_management": selected_time_recs,
            "study_environment": selected_environment_recs,
            "technology_tools": selected_tech_recs
        }
        
        return all_recommendations


class ResourceRecommendationTool(BaseTool):
    name: str = "ResourceRecommendationTool"
    description: str = "Recommends relevant academic and support resources"
    
    def _execute(self, student_needs: str) -> str:
        """Recommend resources based on student needs and data"""
        # Parse student needs
        if isinstance(student_needs, str):
            try:
                data = json.loads(student_needs)
            except json.JSONDecodeError:
                # If not JSON, treat as direct input
                data = {"input": student_needs}
        else:
            data = student_needs
        
        # Extract relevant information
        student_input = data.get("input", "")
        academic_info = data.get("academic_info", {})
        personal_info = data.get("personal_info", {})
        support_history = data.get("support_history", {})
        
        # Identify need categories from input
        needs = self._identify_needs(student_input, academic_info, support_history)
        
        # Get resources based on identified needs
        academic_resources = self._get_academic_resources(needs, personal_info)
        wellness_resources = self._get_wellness_resources(needs)
        career_resources = self._get_career_resources(needs, personal_info)
        community_resources = self._get_community_resources(needs, personal_info)
        technology_resources = self._get_technology_resources(needs, academic_info)
        
        # Compile recommendations
        recommendations = {
            "identified_needs": needs,
            "resources": {
                "academic_support": academic_resources,
                "wellness_support": wellness_resources,
                "career_development": career_resources,
                "community_engagement": community_resources,
                "technology_tools": technology_resources
            },
            "personalized_recommendations": self._generate_personalized_recommendations(needs, personal_info, academic_info),
            "recommendation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return json.dumps(recommendations, indent=2)
    
    def _identify_needs(self, student_input: str, academic_info: Dict, support_history: Dict) -> Dict:
        """Identify student needs from input and data"""
        identified_needs = {
            "academic_needs": [],
            "wellness_needs": [],
            "career_needs": [],
            "community_needs": [],
            "technology_needs": []
        }
        
        # Check for academic needs based on GPA and flags
        gpa = academic_info.get("overall_gpa", 0.0)
        if gpa < 2.5:
            identified_needs["academic_needs"].append({
                "need": "Academic performance improvement",
                "confidence": "High",
                "source": "GPA below 2.5"
            })
        
        # Check for academic flags
        flags = support_history.get("flags", [])
        academic_flags = [flag for flag in flags if flag.get("type") == "Academic"]
        if academic_flags:
            identified_needs["academic_needs"].append({
                "need": "Address academic concerns",
                "confidence": "High",
                "source": "Academic flags in record"
            })
        
        # Check for wellness flags
        wellness_flags = [flag for flag in flags if flag.get("type") == "Well-being"]
        if wellness_flags:
            identified_needs["wellness_needs"].append({
                "need": "Well-being support",
                "confidence": "High",
                "source": "Well-being flags in record"
            })
        
        # Analyze student input for needs
        if student_input:
            # Academic need keywords
            academic_keywords = ["struggle", "difficult", "confused", "fail", "behind", "trouble", 
                               "understand", "study", "homework", "assignment", "tutor", "help with"]
            
            # Wellness need keywords
            wellness_keywords = ["stress", "anxiety", "overwhelm", "depress", "sleep", "tired", 
                              "exhausted", "worry", "lonely", "sad", "upset", "mental health"]
            
            # Career need keywords
            career_keywords = ["career", "job", "internship", "resume", "interview", "future", 
                             "profession", "work", "employment", "major", "graduate"]
            
            # Community need keywords
            community_keywords = ["friend", "connect", "involved", "belong", "club", 
                               "organization", "activity", "event", "social", "network"]
            
            # Technology need keywords
            technology_keywords = ["computer", "software", "online", "digital", "internet", 
                                "access", "technology", "device", "laptop", "app"]
            
            # Simple keyword analysis
            input_lower = student_input.lower()
            
            # Check for academic needs
            for keyword in academic_keywords:
                if keyword in input_lower:
                    need = "Academic support and resources"
                    if not any(existing_need.get("need") == need for existing_need in identified_needs["academic_needs"]):
                        identified_needs["academic_needs"].append({
                            "need": need,
                            "confidence": "Medium",
                            "source": f"Mentioned '{keyword}' in input"
                        })
                    break
            
            # Check for wellness needs
            for keyword in wellness_keywords:
                if keyword in input_lower:
                    need = "Wellness and mental health support"
                    if not any(existing_need.get("need") == need for existing_need in identified_needs["wellness_needs"]):
                        identified_needs["wellness_needs"].append({
                            "need": need,
                            "confidence": "Medium",
                            "source": f"Mentioned '{keyword}' in input"
                        })
                    break
            
            # Check for career needs
            for keyword in career_keywords:
                if keyword in input_lower:
                    need = "Career guidance and professional development"
                    if not any(existing_need.get("need") == need for existing_need in identified_needs["career_needs"]):
                        identified_needs["career_needs"].append({
                            "need": need,
                            "confidence": "Medium",
                            "source": f"Mentioned '{keyword}' in input"
                        })
                    break
            
            # Check for community needs
            for keyword in community_keywords:
                if keyword in input_lower:
                    need = "Community engagement and social connection"
                    if not any(existing_need.get("need") == need for existing_need in identified_needs["community_needs"]):
                        identified_needs["community_needs"].append({
                            "need": need,
                            "confidence": "Medium",
                            "source": f"Mentioned '{keyword}' in input"
                        })
                    break
            
            # Check for technology needs
            for keyword in technology_keywords:
                if keyword in input_lower:
                    need = "Technology tools and resources"
                    if not any(existing_need.get("need") == need for existing_need in identified_needs["technology_needs"]):
                        identified_needs["technology_needs"].append({
                            "need": need,
                            "confidence": "Medium",
                            "source": f"Mentioned '{keyword}' in input"
                        })
                    break
        
        # If a student is in first year, add community resources
        if personal_info.get("year") == "Freshman" and not identified_needs["community_needs"]:
            identified_needs["community_needs"].append({
                "need": "First-year student community integration",
                "confidence": "Medium",
                "source": "First-year student status"
            })
        
        # If no needs identified, add general resources
        all_needs = [need for category_needs in identified_needs.values() for need in category_needs]
        if not all_needs:
            # Add general academic resources
            identified_needs["academic_needs"].append({
                "need": "General academic resources",
                "confidence": "Low",
                "source": "Default recommendation"
            })
            
            # Add general wellness resources
            identified_needs["wellness_needs"].append({
                "need": "General wellness resources",
                "confidence": "Low",
                "source": "Default recommendation"
            })
        
        return identified_needs
    
    def _get_academic_resources(self, needs: Dict, personal_info: Dict) -> List[Dict]:
        """Get relevant academic resources based on identified needs"""
        academic_resources = []
        major = personal_info.get("major", "")
        
        # General academic resources
        general_resources = [
            {
                "name": "Academic Success Center",
                "description": "Offers tutoring, academic coaching, and study skills workshops",
                "contact": "success.center@university.edu | 555-123-4567",
                "location": "Student Success Building, Room 200"
            },
            {
                "name": "University Library",
                "description": "Provides research assistance, study spaces, and academic resources",
                "contact": "library@university.edu | 555-123-8900",
                "location": "Main Campus Library"
            },
            {
                "name": "Writing Center",
                "description": "Assists with papers, essays, and writing assignments at any stage",
                "contact": "writing.center@university.edu | 555-123-5678",
                "location": "Humanities Building, Room 100"
            }
        ]
        
        # Add major-specific resources
        major_resources = {
            "Computer Science": [
                {
                    "name": "CS Tutoring Lab",
                    "description": "Peer tutoring for programming and computer science courses",
                    "contact": "cs.tutoring@university.edu | 555-234-5678",
                    "location": "Computing Center, Room 302"
                },
                {
                    "name": "Code Debugging Workshops",
                    "description": "Weekly sessions focused on debugging and problem-solving",
                    "contact": "cs.dept@university.edu | 555-234-5679",
                    "location": "Computing Center, Lab 201"
                }
            ],
            "Psychology": [
                {
                    "name": "Psychology Study Group",
                    "description": "Weekly study sessions for psychology courses",
                    "contact": "psych.dept@university.edu | 555-345-6789",
                    "location": "Psychology Building, Room 120"
                },
                {
                    "name": "Research Methods Lab",
                    "description": "Support for research methods and statistics courses",
                    "contact": "methods.lab@university.edu | 555-345-6780",
                    "location": "Psychology Building, Room 210"
                }
            ],
            "Business Administration": [
                {
                    "name": "Business Analytics Center",
                    "description": "Support for business statistics and analytics courses",
                    "contact": "business.analytics@university.edu | 555-456-7890",
                    "location": "Business Building, Room 300"
                },
                {
                    "name": "Case Study Workshop Series",
                    "description": "Regular workshops on analyzing and presenting business cases",
                    "contact": "case.studies@university.edu | 555-456-7891",
                    "location": "Business Building, Room 150"
                }
            ],
            "Engineering": [
                {
                    "name": "Engineering Tutoring Lab",
                    "description": "Support for core engineering courses and problem-solving",
                    "contact": "eng.tutoring@university.edu | 555-567-8901",
                    "location": "Engineering Complex, Room 220"
                },
                {
                    "name": "Design Project Support",
                    "description": "Assistance with engineering design projects and software",
                    "contact": "eng.design@university.edu | 555-567-8902",
                    "location": "Engineering Complex, Lab 150"
                }
            ],
            "Biology": [
                {
                    "name": "Biology Study Center",
                    "description": "Tutoring and resources for biology courses",
                    "contact": "bio.study@university.edu | 555-678-9012",
                    "location": "Science Building, Room 340"
                },
                {
                    "name": "Lab Skills Workshop",
                    "description": "Hands-on sessions to develop laboratory techniques",
                    "contact": "bio.lab@university.edu | 555-678-9013",
                    "location": "Science Building, Lab 220"
                }
            ]
        }
        
        # Check for specific academic needs
        has_performance_need = False
        for need in needs.get("academic_needs", []):
            if "performance" in need.get("need", "").lower():
                has_performance_need = True
                break
        
        # Add general resources
        if has_performance_need:
            # Add all general resources for students with performance issues
            academic_resources.extend(general_resources)
        else:
            # Add just two general resources for other students
            if general_resources:
                academic_resources.extend(random.sample(general_resources, min(2, len(general_resources))))
        
        # Add major-specific resources if available
        major_specific = major_resources.get(major, [])
        if major_specific:
            academic_resources.extend(major_specific)
        
        # Ensure each resource has a type field
        for resource in academic_resources:
            resource["type"] = "academic"
        
        return academic_resources
    
    def _get_wellness_resources(self, needs: Dict) -> List[Dict]:
        """Get relevant wellness resources based on identified needs"""
        wellness_resources = []
        
        # General wellness resources
        general_resources = [
            {
                "name": "University Counseling Center",
                "description": "Offers individual and group counseling services",
                "contact": "counseling@university.edu | 555-789-0123",
                "location": "Health Center, 2nd Floor"
            },
            {
                "name": "Student Wellness Office",
                "description": "Programs for stress management, sleep, nutrition, and overall well-being",
                "contact": "wellness@university.edu | 555-789-0124",
                "location": "Student Center, Room 250"
            },
            {
                "name": "Mindfulness and Meditation Sessions",
                "description": "Weekly sessions teaching mindfulness and stress reduction techniques",
                "contact": "mindfulness@university.edu | 555-789-0125",
                "location": "Wellness Center, Room 120"
            }
        ]
        
        # Mental health specific resources
        mental_health_resources = [
            {
                "name": "Mental Health Crisis Line",
                "description": "24/7 support line for immediate mental health concerns",
                "contact": "555-911-HELP (4357)",
                "location": "Available by phone 24/7"
            },
            {
                "name": "Anxiety Management Group",
                "description": "Weekly group sessions focused on managing anxiety and stress",
                "contact": "anxiety.group@university.edu | 555-789-0126",
                "location": "Health Center, Room 210"
            },
            {
                "name": "Depression Support Resources",
                "description": "Individual counseling and support groups for depression",
                "contact": "depression.support@university.edu | 555-789-0127",
                "location": "Health Center, Room 215"
            }
        ]
        
        # Sleep and stress resources
        lifestyle_resources = [
            {
                "name": "Sleep Improvement Program",
                "description": "Resources and coaching for better sleep habits",
                "contact": "sleep.health@university.edu | 555-789-0128",
                "location": "Health Center, Room 230"
            },
            {
                "name": "Stress Management Workshop Series",
                "description": "Weekly workshops teaching practical stress management techniques",
                "contact": "stress.workshops@university.edu | 555-789-0129",
                "location": "Student Center, Room 150"
            },
            {
                "name": "Work-Life Balance Coaching",
                "description": "Individual coaching sessions for managing academic and personal demands",
                "contact": "balance.coaching@university.edu | 555-789-0130",
                "location": "Career Center, Room 120"
            }
        ]
        
        # Check for specific wellness needs
        has_mental_health_need = False
        has_stress_need = False
        
        for need in needs.get("wellness_needs", []):
            need_text = need.get("need", "").lower()
            if "mental health" in need_text:
                has_mental_health_need = True
            if "stress" in need_text or "overwhelm" in need_text:
                has_stress_need = True
        
        # Add appropriate resources based on identified needs
        if has_mental_health_need:
            wellness_resources.extend(mental_health_resources)
            wellness_resources.append(general_resources[0])  # Add counseling center
        
        if has_stress_need:
            wellness_resources.extend(lifestyle_resources)
            if general_resources[2] not in wellness_resources:  # Add mindfulness if not already added
                wellness_resources.append(general_resources[2])
        
        # If no specific needs identified but wellness category exists, add general resources
        if needs.get("wellness_needs") and not (has_mental_health_need or has_stress_need):
            wellness_resources.extend(general_resources)
        
        # Ensure each resource has a type field
        for resource in wellness_resources:
            resource["type"] = "wellness"
        
        return wellness_resources
    
    def _get_career_resources(self, needs: Dict, personal_info: Dict) -> List[Dict]:
        """Get relevant career resources based on identified needs"""
        career_resources = []
        major = personal_info.get("major", "")
        year = personal_info.get("year", "")
        
        # General career resources
        general_resources = [
            {
                "name": "University Career Center",
                "description": "Career counseling, job search support, and professional development",
                "contact": "careers@university.edu | 555-890-1234",
                "location": "Career Center Building"
            },
            {
                "name": "Resume and Cover Letter Workshop",
                "description": "Regular workshops on creating effective application materials",
                "contact": "resume.workshop@university.edu | 555-890-1235",
                "location": "Career Center, Room 120"
            },
            {
                "name": "Interview Skills Practice",
                "description": "Mock interviews with feedback from career counselors",
                "contact": "interview.practice@university.edu | 555-890-1236",
                "location": "Career Center, Room 140"
            }
        ]
        
        # Year-specific resources
        year_resources = {
            "Freshman": [
                {
                    "name": "First-Year Career Exploration",
                    "description": "Programs to help explore majors and career paths",
                    "contact": "explore.careers@university.edu | 555-890-1237",
                    "location": "Career Center, Room 110"
                },
                {
                    "name": "Major Selection Support",
                    "description": "Guidance in choosing or confirming your major",
                    "contact": "major.selection@university.edu | 555-890-1238",
                    "location": "Academic Advising Center"
                }
            ],
            "Sophomore": [
                {
                    "name": "Sophomore Career Planning",
                    "description": "Workshops to develop career plans aligned with your major",
                    "contact": "sophomore.planning@university.edu | 555-890-1239",
                    "location": "Career Center, Room 130"
                },
                {
                    "name": "Early Internship Guidance",
                    "description": "Support for finding and applying to initial internships",
                    "contact": "early.internships@university.edu | 555-890-1240",
                    "location": "Career Center, Room 150"
                }
            ],
            "Junior": [
                {
                    "name": "Junior Career Intensive",
                    "description": "Comprehensive career planning and preparation program",
                    "contact": "junior.intensive@university.edu | 555-890-1241",
                    "location": "Career Center, Room 160"
                },
                {
                    "name": "Industry-Specific Internship Program",
                    "description": "Targeted support for finding relevant internships",
                    "contact": "industry.internships@university.edu | 555-890-1242",
                    "location": "Career Center, Room 170"
                }
            ],
            "Senior": [
                {
                    "name": "Senior Job Search Support",
                    "description": "Intensive support for the post-graduation job search",
                    "contact": "senior.jobs@university.edu | 555-890-1243",
                    "location": "Career Center, Room 180"
                },
                {
                    "name": "Graduate School Application Support",
                    "description": "Guidance for those pursuing advanced degrees",
                    "contact": "grad.applications@university.edu | 555-890-1244",
                    "location": "Career Center, Room 190"
                }
            ]
        }
        
        # Major-specific career resources
        major_resources = {
            "Computer Science": [
                {
                    "name": "Tech Career Fair",
                    "description": "Connect with technology companies and startups",
                    "contact": "tech.fair@university.edu | 555-890-1245",
                    "location": "Computing Center, Main Hall"
                },
                {
                    "name": "Technical Interview Preparation",
                    "description": "Practice for coding interviews and technical assessments",
                    "contact": "tech.interviews@university.edu | 555-890-1246",
                    "location": "Computing Center, Room 250"
                }
            ],
            "Psychology": [
                {
                    "name": "Psychology Career Paths Panel",
                    "description": "Alumni discuss various psychology career options",
                    "contact": "psych.careers@university.edu | 555-890-1247",
                    "location": "Psychology Building, Room 300"
                },
                {
                    "name": "Human Services Employment Network",
                    "description": "Connections to social service and mental health employers",
                    "contact": "human.services@university.edu | 555-890-1248",
                    "location": "Career Center, Room 200"
                }
            ],
            "Business Administration": [
                {
                    "name": "Business Networking Events",
                    "description": "Regular opportunities to connect with business professionals",
                    "contact": "business.network@university.edu | 555-890-1249",
                    "location": "Business Building, Conference Center"
                },
                {
                    "name": "Finance and Consulting Interview Prep",
                    "description": "Specialized preparation for business interviews",
                    "contact": "business.interviews@university.edu | 555-890-1250",
                    "location": "Business Building, Room 350"
                }
            ],
            "Engineering": [
                {
                    "name": "Engineering Industry Connections",
                    "description": "Program connecting students with engineering firms",
                    "contact": "eng.connections@university.edu | 555-890-1251",
                    "location": "Engineering Complex, Room 300"
                },
                {
                    "name": "Technical Portfolio Development",
                    "description": "Support for creating engineering portfolios and project documentation",
                    "contact": "eng.portfolio@university.edu | 555-890-1252",
                    "location": "Engineering Complex, Room 320"
                }
            ],
            "Biology": [
                {
                    "name": "Health Professions Advising",
                    "description": "Guidance for pre-med and other health career paths",
                    "contact": "health.professions@university.edu | 555-890-1253",
                    "location": "Science Building, Room 400"
                },
                {
                    "name": "Research Career Pathways",
                    "description": "Support for students interested in research careers",
                    "contact": "research.careers@university.edu | 555-890-1254",
                    "location": "Science Building, Room 420"
                }
            ]
        }
        
        # Check if there are career needs
        has_career_needs = len(needs.get("career_needs", [])) > 0
        
        # Add resources based on needs and student information
        if has_career_needs:
            # Add general career resources
            career_resources.append(general_resources[0])  # Always add career center
            
            # Add year-specific resources if available
            year_specific = year_resources.get(year, [])
            if year_specific:
                career_resources.extend(year_specific)
            
            # Add major-specific resources if available
            major_specific = major_resources.get(major, [])
            if major_specific:
                career_resources.extend(major_specific[:1])  # Add one major-specific resource
        else:
            # If no specific career needs, just add the main career center
            career_resources.append(general_resources[0])
        
        # Ensure each resource has a type field
        for resource in career_resources:
            resource["type"] = "career"
        
        return career_resources
    
    def _get_community_resources(self, needs: Dict, personal_info: Dict) -> List[Dict]:
        """Get relevant community resources based on identified needs"""
        community_resources = []
        
        # General community resources
        general_resources = [
            {
                "name": "Student Organizations Office",
                "description": "Information on joining or creating student organizations",
                "contact": "student.orgs@university.edu | 555-012-3456",
                "location": "Student Center, Room 300"
            },
            {
                "name": "Campus Events Calendar",
                "description": "Comprehensive listing of campus activities and events",
                "contact": "events@university.edu | 555-012-3457",
                "location": "Online and Student Center Information Desk"
            },
            {
                "name": "Student Community Center",
                "description": "Space for student gatherings, events, and community building",
                "contact": "community.center@university.edu | 555-012-3458",
                "location": "Student Community Building"
            }
        ]
        
        # Special interest community resources
        interest_resources = [
            {
                "name": "Cultural Student Associations",
                "description": "Organizations celebrating diverse cultural backgrounds",
                "contact": "cultural.orgs@university.edu | 555-012-3459",
                "location": "Multicultural Center"
            },
            {
                "name": "LGBTQ+ Resource Center",
                "description": "Support, programming, and community for LGBTQ+ students",
                "contact": "lgbtq.center@university.edu | 555-012-3460",
                "location": "Student Services Building, Room 250"
            },
            {
                "name": "Religious and Spiritual Life",
                "description": "Faith-based organizations and spiritual support",
                "contact": "spiritual.life@university.edu | 555-012-3461",
                "location": "Interfaith Center"
            },
            {
                "name": "Recreational Sports Clubs",
                "description": "Casual and competitive sports opportunities",
                "contact": "rec.sports@university.edu | 555-012-3462",
                "location": "Recreation Center"
            }
        ]
        
        # First-year specific resources
        first_year_resources = [
            {
                "name": "First-Year Experience Program",
                "description": "Events and support specifically for new students",
                "contact": "first.year@university.edu | 555-012-3463",
                "location": "Student Success Center, Room 100"
            },
            {
                "name": "Residence Hall Community Activities",
                "description": "Social events and community building in residence halls",
                "contact": "res.life@university.edu | 555-012-3464",
                "location": "Housing Office"
            },
            {
                "name": "Peer Mentor Program",
                "description": "Connect with experienced students for guidance and friendship",
                "contact": "peer.mentors@university.edu | 555-012-3465",
                "location": "Student Success Center, Room 120"
            }
        ]
        
        # Check if there are community needs
        has_community_needs = len(needs.get("community_needs", [])) > 0
        
        # Check if student is a first-year student
        is_first_year = personal_info.get("year") == "Freshman"
        
        # Add appropriate resources
        if has_community_needs:
            # Add general community resources
            community_resources.extend(general_resources[:2])
            
            # Add some interest-based resources
            if interest_resources:
                community_resources.extend(random.sample(interest_resources, min(2, len(interest_resources))))
        
        # Add first-year resources if applicable
        if is_first_year:
            community_resources.extend(first_year_resources[:2])
        
        # If no community resources added yet, add at least one general resource
        if not community_resources and general_resources:
            community_resources.append(general_resources[0])
        
        # Ensure each resource has a type field
        for resource in community_resources:
            resource["type"] = "community"
        
        return community_resources
    
    def _get_technology_resources(self, needs: Dict, academic_info: Dict) -> List[Dict]:
        """Get relevant technology resources based on identified needs"""
        technology_resources = []
        
        # General technology resources
        general_resources = [
            {
                "name": "University IT Help Desk",
                "description": "Technical support for university systems and software",
                "contact": "helpdesk@university.edu | 555-123-7890",
                "location": "Technology Center, 1st Floor"
            },
            {
                "name": "Student Technology Loan Program",
                "description": "Borrow laptops, tablets, and other technology",
                "contact": "tech.loan@university.edu | 555-123-7891",
                "location": "Technology Center, Room 150"
            },
            {
                "name": "Campus Computer Labs",
                "description": "Access to computers, software, and printing",
                "contact": "computer.labs@university.edu | 555-123-7892",
                "location": "Multiple locations across campus"
            }
        ]
        
        # Advanced technology resources
        advanced_resources = [
            {
                "name": "Data Science and Analytics Lab",
                "description": "Advanced software and support for data analysis",
                "contact": "data.lab@university.edu | 555-123-7893",
                "location": "Technology Center, Room 300"
            },
            {
                "name": "Creative Media Studio",
                "description": "Resources for digital media creation and editing",
                "contact": "media.studio@university.edu | 555-123-7894",
                "location": "Arts Building, Room 250"
            },
            {
                "name": "Advanced Research Computing",
                "description": "High-performance computing resources for research",
                "contact": "research.computing@university.edu | 555-123-7895",
                "location": "Research Computing Center"
            }
        ]
        
        # Digital access resources
        access_resources = [
            {
                "name": "Internet Access Program",
                "description": "Support for students with limited internet access",
                "contact": "digital.access@university.edu | 555-123-7896",
                "location": "Technology Center, Room 120"
            },
            {
                "name": "Technology Accessibility Services",
                "description": "Assistive technology and accessibility support",
                "contact": "tech.accessibility@university.edu | 555-123-7897",
                "location": "Student Services Building, Room 200"
            }
        ]
        
        # Check if there are technology needs
        has_technology_needs = len(needs.get("technology_needs", [])) > 0
        
        # Add appropriate resources
        if has_technology_needs:
            # Add general technology resources
            technology_resources.extend(general_resources[:2])
            
            # Add some advanced resources
            technology_resources.append(random.choice(advanced_resources))
            
            # Add access resources if needed
            for need in needs.get("technology_needs", []):
                if "access" in need.get("need", "").lower():
                    technology_resources.extend(access_resources)
                    break
        else:
            # If no specific technology needs, just add basic resources
            technology_resources.append(general_resources[0])
        
        # Ensure each resource has a type field
        for resource in technology_resources:
            resource["type"] = "technology"
        
        return technology_resources
    
    def _generate_personalized_recommendations(self, needs: Dict, personal_info: Dict, academic_info: Dict) -> List[str]:
        """Generate personalized resource recommendations"""
        recommendations = []
        
        # Check for specific needs and generate targeted recommendations
        
        # Academic recommendations
        if needs.get("academic_needs"):
            # Add recommendations based on academic needs
            gpa = academic_info.get("overall_gpa", 0.0)
            if gpa < 2.5:
                recommendations.append("Schedule an appointment with an academic advisor to develop a performance improvement plan")
                recommendations.append("Visit the Academic Success Center for personalized tutoring and study strategy development")
            else:
                recommendations.append("Consider connecting with the Academic Success Center to maintain and enhance your academic performance")
        
        # Wellness recommendations
        if needs.get("wellness_needs"):
            for need in needs.get("wellness_needs", []):
                need_text = need.get("need", "").lower()
                if "mental health" in need_text:
                    recommendations.append("Schedule an initial consultation with the University Counseling Center for personalized support")
                elif "stress" in need_text or "overwhelm" in need_text:
                    recommendations.append("Try the weekly mindfulness sessions to develop stress management techniques")
        
        # First-year specific recommendations
        if personal_info.get("year") == "Freshman":
            recommendations.append("Join the First-Year Experience Program to connect with other new students and build your campus network")
            if not any("academic advisor" in rec.lower() for rec in recommendations):
                recommendations.append("Meet with your academic advisor to review your first-semester progress and plan for upcoming terms")
        
        # Career recommendations based on year
        year = personal_info.get("year", "")
        if year == "Junior" or year == "Senior":
            recommendations.append("Visit the Career Center to develop your job search strategy and review your resume")
        elif year == "Sophomore":
            recommendations.append("Explore internship opportunities through the Career Center's Sophomore Career Planning program")
        
        # Add general recommendation if none were generated
        if not recommendations:
            recommendations.append("Schedule a meeting with your academic advisor to discuss your specific needs and goals")
        
        return recommendations