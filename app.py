from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import requests
import json

app = FastAPI()

db = pd.read_csv("product.csv")

class QueryRequest(BaseModel):
    query: str 

conversation_history = [
    {"role": "system", "content": "تو یک دستیار خرید هستی و باید هر ورودی رو به درستی تحلیل کنی. اگر کاربر اشتباه تایپی داشته باشد، آن را اصلاح کن."}
]

@app.post("/detect-intent/")
def detect_intent(query: QueryRequest):
   
    conversation_history.append({"role": "user", "content": query.query})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }


    prompt = f"""
    اگر کاربر گفت گشنمه یا گرسنمه یا ... از کاربر بپرس چه نوع خوراکی مدنظر دارد "سالم" , "ناسالم" باتوجه به جواب نوع سالم و ناسالم تنقلات مرتبط را پیشنهاد بده و از کاربر :
بپرس کدام تنقلات  و باتوجه به نوع تنقلات نوشیدنی مرتبط را هم پیشنهاد بده مثلا کیک با شیر
    - category را "میان وعده" قرار بده
    - preference تتقلات انتخابی با نوشیدنی مرتبط
    - quantites تنقلات با نوشیدنی مرتبط بصورت dict
    - action را "finish" بگذار
    - question (فقط اگر action = "next question")

    
    اگر کاربر نام یک غذا یا خوراکی نهایی مثل "املت"، "قرمه سبزی"، "سالاد"، "کیک" یا "پاستا" گفت، فرض کن که هدف کاربر تهیه آن غذاست. در این صورت:
    - category را "غذا" قرار بده
    - preference را لیستی از مواد اولیه آن غذا قرار بده
    - quantites لیست مواد اولیه به ازای یک نفر بصورت dict قرار بده
    - action را "finish" بگذار
    - question (فقط اگر action = "next question")
   
    اگر کاربر گفت "چی بخورم؟" یا "چی بخرم؟" یا "چی بزنم؟" یا "چی بزنیم؟" یا "چی بپزم؟" یا "چی درست کنم؟"، از کاربر بپرس که آیا می‌خواهد غذا، نوشیدنی، بهداشتی، انرژی‌زا، تنقلات یا پاکیزگی را انتخاب کند. اگر کاربر گفت "غذا"، از او بپرس که آیا می‌خواهد غذاهای سالم یا ناسالم را انتخاب کند. اگر کاربر گفت "غذای سالم"، از او بپرس که آیا می‌خواهد غذاهای گیاهی یا غیر گیاهی را انتخاب کند. در غیر این‌صورت، مثل حالت عادی عمل کن:
    - category: (غذا، نوشیدنی، بهداشتی، انرژی‌زا، تنقلات، پاکیزگی)
    - preference: (مثلاً پد، تامپون، قهوه، دمنوش آرامش‌بخش)
    - action: ("next question" اگر نیاز به سوال بیشتر باشد، در غیر این‌صورت "finish")
    - question: (فقط اگر action = "next question")
    
اگر کاربر گفت "حالم خوب نیست" یا "خسته ام" یا "انرژی ندارم" یا عباراتی مشابه:
    - category را "سلامتی" قرار بده 
    - preference را خالی بگذار
    - action را "next question" قرار بده
    - question را "جنسیت شما چیست؟" قرار بده

اگر کاربر در پاسخ گفت "زن" یا "دختر" یا "خانم":
    - category را "سلامتی" قرار بده
    - preference را لیستی از ["شکلات تلخ", "دمنوش آرامبخش", "ویتامین B", "قرص آهن"] قرار بده
    - action را "finish" قرار بده

اگر کاربر در پاسخ گفت "مرد" یا "پسر" یا "آقا":
    - category را "سلامتی" قرار بده
    - preference را لیستی از ["پروتئین بار", "نوشیدنی انرژی زا", "ویتامین D", "مکمل زینک"] قرار بده 
    - action را "finish" قرار بده

    در غیر این‌صورت، مثل حالت عادی عمل کن:
    - category: (غذا، نوشیدنی، بهداشتی، انرژی‌زا، تنقلات، پاکیزگی)
    - preference: (مثلاً پد، تامپون، قهوه، دمنوش آرامش‌بخش)L
    - action: ("next question" اگر نیاز به سوال بیشتر باشد، در غیر این‌صورت "finish")
    - question: (فقط اگر action = "next question")

    ورودی: "{query.query}"
    خروجی:
"""

    payload = {
        "model": "gpt-4o-mini",
        "messages": conversation_history + [{"role": "user", "content": prompt}],
        "max_tokens": 1000
    }

    response = requests.post(URL, headers=headers, json=payload)
    try:
        result = response.json()
        response_text = result["choices"][0]["message"]["content"].strip()

        print("🔍 API:", response_text)  
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        intent_data = json.loads(response_text)
        conversation_history.append({"role": "assistant", "content": response_text})
        return intent_data

    except json.JSONDecodeError:
        print("invalid error:", response_text)
        return None
    except Exception as e:
        print("unhandler error:", e)
        return None

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
