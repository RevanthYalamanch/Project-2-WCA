from pydantic import BaseModel, HttpUrl, Field, validator
from typing import Optional, List

# --- Input Validation Models (No Change) ---

class URLAnalysisRequest(BaseModel):
    url: HttpUrl

# --- Intermediate & Final Content Models (UPDATED) ---

class Heading(BaseModel):
    level: int = Field(..., ge=1, le=6)
    text: str

class ProcessedContent(BaseModel):
    title: Optional[str] = None
    meta_description: Optional[str] = None
    detected_language: str
    content_type: str
    key_phrases: List[str]
    document_outline: List[Heading]
    main_content_text: str = Field(..., min_length=50)

    @validator('main_content_text')
    def content_must_be_substantive(cls, value):
        if len(value.split()) < 10:
            raise ValueError('Extracted content must contain at least 10 words for analysis.')
        return value

# --- NEW: Sub-models for the multi-faceted AI analysis ---

class SentimentAnalysis(BaseModel):
    sentiment: str = Field(..., description="Overall sentiment (e.g., Positive, Neutral, Negative)")
    tone: str = Field(..., description="The tone of the content (e.g., Professional, Casual, Promotional)")

class SEOAnalysis(BaseModel):
    recommendations: List[str]
    target_keywords: List[str]

class Readability(BaseModel):
    score_description: str = Field(..., description="A description of the readability level (e.g., 'High school level')")
    accessibility_notes: List[str]

class AIAnalysis(BaseModel):
    """
    Structures the comprehensive output from the multi-faceted LLM analysis.
    """
    summary: str
    key_points: List[str]
    sentiment_analysis: SentimentAnalysis
    topic_identification: List[str]
    seo_analysis: SEOAnalysis
    readability: Readability
    competitive_positioning: str

class AnalysisReport(BaseModel):
    """
    The final, comprehensive output format returned to the client.
    """
    url: HttpUrl
    content_analysis: ProcessedContent
    ai_summary: AIAnalysis