#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ابزار تست چت‌بات هوش مصنوعی — قدم ۲: پرسش‌وپاسخ با مدل محلی Ollama
=====================================================================

این فایل کاملاً جداگانه و مستقل است. به هیچ‌کدوم از فایل‌های سامانه‌ی
اصلی وابسته نیست و هیچ‌کدومشون رو تغییر نمی‌ده — فقط فایل
"strategic_export.json" (که با export_strategic_data.py ساخته شده)
رو می‌خونه و به Ollama که روی همین سیستم نصبه وصل می‌شه.

اگه هر زمانی خواستید این آزمایش رو کنار بذارید، کافیه کل پوشه‌ی
"ai_chat_test" رو پاک کنید — هیچ اثری روی بقیه‌ی سامانه نمی‌ذاره.
این فایل حتی به جنگو (Django) هم نیازی نداره — فقط پایتون معمولی.

پیش‌نیاز:
  - Ollama باید روی همین سیستم نصب و در حال اجرا باشه (پیش‌فرض روی
    آدرس http://localhost:11434).
  - مدل qwen2.5:1.5b باید از قبل دانلود شده باشه (با دستور
    "ollama pull qwen2.5:1.5b" — که شما قبلاً انجام دادید).
  - فایل strategic_export.json باید کنار همین فایل باشه (با اجرای
    export_strategic_data.py ساخته می‌شه).

نحوه‌ی اجرا:

    python ai_chat_test\\chat_with_ollama.py

بعد یه لیست از کسب‌وکارها نشون داده می‌شه، یکی رو با شماره انتخاب
می‌کنید، و بعد می‌تونید هر سوالی درباره‌ی وضعیت اهداف استراتژیک اون
کسب‌وکار بپرسید. برای خروج، کلمه‌ی "خروج" رو بنویسید.
"""

import os
import sys
import json
import urllib.request
import urllib.error

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(THIS_DIR, "strategic_export.json")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")

MAX_HISTORY_TURNS = 4  # فقط ۴ پرسش‌وپاسخ آخر رو نگه می‌داریم که حافظه مدل شلوغ نشه


def load_export():
    if not os.path.exists(DATA_PATH):
        print("فایل داده پیدا نشد:", DATA_PATH)
        print("اول باید این دستور رو اجرا کنید تا داده‌ها ساخته بشن:")
        print("    python ai_chat_test\\export_strategic_data.py")
        sys.exit(1)
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def render_business_unit_as_text(bu):
    """اطلاعات یک کسب‌وکار رو به یه متن ساده و خوانا برای مدل تبدیل می‌کنه
    (به‌جای دادن JSON خام، چون مدل‌های کوچیک متن ساده رو بهتر می‌فهمن)."""
    lines = []
    lines.append(f"کسب‌وکار: {bu['نام']}")
    s = bu["خلاصه"]
    lines.append(
        f"خلاصه‌ی وضعیت: از مجموع {s['تعداد_کل_اهداف']} هدف استراتژیک، "
        f"{s['در_مسیر']} هدف در مسیر، {s['نیازمند_پیگیری']} هدف نیازمند پیگیری، "
        f"{s['در_معرض_ریسک']} هدف در معرض ریسک، و {s['بدون_شاخص']} هدف هنوز "
        f"هیچ شاخصی وصل نداره."
    )
    lines.append("")
    lines.append("جزئیات هر هدف:")
    for o in bu["اهداف"]:
        pct = o["درصد_تحقق_کارت"]
        pct_txt = f"{pct}٪" if pct is not None else "نامشخص"
        lines.append(f"- [{o['کد']}] {o['عنوان']} | منظر: {o['منظر']} | "
                     f"وضعیت: {o['وضعیت_کارت']} ({pct_txt})")
        for k in o["شاخص‌ها"]:
            kp = k["درصد_تحقق"]
            kp_txt = f"{kp}٪" if kp is not None else "بدون مقدار ثبت‌شده"
            lines.append(f"    · شاخص {k['نوع']} {k['کد']} — {k['نام']} — "
                         f"تحقق: {kp_txt} — وزن در این هدف: {k['وزن']}")
    return "\n".join(lines)


def detect_deterministic_facts(question, objectives):
    """این تابع، قبل از اینکه اصلاً به مدل چیزی بدیم، خودش (با کد پایتون
    ساده و همیشه دقیق، نه با حدس مدل) دنبال می‌گرده ببینه سوال کاربر
    شبیه یکی از این حالت‌های رایج هست یا نه: «کدوم اهداف در معرض
    ریسکن؟»، «ضعیف‌ترین اهداف کدومن؟» و امثال این.

    چرا این کار لازم بود: مدل ۱.۵ میلیاردی وقتی خودش بخواد بین ۳۰-۴۵
    هدف بگرده و فیلتر/شمارش کنه، گاهی اشتباه می‌کنه (مثلاً هدفی با
    ۸۰٪ که باید «نیازمند پیگیری» باشه رو «در معرض ریسک» جا می‌زنه، یا
    تعداد رو اشتباه می‌گه). با این تابع، لیستِ درست و قطعی رو از قبل
    با کد پایتون (دقیقاً همون منطقی که خود سامانه استفاده می‌کنه)
    می‌سازیم و به مدل می‌گیم فقط همین رو با جمله‌ی روان بازنویسی کنه —
    یعنی کار مدل فقط «نوشتن»، نه «شمردن»."""
    q = question

    def make_block(label, matched):
        if not matched:
            return f"{label} (تعداد: ۰) — فعلاً هیچ موردی با این شرط وجود نداره."
        lines = [f"{label} — این فهرست دقیق و قطعی است (مستقیماً از دیتابیس سامانه محاسبه شده، تعداد: {len(matched)}):"]
        for o in matched:
            pct = o["درصد_تحقق_کارت"]
            pct_txt = f"{pct}٪" if pct is not None else "نامشخص"
            lines.append(f"- [{o['کد']}] {o['عنوان']} — {pct_txt}")
        return "\n".join(lines)

    if any(k in q for k in ["ریسک", "قرمز"]):
        matched = [o for o in objectives if o["وضعیت_کارت"] == "در معرض ریسک"]
        return make_block("اهداف در معرض ریسک", matched)

    if any(k in q for k in ["نیازمند پیگیری", "نیاز به پیگیری", "زرد"]):
        matched = [o for o in objectives if o["وضعیت_کارت"] == "نیازمند پیگیری"]
        return make_block("اهداف نیازمند پیگیری", matched)

    if any(k in q for k in ["در مسیر", "سبز"]) and "ریسک" not in q:
        matched = [o for o in objectives if o["وضعیت_کارت"] == "در مسیر"]
        return make_block("اهداف در مسیر هدف", matched)

    if any(k in q for k in ["بدون شاخص", "شاخص ندار", "شاخصی ندار"]):
        matched = [o for o in objectives if o["درصد_تحقق_کارت"] is None]
        return make_block("اهداف بدون شاخص وصل‌شده", matched)

    if any(k in q for k in ["ضعیف‌ترین", "بدترین", "کمترین", "پایین‌ترین"]):
        scored = [o for o in objectives if o["درصد_تحقق_کارت"] is not None]
        matched = sorted(scored, key=lambda o: o["درصد_تحقق_کارت"])[:5]
        return make_block("۵ هدف با کمترین درصد تحقق", matched)

    if any(k in q for k in ["بهترین", "بیشترین", "بالاترین"]):
        scored = [o for o in objectives if o["درصد_تحقق_کارت"] is not None]
        matched = sorted(scored, key=lambda o: o["درصد_تحقق_کارت"], reverse=True)[:5]
        return make_block("۵ هدف با بیشترین درصد تحقق", matched)

    return None


def render_all_summary(export):
    """یه خلاصه‌ی سراسری از همه‌ی کسب‌وکارها (بدون جزئیات هر شاخص) —
    برای وقتی که کاربر می‌خواد یه نگاه کلی به کل سازمان داشته باشه."""
    lines = ["خلاصه‌ی وضعیت همه‌ی کسب‌وکارهای سازمان:"]
    for bu in export["کسب‌وکارها"]:
        s = bu["خلاصه"]
        lines.append(
            f"- {bu['نام']}: از {s['تعداد_کل_اهداف']} هدف، "
            f"{s['در_مسیر']} در مسیر، {s['نیازمند_پیگیری']} نیازمند پیگیری، "
            f"{s['در_معرض_ریسک']} در معرض ریسک، {s['بدون_شاخص']} بدون شاخص."
        )
    return "\n".join(lines)


SYSTEM_INSTRUCTIONS = (
    "شما دستیار تحلیل استراتژیک یک سازمان هستید. فقط و فقط بر اساس اطلاعاتی "
    "که در ادامه به شما داده می‌شه جواب بدید — هیچ عدد یا واقعیتی که در این "
    "اطلاعات نیست رو حدس نزنید یا نسازید. اگه جواب سوالی توی این اطلاعات "
    "نبود، صادقانه بگید که این اطلاعات رو ندارید. همیشه به زبان فارسی و با "
    "لحنی حرفه‌ای و کوتاه جواب بدید."
)


def call_ollama(messages):
    """یه درخواست به Ollama محلی می‌فرسته و متن جواب مدل رو برمی‌گردونه.

    این تابع به‌صورت «جریانی» (streaming) کار می‌کنه: یعنی به‌جای اینکه
    منتظر بمونه کل جواب یک‌جا آماده بشه (که روی یه مدل کوچیک روی CPU
    ممکنه چند دقیقه طول بکشه و باعث خطای timeout بشه)، هر تکه از جواب
    که آماده شد بلافاصله می‌گیره و روی صفحه نشون می‌ده. به همین خاطر
    محدودیت زمانی فقط برای «هر تکه» هست (اگه ۱۲۰ ثانیه هیچ داده‌ی
    جدیدی نیاد خطا می‌ده)، نه برای کل مدت پاسخ‌گویی."""
    url = OLLAMA_HOST.rstrip("/") + "/api/chat"
    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
        "options": {"temperature": 0.2},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST",
    )
    full_text = []
    try:
        # timeout اینجا یعنی «حداکثر بین دو تکه‌ی متوالی از پاسخ»، نه کل
        # مدت زمان. مدل کوچیک روی CPU ممکنه اولین تکه رو دیر بفرسته
        # (بارگذاری مدل توی حافظه)، برای همون یه مهلت اولیه‌ی بلند هم
        # در نظر گرفتیم.
        with urllib.request.urlopen(req, timeout=120) as resp:
            print("(مدل شروع به نوشتن کرد؛ متن هرچی آماده بشه همینجا نشون داده می‌شه)")
            print("-" * 40)
            for raw_line in resp:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue
                piece = chunk.get("message", {}).get("content", "")
                if piece:
                    print(piece, end="", flush=True)
                    full_text.append(piece)
                if chunk.get("done"):
                    break
            print()
            print("-" * 40)
        return "".join(full_text).strip()
    except urllib.error.URLError as e:
        msg = (
            "❌ نتونستم به Ollama وصل بشم. مطمئن بشید Ollama روی این سیستم "
            f"در حال اجراست (آدرس تست‌شده: {OLLAMA_HOST}).\n"
            f"جزئیات خطا: {e}"
        )
        print(msg)
        return msg
    except TimeoutError:
        partial = "".join(full_text).strip()
        note = (
            "\n\n⏱️ (پاسخ کامل نشد — بیش از حد معمول طول کشید و قطع شد. "
            "این معمولاً با سوال‌های خیلی کلی و باز روی این مدل کوچیک پیش "
            "میاد. سوال رو دقیق‌تر و کوچیک‌تر بپرسید، مثلاً «۳ تا هدف با "
            "کمترین درصد تحقق رو اسم ببر» به‌جای «همه‌چیز رو توضیح بده».)"
        )
        msg = (partial + note) if partial else ("❌ زمان پاسخ تموم شد." + note)
        print(note)
        return msg
    except Exception as e:
        msg = f"❌ خطای غیرمنتظره در ارتباط با مدل: {e}"
        print(msg)
        return msg


def choose_business_unit(export):
    bus = export["کسب‌وکارها"]
    print("\nکسب‌وکارها:")
    for i, bu in enumerate(bus, start=1):
        print(f"  {i}) {bu['نام']}")
    print(f"  {len(bus) + 1}) خلاصه‌ی کل سازمان (همه‌ی کسب‌وکارها با هم)")

    while True:
        choice = input("\nکدوم رو انتخاب می‌کنید؟ (شماره): ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(bus):
                return bus[idx - 1]
            if idx == len(bus) + 1:
                return None  # یعنی حالت خلاصه‌ی کل سازمان
        print("عدد وارد شده معتبر نیست، دوباره امتحان کنید.")


def main():
    export = load_export()
    print(f"داده‌ها مربوط به تاریخ تولید: {export['تاریخ_تولید']}")
    print(f"مدل انتخاب‌شده: {MODEL_NAME}   |   آدرس Ollama: {OLLAMA_HOST}")

    selected_bu = choose_business_unit(export)
    if selected_bu is None:
        context_text = render_all_summary(export)
        scope_label = "کل سازمان (فقط خلاصه)"
        objectives_for_facts = None
    else:
        context_text = render_business_unit_as_text(selected_bu)
        scope_label = selected_bu["نام"]
        objectives_for_facts = selected_bu["اهداف"]

    print(f"\n✅ آماده‌س. الان می‌تونید درباره‌ی «{scope_label}» سوال بپرسید.")
    print("برای خروج، بنویسید: خروج\n")

    history = []  # هر آیتم: {"role": "user"/"assistant", "content": "..."}

    while True:
        question = input("سوال شما: ").strip()
        if not question:
            continue
        if question in ("خروج", "exit", "quit"):
            print("خداحافظ 🙂")
            break

        system_content = SYSTEM_INSTRUCTIONS

        facts_block = None
        if objectives_for_facts is not None:
            facts_block = detect_deterministic_facts(question, objectives_for_facts)
        if facts_block:
            system_content += (
                "\n\nبرای این سوال، فهرست دقیقی از قبل برات آماده شده — این "
                "فهرست همیشه صددرصد درست است چون مستقیم از دیتابیس محاسبه "
                "شده، هیچ عدد یا موردی رو از خودت اضافه یا کم نکن، فقط اون "
                "رو به یه جواب روان و حرفه‌ای فارسی تبدیل کن:\n\n" + facts_block
            )

        system_content += "\n\n" + context_text

        messages = [
            {"role": "system", "content": system_content},
        ]
        messages.extend(history[-(MAX_HISTORY_TURNS * 2):])
        messages.append({"role": "user", "content": question})

        print("... در حال فکر کردن مدل (ممکنه روی سیستم شما چند ثانیه تا چند دقیقه طول بکشه) ...")
        answer = call_ollama(messages)
        print()

        history.append({"role": "user", "content": question})
        history.append({"role": "assistant", "content": answer})


if __name__ == "__main__":
    main()
