import pandas as pd
import requests
import json

db = pd.read_csv("product.csv")

API_KEY = ""  
URL = ""

conversation_history = [
    {"role": "system", "content": "تو یک دستیار خرید هستی . همیشه پاسخ را به همان زبانی که ورودی دریافت می‌کنی بده و همیشه خروجی را به صورت JSON معتبر برگردان."+"کلمات کلیدی رو از اینا انتخاب کن:"+db['related_keywords'].to_string()}
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
      - preference: (مثلاً پد، تامپون، قهوه، دمنوش آرامش‌بخش)
      - action: ("سوال بعدی" اگر نیاز به سوال بیشتر باشد، در غیر این‌صورت "تمام")
      - question: (فقط اگر action = "سوال بعدی"، سوال تکمیلی ارائه کن)
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
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
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
    elif action == "تمام":
        print()

    if category == "بهداشتی" and preference in ["پد", "تامپون", "کاپ"]:
        print(f"پیشنهادات برای {preference} دریافت می‌شود...")
        if preference == "پد":
            cart.append("پد بهداشتی با جذب بالا")
        elif preference == "تامپون":
            cart.append("تامپون ضد حساسیت")
        elif preference == "کاپ":
            cart.append("کاپ قاعدگی ضد حساسیت")

    elif category == "نوشیدنی" and preference in ["قهوه", "دمنوش آرامبخش"]:
        if preference == "قهوه":
            cart.append("قهوه فوری 3 در 1")
        elif preference == "دمنوش آرامبخش":
            cart.append("دمنوش گل گاوزبان")

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
