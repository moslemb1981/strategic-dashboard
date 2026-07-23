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
    LEVEL_CHOICES = [(1, "۱ - بسیار کم"), (2, "۲ - کم"), (3, "۳ - متوسط"), (4, "۴ - زیاد"), (5, "۵ - بسیار زیاد")]
    CATEGORY_CHOICES = [
        ("ops", "زنجیره تأمین/عملیاتی"), ("mkt", "بازار و رقابت"), ("fin", "مالی و ارزی"),
        ("legal", "انطباق و قانونی"), ("it", "فناوری اطلاعات"), ("hr", "منابع انسانی"),
    ]
    CATEGORY_COLOR = {"ops": "#1183c9", "mkt": "#d6402f", "fin": "#0f8a6a",
                       "legal": "#d08a1f", "it": "#17a3a3", "hr": "#7b5cd6"}
    RESPONSE_CHOICES = [
        ("mitigate", "کاهش (Mitigate)"), ("transfer", "انتقال (Transfer)"),
        ("accept", "پذیرش (Accept)"), ("avoid", "اجتناب (Avoid)"),
    ]
    TREND_CHOICES = [("up", "افزایشی"), ("down", "کاهشی"), ("flat", "پایدار")]

    title = models.CharField(max_length=300, verbose_name="عنوان ریسک")
    owner = models.CharField(max_length=150, verbose_name="مالک ریسک", blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="ops", verbose_name="دسته‌بندی")

    # ریسک ذاتی: پیش از هرگونه کنترل
    inherent_likelihood = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=4, verbose_name="احتمال (ذاتی)")
    inherent_impact = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=4, verbose_name="شدت اثر (ذاتی)")

    # ریسک باقیمانده: وضعیت فعلی، پس از کنترل‌های موجود
    likelihood = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=3, verbose_name="احتمال (باقیمانده)")
    impact = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=3, verbose_name="شدت اثر (باقیمانده)")

    # ریسک هدف: سطح قابل‌قبول پس از تکمیل اقدامات برنامه‌ریزی‌شده
    target_likelihood = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=2, verbose_name="احتمال (هدف)")
    target_impact = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=2, verbose_name="شدت اثر (هدف)")

    response_strategy = models.CharField(max_length=10, choices=RESPONSE_CHOICES, default="mitigate", verbose_name="راهبرد پاسخ")
    trend = models.CharField(max_length=5, choices=TREND_CHOICES, default="flat", verbose_name="روند نسبت به دوره قبل")
    kri = models.CharField(max_length=200, blank=True, verbose_name="شاخص کلیدی ریسک (KRI)")
    mitigation = models.TextField(verbose_name="اقدامات کنترلی (هر خط یک مورد)", blank=True)
    linked_objective = models.ForeignKey(
        "StrategicObjective", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="risks", verbose_name="هدف استراتژیک تهدیدشده",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "ریسک"
        verbose_name_plural = "ریسک‌ها"

    def __str__(self):
        return self.title

    @staticmethod
    def _zone_of(score):
        if score >= 15:
            return "crit"
        if score >= 10:
            return "high"
        if score >= 5:
            return "med"
        return "low"

    @property
    def inherent_score(self):
        return self.inherent_likelihood * self.inherent_impact

    @property
    def residual_score(self):
        return self.likelihood * self.impact

    @property
    def target_score(self):
        return self.target_likelihood * self.target_impact

    # نگه‌داری برای سازگاری با کدهای قبلی که severity_sum را صدا می‌زنند
    @property
    def severity_sum(self):
        return self.residual_score

    @property
    def zone(self):
        return self._zone_of(self.residual_score)

    @property
    def inherent_zone(self):
        return self._zone_of(self.inherent_score)

    @property
    def target_zone(self):
        return self._zone_of(self.target_score)

    @property
    def category_color(self):
        return self.CATEGORY_COLOR.get(self.category, "#5a6474")

    @property
    def effectiveness_pct(self):
        """چند درصد از ریسک ذاتی، توسط کنترل‌های موجود کاهش یافته."""
        if self.inherent_score <= 0:
            return 0
        return round((self.inherent_score - self.residual_score) / self.inherent_score * 100)

    @property
    def mitigation_list(self):
        return [m.strip() for m in self.mitigation.splitlines() if m.strip()]

    @property
    def sev_class(self):
        return {"crit": "high", "high": "high", "med": "med", "low": "low"}[self.zone]


class SWOTItem(models.Model):
    CATEGORY_CHOICES = [
        ("s", "نقطه قوت"),
        ("w", "نقطه ضعف"),
        ("o", "فرصت"),
        ("t", "تهدید"),
    ]
    IMPACT_CHOICES = [("high", "بالا"), ("med", "متوسط")]
    WEIGHT_CHOICES = [(1, "۱"), (2, "۲"), (3, "۳"), (4, "۴"), (5, "۵")]

    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES)
    text = models.CharField(max_length=300, verbose_name="متن")
    impact = models.CharField(max_length=10, choices=IMPACT_CHOICES, default="med", verbose_name="اهمیت")
    weight = models.PositiveSmallIntegerField(choices=WEIGHT_CHOICES, default=3, verbose_name="وزن اهمیت (۱ تا ۵)")
    business_unit = models.ForeignKey(
        "BusinessUnit", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="swot_items", verbose_name="کسب‌وکار",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-weight", "created_at"]
        verbose_name = "مورد SWOT"
        verbose_name_plural = "موارد SWOT"

    def __str__(self):
        return self.text


class TOWSStrategy(models.Model):
    CATEGORY_CHOICES = [
        ("so", "SO — تهاجمی"),
        ("st", "ST — تنوع"),
        ("wo", "WO — بازنگری"),
        ("wt", "WT — تدافعی"),
    ]

    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, verbose_name="نوع راهبرد")
    text = models.CharField(max_length=300, verbose_name="متن راهبرد")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    business_unit = models.ForeignKey(
        "BusinessUnit", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="tows_strategies", verbose_name="کسب‌وکار",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["category", "order"]
        verbose_name = "راهبرد TOWS"
        verbose_name_plural = "راهبردهای TOWS"

    def __str__(self):
        return f"{self.get_category_display()} — {self.text}"


class BusinessUnit(models.Model):
    ARCHETYPE_CHOICES = [
        ("intimacy", "صمیمیت با مشتری"),
        ("excellence", "برتری عملیاتی"),
        ("exclusive", "ایجاد فضای انحصاری"),
        ("other", "سایر"),
    ]

    name = models.CharField(max_length=150, verbose_name="نام کسب‌وکار")
    archetype = models.CharField(max_length=20, choices=ARCHETYPE_CHOICES, default="other", verbose_name="رویکرد استراتژیک")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "کسب‌وکار"
        verbose_name_plural = "کسب‌وکارها"

    def __str__(self):
        return self.name


class StrategyTheme(models.Model):
    """محور استراتژیک — ستون‌های نقشه، مخصوص هر کسب‌وکار (نه یک لیست ثابت سراسری)."""
    business_unit = models.ForeignKey(
        BusinessUnit, on_delete=models.CASCADE, related_name="themes", verbose_name="کسب‌وکار",
    )
    name = models.CharField(max_length=100, verbose_name="نام محور")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["business_unit", "order"]
        verbose_name = "محور نقشه استراتژیک"
        verbose_name_plural = "محورهای نقشه استراتژیک"

    def __str__(self):
        return f"{self.business_unit.name} — {self.name}"


class StrategicObjective(models.Model):
    PERSPECTIVE_CHOICES = [
        ("financial", "مالی"),
        ("customer", "مشتری"),
        ("process", "فرآیندهای داخلی"),
        ("learning", "یادگیری و رشد"),
    ]
    STATUS_CHOICES = [
        ("on", "در مسیر هدف"),
        ("watch", "نیازمند پیگیری"),
        ("risk", "در معرض ریسک"),
    ]

    code = models.CharField(max_length=10, verbose_name="کد (مثل F1، C2)")
    perspective = models.CharField(max_length=20, choices=PERSPECTIVE_CHOICES, verbose_name="منظر BSC")
    theme = models.ForeignKey(
        StrategyTheme, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="objectives", verbose_name="محور استراتژیک",
    )
    title = models.CharField(max_length=300, verbose_name="عنوان هدف")
    kpi = models.CharField(max_length=300, verbose_name="KPI", blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="on", verbose_name="وضعیت")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    feeds_into = models.ManyToManyField(
        "self", blank=True, symmetrical=False, related_name="fed_by",
        verbose_name="این هدف به کدام هدف(ها) کمک می‌کند",
    )
    business_unit = models.ForeignKey(
        BusinessUnit, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="objectives", verbose_name="کسب‌وکار",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order", "code"]
        verbose_name = "هدف استراتژیک"
        verbose_name_plural = "اهداف استراتژیک (نقشه استراتژیک)"

    def __str__(self):
        return f"{self.code} — {self.title}"


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

    KIND_CHOICES = [
        ("factor", "عامل محیطی"),
        ("opportunity", "فرصت"),
        ("threat", "تهدید"),
    ]

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="بُعد")
    kind = models.CharField(max_length=15, choices=KIND_CHOICES, default="factor", verbose_name="نوع")
    text = models.CharField(max_length=500, verbose_name="متن")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["category", "order"]
        verbose_name = "عامل PESTEL"
        verbose_name_plural = "تحلیل PESTEL"

    def __str__(self):
        return f"{self.get_category_display()} — {self.text}"


class PorterForce(models.Model):
    FORCE_CHOICES = [
        ("rivalry", "شدت رقابت موجود"),
        ("buyer_power", "قدرت چانه‌زنی مشتریان"),
        ("supplier_power", "قدرت چانه‌زنی تأمین‌کنندگان"),
        ("new_entrants", "تهدید ورود رقبای جدید"),
        ("substitutes", "تهدید کالاها/خدمات جایگزین"),
    ]
    LEVEL_CHOICES = [
        ("low", "کم"), ("medium", "متوسط"), ("high", "زیاد"), ("very_high", "بسیار زیاد"),
    ]
    LEVEL_COLOR = {"low": "var(--success)", "medium": "var(--accent)", "high": "#B0413E", "very_high": "#7B1E1E"}

    force = models.CharField(max_length=20, choices=FORCE_CHOICES, unique=True, verbose_name="نیرو")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default="medium", verbose_name="شدت")
    reasons = models.TextField(blank=True, verbose_name="دلایل (هر خط یک مورد)")
    conclusion = models.TextField(blank=True, verbose_name="نتیجه")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["force"]
        verbose_name = "نیروی پورتر"
        verbose_name_plural = "تحلیل پنج نیروی پورتر"

    def __str__(self):
        return self.get_force_display()

    @property
    def reasons_list(self):
        return [r.strip() for r in self.reasons.splitlines() if r.strip()]

    @property
    def level_color(self):
        return self.LEVEL_COLOR.get(self.level, "var(--ink-faint)")
