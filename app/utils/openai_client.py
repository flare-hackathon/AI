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
#client = OpenAI(api_key="ollama", base_url='http://localhost:11434/v1')
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

async def score_post(title: str, content: str, model: str = "gemini-2.0-flash") -> ContentScore:
    """
    Evaluate content and return structured ratings using prompt engineering for structured output.
    
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

    # Define the expected JSON structure in the prompt
    json_format = """{
  "rating": integer between 0-100,
  "justification": "detailed explanation",
  "sentimentAnalysisLabel": "One of: Very Positive, Positive, Neutral, Negative, Very Negative",
  "sentimentAnalysisScore": float between 0-1,
  "biasDetectionScore": float between 0-1,
  "biasDetectionDirection": "One of: strong left, moderate left, neutral, moderate right, strong right, non-political",
  "originalityScore": float between 0-1,
  "similarityScore": float between 0-1,
  "readabilityFleschKincaid": float representing grade level,
  "readabilityGunningFog": float representing index score,
  "mainTopic": "primary subject",
  "secondaryTopics": ["topic1", "topic2", "topic3"]
}"""

    system_prompt = f"""You are an expert content evaluator with experience in journalism, SEO, and content marketing.

Evaluate this content objectively, considering clarity, coherence, accuracy, and value.
Base your evaluation solely on the provided content. Remain objective regardless of subject matter.

IMPORTANT: Your response MUST be valid JSON that matches this structure:

{json_format}

Do NOT include any explanations, markdown formatting, or other text outside the JSON structure.
Ensure all values conform to the specified types and ranges.
"""

    try:
        logger.info(f"Evaluating content with title: '{title}' (length: {len(content)} chars)")
        
        # Make the API call requesting structured output
        response = client.chat.completions.create(
            model="gemini-2.0-flash",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Title: {title}\n\nContent: {content}"}
            ],
            response_format={"type": "json_object"}  # For models that support JSON mode
        )
        
        # Extract and parse the response
        if not response or not hasattr(response, 'choices') or not response.choices:
            logger.error(f"API response is empty or malformed: {response}")
            raise RuntimeError("API response is empty or malformed.")
        
        try:
            # Get the content from the response
            content_str = response.choices[0].message.content.strip()
            print('AI GENERATED RESPONSE:', content_str)
            
            # Parse the JSON response
            score_data = json.loads(content_str)
        except Exception as e:
            logger.error(f"Error extracting or parsing response: {e}, response: {content_str}")
            raise RuntimeError(f"Error extracting or parsing response: {e}")
        
        # Parse into Pydantic model for validation
        content_score = ContentScore(**score_data)
        
        logger.info(f"Scoring completed for '{title}' with rating: {content_score.rating}")
        return content_score

    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise RuntimeError(f"Response validation failed: {ve}")
    except json.JSONDecodeError as je:
        logger.error(f"JSON parsing error: {je}, raw content: {content_str if 'content_str' in locals() else 'N/A'}")
        raise RuntimeError(f"Failed to parse JSON response: {je}")
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise RuntimeError(f"Content scoring failed: {str(e)}")