"""اصلاح «ی» اضافه بعد از «ه» (مثل «نقشه‌ی» ← «نقشه») در متن بوم کسب‌وکار (همه‌ی کسب‌وکارها)
و SWOT/TOWS سه کسب‌وکار جدید. فقط همین قاعده؛ بقیه‌ی متن دست نمی‌خورد.

    python manage.py fix_ezafe_ye           # گزارش
    python manage.py fix_ezafe_ye --apply   # اعمال
"""
import re

from django.core.management.base import BaseCommand

from strategic.models import BusinessCanvasItem, SWOTItem, TOWSStrategy

Z = "‌"
PAT = re.compile("ه" + Z + "ی(?=[\\s،؛:.\\)\\(«»\\-—/'\"]|$)")
NEW_KEYS = ("صافکاری", "وارانتی", "صادرات")


def fix(s):
    s = PAT.sub("ه", s)
    return s.replace("وارد" + Z + "کنندگان", "واردکنندگان").replace("از" + Z + "دست" + Z + "رفته", "ازدست" + Z + "رفته")


class Command(BaseCommand):
    def add_arguments(self, p):
        p.add_argument("--apply", action="store_true")

    def handle(self, *a, **o):
        n = 0
        qs = [
            list(BusinessCanvasItem.objects.all()),
            list(SWOTItem.objects.filter(business_unit__name__regex="|".join(NEW_KEYS))),
            list(TOWSStrategy.objects.filter(business_unit__name__regex="|".join(NEW_KEYS))),
        ]
        for rows in qs:
            for r in rows:
                new = fix(r.text)
                if new != r.text:
                    n += 1
                    if o["apply"]:
                        r.text = new
                        r.save(update_fields=["text"])
        self.stdout.write(f"{n} متن نیاز به اصلاح داشت" + (" و اصلاح شد." if o["apply"] else ". برای اعمال: --apply"))
