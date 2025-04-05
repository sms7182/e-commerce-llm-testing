import pandas as pd
import requests
import json


db = pd.read_csv("product.csv")

conversation_history = [
    {"role": "system", "content": "تو یک دستیار خرید هستی. همیشه پاسخ را به همان زبانی که ورودی دریافت می‌کنی بده و همیشه خروجی را به صورت JSON معتبر برگردان."}
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
      - category: (مواد غذایی, لبنیات, نوشیدنی, بهداشتی, انرژی‌زا, تنقلات, پاکیزگی)
      - preference: (مثلاً پیتزا, کیک, قهوه, دمنوش آرامش‌بخش)
      - action: ("سوال بعدی" اگر نیاز به سوال بیشتر باشد، در غیر این‌صورت "تمام")
      - question: (فقط اگر action = "سوال بعدی"، سوال تکمیلی ارائه کن)
    ورودی: "{query}"
    خروجی:
    """

    payload = {
        "model": "gpt-4o-mini",
        "messages": conversation_history + [{"role": "user", "content": prompt}],
        "max_tokens": 200
    }

    response = requests.post(URL, headers=headers, json=payload)
    
    try:
        result = response.json()
        response_text = result["choices"][0]["message"]["content"].strip()

        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        intent_data = json.loads(response_text)
        conversation_history.append({"role": "assistant", "content": response_text})
        return intent_data

    except Exception as e:
        print("⚠️ خطا در پردازش درخواست:", e)
        return None

def get_suggestions(intent_data):
    """پردازش داده‌های تشخیص قصد و پیشنهاد سبد خرید بر اساس دیتابیس"""
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
        if preference == "پیتزا":
            related_products = db[db['related_keywords'].str.contains('پیتزا', na=False)]
            if not related_products.empty:
                print("\nمواد اولیه مورد نیاز برای پیتزا:")
                for _, product in related_products.iterrows():
                    cart.append(f"{product['product_name']} ({product['quantity']} {product['unit']})")
        
        elif preference == "کیک":
            related_products = db[db['related_keywords'].str.contains('کیک', na=False)]
            if not related_products.empty:
                print("\nمواد اولیه مورد نیاز برای کیک:")
                for _, product in related_products.iterrows():
                    cart.append(f"{product['product_name']} ({product['quantity']} {product['unit']})")

    return cart

print("سلام! من دستیار خرید شما هستم. می‌تونم در تهیه مواد اولیه بهتون کمک کنم.")
while True:
    user_input = input("\nچه غذایی می‌خوای درست کنی؟ (برای خروج q بزنید) ")
    if user_input.lower() == "q":
        print("خداحافظ! 😊")
        break
    
    intent_data = detect_intent(user_input)
    cart = get_suggestions(intent_data)
    
    if cart:
        print("\n🛒 لیست مواد اولیه پیشنهادی:")
        for item in cart:
            print(f"- {item}")
    else:
        print("متاسفانه محصولی یافت نشد. می‌تونید سوال دیگری بپرسید.")