import re
from django.db import models
from django.utils import timezone
from django.utils.html import escape
from django.utils.safestring import mark_safe


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
    STATUS_HEX = {
        "in_progress": "#3E7A52",
        "on_track": "#2E5C8A",
        "needs_attention": "#C97A2B",
        "digital": "#6C56A3",
        "done": "#8B93A1",
    }

    title = models.CharField(max_length=300, verbose_name="عنوان پروژه")
    owner = models.CharField(max_length=150, verbose_name="واحد مسئول", blank=True)
    start_date = models.DateField(verbose_name="تاریخ شروع")
    end_date = models.DateField(verbose_name="تاریخ پایان")
    progress = models.PositiveSmallIntegerField(default=0, verbose_name="پیشرفت (٪)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="on_track", verbose_name="وضعیت")
    business_unit = models.ForeignKey(
        "BusinessUnit", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="initiatives", verbose_name="کسب‌وکار",
    )
    work_group = models.CharField(max_length=150, blank=True, verbose_name="کارگروه")
    division = models.CharField(max_length=150, blank=True, verbose_name="معاونت")
    objectives = models.ManyToManyField(
        "StrategicObjective", blank=True, related_name="initiatives",
        verbose_name="اهداف استراتژیک مرتبط",
    )
    source_kpi = models.ManyToManyField(
        "CompanyKPI", blank=True, related_name="initiatives", verbose_name="شاخص‌های مبنا (اختیاری)",
    )
    source_operational_kpi = models.ManyToManyField(
        "OperationalKPI", blank=True, related_name="initiatives", verbose_name="شاخص‌های عملیاتی مبنا (اختیاری)",
    )
    source_tows = models.ManyToManyField(
        "TOWSStrategy", blank=True, related_name="initiatives", verbose_name="راهبردهای TOWS مبنا (اختیاری)",
    )
    source_risk = models.ManyToManyField(
        "Risk", blank=True, related_name="initiatives", verbose_name="ریسک‌های مبنا (اختیاری)",
    )
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

    @property
    def status_hex(self):
        return self.STATUS_HEX.get(self.status, "#2E5C8A")

    @property
    def traced_origins(self):
        """ردیابی خودکار (فقط نمایشی، بدون رابطه‌ی دیتابیسی جدید): از راهبرد TOWS مبنا،
        به موارد SWOT مبنای همون راهبرد، تا منبع اصلی هرکدوم (PESTEL/Porter/ذینفع/
        McKinsey 7S/زنجیره ارزش/سناریو) — همه از قبل توی سامانه وصل بودن."""
        seen = set()
        origins = []
        for tows in self.source_tows.all():
            for si in tows.source_items.all():
                source_type, source_detail = si.source_full_detail
                if not source_type:
                    continue
                key = (tows.pk, si.pk)
                if key in seen:
                    continue
                seen.add(key)
                origins.append({
                    "tows": tows, "swot_item": si,
                    "source_type": source_type, "source_detail": source_detail,
                })
        return origins


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
    cause = models.TextField(blank=True, verbose_name="منشأ/علت بروز ریسک")
    consequence = models.TextField(blank=True, verbose_name="پیامد ریسک")
    owner = models.CharField(max_length=150, verbose_name="مسئول ریسک/پروژه", blank=True)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default="ops", verbose_name="دسته‌بندی")

    # ارزیابی ریسک — طبق فایل رسمی شرکت، فقط یک ارزیابی (نه سه‌لایه)
    likelihood = models.DecimalField(max_digits=3, decimal_places=2, default=3, verbose_name="احتمال رخداد (P)")
    impact = models.DecimalField(max_digits=3, decimal_places=2, default=3, verbose_name="شدت اثر (R)")

    response_strategy = models.CharField(max_length=10, choices=RESPONSE_CHOICES, default="mitigate", verbose_name="راهبرد پاسخ")
    trend = models.CharField(max_length=5, choices=TREND_CHOICES, default="flat", verbose_name="روند نسبت به دوره قبل")
    kri = models.CharField(max_length=200, blank=True, verbose_name="شاخص کلیدی ریسک (KRI)")
    mitigation = models.TextField(verbose_name="اقدامات کنترلی (هر خط یک مورد)", blank=True)
    linked_objective = models.ForeignKey(
        "StrategicObjective", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="risks", verbose_name="هدف استراتژیک تهدیدشده",
    )
    related_swot_items = models.ManyToManyField(
        "SWOTItem", blank=True, related_name="risks", verbose_name="منشأ (تهدید/ضعف SWOT)",
        limit_choices_to={"category__in": ["t", "w"]},
    )
    related_scenario = models.ManyToManyField(
        "Scenario", blank=True, related_name="risks", verbose_name="سناریوهای مرتبط",
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
    def residual_score(self):
        """امتیاز ریسک (RPN) = احتمال × شدت اثر، طبق فایل رسمی."""
        return round(float(self.likelihood) * float(self.impact), 2)

    # نگه‌داری برای سازگاری با کدهای قبلی که severity_sum را صدا می‌زنند
    @property
    def severity_sum(self):
        return self.residual_score

    @property
    def zone(self):
        return self._zone_of(self.residual_score)

    @property
    def category_color(self):
        return self.CATEGORY_COLOR.get(self.category, "#5a6474")

    @property
    def traced_swot_origins(self):
        """ردیابی خودکار منشأ (فقط نمایشی، بدون رابطه‌ی دیتابیسی جدید): از موارد SWOT
        (تهدید/ضعف) که دستی به این ریسک وصل کردید، تا منبع اصلی هرکدوم (PESTEL/Porter/
        ذینفع/McKinsey 7S/زنجیره ارزش/سناریو)."""
        origins = []
        for si in self.related_swot_items.all():
            source_type, source_detail = si.source_full_detail
            if not source_type:
                continue
            origins.append({"swot_item": si, "source_type": source_type, "source_detail": source_detail})
        return origins

    @property
    def mitigation_list(self):
        return [m.strip() for m in self.mitigation.splitlines() if m.strip()]

    @property
    def consequence_list(self):
        return [c.strip() for c in self.consequence.splitlines() if c.strip()]

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
    # ردیابی منشأ — فرصت/تهدید معمولاً از PESTEL یا پورتر می‌آید؛ قوت/ضعف از 7S یا زنجیره ارزش
    source_pestel = models.ForeignKey(
        "PestelFactor", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="swot_items", verbose_name="عامل محیطی مرتبط (PESTEL)",
    )
    source_porter = models.ForeignKey(
        "PorterForce", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="swot_items", verbose_name="نیروی پورتر مرتبط",
    )
    source_7s = models.ForeignKey(
        "McKinsey7S", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="swot_items", verbose_name="مؤلفه McKinsey 7S مرتبط",
    )
    source_value_chain = models.ForeignKey(
        "ValueChainActivity", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="swot_items", verbose_name="فعالیت زنجیره ارزش مرتبط",
    )
    source_stakeholder = models.ForeignKey(
        "Stakeholder", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="swot_items", verbose_name="ذینفع مرتبط",
    )
    source_scenario = models.ForeignKey(
        "Scenario", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="swot_items", verbose_name="سناریوی مرتبط",
    )
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

    @property
    def source(self):
        """اولین منبع تعریف‌شده (اگر باشد) را برمی‌گرداند."""
        return (
            self.source_pestel or self.source_porter or self.source_stakeholder
            or self.source_scenario or self.source_7s or self.source_value_chain
        )

    @property
    def source_label(self):
        """نام ماژول منبع + متن آن را برمی‌گرداند تا نوع منبع همیشه مشخص باشد."""
        if self.source_pestel:
            return f"PESTEL: {self.source_pestel.text}"
        if self.source_porter:
            return f"پورتر: {self.source_porter.get_force_display()}"
        if self.source_stakeholder:
            return f"ذی‌نفع: {self.source_stakeholder.name}"
        if self.source_scenario:
            return f"سناریو: {self.source_scenario.display_title}"
        if self.source_7s:
            return f"McKinsey 7S: {self.source_7s.get_component_display()}"
        if self.source_value_chain:
            return f"زنجیره ارزش: {self.source_value_chain.get_activity_display()}"
        return ""

    @property
    def source_label_full(self):
        """متن کامل و آماده برای هاور — دقیقاً فرمت «نوع: جزئیات کامل» طبق الگوی استاندارد سامانه."""
        source_type, source_detail = self.source_full_detail
        if not source_type:
            return ""
        return f"{source_type}: {source_detail}"

    @property
    def source_full_detail(self):
        """جزئیات کامل منبع (نه فقط عنوان کوتاه) برای ردیابی خودکار — (نوع، متن تفصیلی)."""
        f = self.source_pestel
        if f:
            extra = []
            if f.effect_type:
                extra.append(f"نوع اثر: {f.get_effect_type_display()}")
            if f.related_standard:
                extra.append(f"استاندارد: {f.related_standard}")
            extra_txt = (" — " + " — ".join(extra)) if extra else ""
            return ("PESTEL", f"{f.letter} ({f.get_category_display()}) — {f.text}{extra_txt}")
        f = self.source_porter
        if f:
            extra = f" — نوع اثر: {f.get_effect_type_display()}" if f.effect_type else ""
            return ("Porter", f"{f.get_force_display()} — {f.text}{extra}")
        f = self.source_stakeholder
        if f:
            return ("ذی‌نفع", f"{f.name} — واحد: {f.department or '—'} — نیاز/انتظار: {f.need or '—'}")
        f = self.source_scenario
        if f:
            return ("سناریو", f.display_title)
        f = self.source_7s
        if f:
            return ("McKinsey 7S", f.get_component_display())
        f = self.source_value_chain
        if f:
            return ("زنجیره ارزش", f.get_activity_display())
        return ("", "")


class TOWSStrategy(models.Model):
    CATEGORY_CHOICES = [
        ("so", "SO — تهاجمی"),
        ("st", "ST — تنوع"),
        ("wo", "WO — بازنگری"),
        ("wt", "WT — تدافعی"),
    ]

    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, verbose_name="نوع راهبرد")
    text = models.TextField(verbose_name="متن راهبرد")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    source_items = models.ManyToManyField(
        "SWOTItem", blank=True, related_name="tows_strategies", verbose_name="موارد SWOT مبنا",
    )
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
    source_tows = models.ForeignKey(
        "TOWSStrategy", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="objectives", verbose_name="راهبرد TOWS مبنا",
    )
    linked_kpis = models.ManyToManyField(
        "CompanyKPI", blank=True, related_name="strategic_objectives", verbose_name="شاخص‌های استراتژیک مرتبط",
    )
    linked_operational_kpis = models.ManyToManyField(
        "OperationalKPI", blank=True, related_name="strategic_objectives", verbose_name="شاخص‌های عملیاتی مرتبط",
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
    CATEGORY_LETTER = {
        "political": "P", "economic": "E", "social": "S",
        "technological": "T", "environmental": "E", "legal": "L",
    }
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
    SCALE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    UNCERTAINTY_CHOICES = [("low", "کم"), ("medium", "متوسط"), ("high", "زیاد")]
    HORIZON_CHOICES = [("short", "کوتاه‌مدت"), ("medium", "میان‌مدت"), ("long", "بلندمدت")]
    TREND_CHOICES = [("up", "صعودی"), ("down", "نزولی"), ("flat", "ثابت")]
    UNCERTAINTY_COLOR = {"low": "var(--success)", "medium": "var(--accent)", "high": "#B0413E"}

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, verbose_name="بُعد")
    kind = models.CharField(max_length=15, choices=KIND_CHOICES, default="factor", verbose_name="نوع")
    text = models.CharField(max_length=500, verbose_name="متن")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    impact_level = models.PositiveSmallIntegerField(choices=SCALE_CHOICES, default=3, verbose_name="میزان اثر")
    probability = models.PositiveSmallIntegerField(choices=SCALE_CHOICES, default=3, verbose_name="احتمال وقوع")
    uncertainty = models.CharField(max_length=10, choices=UNCERTAINTY_CHOICES, default="medium", verbose_name="میزان عدم‌قطعیت")
    horizon = models.CharField(max_length=10, choices=HORIZON_CHOICES, default="medium", verbose_name="افق زمانی")
    trend = models.CharField(max_length=10, choices=TREND_CHOICES, default="flat", verbose_name="روند تغییر")
    created_at = models.DateTimeField(default=timezone.now)

    EFFECT_TYPE_CHOICES = [
        ("opportunity", "فرصت"), ("threat", "تهدید"), ("both", "فرصت/تهدید"),
    ]
    effect_type = models.CharField(max_length=15, choices=EFFECT_TYPE_CHOICES, blank=True, verbose_name="نوع اثر")
    related_standard = models.CharField(max_length=150, blank=True, verbose_name="استاندارد مرتبط")
    detailed_description = models.TextField(blank=True, verbose_name="توضیح تفصیلی (راهنمای درک و امتیازدهی)")
    scoring_guide = models.TextField(blank=True, verbose_name="راهنمای امتیازدهی")
    related_stakeholders = models.ManyToManyField(
        "Stakeholder", blank=True, related_name="linked_pestel_factors", verbose_name="ذینفعان مرتبط",
    )

    class Meta:
        ordering = ["category", "order"]
        verbose_name = "عامل PESTEL"
        verbose_name_plural = "تحلیل PESTEL"

    @property
    def priority_score(self):
        return self.impact_level * self.probability

    @property
    def letter(self):
        return self.CATEGORY_LETTER.get(self.category, "")

    @property
    def uncertainty_color(self):
        return self.UNCERTAINTY_COLOR.get(self.uncertainty, "var(--ink-faint)")

    def __str__(self):
        return f"{self.get_category_display()} — {self.text}"


