# app/utils/openai_client.py
from openai import OpenAI
import logging
import json
from pydantic import BaseModel, Field, ValidationError
from typing import List
from app.config import OPENAI_API_KEY, OPENAI_BASE_URL

# Logger setup
logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# Schema aligned with your DB model
class ContentScore(BaseModel):
    rating: int = Field(..., ge=0, le=100)
    justification: str
    sentimentAnalysisLabel: str
    sentimentAnalysisScore: float = Field(..., ge=0, le=1)
    biasDetectionScore: float = Field(..., ge=0, le=1)
    biasDetectionDirection: str
    originalityScore: float = Field(..., ge=0, le=1)
    similarityScore: float = Field(..., ge=0, le=1)
    readabilityFleschKincaid: float
    readabilityGunningFog: float
    mainTopic: str
    secondaryTopics: List[str]

# Define the function schema for OpenAI function calling
content_score_schema = {
    "type": "function",
    "function": {
        "name": "evaluate_content",
        "description": "Evaluate content and provide structured ratings across multiple dimensions",
        "parameters": {
            "type": "object",
            "properties": {
                "rating": {
                    "type": "integer",
                    "description": "Overall quality score (0-100)",
                    "minimum": 0,
                    "maximum": 100
                },
                "justification": {
                    "type": "string",
                    "description": "Evidence-based explanation for the rating with specific examples"
                },
                "sentimentAnalysisLabel": {
                    "type": "string",
                    "enum": ["Very Positive", "Positive", "Neutral", "Negative", "Very Negative"],
                    "description": "Categorical sentiment assessment"
                },
                "sentimentAnalysisScore": {
                    "type": "number",
                    "description": "Float 0-1 (0 = extremely negative, 1 = extremely positive)",
                    "minimum": 0,
                    "maximum": 1
                },
                "biasDetectionScore": {
                    "type": "number",
                    "description": "Float 0-1 (0 = unbiased, 1 = heavily biased)",
                    "minimum": 0,
                    "maximum": 1
                },
                "biasDetectionDirection": {
                    "type": "string",
                    "enum": ["strong left", "moderate left", "neutral", "moderate right", "strong right", "non-political"],
                    "description": "Political leaning or bias direction"
                },
                "originalityScore": {
                    "type": "number",
                    "description": "Float 0-1 (0 = entirely derivative, 1 = highly original)",
                    "minimum": 0,
                    "maximum": 1
                },
                "similarityScore": {
                    "type": "number",
                    "description": "Float 0-1 (0 = unique, 1 = highly similar to common content)",
                    "minimum": 0,
                    "maximum": 1
                },
                "readabilityFleschKincaid": {
                    "type": "number",
                    "description": "Standard Flesch-Kincaid reading grade level"
                },
                "readabilityGunningFog": {
                    "type": "number",
                    "description": "Gunning Fog Index score"
                },
                "mainTopic": {
                    "type": "string",
                    "description": "Single phrase describing the primary subject"
                },
                "secondaryTopics": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "List of 2-4 supporting topics or themes"
                }
            },
            "required": [
                "rating", "justification", "sentimentAnalysisLabel", "sentimentAnalysisScore", 
                "biasDetectionScore", "biasDetectionDirection", "originalityScore", 
                "similarityScore", "readabilityFleschKincaid", "readabilityGunningFog", 
                "mainTopic", "secondaryTopics"
            ]
        }
    }
}

async def score_post(title: str, content: str, model: str = "gpt-4o") -> ContentScore:
    """
    Evaluate content and return structured ratings using OpenAI function calling.
    
    Args:
        title: The title of the blog post
        content: The full text content to evaluate
        model: OpenAI model to use
        
    Returns:
        ContentScore: Structured content evaluation
        
    Raises:
        ValueError: For empty inputs
        RuntimeError: For API or validation errors
    """
    if not title.strip() or not content.strip():
        logger.error("Empty title or content provided")
        raise ValueError("Title and content must be non-empty.")

    system_prompt = """You are an expert content evaluator with experience in journalism, SEO, and content marketing.

Evaluate this content objectively, considering clarity, coherence, accuracy, and value.
Base your evaluation solely on the provided content. Remain objective regardless of subject matter.
You will analyze the content with specific metrics, which will be provided in a structured format.
"""

    try:
        logger.info(f"Evaluating content with title: '{title}' (length: {len(content)} chars)")
        
        # Make the API call with function calling
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Title: {title}\n\nContent: {content}"}
            ],
            tools=[content_score_schema],
            tool_choice={"type": "function", "function": {"name": "evaluate_content"}}
        )
        
        # Extract the function call arguments
        function_call = response.choices[0].message.tool_calls[0].function
        score_data = json.loads(function_call.arguments)
        
        # Parse into Pydantic model for validation
        content_score = ContentScore(**score_data)
        
        logger.info(f"Scoring completed for '{title}' with rating: {content_score.rating}")
        return content_score

    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise RuntimeError(f"Response validation failed: {ve}")
    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing error: {je}")
        raise RuntimeError(f"Failed to parse function arguments: {je}")
    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise RuntimeError(f"Content scoring failed: {str(e)}")