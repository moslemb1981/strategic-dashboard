from django.db import models
from django.utils import timezone


class Study(models.Model):
    STATUS_CHOICES = [
        ("planned", "برنامه‌ریزی‌شده"),
        ("progress", "در حال انجام"),
        ("done", "تکمیل‌شده"),
    ]

    title = models.CharField(max_length=300, verbose_name="عنوان مطالعه")
    field = models.CharField(max_length=100, verbose_name="حوزه", blank=True, default="عمومی")
    date = models.CharField(max_length=20, verbose_name="تاریخ (شمسی)", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned", verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "مطالعه"
        verbose_name_plural = "مطالعات"

    def __str__(self):
        return self.title


class Initiative(models.Model):
    STATUS_CHOICES = [
        ("in_progress", "در حال اجرا"),
        ("on_track", "در مسیر"),
        ("needs_attention", "نیازمند پیگیری"),
        ("digital", "ابتکار دیجیتال"),
        ("done", "تکمیل‌شده"),
    ]
    STATUS_COLOR = {
        "in_progress": "bar-green",
        "on_track": "bar-blue",
        "needs_attention": "bar-amber",
        "digital": "bar-purple",
        "done": "bar-gray",
    }

    title = models.CharField(max_length=300, verbose_name="عنوان ابتکار")
    owner = models.CharField(max_length=150, verbose_name="واحد مسئول", blank=True)
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    progress = models.PositiveSmallIntegerField(default=0, verbose_name="پیشرفت (٪)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="on_track", verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start_date"]
        verbose_name = "ابتکار"
        verbose_name_plural = "ابتکارات"

    def __str__(self):
        return self.title

    @property
    def bar_class(self):
        return self.STATUS_COLOR.get(self.status, "bar-blue")


class Risk(models.Model):
    LEVEL_CHOICES = [(1, "کم"), (2, "متوسط"), (3, "زیاد"), (4, "خیلی زیاد")]

    title = models.CharField(max_length=300, verbose_name="عنوان ریسک")
    owner = models.CharField(max_length=150, verbose_name="مسئول", blank=True)
    likelihood = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=2, verbose_name="احتمال وقوع")
    impact = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=2, verbose_name="شدت اثر")
    mitigation = models.TextField(verbose_name="اقدام کاهشی", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "ریسک"
        verbose_name_plural = "ریسک‌ها"

    def __str__(self):
        return self.title

    @property
    def severity_sum(self):
        return self.likelihood + self.impact

    @property
    def zone(self):
        s = self.severity_sum
        if s <= 4:
            return "green"
        if s <= 6:
            return "amber"
        return "red"

    @property
    def sev_class(self):
        return {"red": "high", "amber": "med", "green": "low"}[self.zone]


class SWOTItem(models.Model):
    CATEGORY_CHOICES = [
        ("s", "نقطه قوت"),
        ("w", "نقطه ضعف"),
        ("o", "فرصت"),
        ("t", "تهدید"),
    ]
    IMPACT_CHOICES = [("high", "بالا"), ("med", "متوسط")]

    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    text = models.CharField(max_length=300, verbose_name="متن")
    impact = models.CharField(max_length=10, choices=IMPACT_CHOICES, default="med", verbose_name="اهمیت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "مورد SWOT"
        verbose_name_plural = "موارد SWOT"

    def __str__(self):
        return self.text


class StrategicObjective(models.Model):
    PERSPECTIVE_CHOICES = [
        ("financial", "مالی"),
        ("customer", "مشتری"),
        ("process", "فرآیندهای داخلی"),
        ("learning", "یادگیری و رشد"),
    ]
    THEME_CHOICES = [
        ("operational", "تعالی عملیاتی و کیفیت"),
        ("growth", "رشد بازار و سودآوری"),
        ("digital", "نوآوری و تحول دیجیتال"),
    ]
    STATUS_CHOICES = [
        ("on", "در مسیر هدف"),
        ("watch", "نیازمند پیگیری"),
        ("risk", "در معرض ریسک"),
    ]
    THEME_COLOR = {
        "operational": "var(--success)",
        "growth": "var(--primary)",
        "digital": "var(--purple)",
    }

    code = models.CharField(max_length=10, verbose_name="کد (مثل F1، C2)")
    perspective = models.CharField(max_length=20, choices=PERSPECTIVE_CHOICES, verbose_name="منظر BSC")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, verbose_name="محور استراتژیک")
    title = models.CharField(max_length=300, verbose_name="عنوان هدف")
    kpi = models.CharField(max_length=300, verbose_name="KPI", blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="on", verbose_name="وضعیت")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order", "code"]
        verbose_name = "هدف استراتژیک"
        verbose_name_plural = "اهداف استراتژیک (نقشه استراتژیک)"

    def __str__(self):
        return f"{self.code} — {self.title}"

    @property
    def theme_css(self):
        return self.THEME_COLOR.get(self.theme, "var(--primary)")


class Competitor(models.Model):
    name = models.CharField(max_length=200, verbose_name="نام بازیگر")
    market_share = models.PositiveSmallIntegerField(default=0, verbose_name="سهم بازار (٪)")
    strengths = models.TextField(blank=True, verbose_name="نقاط قوت (هر خط یک مورد)")
    weaknesses = models.TextField(blank=True, verbose_name="نقاط ضعف (هر خط یک مورد)")
    recent_move = models.CharField(max_length=300, blank=True, verbose_name="آخرین حرکت")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order", "-market_share"]
        verbose_name = "بازیگر بازار"
        verbose_name_plural = "هوش رقابتی و بازار"

    def __str__(self):
        return self.name

    @property
    def strengths_list(self):
        return [s.strip() for s in self.strengths.splitlines() if s.strip()]

    @property
    def weaknesses_list(self):
        return [s.strip() for s in self.weaknesses.splitlines() if s.strip()]


class PestelFactor(models.Model):
    CATEGORY_CHOICES = [
        ("political", "سیاسی"),
        ("economic", "اقتصادی"),
        ("social", "اجتماعی"),
        ("technological", "فناورانه"),
        ("environmental", "زیست‌محیطی"),
        ("legal", "قانونی"),
    ]
    CATEGORY_STYLE = {
        "political": ("var(--primary)", "var(--primary-soft)", "fa-flag"),
        "economic": ("var(--accent)", "var(--accent-soft)", "fa-coins"),
        "social": ("var(--success)", "var(--success-soft)", "fa-users"),
        "technological": ("var(--purple)", "var(--purple-soft)", "fa-microchip"),
        "environmental": ("var(--teal)", "var(--teal-soft)", "fa-leaf"),
        "legal": ("var(--coral)", "var(--coral-soft)", "fa-gavel"),
    }

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="بُعد")
    text = models.CharField(max_length=300, verbose_name="عامل محیطی")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["category", "order"]
        verbose_name = "عامل PESTEL"
        verbose_name_plural = "تحلیل PESTEL"

    def __str__(self):
        return f"{self.get_category_display()} — {self.text}"
