پورتال اداره مطالعات و توسعه استراتژیک — نسخه Django
========================================================

این نسخه برای اجرا داخل پروژه جنگوی موجود شما در مسیر D:\sysapp\strategic
ساخته شده و فقط از فایل‌های استاتیک لوکال شما استفاده می‌کند — هیچ درخواستی
به گوگل فونت، CDN یا هر منبع اینترنتی دیگری زده نمی‌شود.

ساختار فایل‌ها
---------------
templates/strategic/   → قالب‌های HTML (base.html + ۸ صفحه)
static/css/            → strategic-fonts.css و strategic.css (اضافه به static موجود شما)
static/js/              → strategic-app.js (اضافه به static موجود شما)
views.py, urls.py       → نمونه ویوها و مسیرها

مرحله ۱ — ساخت اپ جنگو (اگر هنوز نساخته‌اید)
-----------------------------------------------
(venv) PS D:\sysapp\strategic> python manage.py startapp strategic

سپس "strategic" را به INSTALLED_APPS در settings.py اضافه کنید.

مرحله ۲ — کپی فایل‌ها
------------------------
- محتوای پوشه templates/strategic/ این پکیج را در:
  D:\sysapp\strategic\strategic\templates\strategic\
  کپی کنید (یا هر مسیر templates دیگری که در TEMPLATES / APP_DIRS تنظیم کرده‌اید).

- فایل‌های static/css/strategic-fonts.css و static/css/strategic.css را در:
  D:\sysapp\strategic\static\css\
  کپی کنید (کنار فایل‌های bootstrap.rtl.min.css و all.min.css که از قبل دارید).

- فایل static/js/strategic-app.js را در:
  D:\sysapp\strategic\static\js\
  کپی کنید.

- views.py و urls.py این پکیج را جایگزین/ادغام با فایل‌های مشابه در اپ
  strategic خودتان کنید.

مرحله ۳ — اتصال به urls.py اصلی پروژه
----------------------------------------
در D:\sysapp\strategic\strategic\urls.py (یا نام پروژه اصلی شما):

    from django.urls import include, path
    urlpatterns = [
        ...,
        path("strategic/", include("strategic.urls")),
    ]

مرحله ۴ — تنظیمات استاتیک
----------------------------
مطمئن شوید در settings.py دارید:

    STATIC_URL = "/static/"
    STATICFILES_DIRS = [BASE_DIR / "static"]   # همان پوشه‌ای که فرستادید

و در حالت توسعه (DEBUG=True) جنگو خودش استاتیک‌ها را سرو می‌کند؛ برای
تولید (production) دستور زیر را اجرا کنید:

    python manage.py collectstatic

مرحله ۵ — اجرا
-----------------
(venv) PS D:\sysapp\strategic> python manage.py runserver

سپس آدرس http://127.0.0.1:8000/strategic/ باید داشبورد را نشان دهد.

نکات مهم
---------
۱. منو حالا سمت راست است — با flex + dir="rtl" و قرار گرفتن <aside> پیش از
   <main> در HTML، به‌صورت طبیعی سمت راست می‌نشیند (مثل قبل که با grid
   اشتباه به چپ می‌رفت).

۲. گیج‌های صفحه خانه حالا واقعی هستند — از JustGage + Raphael محلی شما
   ساخته شده‌اند (نه دایره‌های CSS ساختگی).

۳. نقشه راه ابتکارات حالا یک نمودار گانت واقعی است — از frappe-gantt محلی
   شما استفاده می‌کند (Highcharts-Gantt هم دارید، اما توجه کنید که
   Highcharts برای استفاده تجاری/سازمانی نیاز به لایسنس پولی دارد، در حالی
   که frappe-gantt رایگان و متن‌باز (MIT) است — به همین دلیل frappe-gantt
   را انتخاب کردم. اگر لایسنس Highcharts دارید و ترجیح می‌دهید از آن
   استفاده شود، بگویید تا جایگزین کنم).

۴. فیلد تاریخ در فرم «افزودن مطالعه» به jalali-datepicker شما وصل شده، اما
   چون API دقیق نسخه‌ای که نصب کرده‌اید را نمی‌دانم، در research.html یک
   کامنت گذاشتم که این بخش را مطابق مستندات نسخه خودتان تنظیم کنید.

۵. کتابخانه مطالعات و SWOT فعلاً داده‌ی نمایشی در حافظه مرورگر دارند (نه
   دیتابیس واقعی). قدم بعدی طبیعی این است که یک مدل Django (models.py) برای
   «مطالعات» و «SWOT» بسازیم و این صفحات را به آن وصل کنیم تا داده‌ها واقعاً
   در پایگاه‌داده ذخیره شوند و بین همه کاربران مشترک باشند.

مراحل پیشنهادی بعدی
---------------------
۱. تست اجرا روی سیستم شما و بازخورد روی چیدمان
۲. ساخت models.py برای مطالعات، ابتکارات نقشه راه، ریسک‌ها و SWOT
۳. تبدیل داده‌های نمایشی به فرم‌های واقعی متصل به دیتابیس (Django Forms)
۴. افزودن سیستم ورود کاربری برای سطح دسترسی
