@echo off
REM اجرای پورتال با سرور واقعی (Waitress) به‌جای سرور توسعه Django
REM قبل از اولین اجرا: pip install -r requirements.txt  و  python manage.py collectstatic

call venv\Scripts\activate
waitress-serve --listen=0.0.0.0:8000 config.wsgi:application
