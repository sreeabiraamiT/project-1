# services.py
import json
import os
import asyncio
from datetime import datetime
from fastapi import UploadFile
from google import genai
from google.genai import types, errors
from dotenv import load_dotenv

load_dotenv()

# Initialize the Gemini Client
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from the environment configuration.")

client = genai.Client(api_key=api_key)


class AIServiceUnavailableError(Exception):
    """Raised when the Gemini API is overloaded/unavailable after retries."""
    pass

async def run_complete_student2_pipeline(file: UploadFile) -> dict:
    """
    Unified processing pipeline:
    1. Extracts core textual data from the raw bill file (Student 2)
    2. Uses consumption parameters to build tailored savings tips (Student 3)
    """
    # Read the upload stream into raw bytes
    file_bytes = await file.read()
    
    # Combined Prompt for both extraction and contextual advisory tips
    prompt = """
    You are an expert utility bill analysis assistant.
    Analyze this electricity bill document carefully and extract data matching the instructions below.
    
    Return ONLY a valid JSON object structure with the exact keys:
    {
      "consumer_number": "string",
      "bill_month": "YYYY-MM-DD",
      "tariff_category": "Domestic or Commercial",
      "units_consumed": 0.0,
      "ai_summary": "A brief 2-3 sentence summary of the consumption behavior displayed.",
      "saving_tips": ["Actionable Tip 1", "Actionable Tip 2", "Actionable Tip 3"]
    }
    
    Rules:
    1. 'bill_month' MUST be parsed into an absolute ISO standard date string (e.g., '2026-06-01'). If only Month/Year is visible, default to day 1.
    2. 'tariff_category' must evaluate to either 'Domestic' or 'Commercial'.
    3. 'units_consumed' must be isolated as a float value.
    4. Provide exactly 3 highly functional electricity-saving tips inside the 'saving_tips' array.
    5. Do not include any markdown format tags like ```json or trailing text blocks.
    """

    # Call Gemini model — retry transient 5xx errors (e.g. "high demand") before giving up
    max_attempts = 3
    last_error = None
    response = None

    for attempt in range(1, max_attempts + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=file.content_type
                    )
                ]
            )
            break  # success — stop retrying
        except errors.ServerError as e:
            # Transient overload (503 UNAVAILABLE etc.) — worth retrying
            last_error = e
            if attempt < max_attempts:
                await asyncio.sleep(2 * attempt)  # 2s, then 4s backoff
                continue
        # Non-retryable client errors (bad key, bad request, etc.) bubble up immediately
        except errors.ClientError as e:
            raise

    if response is None:
        # All retries exhausted — surface a clean, client-safe error
        raise AIServiceUnavailableError(
            "The AI analysis service is currently experiencing high demand. "
            "Please try again in a minute."
        ) from last_error

    # Sanitize and strip response formatting
    raw_text = response.text.strip()
    raw_text = raw_text.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError:
        raise ValueError("AI response structure could not be correctly decoded into structured JSON data.")

    # Convert string-based date to a native Python datetime object for compatibility with database models
    try:
        parsed_date = datetime.strptime(data.get("bill_month", ""), "%Y-%m-%d").date()
    except Exception:
        parsed_date = datetime.now().date()  # Emergency fallback

    # Reassemble consistent mapping for upload.py
    return {
        "consumer_number": str(data.get("consumer_number", "UNKNOWN")),
        "bill_month": parsed_date,
        "units_consumed": float(data.get("units_consumed", 0.0)),
        "tariff_category": str(data.get("tariff_category", "Domestic")),
        "ai_summary": str(data.get("ai_summary", "Extraction complete.")),
        "saving_tips": list(data.get("saving_tips", ["Optimize usage where applicable."]))
    }