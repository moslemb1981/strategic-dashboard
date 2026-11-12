"""ساخت «پیش‌نویس» بوم کسب‌وکار برای همه کسب‌وکارها، فقط از داده‌های همین دیتابیس.

    python manage.py draft_business_canvas                  # فقط گزارش + فایل CSV برای بازبینی (بدون تغییر)
    python manage.py draft_business_canvas --apply          # ثبت پیش‌نویس‌ها
    python manage.py draft_business_canvas --remove-drafts  # گزارش حذف پیش‌نویس‌های خودکار
    python manage.py draft_business_canvas --remove-drafts --apply

• همه موارد با وضعیت «پیش‌نویس (نیازمند تأیید)» و با ذکر منبع در «توضیح / منبع» ثبت می‌شوند.
• کسب‌وکاری که از قبل مورد بوم دارد دست نمی‌خورد (رد می‌شود).
• پیش از ثبت، پشتیبان JSON در backups/ ساخته می‌شود. چیزی از خارج دیتابیس ساخته نمی‌شود؛
  بلوکی که داده‌ای برایش نبود خالی می‌ماند.
"""
import csv
import datetime
import json
import os
import re

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Q

from strategic.models import (
    BusinessUnit, BusinessCanvasItem, SWOTItem, StrategicObjective, FunctionalStrategy,
    Initiative, Stakeholder, TOWSStrategy, Management,
)

TAG = "[پیش‌نویس خودکار]"
CAP = 7  # حداکثر مورد در هر بلوک

# کلیدواژه هر کسب‌وکار جدید (برای کسب‌وکاری که داده اختصاصی ندارد)
NEW_BU_KEYWORDS = [
    ("صافکاری", ["صافکاری", "نقاشی", "PDR"]),
    ("وارانتی", ["وارانتی", "خارج از گارانتی", "خارج از دوره", "پس از گارانتی", "بعد از گارانتی", "اتمام گارانتی"]),
    ("صادرات", ["صادرات", "صادراتی"]),
]

# قواعد دسته‌بندی متن به بلوک (به ترتیب اولویت). فقط واژه‌های صریح؛ اگر چیزی نخورد، پیش‌فرض منبع به‌کار می‌رود.
RULES = [
    ("relations", r"وفادار|نگهداشت|رضایت|باشگاه|CRM|شکایات|پاسخگویی"),
    ("channels", r"پلتفرم|آنلاین|اینترنتی|سایت|اپلیکیشن|پیامک"),
    ("partners", r"شریک|قطعه‌?ساز|تأمین‌?کننده|تامین‌?کننده|واردکننده|تولیدکننده|عاملیت|نمایندگی|پیمانکار"),
    ("segments", r"مشتریان|خریدار|مالکان|ناوگان|تعمیرکار|فروشگاه‌ها|بازارهای صادراتی"),
    ("revenue", r"درآمد|کارمزد|اجرت|فروش|سود"),
    ("costs", r"هزینه|سربار|بهره‌?وری"),
    ("resources", r"نیروی انسانی|تجهیزات|زیرساخت|ظرفیت|دارایی|بانک اطلاعات|سامانه"),
]


def classify(text, allowed, default):
    for block, pat in RULES:
        if block in allowed and re.search(pat, text):
            return block
    return default


def clean_code(t):
    return re.sub(r"^[A-Za-z]\d+\s*[—\-–]\s*", "", t or "").strip()


def split_title(text):
    """«عنوان: توضیح» → (عنوان، توضیح)."""
    if ":" in text:
        a, b = text.split(":", 1)
        if 6 <= len(a.strip()) <= 120:
            return a.strip(), b.strip()
    return text.strip(), ""


def short(bu):
    return bu.name.replace("کسب و کار", "").replace("کسب‌وکار", "").strip()


def anyq(field, words):
    q = Q()
    for w in words:
        q |= Q(**{f"{field}__icontains": w})
    return q


class Collector:
    def __init__(self):
        self.out = {}      # block → list[(text, note)]
        self.seen = set()

    def add(self, block, text, note=""):
        text = (text or "").strip()
        key = re.sub(r"\s+", " ", text)[:80]
        if not text or key in self.seen:
            return
        if len(self.out.setdefault(block, [])) >= CAP:
            return
        self.seen.add(key)
        self.out[block].append((text[:300], f"{TAG} {note}".strip()))


def own_mode(bu, c):
    """کسب‌وکارِ دارای نقشه/SWOT: نگاشت ساختاری منظرها و قوت‌ها."""
    short_name = short(bu)
    for o in StrategicObjective.objects.filter(business_unit=bu).order_by("order", "code"):
        t = clean_code(o.title)
        src = f"منبع: هدف {o.code} در نقشه استراتژیک «{short_name}»"
        if o.perspective == "customer":
            c.add("value", t, src)
        elif o.perspective == "financial":
            b = classify(t, ("revenue", "costs"), "")
            if b:
                c.add(b, t, src)
        elif o.perspective == "process":
            c.add(classify(t, ("relations", "channels", "partners", "segments"), "activities"), t, src)
        elif o.perspective == "learning":
            b = classify(t, ("channels",), "")
            if b:
                c.add(b, t, src)
    for s in SWOTItem.objects.filter(business_unit=bu, category="s").order_by("-weight", "id"):
        title, expl = split_title(s.text)
        b = classify(title, ("relations", "channels", "partners", "segments"), "resources")
        c.add(b, title, f"منبع: نقطه قوت SWOT «{short_name}»" + (f" — {expl[:160]}" if expl else ""))
    for s in SWOTItem.objects.filter(business_unit=bu, category="o").order_by("-weight", "id"):
        title, expl = split_title(s.text)
        b = classify(title, ("segments",), "")
        if b:
            c.add(b, title, f"منبع: فرصت SWOT «{short_name}»" + (f" — {expl[:160]}" if expl else ""))
    for f in FunctionalStrategy.objects.filter(business_unit_text__icontains=short_name).order_by("order")[:80]:
        c.add(classify(f.title, ("revenue", "costs"), "activities"), f.title, f"منبع: استراتژی وظیفه‌ای ({f.org_unit})")


