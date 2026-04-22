import requests
from fastapi import APIRouter
import os
from dotenv import load_dotenv


router = APIRouter()

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")

@router.post("/chat")
async def chat(data: dict):
    question = data.get("question")
    dataset = data.get("data")

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openrouter/auto",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a data analyst AI."
                    },
                    {
                        "role": "user",
                        "content": f"Dataset: {dataset}\nQuestion: {question}"
                    }
                ]
            }
        )

        result = response.json()

        # 🔍 DEBUG (check terminal)
        print("OPENROUTER RESPONSE:", result)

        # ✅ SAFE EXTRACTION
        if "choices" in result and len(result["choices"]) > 0:
            answer = result["choices"][0]["message"]["content"]
        else:
            answer = "⚠️ AI error: " + str(result)

        return {"answer": answer}

    except Exception as e:
        return {"answer": "❌ Server error: " + str(e)}