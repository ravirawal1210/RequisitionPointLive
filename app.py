import io
import json
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pypdf import PdfReader
from groq import Groq

app = FastAPI(title="Groq AI Document Extraction Agent API")

# Enable CORS for cross-origin frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ExtractedPoints(BaseModel):
    points: list[str] = Field(description="A sequential list of key points extracted from the text, numbered 1, 2, 3, etc.")

@app.post("/extract-points", response_model=ExtractedPoints)
async def extract_points_from_pdf(
    file: UploadFile = File(...), 
    x_groq_api_key: str = Header(None, alias="X-Groq-API-Key")
):
    # Enforce API Key validation
    if not x_groq_api_key:
        raise HTTPException(
            status_code=401, 
            detail="Missing API Key. Please pass your Groq API key in the 'X-Groq-API-Key' header."
        )

    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        # Initialize Groq client dynamically with incoming client key
        client = Groq(api_key=x_groq_api_key)

        file_bytes = await file.read()
        pdf_file = io.BytesIO(file_bytes)
        
        reader = PdfReader(pdf_file)
        document_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                document_text += text + "\n"
        
        if not document_text.strip():
            raise HTTPException(status_code=400, detail="The uploaded PDF contains no extractable text.")

        prompt = (
            "Extract all the key bullet points from this document text. "
            "Crucial requirement: Prefix every single extracted point with its sequential number item "
            "using the exact format '1. ', '2. ', '3. ', etc. inside the JSON array values."
            f"\n\nDocument Text:\n{document_text}"
        )

        # Utilizing the stable production versatile model flag
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"},
        )
        
        response_data = json.loads(chat_completion.choices[0].message.content)
        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq Agent Error: {str(e)}")