# gemini_canvas_app.py
# Enhanced Python script using Gemini API to generate and edit text like Gemini Canvas

import google.generativeai as genai
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import os
from typing import Optional
import logging
import dotenv
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Step 1: Configure Gemini API key from environment variable
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set")
    raise ValueError("Please set GEMINI_API_KEY environment variable")

genai.configure(api_key=API_KEY)

# Step 2: Initialize model
model = genai.GenerativeModel("gemini-2.5-flash")

# Step 3: Create FastAPI app
app = FastAPI(
    title="Gemini Canvas App",
    description="A text processing API using Gemini AI",
    version="1.0.0"
)

# Configure CORS more securely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Specify allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Request models
class TextRequest(BaseModel):
    text: str
    action: str  # 'rewrite', 'summarize', 'expand', 'improve', 'simplify'
    style: Optional[str] = None  # 'formal', 'casual', 'professional', 'creative'

class GenerateRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 1000

# Step 4: Enhanced text manipulation endpoint
@app.post("/process")
async def process_text(req: TextRequest):
    """Process text with various actions and styles"""
    
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Enhanced prompt mapping with style considerations
    style_modifier = ""
    if req.style:
        style_modifier = f" Make the tone {req.style}."
    
    prompt_map = {
        "rewrite": f"Rewrite the following text in a clear, concise manner{style_modifier}:\n\n{req.text}",
        "summarize": f"Summarize the following text concisely{style_modifier}:\n\n{req.text}",
        "expand": f"Expand the following into more detailed content{style_modifier}:\n\n{req.text}",
        "improve": f"Improve the following text for clarity and engagement{style_modifier}:\n\n{req.text}",
        "simplify": f"Simplify the following text to make it easier to understand{style_modifier}:\n\n{req.text}",
    }
    
    prompt = prompt_map.get(req.action)
    if not prompt:
        raise HTTPException(status_code=400, detail=f"Unsupported action: {req.action}")

    try:
        response = model.generate_content(prompt)
        if not response.text:
            raise HTTPException(status_code=500, detail="No response generated")
        
        logger.info(f"Successfully processed text with action: {req.action}")
        return {"result": response.text, "action": req.action, "style": req.style}
    
    except Exception as e:
        logger.error(f"Error processing text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")

# Step 5: Generate new content endpoint
@app.post("/generate")
async def generate_content(req: GenerateRequest):
    """Generate new content from a prompt"""
    
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    
    try:
        response = model.generate_content(req.prompt)
        if not response.text:
            raise HTTPException(status_code=500, detail="No content generated")
        
        logger.info("Successfully generated new content")
        return {"result": response.text, "prompt": req.prompt}
    
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating content: {str(e)}")

# Step 6: Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Gemini Canvas App"}

# Step 7: List available models endpoint
@app.get("/models")
async def list_models():
    """List available Gemini models"""
    try:
        models = genai.list_models()
        model_names = [model.name for model in models]
        return {"models": model_names}
    except Exception as e:
        logger.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing models: {str(e)}")

# Step 8: Simple frontend for testing
@app.get("/", response_class=HTMLResponse)
async def get_frontend():
    """Simple HTML frontend for testing the API"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Gemini Canvas App</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            textarea { width: 100%; height: 200px; margin: 10px 0; }
            button { padding: 10px 20px; margin: 5px; cursor: pointer; }
            .result { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
            select { padding: 5px; margin: 5px; }
        </style>
    </head>
    <body>
        <h1>Gemini Canvas App</h1>
        <div>
            <h3>Process Text</h3>
            <textarea id="inputText" placeholder="Enter your text here..."></textarea>
            <div>
                <label>Action:</label>
                <select id="action">
                    <option value="rewrite">Rewrite</option>
                    <option value="summarize">Summarize</option>
                    <option value="expand">Expand</option>
                    <option value="improve">Improve</option>
                    <option value="simplify">Simplify</option>
                </select>
                <label>Style:</label>
                <select id="style">
                    <option value="">Default</option>
                    <option value="formal">Formal</option>
                    <option value="casual">Casual</option>
                    <option value="professional">Professional</option>
                    <option value="creative">Creative</option>
                </select>
                <button onclick="processText()">Process</button>
            </div>
            <div id="result" class="result" style="display:none;"></div>
        </div>
        
        <script>
            async function processText() {
                const text = document.getElementById('inputText').value;
                const action = document.getElementById('action').value;
                const style = document.getElementById('style').value;
                
                if (!text.trim()) {
                    alert('Please enter some text');
                    return;
                }
                
                try {
                    const response = await fetch('/process', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ text, action, style })
                    });
                    
                    const data = await response.json();
                    
                    if (response.ok) {
                        document.getElementById('result').style.display = 'block';
                        document.getElementById('result').innerHTML = `<strong>Result:</strong><br>${data.result}`;
                    } else {
                        alert('Error: ' + data.detail);
                    }
                } catch (error) {
                    alert('Error: ' + error.message);
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content

# Run the server
if __name__ == "__main__":
    uvicorn.run(
        "gemini_canvas_app:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=True,
        log_level="info"
    )