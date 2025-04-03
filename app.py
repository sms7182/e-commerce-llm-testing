from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import requests
import json

app = FastAPI()

db = pd.read_csv("product.csv")

class QueryRequest(BaseModel):
    query: str 

API_KEY = "" 
URL = ""

conversation_history = [
    {"role": "system", "content": "تو یک دستیار خرید هستی و باید هر ورودی رو به درستی تحلیل کنی. اگر کاربر اشتباه تایپی داشته باشد، آن را اصلاح کن."}
]

@app.post("/detect-intent/")
def detect_intent(query: QueryRequest):
    """تحلیل نیازهای کاربر از طریق API و بازگشت نتیجه در قالب JSON"""
    global conversation_history
    conversation_history.append({"role": "user", "content": query.query})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    تحلیل کن که کاربر چه چیزی نیاز دارد و خروجی را در قالب JSON معتبر برگردان. ساختار پاسخ باید این‌گونه باشد:
      - category: (غذا، نوشیدنی، بهداشتی، انرژی‌زا، تنقلات، پاکیزگی)
      - preference: (اگر غذاست، سالم یا معمولی / اگر نوشیدنی است، آب یا انرژی‌زا / ... )
      - action: ("سوال بعدی" اگر نیاز به سوال بیشتر باشد، در غیر این‌صورت "تمام")
      - question: (فقط اگر action = "سوال بعدی", سوال تکمیلی ارائه کن)

    ورودی: "{query.query}"
    خروجی:
    """

    payload = {
        "model": "",
        "messages": conversation_history + [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }

    response = requests.post(URL, headers=headers, json=payload)
    
    try:
        result = response.json()
        response_text = result["choices"][0]["message"]["content"].strip()

        print("🔍 پاسخ خام API:", repr(response_text))  

        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        
        intent_data = json.loads(response_text)
        conversation_history.append({"role": "assistant", "content": response_text})
        return intent_data
    except Exception as e:
        return {"error": str(e)}

@app.post("/get-suggestions/")
def get_suggestions(intent_data: dict):
    """پردازش داده‌های تشخیص نیاز و پیشنهاد سبد خرید"""
    category = intent_data.get("category", "")
    preference = intent_data.get("preference", "")
    action = intent_data.get("action", "")
    question = intent_data.get("question", "")

    cart = []

    if preference == "پیتزا":
        pizza_type = input("چه نوع پیتزایی؟ (پپرونی، سبزیجات، مرغ و قارچ) ")
        if pizza_type == "پپرونی":
            cart.extend(["خمیر پیتزا", "پنیر موزارلا", "سس گوجه", "پپرونی"])
        elif pizza_type == "سبزیجات":
            cart.extend(["خمیر پیتزا", "پنیر موزارلا", "سس گوجه", "فلفل دلمه", "قارچ", "زیتون"])
        elif pizza_type == "مرغ و قارچ":
            cart.extend(["خمیر پیتزا", "پنیر موزارلا", "سس گوجه", "قارچ", "سینه مرغ"])
        print(f"برای پیتزای {pizza_type} این مواد رو بگیر:")

    elif preference == "ماست":
        cart.append("ماست کم چرب یا پرچرب")

    return {"cart": cart, "action": action, "question": question}
