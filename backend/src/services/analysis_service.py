import google.generativeai as genai
import json
from ..config import settings
from ..models.data_models import AIAnalysis  # Import the new, comprehensive model

# Configure the Gemini client
if settings.GOOGLE_API_KEY:
    genai.configure(api_key=settings.GOOGLE_API_KEY)
else:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")

class AnalysisService:
    """
    A comprehensive AI analysis engine that performs multi-faceted content analysis.
    """
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest')

    def analyze_content(self, content: str) -> AIAnalysis:
        """
        Analyzes content across multiple dimensions and returns a structured Pydantic model.
        """
        # A new, highly-detailed prompt to generate the multi-faceted report
        prompt = f"""
        Analyze the following website content and generate a comprehensive, multi-faceted report.
        The report MUST be a single, valid JSON object with the exact following structure:
        {{
          "summary": "A concise summary of the content, written in an engaging style.",
          "key_points": ["A list of the three to five most important key points as strings."],
          "sentiment_analysis": {{
            "sentiment": "The overall sentiment (Positive, Neutral, or Negative).",
            "tone": "The primary tone of the content (e.g., Professional, Casual, Promotional, Technical)."
          }},
          "topic_identification": ["A list of the main topics or themes as strings."],
          "seo_analysis": {{
            "recommendations": ["A list of 2-3 actionable SEO recommendations based on the text."],
            "target_keywords": ["A list of 3-5 likely target keywords for this page."]
          }},
          "readability": {{
            "score_description": "A brief description of the readability level (e.g., 'Easily understandable by a general audience', 'Requires expert knowledge').",
            "accessibility_notes": ["A list of 1-2 notes for improving content accessibility."]
          }},
          "competitive_positioning": "A brief analysis of the company's competitive position, unique selling proposition, or market standing based on the text."
        }}

        Website Content to Analyze:
        ---
        {content[:15000]}
        ---

        Provide ONLY the raw JSON object in your response. Do not include markdown formatting like ```json.
        """
        try:
            response = self.model.generate_content(prompt)
            # Clean the response to ensure it's a valid JSON string
            cleaned_response_text = response.text.strip().replace('```json', '').replace('```', '')
            analysis_data = json.loads(cleaned_response_text)

            # Validate the data by parsing it with the Pydantic model
            # This ensures the LLM's output matches our required structure
            validated_analysis = AIAnalysis.parse_obj(analysis_data)
            return validated_analysis

        except Exception as e:
            print(f"Error during Gemini analysis or Pydantic validation: {e}")
            raise ValueError(f"Failed to generate or validate the AI analysis. The LLM response may have been malformed.")