class PorterForce(models.Model):
    FORCE_CHOICES = [
        ("rivalry", "قدرت رقبای موجود"),
        ("buyer_power", "قدرت چانه‌زنی خریداران"),
        ("supplier_power", "قدرت چانه‌زنی تأمین‌کنندگان"),
        ("new_entrants", "تهدید تازه‌واردان"),
        ("substitutes", "تهدید کالاها/خدمات جایگزین"),
    ]
    FORCE_STYLE = {
        # مرکز (رقبای موجود) رنگ برجسته‌ی خودش را دارد؛ ۴ نیروی بیرونی رنگ‌های متفاوت
        "rivalry": ("#A8321E", "#FBE7E3", "fa-chess-king"),
        "buyer_power": ("#0EA5E9", "#E3F4FC", "fa-user-tag"),
        "supplier_power": ("#8B5CF6", "#EFE9FD", "fa-truck"),
        "new_entrants": ("#EAB308", "#FDF6DD", "fa-door-open"),
        "substitutes": ("#22C55E", "#E4F8EA", "fa-retweet"),
    }
    SCALE_CHOICES = [(i, str(i)) for i in range(1, 6)]
    UNCERTAINTY_CHOICES = [("low", "کم"), ("medium", "متوسط"), ("high", "زیاد")]
    HORIZON_CHOICES = [("short", "کوتاه‌مدت"), ("medium", "میان‌مدت"), ("long", "بلندمدت")]
    TREND_CHOICES = [("up", "صعودی"), ("down", "نزولی"), ("flat", "ثابت")]
    UNCERTAINTY_COLOR = {"low": "var(--success)", "medium": "var(--accent)", "high": "#B0413E"}
    EFFECT_TYPE_CHOICES = [
        ("opportunity", "فرصت"), ("threat", "تهدید"), ("both", "فرصت/تهدید"),
    ]

    force = models.CharField(max_length=20, choices=FORCE_CHOICES, verbose_name="نیروی رقابتی")
    text = models.CharField(max_length=500, verbose_name="متن")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    impact_level = models.PositiveSmallIntegerField(choices=SCALE_CHOICES, default=3, verbose_name="میزان اثر")
    probability = models.PositiveSmallIntegerField(choices=SCALE_CHOICES, default=3, verbose_name="احتمال وقوع")
    uncertainty = models.CharField(max_length=10, choices=UNCERTAINTY_CHOICES, default="medium", verbose_name="میزان عدم‌قطعیت")
    horizon = models.CharField(max_length=10, choices=HORIZON_CHOICES, default="medium", verbose_name="افق زمانی")
    trend = models.CharField(max_length=10, choices=TREND_CHOICES, default="flat", verbose_name="روند تغییر")
    effect_type = models.CharField(max_length=15, choices=EFFECT_TYPE_CHOICES, blank=True, verbose_name="نوع اثر")
    related_standard = models.CharField(max_length=150, blank=True, verbose_name="استاندارد مرتبط")
    detailed_description = models.TextField(blank=True, verbose_name="توضیح تفصیلی (راهنمای درک و امتیازدهی)")
    scoring_guide = models.TextField(blank=True, verbose_name="راهنمای امتیازدهی")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["force", "order"]
        verbose_name = "عامل پورتر"
        verbose_name_plural = "تحلیل پنج نیروی پورتر"

    @property
    def priority_score(self):
        return self.impact_level * self.probability

    @property
    def uncertainty_color(self):
        return self.UNCERTAINTY_COLOR.get(self.uncertainty, "var(--ink-faint)")

    def __str__(self):
        return f"{self.get_force_display()} — {self.text}"

    @property
    def reasons_list(self):
        return [r.strip() for r in self.reasons.splitlines() if r.strip()]

    @property
    def level_color(self):
        return self.LEVEL_COLOR.get(self.level, "var(--ink-faint)")


