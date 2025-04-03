import pandas as pd
import requests


db = pd.read_csv("product.csv")


API_KEY = "" 
URL = ""

def detect_intent(query):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "",
        "messages": [
            {
                "role": "system",
                "content": "تو یه دستیار خرید ساده هستی. نیاز مشتری رو تشخیص بده و یه کلمه کلیدی از اینا برگردون: " + db['related_keywords'].to_string()
            },
            {
                "role": "user",
                "content": f"مشتری نوشته: '{query}'. فقط یه کلمه کلیدی بگو."
            }
        ],
        "max_tokens": 10
    }
    response = requests.post(URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip()

def get_suggestions(intent):
    cart = []

    if "کیک" in intent:
        preference = input("با پودر آماده یا از صفر؟ (پودر/صفر) ")
        if preference == "پودر":
            cart.append("پودر کیک شکلاتی (500 گرم)")
            print("یه کیک سریع آماده کن!")
        elif preference == "صفر":
            cart.extend(["آرد سفید (2 پیمانه)", "شکر (1 پیمانه)", "تخم‌مرغ (3 عدد)", "روغن مایع (0.5 پیمانه)"])
            print("کیکت رو با عشق درست کن!")

    elif "پیتزا" in intent:
        cart.extend(["خمیر پیتزا تازه (300 گرم)", "پنیر موزارلا (150 گرم)", "سس گوجه (3 قاشق غذاخوری)"])
        print("پیتزای خونگی همیشه خوبه!")

    elif "بی‌حال" in intent or "خستم" in intent:
        preference = input("نوشیدنی انرژی‌زا می‌خوای یا آب؟ (انرژی/آب) ")
        if preference == "انرژی":
            cart.extend(["قهوه فوری (10 گرم)", "هایپ (250 میلی‌لیتر)"])
            print("اینا حالتو جا میاره!")
        elif preference == "آب":
            cart.append("آب معدنی (1.5 لیتر)")
            print("آب بخور، تازه شی!")

    elif "تشنمه" in intent:
        cart.append("آب معدنی (1.5 لیتر)")
        print("تشنگیت رفع می‌شه!")

    elif "پریود" in intent or "قاعدگی" in intent:
        cart.extend(["نوار بهداشتی (1 بسته)", "شکلات تلخ (50 گرم)"])
        print("استراحت کن و شکلات بخور!")

    elif "تمیز" in intent or "خونه" in intent:
        cart.extend(["مایع ظرفشویی (500 میلی‌لیتر)", "دستمال کاغذی (1 بسته)"])
        print("خونه‌ت برق بزنه!")

    else:
        suggestions = db[db["related_keywords"].str.contains(intent, na=False)]
        if not suggestions.empty:
            for _, row in suggestions.iterrows():
                cart.append(f"{row['product_name']} ({row['quantity']} {row['unit']})")
        else:
            print("متوجه نشدم! یه بار دیگه بگو.")
            return []

    return cart


print("سلام! من دستیار خریدتم. بگو چی می‌خوای.")
while True:
    user_input = input("چی می‌خوای؟ (برای خروج q بزن) ")
    if user_input.lower() == "q":
        print("خداحافظ! تست دموت موفق باشه!")
        break
    intent = detect_intent(user_input)
    cart = get_suggestions(intent)
    if cart:
        print("سبد خرید:", cart)