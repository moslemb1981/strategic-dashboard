استقرار یک‌باره روی D:\sysapp\strategic
==========================================

این پکیج دقیقاً همون ساختاری رو داره که باید روی D:\sysapp\strategic بشینه.
چیزی که از قبل دارید (venv، static\vendor، static\fonts، static\js کتابخانه‌ها،
config\) دست‌نخورده می‌مونه — این پکیج فقط این‌ها رو اضافه/جایگزین می‌کنه:

strategic\           ← کل اپ جنگو (views.py, urls.py, apps.py, admin.py, ...)
templates\strategic\ ← همه‌ی ۹ قالب HTML (تمیز و با انکودینگ درست UTF-8)
static\css\           ← فقط ۲ فایل جدید: strategic-fonts.css و strategic.css
static\js\             ← فقط ۱ فایل جدید: strategic-app.js

مراحل (فقط با File Explorer، نه PowerShell — تا انکودینگ فارسی خراب نشه)
----------------------------------------------------------------------------
۱. این زیپ رو دانلود کنید و روش راست‌کلیک → Extract All بزنید.

۲. اگه از قبل پوشه‌ی strategic\ (اپ جنگو) و templates\strategic\ ساخته‌اید
   و می‌خواید کاملاً تمیز جایگزین بشه، اول این دو پوشه رو حذف کنید:
   - D:\sysapp\strategic\strategic
   - D:\sysapp\strategic\templates\strategic

۳. از پوشه‌ی استخراج‌شده، این سه مورد رو کپی کنید و توی
   D:\sysapp\strategic پیست کنید (وقتی سؤال overwrite داد، بزنید Yes):
   - پوشه‌ی strategic
   - پوشه‌ی templates
   - پوشه‌ی static  (فقط css و js جدید رو اضافه می‌کنه، چیزی رو حذف نمی‌کنه)

۴. یه چک سریع بزنید که settings.py شما (D:\sysapp\strategic\config\settings.py)
   همچنان این سه خط رو داشته باشه (اگه قبلاً اضافه کرده بودید، لازم نیست
   دوباره دست بزنید):

   INSTALLED_APPS = [ ..., 'strategic' ]
   TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']
   STATICFILES_DIRS = [BASE_DIR / 'static']

   و config\urls.py این خط رو داشته باشه:
   path('strategic/', include('strategic.urls'))

۵. اجرا:
   (venv) PS D:\sysapp\strategic> python manage.py runserver

   بعد http://127.0.0.1:8000/strategic/ رو باز کنید.

۵. مدل‌ها رو به دیتابیس اضافه کنید — چهار مدل جدید داریم (Study, Initiative,
   Risk, SWOTItem) که کتابخانه مطالعات، نقشه راه، نقشه ریسک و SWOT همه واقعاً
   بهشون وصلن (نه دیگه داده‌ی نمایشی):
   (venv) PS D:\sysapp\strategic> python manage.py makemigrations strategic
   (venv) PS D:\sysapp\strategic> python manage.py migrate

۶. سیستم ورود کاربری فعال شده — همه‌ی صفحات الان نیاز به لاگین دارن. دو خط
   زیر رو به config\settings.py اضافه کنید (هرجای فایل، مثلاً زیر STATIC_URL):

   LOGIN_URL = "strategic:login"
   LOGIN_REDIRECT_URL = "strategic:home"

   اگه هنوز کاربری نساختید:
   (venv) PS D:\sysapp\strategic> python manage.py createsuperuser

۷. اجرا:
   (venv) PS D:\sysapp\strategic> python manage.py runserver

   بعد http://127.0.0.1:8000/ رو باز کنید — باید به صفحه ورود هدایت بشید.

