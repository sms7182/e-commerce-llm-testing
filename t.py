import pandas as pd
import requests
import json

db = pd.read_csv("product.csv")

API_KEY = ""
URL = ""

conversation_history = [
    {"role": "system", "content": "تو یک دستیار خرید هستی. پاسخ را به همان زبانی که ورودی دریافت می‌کنی ارائه بده. همیشه خروجی را در قالب JSON معتبر برگردان."}
]

def detect_intent(query):
    """ارسال درخواست به API و دریافت داده‌های مربوط به قصد کاربر"""
    global conversation_history

    conversation_history.append({"role": "user", "content": query})

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    prompt = f"""
    تحلیل کن که کاربر چه چیزی نیاز دارد و خروجی را در قالب JSON معتبر برگردان. ساختار پاسخ باید این‌گونه باشد:
      - category: (غذا، نوشیدنی، بهداشتی، انرژی‌زا، تنقلات، پاکیزگی)
      - preference: (اگر غذاست، سالم یا معمولی / اگر نوشیدنی است، آب یا انرژی‌زا / ... )
      - action: ("سوال بعدی" اگر نیاز به سوال بیشتر باشد، در غیر این‌صورت "تمام")
      - question: (فقط اگر action = "سوال بعدی"، سوال تکمیلی ارائه کن)

    مثال:
    ورودی: "ماست می‌خوام"
    خروجی:
    {{
        "category": "غذا",
        "preference": "ماست",
        "action": "سوال بعدی",
        "question": "چه نوع ماستی می‌خواهید؟ کم چرب یا پرچرب؟"
    }}

    ورودی: "{query}"
    خروجی:
    """

    payload = {
        "model": "gpt-4o-mini",
        "messages": conversation_history + [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }

    response = requests.post(URL, headers=headers, json=payload)
    
    try:
        result = response.json()
        response_text = result["choices"][0]["message"]["content"].strip()

        print("🔍 پاسخ خام API:", response_text)  

        intent_data = json.loads(response_text)
        conversation_history.append({"role": "assistant", "content": response_text})
        return intent_data

    except json.JSONDecodeError:
        print("⚠️ API پاسخ نامعتبر فرستاده است:", response_text)
        return None
    except Exception as e:
        print("⚠️ خطای غیرمنتظره:", e)
        return None

def get_suggestions(intent_data):
    """پردازش داده‌های تشخیص قصد و پیشنهاد سبد خرید"""
    if not intent_data:
        return []

    category = intent_data.get("category", "")
    preference = intent_data.get("preference", "")
    action = intent_data.get("action", "")
    question = intent_data.get("question", "")

    cart = []

    if action == "سوال بعدی":
        follow_up = input(f"{question} (برای خروج q بزنید) ")
        if follow_up.lower() == "q":
            print("خدانگهدار!")
            return []
        return get_suggestions(detect_intent(follow_up))  
    
    if preference == "پیتزا":
        pizza_type = input("چه نوع پیتزایی؟ (پپرونی، سبزیجات، مرغ و قارچ) ")
        if pizza_type == "پپرونی":
            cart.extend(["خمیر پیتزا", "پنیر موزارلا", "سس گوجه", "پپرونی"])
        elif pizza_type == "سبزیجات":
            cart.extend(["خمیر پیتزا", "پنیر موزارلا", "سس گوجه", "فلفل دلمه", "قارچ", "زیتون"])
        elif pizza_type == "مرغ و قارچ":
            cart.extend(["خمیر پیتزا", "پنیر موزارلا", "سس گوجه", "قارچ", "سینه مرغ"])
        print(f"برای پیتزای {pizza_type} این مواد را تهیه کنید:")

    return cart

print("سلام! من دستیار خرید شما هستم. بگویید چه می‌خواهید.")
while True:
    user_input = input("چی می‌خوای؟ (برای خروج q بزنید) ")
    if user_input.lower() == "q":
        print("خداحافظ! 😊")
        break
    intent_data = detect_intent(user_input)
    cart = get_suggestions(intent_data)
    if cart:
        print("🛒 سبد خرید:", cart)