def keyword_mode(bu, words, c):
    """کسب‌وکارِ جدید و بدون داده اختصاصی: هر چه در دیتابیس به این حوزه اشاره دارد، با ذکر منبع."""
    for s in SWOTItem.objects.filter(anyq("text", words)).select_related("business_unit"):
        if s.category not in ("s", "o"):
            continue
        title, expl = split_title(s.text)
        allowed = ("relations", "channels", "partners", "segments")
        b = classify(title, allowed, "resources" if s.category == "s" else "")
        if b:
            c.add(b, title, f"منبع: {'قوت' if s.category == 's' else 'فرصت'} SWOT «{short(s.business_unit)}»"
                  + (f" — {expl[:160]}" if expl else ""))
    for f in FunctionalStrategy.objects.filter(anyq("title", words) | anyq("detail", words)):
        c.add(classify(f.title, ("revenue", "costs"), "activities"), f.title, f"منبع: استراتژی وظیفه‌ای ({f.org_unit})")
    for i in Initiative.objects.filter(anyq("title", words)).select_related("business_unit")[:40]:
        c.add("activities", i.title, f"منبع: پروژه {i.code or ''} «{short(i.business_unit) if i.business_unit else '—'}»")
    for t in TOWSStrategy.objects.filter(anyq("text", words)).select_related("business_unit"):
        c.add(classify(t.text, ("revenue", "costs"), "activities"), t.text,
              f"منبع: راهبرد TOWS «{short(t.business_unit) if t.business_unit else '—'}»")
    for s in Stakeholder.objects.filter(anyq("name", words) | anyq("need", words)):
        if s.is_external:
            b = "segments" if re.search(r"مشتری|خریدار|بازار", s.name) else "partners"
        else:
            b = "resources"
        c.add(b, s.name, f"منبع: تحلیل ذینفعان ({s.department})")
    for m in Management.objects.filter(anyq("name", words)):
        c.add("resources", m.name, "منبع: ساختار سازمانی")


class Command(BaseCommand):
    help = "ساخت پیش‌نویس بوم کسب‌وکار از داده‌های دیتابیس"

    def add_arguments(self, p):
        p.add_argument("--apply", action="store_true")
        p.add_argument("--remove-drafts", action="store_true")

    def handle(self, *a, **o):
        apply = o["apply"]
        os.makedirs("backups", exist_ok=True)
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        if o["remove_drafts"]:
            qs = BusinessCanvasItem.objects.filter(status="draft", note__startswith=TAG)
            self.stdout.write(f"پیش‌نویس‌های خودکار موجود: {qs.count()} مورد")
            if apply:
                n = qs.delete()[0]
                self.stdout.write(self.style.SUCCESS(f"{n} مورد حذف شد."))
            else:
                self.stdout.write("برای حذف: --remove-drafts --apply")
            return

        plan, rows = [], []
        for bu in BusinessUnit.objects.all():
            if BusinessCanvasItem.objects.filter(business_unit=bu).exists():
                self.stdout.write(f"· {bu.name}: از قبل بوم دارد — رد شد")
                continue
            c = Collector()
            has_data = StrategicObjective.objects.filter(business_unit=bu).exists() or \
                SWOTItem.objects.filter(business_unit=bu).exists()
            if has_data:
                mode = "نقشه/SWOT خود کسب‌وکار"
                own_mode(bu, c)
            else:
                words = next((w for k, w in NEW_BU_KEYWORDS if k in bu.name), None)
                if not words:
                    self.stdout.write(f"· {bu.name}: داده اختصاصی ندارد و کلیدواژه‌ای برایش تعریف نشده — رد شد")
                    continue
                mode = "جست‌وجوی کلیدواژه در کل دیتابیس"
                keyword_mode(bu, words, c)
            plan.append((bu, c.out))
            self.stdout.write(f"\n■ {bu.name}  [{mode}]")
            for key, title in BusinessCanvasItem.BLOCK_CHOICES:
                items = c.out.get(key, [])
                self.stdout.write(f"   {title}: {len(items) if items else '— خالی —'}")
                for order, (t, n) in enumerate(items):
                    rows.append([bu.name, title, t, n])
        csv_path = f"backups/canvas_draft_preview_{stamp}.csv"
        with open(csv_path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["کسب‌وکار", "بلوک", "متن", "منبع"])
            w.writerows(rows)
        self.stdout.write(f"\nفایل بازبینی: {csv_path}  ({len(rows)} مورد)")

        if not apply:
            self.stdout.write(self.style.WARNING("حالت گزارش — چیزی ثبت نشد. برای ثبت: --apply"))
            return
        existing = list(BusinessCanvasItem.objects.values())
        bpath = f"backups/canvas_before_{stamp}.json"
        with open(bpath, "w", encoding="utf-8") as fh:
            json.dump(existing, fh, ensure_ascii=False, default=str)
        with transaction.atomic():
            n = 0
            for bu, out in plan:
                for block, items in out.items():
                    for order, (t, note) in enumerate(items):
                        BusinessCanvasItem.objects.create(
                            business_unit=bu, block=block, text=t, note=note, status="draft", order=order)
                        n += 1
        self.stdout.write(self.style.SUCCESS(f"{n} پیش‌نویس ثبت شد. پشتیبان: {bpath}"))