class OrgIdentity(models.Model):
    """رکورد تکی (singleton) برای چشم‌انداز، مأموریت و امضای مدیریت ارشد."""
    vision = models.TextField(blank=True, verbose_name="چشم‌انداز")
    mission = models.TextField(blank=True, verbose_name="مأموریت")
    management_statement = models.TextField(blank=True, verbose_name="پیام مدیریت ارشد (بالای امضا)")
    signed_by = models.CharField(max_length=150, blank=True, verbose_name="امضاکننده")
    signed_role = models.CharField(max_length=150, blank=True, verbose_name="سمت امضاکننده")
    signed_date = models.CharField(max_length=50, blank=True, verbose_name="تاریخ امضا (شمسی، متن آزاد)")

    class Meta:
        verbose_name = "چشم‌انداز و مأموریت"
        verbose_name_plural = "چشم‌انداز و مأموریت"

    def __str__(self):
        return "چشم‌انداز و مأموریت سازمان"


class OrgValue(models.Model):
    ICON_CHOICES = [
        ("fa-solid fa-trophy", "جام (رقابت/دستاورد)"),
        ("fa-solid fa-handshake", "دست‌دادن (اعتماد/شفافیت)"),
        ("fa-solid fa-shield-halved", "سپر (کرامت/حفاظت از حقوق)"),
        ("fa-solid fa-bullhorn", "بلندگو (اطلاع‌رسانی)"),
        ("fa-solid fa-people-group", "گروه افراد (کارتیمی/کارکنان)"),
        ("fa-solid fa-lightbulb", "لامپ (نوآوری)"),
        ("fa-solid fa-users", "کاربران (وحدت/مشتری)"),
        ("fa-solid fa-heart", "قلب (مشتری‌مداری)"),
        ("fa-solid fa-graduation-cap", "کلاه فارغ‌التحصیلی (آموزش/توسعه)"),
        ("fa-solid fa-compass", "قطب‌نما (جهت‌گیری)"),
        ("fa-solid fa-star", "ستاره (پیش‌فرض)"),
    ]
    COLOR_CHOICES = [
        ("#C97A2B", "کهربایی (نارنجی ملایم)"),
        ("#1E6E7A", "سرمه‌ای فیروزه‌ای"),
        ("#6C56A3", "بنفش ملایم"),
        ("#2E5C8A", "آبی سرمه‌ای"),
        ("#B0413E", "قرمز آجری روشن"),
        ("#D9A441", "طلایی خاکی"),
        ("#3E7A52", "سبز زیتونی"),
        ("#A8321E", "قرمز آجری (مرکز)"),
    ]

    text = models.CharField(max_length=150, verbose_name="ارزش سازمانی")
    is_center = models.BooleanField(default=False, verbose_name="آیا مرکز چرخ است؟")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    icon = models.CharField(max_length=40, blank=True, default="fa-solid fa-star",
                             choices=ICON_CHOICES, verbose_name="آیکون")
    color = models.CharField(max_length=20, blank=True, default="#C97A2B",
                              choices=COLOR_CHOICES, verbose_name="رنگ")
    definition = models.TextField(blank=True, verbose_name="تعریف")
    expected_behaviors = models.TextField(blank=True, verbose_name="رفتارهای مورد انتظار (هر خط یک رفتار)")
    examples = models.TextField(blank=True, verbose_name="نمونه‌های اجرایی در سازمان (هر خط یک نمونه)")
    related_policy = models.ForeignKey(
        "QualityPolicyPoint", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="linked_values", verbose_name="بند خط‌مشی مرتبط",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "ارزش سازمانی"
        verbose_name_plural = "ارزش‌های سازمانی"

    def __str__(self):
        return self.text

    @property
    def behaviors_list(self):
        return [b.strip() for b in self.expected_behaviors.splitlines() if b.strip()]

    @property
    def examples_list(self):
        return [e.strip() for e in self.examples.splitlines() if e.strip()]


class QualityPolicyPoint(models.Model):
    number = models.PositiveSmallIntegerField(verbose_name="شماره بند")
    text = models.TextField(verbose_name="متن بند")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["order"]
        verbose_name = "بند خط‌مشی کیفیت"
        verbose_name_plural = "بندهای خط‌مشی کیفیت"

    def __str__(self):
        return f"بند {self.number}"


class McKinsey7S(models.Model):
    COMPONENT_CHOICES = [
        ("strategy", "استراتژی"),
        ("structure", "ساختار"),
        ("systems", "سیستم‌ها"),
        ("shared_values", "ارزش‌های مشترک"),
        ("skills", "مهارت‌ها"),
        ("staff", "کارکنان"),
        ("style", "سبک"),
    ]
    # رنگ، آیکون، نام انگلیسیِ مصوبِ خودِ مدل مکنزی، و گروه (سخت/نرم/مرکز)
    STYLE = {
        "strategy": ("#2E5C8A", "#E3EBF2", "fa-chess-knight", "Strategy", "hard"),
        "structure": ("#1E3F60", "#E3EBF2", "fa-sitemap", "Structure", "hard"),
        "systems": ("#1D7A73", "#DFF0EE", "fa-gears", "Systems", "hard"),
        "shared_values": ("#C97A2B", "#F5E6D3", "fa-star", "Shared Values", "center"),
        "skills": ("#6C56A3", "#ECE8F5", "fa-graduation-cap", "Skills", "soft"),
        "staff": ("#B5583F", "#F7E3DC", "fa-users", "Staff", "soft"),
        "style": ("#3E7A52", "#E1EDE4", "fa-handshake", "Style", "soft"),
    }

    component = models.CharField(max_length=20, choices=COMPONENT_CHOICES, unique=True, verbose_name="مؤلفه")
    status = models.TextField(blank=True, verbose_name="وضعیت فعلی")
    strengths = models.TextField(blank=True, verbose_name="نقاط قوت (هر خط یک مورد)")
    weaknesses = models.TextField(blank=True, verbose_name="نقاط ضعف/ریسک‌ها (هر خط یک مورد)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "مؤلفه McKinsey 7S"
        verbose_name_plural = "تحلیل McKinsey 7S"

    def __str__(self):
        return self.get_component_display()

    @property
    def strengths_list(self):
        return [s.strip() for s in self.strengths.splitlines() if s.strip()]

    @property
    def weaknesses_list(self):
        return [w.strip() for w in self.weaknesses.splitlines() if w.strip()]


class ValueChainActivity(models.Model):
    """زنجیره ارزش پورتر — ۹ فعالیت ثابت (۵ اصلی + ۴ پشتیبان)."""
    ACTIVITY_CHOICES = [
        ("infra", "زیرساخت‌های شرکت"),
        ("hr", "مدیریت منابع انسانی"),
        ("tech", "توسعه فناوری"),
        ("procurement", "تدارکات"),
        ("inbound", "لجستیک ورودی"),
        ("operations", "عملیات"),
        ("outbound", "لجستیک خروجی"),
        ("marketing", "بازاریابی و فروش"),
        ("service", "خدمات به مشتری"),
    ]
    ACTIVITY_TYPE = {
        "infra": "support", "hr": "support", "tech": "support", "procurement": "support",
        "inbound": "primary", "operations": "primary", "outbound": "primary",
        "marketing": "primary", "service": "primary",
    }

    activity = models.CharField(max_length=20, choices=ACTIVITY_CHOICES, unique=True, verbose_name="فعالیت")
    content = models.TextField(blank=True, verbose_name="اقدامات/محتوا (هر خط یک مورد)")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "فعالیت زنجیره ارزش پورتر"
        verbose_name_plural = "زنجیره ارزش پورتر"

    def __str__(self):
        return self.get_activity_display()

    @property
    def activity_type(self):
        return self.ACTIVITY_TYPE.get(self.activity, "primary")

    @property
    def content_list(self):
        return [c.strip() for c in self.content.splitlines() if c.strip()]


class Stakeholder(models.Model):
    STATUS_CHOICES = [
        ("open", "باز"),
        ("in_progress", "در حال بررسی"),
        ("done", "رسیدگی‌شده"),
    ]
    related_porters = models.ManyToManyField(
        "PorterForce", blank=True, related_name="linked_stakeholders", verbose_name="عوامل Porter مرتبط",
    )

    department = models.CharField(max_length=200, verbose_name="واحد/مدیریت ثبت‌کننده", blank=True)
    name = models.CharField(max_length=200, verbose_name="نام ذینفع")
    is_internal = models.BooleanField(default=False, verbose_name="درون سازمانی")
    is_external = models.BooleanField(default=False, verbose_name="برون سازمانی")
    channel = models.CharField(max_length=300, verbose_name="کانال ارتباطی", blank=True)
    need = models.TextField(verbose_name="نیاز/انتظار ذینفع", blank=True)
    need_flag = models.BooleanField(default=False, verbose_name="نوع: نیاز")
    expectation_flag = models.BooleanField(default=False, verbose_name="نوع: انتظار")
    risk_text = models.TextField(verbose_name="ریسک", blank=True)
    risk_occurrence = models.PositiveIntegerField(null=True, blank=True, verbose_name="احتمال وقوع ریسک")
    risk_severity = models.PositiveIntegerField(null=True, blank=True, verbose_name="شدت ریسک")
    risk_detection = models.PositiveIntegerField(null=True, blank=True, verbose_name="قابلیت تشخیص ریسک")
    risk_score = models.PositiveIntegerField(null=True, blank=True, verbose_name="عدد ریسک")
    opportunity_text = models.TextField(verbose_name="فرصت", blank=True)
    opportunity_importance = models.PositiveIntegerField(null=True, blank=True, verbose_name="امتیاز اهمیت فرصت")
    opportunity_impact = models.PositiveIntegerField(null=True, blank=True, verbose_name="امتیاز تأثیر فرصت")
    opportunity_score = models.PositiveIntegerField(null=True, blank=True, verbose_name="عدد فرصت")
    action = models.TextField(verbose_name="اقدام تعریف‌شده", blank=True)
    related_initiatives = models.ManyToManyField(
        "Initiative", blank=True, related_name="linked_stakeholders", verbose_name="پروژه‌های تحول مرتبط",
    )
    domain = models.CharField(max_length=100, blank=True, verbose_name="حوزه")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="open", verbose_name="وضعیت رسیدگی")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-risk_score"]
        verbose_name = "ذینفع"
        verbose_name_plural = "مخزن ذینفعان"

    def __str__(self):
        return f"{self.name} — {self.need[:40]}"


class CrossImpactFactor(models.Model):
    """نتیجه‌ی نهایی تحلیل اثرات متقابل — جای‌گذاری عوامل کلیدی در ۴ ناحیه (روش MICMAC)."""
    QUADRANT_CHOICES = [
        ("driver", "پیشران‌ها (متغیرهای مستقل)"),
        ("relay", "دوجانبه (سیاست‌گذاری)"),
        ("watch", "خنثی (خودمتصل)"),
        ("resultant", "رصد و دیده‌بانی (وابسته)"),
    ]
    QUADRANT_COLOR = {
        "driver": "#B0413E", "relay": "#C97A2B", "watch": "#5a6474", "resultant": "#2E5C8A",
    }

    text = models.CharField(max_length=200, verbose_name="عامل")
    quadrant = models.CharField(max_length=12, choices=QUADRANT_CHOICES, verbose_name="ناحیه")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    linked_pestel = models.ForeignKey(
        "PestelFactor", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="cross_impact_factors", verbose_name="عامل PESTEL مرتبط (اختیاری)",
    )
    linked_porter = models.ForeignKey(
        "PorterForce", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="cross_impact_factors", verbose_name="نیروی پورتر مرتبط (اختیاری)",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["quadrant", "order"]
        verbose_name = "عامل اثرات متقابل"
        verbose_name_plural = "تحلیل اثرات متقابل"

    def __str__(self):
        return self.text

    @property
    def quadrant_color(self):
        return self.QUADRANT_COLOR.get(self.quadrant, "var(--ink-faint)")


class CrossImpactLink(models.Model):
    """امتیاز اثرگذاری مستقیم یک عامل بر عامل دیگر — پایه‌ی محاسبه‌ی روش MICMAC."""
    SCORE_CHOICES = [(0, "بدون اثر"), (1, "کم"), (2, "متوسط"), (3, "زیاد")]

    from_factor = models.ForeignKey(CrossImpactFactor, related_name="outgoing_links", on_delete=models.CASCADE)
    to_factor = models.ForeignKey(CrossImpactFactor, related_name="incoming_links", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES, default=0, verbose_name="میزان اثر")

    class Meta:
        unique_together = ("from_factor", "to_factor")
        verbose_name = "اثر مستقیم"
        verbose_name_plural = "ماتریس اثرات مستقیم"

    def __str__(self):
        return f"{self.from_factor} ← {self.to_factor}: {self.score}"


class ScenarioResponseStrategy(models.Model):
    """راهبردهای پاسخ/تاب‌آوری سازمان در چارچوب یک سناریوی مشخص — هر راهبرد به یک سناریو
    وصل است، پس هر سناریو مستقل از بقیه، راهبردهای خودش را (هروقت نوشته شدند) نشان می‌دهد."""
    scenario = models.ForeignKey(
        "Scenario", on_delete=models.CASCADE, related_name="response_strategies", verbose_name="سناریو",
    )
    text = models.TextField(verbose_name="متن راهبرد")
    related_standard = models.CharField(max_length=100, blank=True, verbose_name="استاندارد مرتبط (اختیاری)")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["order"]
        verbose_name = "راهبرد پاسخ به سناریو"
        verbose_name_plural = "راهبردهای پاسخ به سناریو"

    def __str__(self):
        return f"{self.scenario} — {self.text[:40]}"


class ScenarioHighlight(models.Model):
    """تکه‌متن‌هایی از روایت سناریو که دستی (توسط کاربر) به یه عامل ماتریس اثر متقابل
    برچسب‌گذاری شدن — جایگزین تشخیص خودکار قبلی، چون دقت صددرصد و کنترل کامل می‌ده."""
    scenario = models.ForeignKey("Scenario", on_delete=models.CASCADE, related_name="highlights")
    cross_impact_factor = models.ForeignKey(
        "CrossImpactFactor", on_delete=models.CASCADE, related_name="scenario_highlights",
        verbose_name="عامل ماتریس اثر متقابل",
    )
    phrase = models.CharField(max_length=300, verbose_name="تکه‌متن انتخاب‌شده")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "برچسب متن سناریو"
        verbose_name_plural = "برچسب‌های متن سناریو"

    def __str__(self):
        return f"{self.scenario} — «{self.phrase[:30]}» → {self.cross_impact_factor.text}"


class ScenarioAxes(models.Model):
    """رکورد تکی (singleton) برای نام دو محور عدم‌قطعیت سناریوها."""
    axis1_name = models.CharField(max_length=200, default="امکان تأمین منابع مالی", verbose_name="عنوان محور عمودی")
    axis1_positive = models.CharField(max_length=150, default="دستیابی به منابع مالی", verbose_name="قطب مثبت محور عمودی")
    axis1_negative = models.CharField(max_length=150, default="عدم دستیابی به منابع مالی", verbose_name="قطب منفی محور عمودی")
    axis1_source = models.ForeignKey(
        "CrossImpactFactor", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="پیشران مبنای محور عمودی (ماتریس اثر متقابل)",
    )
    axis2_name = models.CharField(max_length=200, default="وضعیت بین‌المللی", verbose_name="عنوان محور افقی")
    axis2_positive = models.CharField(max_length=150, default="تعاملات هدفمند بین‌المللی", verbose_name="قطب مثبت محور افقی")
    axis2_negative = models.CharField(max_length=150, default="تشدید محدودیت‌های بین‌المللی", verbose_name="قطب منفی محور افقی")
    axis2_source = models.ForeignKey(
        "CrossImpactFactor", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="+", verbose_name="پیشران مبنای محور افقی (ماتریس اثر متقابل)",
    )

    class Meta:
        verbose_name = "محورهای سناریو"
        verbose_name_plural = "محورهای سناریو"

    def __str__(self):
        return "محورهای سناریوسازی"


class Scenario(models.Model):
    """۴ سناریوی ثابت — تقاطع دو محور عدم‌قطعیت (روش سناریونویسی)."""
    QUADRANT_CHOICES = [
        ("prosperity", "پیش به سوی بالندگی"),
        ("exploration", "کنکاش محیطی"),
        ("rocky", "گذر از سنگلاخ"),
        ("foggy", "هوای مه‌آلود"),
    ]
    QUADRANT_COLOR = {
        "prosperity": "#3E7A52", "exploration": "#C97A2B", "rocky": "#2E5C8A", "foggy": "#5a6474",
    }

    quadrant = models.CharField(max_length=15, choices=QUADRANT_CHOICES, unique=True, verbose_name="ناحیه")
    title = models.CharField(max_length=150, blank=True, verbose_name="عنوان سناریو")
    narrative = models.TextField(blank=True, verbose_name="روایت کامل سناریو")
    is_selected = models.BooleanField(default=False, verbose_name="سناریوی منتخب/مبنا")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["quadrant"]
        verbose_name = "سناریو"
        verbose_name_plural = "سناریوهای راهبردی"

    def __str__(self):
        return self.title or self.get_quadrant_display()

    @property
    def manual_highlighted_narrative(self):
        """نسخه‌ی برجسته‌شده‌ی روایت، بر پایه‌ی برچسب‌های دستی کاربر (نه تشخیص خودکار) —
        هر تکه‌متن که کاربر انتخاب و به یه عامل ماتریس وصل کرده، رنگی نشون داده می‌شه؛
        قرمز برای پیشران‌ها، رنگ خودِ ناحیه برای بقیه."""
        text = self.narrative or ""
        if not text:
            return ""
        spans = []
        for h in self.highlights.select_related("cross_impact_factor__linked_pestel", "cross_impact_factor__linked_porter"):
            if not h.phrase:
                continue
            idx = text.find(h.phrase)
            if idx == -1:
                continue
            spans.append((idx, idx + len(h.phrase), h))
        spans.sort(key=lambda s: s[0])
        selected = []
        for s, e, h in spans:
            if any(not (e <= ss or s >= ee) for ss, ee, _ in selected):
                continue
            selected.append((s, e, h))

        out, pos = [], 0
        for s, e, h in selected:
            out.append(escape(text[pos:s]))
            f = h.cross_impact_factor
            color = f.QUADRANT_COLOR.get(f.quadrant, "#5a6474")
            detail_parts = [f"ماتریس اثر متقابل ({f.get_quadrant_display()}): {f.text}"]
            if f.linked_pestel:
                detail_parts.append(f"← منبع (PESTEL): {f.linked_pestel.letter} ({f.linked_pestel.get_category_display()}) — {f.linked_pestel.text}")
            if f.linked_porter:
                detail_parts.append(f"← منبع (Porter): {f.linked_porter.get_force_display()} — {f.linked_porter.text}")
            detail = "&#10;".join(escape(p) for p in detail_parts)
            out.append(f'<span class="manual-highlight" style="color:{color};border-bottom-color:{color};" title="{detail}">{escape(text[s:e])}</span>')
            pos = e
        out.append(escape(text[pos:]))
        return mark_safe("".join(out))

    @property
    def display_title(self):
        return self.title or self.get_quadrant_display()

    @property
    def quadrant_color(self):
        return self.QUADRANT_COLOR.get(self.quadrant, "var(--ink-faint)")


class CompanyObjective(models.Model):
    """اهداف کلان سطح کل شرکت سایپا یدک — مرتبط با اهداف استراتژیک گروه سایپا (شرکت مادر)."""
    code = models.CharField(max_length=10, unique=True, verbose_name="کد هدف")
    group_title = models.CharField(max_length=300, blank=True, verbose_name="هدف کلان استراتژیک گروه")
    title = models.CharField(max_length=300, verbose_name="عنوان هدف")
    description = models.TextField(blank=True, verbose_name="تشریح هدف")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order"]
        verbose_name = "هدف کلان شرکت"
        verbose_name_plural = "اهداف کلان شرکت"

    def __str__(self):
        return f"{self.code} — {self.title}"


class CompanyKPI(models.Model):
    """شاخص‌های کلیدی عملکرد سطح کل شرکت — وصل به اهداف کلان شرکت."""
    DOMAIN_CHOICES = [
        ("Q", "کیفیت (Quality)"),
        ("D", "تحویل/حجم (Delivery)"),
        ("C", "هزینه/درآمد (Cost)"),
        ("M", "مدیریتی (Management)"),
    ]
    DOMAIN_COLOR = {"Q": "#2E5C8A", "D": "#C97A2B", "C": "#3E7A52", "M": "#5a6474"}

    code = models.CharField(max_length=10, unique=True, verbose_name="کد شاخص")
    domain = models.CharField(max_length=1, choices=DOMAIN_CHOICES, default="Q", verbose_name="حوزه اثربخشی")
    name = models.CharField(max_length=300, verbose_name="شاخص کلیدی")
    source_operational_kpi = models.ForeignKey(
        "OperationalKPI", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="promoted_to_company_kpis", verbose_name="برگرفته از شاخص عملیاتی (اختیاری)",
    )
    unit = models.CharField(max_length=60, blank=True, verbose_name="واحد سنجش")
    target_1404 = models.CharField(max_length=60, blank=True, verbose_name="هدف سال ۱۴۰۴")
    actual_1404 = models.CharField(max_length=60, blank=True, verbose_name="عملکرد ۱۴۰۴")
    target_1405 = models.CharField(max_length=60, blank=True, verbose_name="هدف سال ۱۴۰۵")
    actual_1405 = models.CharField(max_length=60, blank=True, verbose_name="عملکرد ۱۴۰۵")
    progress_1405 = models.CharField(max_length=20, blank=True, verbose_name="درصد تحقق (دستی)")
    objectives = models.ManyToManyField(
        CompanyObjective, blank=True, related_name="kpis", verbose_name="اهداف مرتبط",
    )
    is_monitoring = models.BooleanField(default=False, verbose_name="صرفاً پایشی (بدون هدف مستقیم)")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["order"]
        verbose_name = "شاخص کلان شرکت"
        verbose_name_plural = "شاخص‌های کلان شرکت"

    def __str__(self):
        return f"{self.code} — {self.name}"

    @property
    def domain_color(self):
        return self.DOMAIN_COLOR.get(self.domain, "var(--ink-faint)")

    @property
    def progress_pct(self):
        """درصد پیشرفت نسبت هدف ۱۴۰۴ به عملکرد، فقط اگر هردو عددی باشند."""
        try:
            t = float(self.target_1404)
            a = float(self.actual_1404)
            if t == 0:
                return None
            pct = round(a / t * 100)
            return max(0, min(pct, 150))
        except (TypeError, ValueError):
            return None

    @property
    def progress_pct_1405(self):
        """درصد تحقق هدف ۱۴۰۵ نسبت به عملکرد ۱۴۰۵، فقط اگر هردو عددی باشند."""
        try:
            t = float(self.target_1405)
            a = float(self.actual_1405)
            if t == 0:
                return None
            pct = round(a / t * 100)
            return max(0, min(pct, 150))
        except (TypeError, ValueError):
            return None

    @property
    def manual_progress_value(self):
        """عدد درصد را از فیلد آزاد «درصد تحقق» (مثلاً «۸۵٪» یا «85%») استخراج می‌کند."""
        import re
        if not self.progress_1405:
            return None
        text = self.progress_1405
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        for i, d in enumerate(persian_digits):
            text = text.replace(d, str(i))
        m = re.search(r"\d+(\.\d+)?", text)
        if not m:
            return None
        try:
            return round(float(m.group()))
        except ValueError:
            return None

    @property
    def progress_color(self):
        p = self.progress_pct
        if p is None:
            return "#9aa3ac"
        if p >= 90:
            return "#3E7A52"
        if p >= 60:
            return "#C97A2B"
        return "#B0413E"


class RawIdentifiedFactor(models.Model):
    """آرشیو ۵۲۵ عاملی که در ابتدای کار توسط معاونت‌های مختلف سازمان شناسایی و جمع‌آوری
    شدند — قبل از هرگونه پالایش/امتیازدهی. صرفاً مرجع تاریخی است، نه بخشی از فرآیند فعلی."""
    SOURCE_CHOICES = [("pestel", "PESTEL"), ("porter", "Porter")]

    source_type = models.CharField(max_length=10, choices=SOURCE_CHOICES, verbose_name="نوع")
    department = models.CharField(max_length=150, blank=True, verbose_name="معاونت/واحد پیشنهاددهنده")
    category = models.CharField(max_length=150, blank=True, verbose_name="دسته‌بندی")
    text = models.TextField(verbose_name="شرح عامل")
    row_number = models.PositiveIntegerField(default=0, verbose_name="ردیف اصلی در فایل مرجع")

    class Meta:
        ordering = ["source_type", "row_number"]
        verbose_name = "عامل شناسایی‌شده اولیه (آرشیو)"
        verbose_name_plural = "آرشیو عوامل شناسایی‌شده اولیه"

    def __str__(self):
        return f"{self.get_source_type_display()} — {self.text[:40]}"


class OperationalKPI(models.Model):
    """بانک شاخص‌های عملیاتی/دپارتمانی کل سازمان — سطح جدا و پایین‌تر از «شاخص‌های کلان
    شرکت» (CompanyKPI)، طبق استاندارد Cascading در BSC. مرجع، نه لزوماً همه‌شان پایش‌شونده."""
    DOMAIN_CHOICES = [
        ("Q", "کیفیت (Quality)"),
        ("D", "تحویل/حجم (Delivery)"),
        ("C", "هزینه/درآمد (Cost)"),
        ("M", "مدیریتی (Management)"),
    ]
    DOMAIN_COLOR = {"Q": "#2E5C8A", "D": "#C97A2B", "C": "#3E7A52", "M": "#5a6474"}

    code = models.CharField(max_length=20, unique=True, verbose_name="کد شاخص")
    title = models.CharField(max_length=300, verbose_name="عنوان شاخص")
    domain = models.CharField(max_length=1, choices=DOMAIN_CHOICES, default="Q", verbose_name="حوزه اثربخشی")
    unit = models.CharField(max_length=60, blank=True, verbose_name="واحد سنجش")
    department = models.CharField(max_length=150, blank=True, verbose_name="دپارتمان مالک")
    target_1404 = models.CharField(max_length=60, blank=True, verbose_name="هدف سال ۱۴۰۴")
    actual_1404 = models.CharField(max_length=60, blank=True, verbose_name="عملکرد ۱۴۰۴")
    target_1405 = models.CharField(max_length=60, blank=True, verbose_name="هدف سال ۱۴۰۵")
    actual_1405 = models.CharField(max_length=60, blank=True, verbose_name="عملکرد ۱۴۰۵")
    progress_1405 = models.CharField(max_length=20, blank=True, verbose_name="درصد تحقق (دستی)")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["department", "order", "code"]
        verbose_name = "شاخص عملیاتی"
        verbose_name_plural = "شاخص‌های عملیاتی"

    def __str__(self):
        return f"{self.code} — {self.title}"

    @property
    def progress_pct(self):
        try:
            t = float(self.target_1404)
            a = float(self.actual_1404)
            if t == 0:
                return None
            return max(0, min(round(a / t * 100), 150))
        except (TypeError, ValueError):
            return None

    @property
    def progress_pct_1405(self):
        try:
            t = float(self.target_1405)
            a = float(self.actual_1405)
            if t == 0:
                return None
            return max(0, min(round(a / t * 100), 150))
        except (TypeError, ValueError):
            return None

    @property
    def manual_progress_value(self):
        import re
        if not self.progress_1405:
            return None
        text = self.progress_1405
        persian_digits = "۰۱۲۳۴۵۶۷۸۹"
        for i, d in enumerate(persian_digits):
            text = text.replace(d, str(i))
        m = re.search(r"\d+(\.\d+)?", text)
        if not m:
            return None
        try:
            return round(float(m.group()))
        except ValueError:
            return None

    @property
    def progress_color(self):
        p = self.manual_progress_value
        if p is None:
            return "#9aa3ac"
        if p >= 90:
            return "#3E7A52"
        if p >= 60:
            return "#C97A2B"
        return "#B0413E"

    @property
    def domain_color(self):
        return self.DOMAIN_COLOR.get(self.domain, "var(--ink-faint)")


def document_upload_path(instance, filename):
    from django.utils.text import slugify
    import os
    ext = os.path.splitext(filename)[1]
    return f"documents/{instance.category}/{slugify(instance.title) or 'doc'}{ext}"


class Document(models.Model):
    """اسناد بالادستی و دستورالعمل‌های سازمانی."""
    CATEGORY_CHOICES = [
        ("upstream", "سند بالادستی"),
        ("guideline", "دستورالعمل"),
    ]

    title = models.CharField(max_length=250, verbose_name="عنوان سند")
    code = models.CharField(max_length=60, blank=True, verbose_name="کد دستورالعمل/سند")
    category = models.CharField(max_length=15, choices=CATEGORY_CHOICES, default="upstream", verbose_name="دسته")
    description = models.TextField(blank=True, verbose_name="توضیح کوتاه")
    file = models.FileField(upload_to=document_upload_path, verbose_name="فایل")
    approved_at = models.DateField(null=True, blank=True, verbose_name="تاریخ تصویب")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["category", "order", "-uploaded_at"]
        verbose_name = "سند"
        verbose_name_plural = "اسناد و دستورالعمل‌ها"

    def __str__(self):
        return self.title

    @property
    def file_ext(self):
        import os
        return os.path.splitext(self.file.name)[1].lower().lstrip(".")

    @property
    def file_icon(self):
        return {
            "pdf": "fa-file-pdf", "doc": "fa-file-word", "docx": "fa-file-word",
            "xls": "fa-file-excel", "xlsx": "fa-file-excel",
            "ppt": "fa-file-powerpoint", "pptx": "fa-file-powerpoint",
        }.get(self.file_ext, "fa-file")


class StrategicKPI(models.Model):
    """شاخص کلیدی عملکرد وصل به یک هدف مشخص در نقشه استراتژیک (سطح کسب‌وکار)."""
    STATUS_CHOICES = [
        ("on_track", "در مسیر هدف"),
        ("at_risk", "در معرض ریسک"),
        ("off_track", "خارج از مسیر"),
    ]
    TREND_CHOICES = [("up", "صعودی"), ("down", "نزولی"), ("flat", "پایدار")]
    STATUS_COLOR = {"on_track": "#3E7A52", "at_risk": "#C97A2B", "off_track": "#B0413E"}

    objective = models.ForeignKey(
        StrategicObjective, on_delete=models.CASCADE, related_name="kpis", verbose_name="هدف مرتبط",
    )
    name = models.CharField(max_length=200, verbose_name="نام شاخص")
    unit = models.CharField(max_length=60, blank=True, verbose_name="واحد سنجش")
    target = models.CharField(max_length=60, blank=True, verbose_name="مقدار هدف")
    actual = models.CharField(max_length=60, blank=True, verbose_name="مقدار واقعی")
    trend = models.CharField(max_length=10, choices=TREND_CHOICES, default="flat", verbose_name="روند")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="on_track", verbose_name="وضعیت")
    owner = models.CharField(max_length=150, blank=True, verbose_name="مسئول")
    period = models.CharField(max_length=60, blank=True, verbose_name="دوره پایش")
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ["order"]
        verbose_name = "شاخص هدف استراتژیک"
        verbose_name_plural = "شاخص‌های اهداف استراتژیک"

    def __str__(self):
        return f"{self.name} ({self.objective.code})"

    @property
    def status_color(self):
        return self.STATUS_COLOR.get(self.status, "var(--ink-faint)")

    @property
    def progress_pct(self):
        try:
            t = float(self.target)
            a = float(self.actual)
            if t == 0:
                return None
            return max(0, min(round(a / t * 100), 150))
        except (TypeError, ValueError):
            return None


class LegalRequirement(models.Model):
    """بانک الزامات قانونی و سازمانی سایپا یدک."""
    related_pestel = models.ForeignKey(
        "PestelFactor", null=True, blank=True, on_delete=models.SET_NULL,
        related_name="linked_legal_requirements", verbose_name="عامل PESTEL مرتبط",
    )
    title = models.CharField(max_length=400, verbose_name="الزامات قانونی و سازمانی")
    source = models.CharField(max_length=200, blank=True, verbose_name="مأخذ الزام")
    is_legal = models.BooleanField(default=False, verbose_name="قانونی")
    is_organizational = models.BooleanField(default=False, verbose_name="سازمانی")
    is_internal = models.BooleanField(default=False, verbose_name="درون سازمانی")
    is_external = models.BooleanField(default=False, verbose_name="برون سازمانی")
    revision_date = models.CharField(max_length=40, blank=True, verbose_name="تاریخ ویرایش الزام")
    related_documents = models.TextField(blank=True, verbose_name="مستندات داخلی مرتبط")
    scope = models.CharField(max_length=300, blank=True, verbose_name="محل کاربرد")
    risk_text = models.TextField(blank=True, verbose_name="ریسک")
    opportunity_text = models.TextField(blank=True, verbose_name="فرصت")
    notes = models.TextField(blank=True, verbose_name="توضیحات")
    department = models.CharField(max_length=200, blank=True, verbose_name="نام مدیریت/معاونت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["department", "title"]
        verbose_name = "الزام قانونی"
        verbose_name_plural = "بانک الزامات قانونی"

    def __str__(self):
        return self.title


class EnvironmentalFactor(models.Model):
    """بانک شناسایی و امتیازدهی عوامل محیطی تأثیرگذار (ترکیب PESTEL و پنج نیروی پورتر) —
    منبع انتخاب عوامل کلیدی برای ماتریس اثر متقابل."""
    order = models.PositiveSmallIntegerField(default=0, verbose_name="ردیف اصلی")
    category = models.CharField(max_length=150, verbose_name="دسته‌بندی محیط")
    factor_text = models.CharField(max_length=400, verbose_name="شرح عامل تأثیرگذار")
    detail = models.TextField(blank=True, verbose_name="توضیح تفصیلی (راهنمای درک و امتیازدهی)")
    effect_type = models.CharField(max_length=30, blank=True, verbose_name="نوع اثر")
    scoring_guide = models.CharField(max_length=300, blank=True, verbose_name="راهنمای امتیازدهی")
    avg_score = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, verbose_name="میانگین امتیاز")
    freq_high = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="فراوانی اثر بالا (۷-۸)")
    freq_very_high = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="فراوانی اثر بسیار بالا (۹-۱۰)")
    freq_total = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="جمع فراوانی اثرهای بالا")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-avg_score", "order"]
        verbose_name = "عامل محیطی"
        verbose_name_plural = "بانک عوامل محیطی"

    def __str__(self):
        return self.factor_text

    @property
    def score_color(self):
        if self.avg_score is None:
            return "var(--ink-faint)"
        if self.avg_score >= 8:
            return "#B0413E"
        if self.avg_score >= 6:
            return "#C97A2B"
        return "#3E7A52"

    @property
    def linked_cross_impact_factors(self):
        """تطابق متنی با عوامل موجود در ماتریس اثر متقابل (برای نمایش برچسب ردیابی)."""
        if not self.factor_text:
            return []
        needle = self.factor_text.split("(")[0].strip()
        matches = []
        for f in CrossImpactFactor.objects.all():
            hay = f.text.strip()
            if not hay or not needle:
                continue
            if hay in needle or needle in hay:
                matches.append(f)
        return matches

    def _matched_pestel_porter(self):
        """تطابق متنی این عامل با عامل معادلش در PESTEL یا Porter (فقط برای نمایش، نه رابطه‌ی دیتابیسی)."""
        if not self.factor_text:
            return None
        needle = self.factor_text.split("(")[0].strip()
        if not needle:
            return None
        for f in PestelFactor.objects.all():
            hay = f.text.strip()
            if hay and (hay in needle or needle in hay):
                return f
        for f in PorterForce.objects.all():
            hay = f.text.strip()
            if hay and (hay in needle or needle in hay):
                return f
        return None

    @property
    def related_stakeholders_display(self):
        """ذینفعانی که (از طریق عامل معادل در PESTEL یا Porter) به این عامل مرتبط‌اند — فقط نمایشی."""
        match = self._matched_pestel_porter()
        if match is None:
            return []
        if isinstance(match, PestelFactor):
            return list(match.related_stakeholders.all())
        return list(match.linked_stakeholders.all())

    @property
    def related_legal_requirements_display(self):
        """الزامات قانونی‌ای که (از طریق عامل معادل در PESTEL) به این عامل مرتبط‌اند — فقط نمایشی."""
        match = self._matched_pestel_porter()
        if isinstance(match, PestelFactor):
            return list(match.linked_legal_requirements.all())
        return []
