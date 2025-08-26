# api/endpoints.py
from fastapi import FastAPI, HTTPException, Depends
from typing import Dict
from models.marketing_assistant import MarketingAssistant
from models.qa_bot import NLPQABot
from config.settings import settings

app = FastAPI()
marketing_assistant = MarketingAssistant(api_key=settings.OPENAI_API_KEY)
qa_bot = NLPQABot()

@app.post("/generate-marketing-content/")
async def generate_marketing_content(
    content_type: str,
    parameters: Dict
) -> Dict:
    try:
        content = marketing_assistant.generate_content(
            content_type=content_type,
            **parameters
        )
        return {"content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/answer-question/")
async def answer_question(
    question: str,
    context: str
) -> Dict:
    try:
        answer = qa_bot.answer_question(question, context)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))