۸. نقشه استراتژیک هم الان مدل واقعی داره (StrategicObjective) — همون
   makemigrations/migrate مرحله ۵ این مدل رو هم می‌سازه، نیازی به تکرار نیست
   (اگه فایل‌های جدید رو زودتر کپی کرده بودید، دوباره makemigrations بزنید).

   برای اینکه همون ۱۲ هدف نمونه‌ای که روی سایت دیدید، به‌عنوان الگو توی
   ادمین هم باشه تا دقیق الگو بگیرید، این دستور رو یک‌بار اجرا کنید:

   (venv) PS D:\sysapp\strategic> python manage.py seed_stratmap

   این دستور امن است — اگه دوباره اجرا بشه، رکوردهای تکراری نمی‌سازه.

   بعد از این، توی /admin/ بخش «اهداف استراتژیک» رو باز کنید — همون ۱۲ مورد
   رو می‌بینید با ستون‌های منظر، محور، کد، عنوان، KPI، وضعیت. وضعیت و ترتیب
   نمایش مستقیم توی همون لیست هم قابل ویرایش سریعه (list_editable)، بدون
   نیاز به باز کردن هر رکورد.

۹. رفع باگ دکمه‌های افزودن (کتابخانه مطالعات، نقشه ریسک، نقشه راه، نقشه
   استراتژیک) — علت این بود که کلاس CSS سفارشی ما به اسم «modal» دقیقاً با
   کلاس داخلی خود Bootstrap هم‌نام بود و Bootstrap مقادیر display:none و
   position:fixed رو روی اون تحمیل می‌کرد، برای همین پس‌زمینه تیره می‌شد
   ولی خود کادر سفید هیچ‌وقت نمایش داده نمی‌شد. کلاس رو به «modal-card»
   تغییر دادم — این نسخه دیگه این مشکل رو نداره.

۱۰. نقشه استراتژیک حالا مستقیم توی خود سایت هم به‌طور کامل قابل ویرایشه:
    - دکمه‌ی مداد روی هر کارت → فرم افزودن رو با اطلاعات همون هدف پر می‌کنه
      تا ویرایشش کنید (بدون نیاز به ادمین)
    - برای «جابه‌جا کردن» یک هدف بین منظر/محورهای مختلف، کافیه توی همون
      فرم، فیلد «منظر BSC» یا «محور استراتژیک» رو عوض کنید — کارت خودش به
      خانه‌ی جدید منتقل می‌شه
    - فیلد «ترتیب نمایش» هم تعیین می‌کنه چند هدف داخل یک خانه به چه ترتیبی
      روی هم بچینن

۱۱. رفع سرریز کادر «اقدام کاهشی» — استایل عمومی فیلدها فقط روی input/select
    بود، textarea رو یادش رفته بود؛ الان درست شد.

۱۲. داده‌ی نمونه برای نقشه ریسک — دقیقاً مثل seed_stratmap، این دستور ۶
    ریسک نمونه‌ی نزدیک به عملکرد یک شرکت قطعات یدکی رو ثبت می‌کنه تا الگو
    داشته باشید (امن است، تکراری نمی‌سازد):

    (venv) PS D:\sysapp\strategic> python manage.py seed_risks

۱۳. ماژول‌های «هوش رقابتی و بازار» و «تحلیل PESTEL» هم الان مدل واقعی دارن
    (Competitor و PestelFactor) — همون makemigrations/migrate این‌ها رو هم
    می‌سازه. برای داده‌ی نمونه:

    (venv) PS D:\sysapp\strategic> python manage.py seed_market
    (venv) PS D:\sysapp\strategic> python manage.py seed_pestel

۱۴. سیستم سطح دسترسی — دو گروه کاربری ساخته می‌شه: «ویرایشگران» (اجازه
    افزودن/ویرایش/حذف در همه‌ی ماژول‌ها) و «بینندگان» (فقط مشاهده، دکمه‌های
    افزودن/حذف/ویرایش اصلاً براشون نمایش داده نمی‌شه). این دستور رو یک‌بار
    بزنید:

    (venv) PS D:\sysapp\strategic> python manage.py seed_groups

    بعد برید /admin/ → بخش Users → یوزر مورد نظر رو باز کنید → پایین صفحه
    قسمت «Groups» رو پیدا کنید → یکی از دو گروه رو انتخاب و منتقل کنید به
    ستون «Chosen groups» → Save. کاربر admin (سوپریوزر) نیازی به گروه نداره،
    چون دسترسی کامل به همه‌چیز داره.

