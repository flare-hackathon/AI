#app/services/scorer.py
from app.utils.openai_client import score_post
from app.utils.embeddings import get_post_embedding
from app.services.deduplicator import compute_similarity_score
from app.db.models import AIPostRating, Post
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

SIMILARITY_THRESHOLD = 0.90  

async def score_new_posts(session: AsyncSession):
    """
    Process and score all unrated published posts, handling duplicates gracefully.
    
    Args:
        session: SQLAlchemy async session
    """
    # Get all unrated published posts
    stmt = select(Post).where(Post.aiRatingId == None, Post.published == True)
    result = await session.execute(stmt)
    posts = result.scalars().all()
    
    logging.info(f"Found {len(posts)} unrated posts to process")
    
    processed_count = 0
    duplicate_count = 0
    error_count = 0
    
    for post in posts:
        try:
            # 1. Get embedding
            embedding = get_post_embedding(post.title, post.content)

            # Validate the embedding before proceeding
            if embedding is None or (isinstance(embedding, dict) and not embedding) or (
                isinstance(embedding, list) and not embedding):
                logging.error(f"Invalid embedding returned for post {post.id}: {embedding}")
                error_count += 1
                continue

            # If embedding is a dict with values, convert it to a list
            if isinstance(embedding, dict):
                try:
                    embedding = list(embedding.values())
                except Exception as e:
                    logging.error(f"Failed to convert dict embedding to list for post {post.id}: {embedding} ({e})")
                    error_count += 1
                    continue

            # Ensure it's a valid, non-empty list with numeric values
            if (
                not isinstance(embedding, list) or
                len(embedding) == 0 or
                not all(isinstance(x, (int, float)) for x in embedding)
            ):
                logging.error(f"Embedding for post {post.id} is not a valid numeric 1D list: {embedding}")
                error_count += 1
                continue
            
            # 2. Get similarity score
            similarity_score = await compute_similarity_score(session, embedding)
            
            # 3. Check if it's a duplicate
            if similarity_score >= SIMILARITY_THRESHOLD:
                logging.info(f"Post {post.id} detected as duplicate (similarity: {similarity_score:.4f})")
                
                # Create rating with duplicate flag
                ai_rating = AIPostRating(
                    postId=post.id,
                    embedding=embedding,
                    similarityScore=similarity_score,
                    rating=0,  # Zero rating for duplicates
                    justification="Duplicate content. This post is too similar to existing content.",
                    sentimentAnalysisLabel="Neutral",  # Default values for required fields
                    sentimentAnalysisScore=0.5,
                    biasDetectionScore=0.0,
                    biasDetectionDirection="neutral",
                    originalityScore=0.0,  # Low originality for duplicates
                    readabilityFleschKincaid=0.0,
                    readabilityGunningFog=0.0,
                    mainTopic="duplicate content",
                    secondaryTopics=["duplicate"]
                )
                duplicate_count += 1
                
            else:
                # 4. Not a duplicate, use OpenAI to rate
                logging.info(f"Scoring post {post.id} (similarity: {similarity_score:.4f})")
                rating_data = await score_post(post.title, post.content)
                
                # Merge rating data with embedding and similarity
                data = rating_data.dict()
                data.pop("similarityScore", None)
                ai_rating = AIPostRating(
                    postId=post.id,
                    embedding=embedding,
                    similarityScore=similarity_score,
                    **data
                )
                processed_count += 1
            
            # Add the rating to session
            session.add(ai_rating)
            
            # Update post with rating ID
            post.aiRatingId = ai_rating.id  # This will work after session.flush()
            await session.flush()  # Flush to get the ID
            
        except Exception as e:
            logging.error(f"Failed to score post {post.id}: {str(e)}", exc_info=True)
            error_count += 1
    
    # Commit all changes at once
    try:
        await session.commit()
        logging.info(f"Processed {processed_count} posts, found {duplicate_count} duplicates, encountered {error_count} errors")
    except Exception as e:
        await session.rollback()
        logging.error(f"Failed to commit changes: {str(e)}", exc_info=True)
        raise