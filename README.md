# Simple LLM Resume Parser

A FastAPI application that extracts and summarizes information from resumes/CVs in PDF format using LLaMA models through Ollama.

## Features

- Upload PDF resumes/CVs
- Extract text content from PDFs
- Process extracted text using LLaMA models
- Return structured JSON with profile details, experience, skills, and scoring
- Robust JSON error handling and extraction
- Comprehensive error reporting

## Prerequisites

- Python 3.8+
- [Ollama](https://ollama.ai/) installed locally with LLaMA models

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/shreytrivedi002/simple-llm-resume-parser.git
   cd simple-llm-resume-parser
   ```

2. Install Python dependencies:
   ```bash
   pip install fastapi uvicorn pdfplumber requests
   ```

## Setting up Ollama with LLaMA

1. Install Ollama by following the instructions at [https://ollama.ai/](https://ollama.ai/)

2. Pull the LLaMA model:
   ```bash
   ollama pull llama3.2
   ```
   
   Note: If you want to use a different LLaMA model, update the `OLLAMA_MODEL` variable in `main.py`.

3. Start the Ollama server:
   ```bash
   ollama serve
   ```

## Usage

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`

3. Access the API documentation at `http://localhost:8000/docs`

4. Use the `/process-pdf/` endpoint to upload and process PDF resumes:
   - This can be done via the Swagger UI at `/docs`
   - Or by sending a POST request with a file upload to `/process-pdf/`

### Example API Response

```json
{
  "summary": {
    "profile": "John Doe, Software Engineer with 5 years of experience",
    "experience": ["Company A - Senior Developer (2020-Present)", "Company B - Junior Developer (2018-2020)"],
    "skills": ["Python", "JavaScript", "Machine Learning", "Docker"],
    "profile_score": 85
  }
}
```

### Error Handling

The API includes robust error handling:

- **JSON Parsing Errors**: When the LLM returns malformed JSON, the application attempts to:
  1. First try direct JSON parsing
  2. Use regex-based extraction to find JSON objects in text
  3. Remove markdown code blocks and other non-JSON content
  4. Provide fallback response with error details if extraction fails

- **Request Errors**: Timeouts and connection issues with the Ollama server are properly handled

- **Runtime Errors**: Comprehensive exception handling with detailed error messages

- **Temporary Files**: Proper cleanup of temporary PDF files

## Configuration

- The default Ollama endpoint is set to `http://localhost:11434/api/generate`
- The default LLaMA model is set to `llama3.2`
- You can modify these settings in `main.py`
- Error logging level can be configured through standard Python logging settings

## License

MIT

## Author

SHREY TRIVEDI 