۱۵. آماده‌سازی برای اجرای واقعی (production) — این چند مرحله سیستم رو از
    حالت «فقط روی سیستم من» به حالت «قابل اجرا و امن برای کل سازمان» می‌بره:

    الف) نصب پکیج‌های جدید:
    (venv) PS D:\sysapp\strategic> pip install -r requirements.txt

    ب) فایل .env.example رو کپی کنید و اسمش رو بذارید .env، بعد مقادیرش رو
       با یک کلید تصادفی واقعی و آدرس سرورتون پر کنید. برای ساختن یک
       SECRET_KEY تصادفی امن:
       (venv) PS D:\sysapp\strategic> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

    ج) توی config\settings.py این تغییرات رو بدید:

       - زیر خط `BASE_DIR = Path(__file__).resolve().parent.parent` این
         دو خط رو اضافه کنید:
         import os
         from dotenv import load_dotenv
         load_dotenv(BASE_DIR / ".env")

       - خط‌های SECRET_KEY، DEBUG، ALLOWED_HOSTS رو با این جایگزین کنید
         (مقدار فعلی SECRET_KEY خودتون رو به‌جای «کلید-قبلی-شما» به‌عنوان
         fallback بذارید تا اگه .env نبود، بازم کار کنه):
         SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "کلید-قبلی-شما")
         DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"
         ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

       - توی MIDDLEWARE، بلافاصله بعد از
         'django.middleware.security.SecurityMiddleware' این خط رو اضافه کنید:
         'whitenoise.middleware.WhiteNoiseMiddleware',

       - زیر STATIC_URL این دو تنظیم رو اضافه کنید:
         STATIC_ROOT = BASE_DIR / "staticfiles"
         STORAGES = {
             "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
             "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"},
         }

    د) جمع‌آوری فایل‌های استاتیک برای حالت production:
       (venv) PS D:\sysapp\strategic> python manage.py collectstatic

    ه) اجرا با سرور واقعی (به‌جای runserver):
       (venv) PS D:\sysapp\strategic> run_production.bat
       یا مستقیم:
       (venv) PS D:\sysapp\strategic> waitress-serve --listen=0.0.0.0:8000 config.wsgi:application

       حالا از هر سیستم دیگه‌ای توی شبکه‌ی داخلی شرکت، با آی‌پی این سیستم
       (مثلاً http://192.168.1.50:8000) قابل دسترسیه، نه فقط از خود سیستم.

    نکته: SQLite برای تیم‌های کوچک (چند نفر) کاملاً کافیه. اگه بعداً تعداد
    کاربران همزمان زیاد شد، مهاجرت به PostgreSQL قدم بعدیه — فعلاً لازم
    نیست نگرانش باشید.

۱۶. داشبورد خانه واقعی شد — گیج‌ها، آمار ماژول‌ها، و «آخرین فعالیت‌ها» همه
    الان مستقیم از دیتابیس محاسبه می‌شن، نه اعداد ثابت. چون به مدل‌های
    Competitor/PestelFactor/StrategicObjective یه فیلد created_at اضافه شد،
    یه migration جدید لازمه:

    (venv) PS D:\sysapp\strategic> python manage.py makemigrations strategic
    (venv) PS D:\sysapp\strategic> python manage.py migrate

    (این فیلد جدید خودکار با زمان الان پر می‌شه برای رکوردهای قبلی، نیازی
    به وارد کردن مقدار دستی نیست.)

۱۷. تقویم شمسی — نصب و تنظیمات:

    الف) پکیج جدید رو نصب کنید:
    (venv) PS D:\sysapp\strategic> pip install -r requirements.txt

    ب) فایل settings.py که این‌بار می‌فرستم رو کامل جایگزین config\settings.py
       کنید (LANGUAGE_CODE به 'fa' و TIME_ZONE به 'Asia/Tehran' تغییر کرده —
       همین باعث می‌شه عبارت‌های داخلی جنگو هم فارسی نمایش داده بشن).

    ج) فایل‌های strategic\jalali_utils.py و پوشه‌ی
       strategic\templatetags\ رو کپی کنید (فایل‌های جدید هستن).

    د) هیچ migration جدیدی لازم نیست — تاریخ‌ها همچنان میلادی توی دیتابیس
       ذخیره می‌شن (چون گانت‌چارت بهش نیاز داره)، فقط فرم ورودی و نمایش
       تبدیل به شمسی شدن.

    محدودیت مهم که باید بدونید: خود نمودار گانت‌چارت (کتابخانه frappe-gantt)
    محورهای بالای نمودارش (اسم ماه‌ها) رو میلادی و انگلیسی نشون می‌ده، چون
    این کتابخانه از تقویم شمسی پشتیبانی نمی‌کنه — این یه محدودیت خود
    کتابخانه‌ست، نه باگ. همه‌جای دیگه‌ی سایت (فرم‌ها، لیست‌ها، هدر بالای
    صفحه) کاملاً شمسیه.

