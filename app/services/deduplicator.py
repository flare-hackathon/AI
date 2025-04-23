#app/services/deduplicator.py
from pgvector.sqlalchemy import Vector
from sqlalchemy import select, func, desc
from app.db.models import AIPostRating
import numpy as np
import logging

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 0.90  # Configurable threshold

async def compute_similarity_score(session, new_embedding):
    """
    Compute the maximum similarity between a new embedding and existing embeddings.
    """
    # Check if we have any existing ratings with embeddings
    check_stmt = select(AIPostRating).where(AIPostRating.embedding.is_not(None)).limit(1)
    check_result = await session.execute(check_stmt)
    has_embeddings = check_result.scalar_one_or_none() is not None
    
    # If no embeddings exist in the database, return zero similarity
    if not has_embeddings:
        logger.debug("No existing embeddings to compare with")
        return 0.0
    
    # Ensure new_embedding is properly formatted
    if isinstance(new_embedding, np.ndarray):
        new_embedding = new_embedding.tolist()
    
    # Validate the embedding
    if not isinstance(new_embedding, list) or not new_embedding or not all(isinstance(x, (int, float)) for x in new_embedding):
        logger.error(f"Invalid embedding format: {type(new_embedding)} | Value: {new_embedding}")
        return 0.0
    
    try:
        # Convert the embedding to a Vector for proper comparison
        vector_embedding = Vector(new_embedding)
        
        # Use pgvector's built-in operator for cosine distance
        stmt = (
            select(
                (1 - (AIPostRating.embedding.op("<=>") (vector_embedding))).label("similarity")
            )
            .where(AIPostRating.embedding.is_not(None))
            .order_by(desc("similarity"))
            .limit(1)
        )
        
        result = await session.execute(stmt)
        max_similarity = result.scalar_one_or_none()
        
        # Normalize result to 0-1 range and handle null case
        if max_similarity is None:
            return 0.0
        
        # Ensure the score is within valid range
        similarity = max(0.0, min(float(max_similarity), 1.0))
        logger.debug(f"Maximum similarity score: {similarity:.4f}")
        return similarity
        
    except Exception as e:
        # Proper logging instead of print
        logger.error(f"Error computing similarity score: {str(e)}", exc_info=True)
        return 0.0

# Additional helper function that might be useful
async def get_most_similar_post(session, new_embedding):
    """
    Find the most similar post to the given embedding.
    
    Args:
        session: SQLAlchemy async session
        new_embedding: The vector embedding to compare
        
    Returns:
        tuple: (AIPostRating, similarity_score) or (None, 0.0) if no posts exist
    """
    if isinstance(new_embedding, np.ndarray):
        new_embedding = new_embedding.tolist()
    
    try:
        vector_embedding = Vector(new_embedding)
        logger.debug(f"Embedding being used for similarity computation: {new_embedding}")
        
        stmt = (
            select(
                AIPostRating,
                (1 - (AIPostRating.embedding.op("<=>") (vector_embedding))).label("similarity")
            )
            .where(AIPostRating.embedding.is_not(None))
            .order_by(desc("similarity"))
            .limit(1)
        )
        
        result = await session.execute(stmt)
        row = result.first()
        
        if not row:
            return None, 0.0
            
        return row[0], max(0.0, min(float(row[1]), 1.0))
        
    except Exception as e:
        logger.error(f"Error finding similar post: {str(e)}", exc_info=True)
        return None, 0.0