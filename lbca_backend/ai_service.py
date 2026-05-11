"""
AI Bridge Service - Connects Django backend to Render AI Model
URL: https://lbca-django-ai-model.onrender.com/
"""
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

AI_MODEL_URL = "https://lbca-django-ai-model.onrender.com"
REQUEST_TIMEOUT = 10  # seconds


class AIServiceError(Exception):
    """Custom exception for AI service errors"""
    pass


class AIBridge:
    """Bridge service for communicating with the AI model"""

    @staticmethod
    def call_ai(endpoint: str, data: Dict[str, Any], method: str = "POST") -> Dict[str, Any]:
        """
        Generic method to call AI model endpoints
        
        Args:
            endpoint: API endpoint path (e.g., '/predict', '/analyze')
            data: Data to send to the AI model
            method: HTTP method (POST, GET, etc.)
        
        Returns:
            Response from AI model as dict
        
        Raises:
            AIServiceError: If API call fails
        """
        url = f"{AI_MODEL_URL}{endpoint}"
        
        try:
            if method == "POST":
                response = requests.post(url, json=data, timeout=REQUEST_TIMEOUT)
            elif method == "GET":
                response = requests.get(url, params=data, timeout=REQUEST_TIMEOUT)
            else:
                raise AIServiceError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.Timeout:
            logger.error(f"AI model request timed out: {url}")
            raise AIServiceError("AI model request timed out")
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to AI model: {url}")
            raise AIServiceError("Failed to connect to AI model")
        except requests.exceptions.HTTPError as e:
            logger.error(f"AI model HTTP error: {e.response.status_code} - {e.response.text}")
            raise AIServiceError(f"AI model error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error calling AI model: {str(e)}")
            raise AIServiceError(f"Unexpected error: {str(e)}")

    @staticmethod
    def analyze_student(student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze student data using AI model
        
        Args:
            student_data: Student information
        
        Returns:
            AI analysis result or None if service unavailable
        """
        try:
            result = AIBridge.call_ai("/analyze/student", student_data)
            logger.info(f"Student analysis completed: {student_data.get('id')}")
            return result
        except AIServiceError as e:
            logger.warning(f"AI analysis failed: {str(e)}")
            return None

    @staticmethod
    def predict_enrollment(enrollment_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Predict enrollment success/risk using AI model
        
        Args:
            enrollment_data: Enrollment information
        
        Returns:
            Enrollment prediction or None if service unavailable
        """
        try:
            result = AIBridge.call_ai("/predict/enrollment", enrollment_data)
            logger.info("Enrollment prediction completed")
            return result
        except AIServiceError as e:
            logger.warning(f"Enrollment prediction failed: {str(e)}")
            return None

    @staticmethod
    def validate_student_data(student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate student data using AI model
        
        Args:
            student_data: Student information to validate
        
        Returns:
            Validation result with suggestions or None if service unavailable
        """
        try:
            result = AIBridge.call_ai("/validate/student", student_data)
            logger.info("Student data validation completed")
            return result
        except AIServiceError as e:
            logger.warning(f"Student validation failed: {str(e)}")
            return None

    @staticmethod
    def get_student_recommendations(student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get AI recommendations for a student
        
        Args:
            student_data: Student information
        
        Returns:
            AI recommendations or None if service unavailable
        """
        try:
            result = AIBridge.call_ai("/recommend/student", student_data)
            logger.info(f"Student recommendations generated: {student_data.get('id')}")
            return result
        except AIServiceError as e:
            logger.warning(f"Recommendation generation failed: {str(e)}")
            return None

    @staticmethod
    def analyze_section_performance(section_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze section/class performance using AI model
        
        Args:
            section_data: Section information
        
        Returns:
            Performance analysis or None if service unavailable
        """
        try:
            result = AIBridge.call_ai("/analyze/section", section_data)
            logger.info(f"Section analysis completed: {section_data.get('id')}")
            return result
        except AIServiceError as e:
            logger.warning(f"Section analysis failed: {str(e)}")
            return None

    @staticmethod
    def predict_student_pace(pace_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Predict student learning pace using AI model
        
        Args:
            pace_data: Student pace information
        
        Returns:
            Pace prediction or None if service unavailable
        """
        try:
            result = AIBridge.call_ai("/predict/pace", pace_data)
            logger.info("Student pace prediction completed")
            return result
        except AIServiceError as e:
            logger.warning(f"Pace prediction failed: {str(e)}")
            return None
