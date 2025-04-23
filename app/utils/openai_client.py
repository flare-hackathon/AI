#app/utils/openai_client.py
from openai import OpenAI
import logging
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

async def score_post(title: str, content: str, model: str = "gpt-4o"):
    """
    Evaluate content and return structured ratings.
    
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

Evaluate this content with the following metrics:
- rating (0-100): Overall quality score considering clarity, coherence, accuracy, and value
- justification: Evidence-based explanation for your rating with specific examples
- sentimentAnalysisLabel: One of 'Very Positive', 'Positive', 'Neutral', 'Negative', 'Very Negative'
- sentimentAnalysisScore: Float 0–1 (0 = extremely negative, 1 = extremely positive)
- biasDetectionScore: Float 0–1 (0 = unbiased, 1 = heavily biased)
- biasDetectionDirection: 'strong left', 'moderate left', 'neutral', 'moderate right', 'strong right', or 'non-political'
- originalityScore: Float 0–1 (0 = entirely derivative, 1 = highly original)
- similarityScore: Float 0–1 (0 = unique, 1 = highly similar to common content)
- readabilityFleschKincaid: Standard Flesch-Kincaid reading grade level
- readabilityGunningFog: Gunning Fog Index score
- mainTopic: Single phrase describing the primary subject
- secondaryTopics: List of 2–4 supporting topics or themes

Base your evaluation solely on the provided content. Remain objective regardless of subject matter.
"""

    try:
        logger.info(f"Evaluating content with title: '{title}' (length: {len(content)} chars)")
        
        response = client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Title: {title}\n\nContent: {content}"}
            ],
            text_format=ContentScore,
        )

        logger.info(f"Scoring completed for '{title}' with rating: {response.output_parsed.rating}")
        return response.output_parsed

    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise RuntimeError(f"Response validation failed: {ve}")

    except Exception as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise RuntimeError(f"Content scoring failed: {str(e)}")