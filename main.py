from fastapi import FastAPI, File, UploadFile
import pdfplumber
import requests
import json
import re
import os
import logging
from typing import Dict, Any

app = FastAPI()

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3.2"  # Update to your actual model name

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text[:3000]  # limit tokens

def extract_json_from_text(text: str) -> Dict[Any, Any]:
    """
    Extract valid JSON from text that might contain additional content.
    """
    # Try to find JSON-like content within curly braces
    match = re.search(r'(\{.*\})', text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # If initial extraction fails, try more aggressive cleaning
            pass
    
    # Try to fix common JSON formatting issues
    # 1. Remove markdown code blocks
    cleaned_text = re.sub(r'```json|```', '', text)
    # 2. Try to extract just the JSON part
    cleaned_text = cleaned_text.strip()
    
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON after cleaning: {e}")
        
        # Create a fallback JSON with error information
        return {
            "profile": "Could not extract information",
            "experience": [],
            "skills": [],
            "profile_score": 0,
            "parsing_error": str(e)
        }

@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...)):
    try:
        temp_file = "temp.pdf"
        contents = await file.read()
        
        with open(temp_file, "wb") as f:
            f.write(contents)

        # Extract text
        text = extract_text_from_pdf(temp_file)

        if not text.strip():
            return {"error": "No readable text found in PDF"}

        # Updated prompt for best response with strict JSON requirements
        prompt = (
            "Extract and summarize the following PDF content. Provide a detailed profile summary that includes "
            "the person's name, basic details, work experience, and a list of skills. Additionally, compute a profile "
            "score out of 100. Respond ONLY with a valid, complete JSON object with the following keys: "
            "'profile', 'experience', 'skills', and 'profile_score'. Format the output as a raw JSON object without markdown "
            "formatting, explanation, or any other text. The response must start with '{' and end with '}'.\n\nPDF Content:\n" + text
        )

        payload = {
            "model": OLLAMA_MODEL,
            "stream": False,
            "prompt": prompt,
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            raw_response = result.get("response", "").strip()
            
            try:
                # First attempt: try direct JSON parsing
                json_response = json.loads(raw_response)
                return {"summary": json_response}
            except json.JSONDecodeError:
                # Second attempt: try to extract JSON from text
                logger.warning("Direct JSON parsing failed, attempting extraction")
                json_response = extract_json_from_text(raw_response)
                
                if "parsing_error" in json_response:
                    return {
                        "warning": "Model response required JSON extraction",
                        "summary": json_response,
                        "raw_response": raw_response[:500]  # Include truncated raw response for debugging
                    }
                return {"summary": json_response}
        else:
            return {
                "error": f"Failed to get response from Ollama: Status {response.status_code}",
                "details": response.text[:500] if response.text else "No response details"
            }
            
    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return {"error": f"Request to Ollama failed: {str(e)}"}
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {"error": f"Unexpected error: {str(e)}"}
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {str(e)}")