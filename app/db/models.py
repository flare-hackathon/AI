from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey, UniqueConstraint, ARRAY
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class Post(Base):
    __tablename__ = "Post"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String)
    published = Column(Boolean, default=False)
    ipfsHash = Column(String, unique=True)
    authorAddress = Column(String, nullable=False)
    userRating = Column(Integer, default=0)
    aiRatingId = Column(Integer, unique=True)
    internal_id = Column(Integer, unique=True)

    ai_rating = relationship("AIPostRating", back_populates="post", uselist=False)


class AIPostRating(Base):
    __tablename__ = "AIPostRating"

    id = Column(Integer, primary_key=True, index=True)
    postId = Column(Integer, ForeignKey("Post.id"), unique=True, nullable=False)
    rating = Column(Integer, nullable=False)
    justification = Column(String, nullable=False)
    sentimentAnalysisLabel = Column(String)
    sentimentAnalysisScore = Column(Float)
    biasDetectionScore = Column(Float)
    biasDetectionDirection = Column(String)
    originalityScore = Column(Float)
    similarityScore = Column(Float)
    readabilityFleschKincaid = Column(Float)
    readabilityGunningFog = Column(Float)
    mainTopic = Column(String)
    secondaryTopics = Column(ARRAY(String))
    embedding = Column(Vector(768))  # Adjust size to match your embedding model
    createdAt = Column(DateTime(timezone=True), server_default=func.now())

    post = relationship("Post", back_populates="ai_rating")
