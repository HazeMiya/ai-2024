from fastapi import FastAPI, HTTPException
import wikipedia
from pydantic import BaseModel
from typing import List, Optional
import re

wikipedia.set_lang("ja")

app = FastAPI()

class BookAnalysis(BaseModel):
    title: str
    summary: str
    locations: List[str] = []
    characters: List[str] = []

@app.get("/")
def read_root():
    return {"message": "本の分析APIへようこそ"}

@app.get("/analyze/{title}", response_model=BookAnalysis)
def analyze_book(title: str):
    try:
        # Wikipediaから情報を取得
        page = wikipedia.page(title)
        text = page.content[:3000]

        # 簡易的な場所と人物の抽出（「〜市」「〜県」「〜さん」「〜君」などで判定）
        locations = list(set(re.findall(r'[^\s　]+(市|県|区|町|村)', text)))[:5]
        characters = list(set(re.findall(r'[^\s　]+(さん|君|様|先生)', text)))[:5]

        return {
            "title": title,
            "summary": text[:200] + "...",
            "locations": locations,
            "characters": characters
        }

    except wikipedia.exceptions.PageError:
        raise HTTPException(status_code=404, detail=f"『{title}』の情報が見つかりませんでした")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)