۱۸. نقشه استراتژیک بازطراحی کامل شد — طرح تیره «کاکپیت» با کارت‌های
    درخشان و سیم‌های متحرک بین اهداف که رابطه‌ی علّی واقعی رو نشون می‌دن:

    الف) چون یه رابطه‌ی جدید بین اهداف اضافه شده (اینکه کدوم هدف به کدوم
    هدف دیگه کمک می‌کنه)، یه migration جدید لازمه:
    (venv) PS D:\sysapp\strategic> python manage.py makemigrations strategic
    (venv) PS D:\sysapp\strategic> python manage.py migrate

    ب) توی فرم افزودن/ویرایش هر هدف، یه فیلد چندانتخابی جدید هست: «این
    هدف به کدام هدف(ها) کمک می‌کند». وقتی مشخص کنید، یه سیم متحرک بین
    اون دو کارت روی نقشه کشیده می‌شه. اگه این فیلد رو خالی بذارید،
    کارت بدون سیم نمایش داده می‌شه — کاملاً اختیاریه.

    ج) روی هر هدف کلیک کنید تا زنجیره‌ی علّیش (همه‌ی اهدافی که بهش کمک
    می‌کنن + همه‌ی اهدافی که خودش بهشون کمک می‌کنه) روشن بشه. دکمه‌ی
    «نمای کامل نقشه» همه‌چیز رو برمی‌گردونه.

    د) تعداد اهداف توی هر منظر دیگه محدود به یکی نیست — هر تعداد که
    اضافه کنید، همه زیر هم توی همون منظر نمایش داده می‌شن.

چیزی که این‌بار عوض شده
--------------------------
- چهار ماژول (کتابخانه مطالعات، نقشه راه ابتکارات، نقشه ریسک، SWOT) همه
  الان مدل واقعی Django دارن — افزودن/حذف از فرم واقعاً توی دیتابیس ذخیره
  می‌شه و از پنل ادمین (/admin/) هم قابل مدیریتن.
- سیستم ورود کاربری با auth داخلی خود جنگو اضافه شد — بدون لاگین هیچ
  صفحه‌ای در دسترس نیست. برای خروج، دکمه «خروج» بالای صفحه هست.
- نقشه راه ابتکارات حالا از تاریخ‌های میلادی واقعی (start_date/end_date)
  استفاده می‌کنه که با فیلد تاریخ معمولی HTML وارد می‌شن (نه شمسی) — چون
  گانت چارت به تاریخ میلادی نیاز داره؛ اگه بخواید ورودی شمسی باشه و پشت
  صحنه به میلادی تبدیل بشه، بگید تا اضافه کنم.
- نقشه استراتژیک (BSC) و هوش رقابتی/PESTEL هنوز محتوای ثابت دارن — این‌ها
  رو در قدم بعدی می‌تونیم به مدل وصل کنیم.

اگه بازم متن فارسی خراب دیدید
--------------------------------
یعنی جایی توی مسیر کپی از یه ابزار غیر بایت-به‌بایت (مثل ترمینال یا Notepad
ساده) استفاده شده. راه مطمئن همیشه: کپی/پیست مستقیم فایل از طریق File
Explorer یا استخراج زیپ — هیچ‌وقت محتوای فارسی رو دستی توی PowerShell
تایپ/پیست نکنید.
