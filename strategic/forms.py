import datetime
from django import forms
from .models import (
    Study, Initiative, Risk, SWOTItem, TOWSStrategy, StrategicObjective, Competitor, PestelFactor,
    StrategyTheme, BusinessUnit, PorterForce, McKinsey7S, ValueChainActivity, Stakeholder, CrossImpactFactor, Scenario, ScenarioAxes, CompanyObjective, CompanyKPI, Document, StrategicKPI, LegalRequirement, EnvironmentalFactor,
)
from .jalali_utils import jalali_str_to_gregorian, gregorian_to_jalali_str


class JalaliDateField(forms.CharField):
    """A form field that displays/accepts Jalali (Persian) dates but produces a
    real Python date object for the model's DateField (which stays Gregorian
    internally — required for correct date math and the Gantt chart)."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", forms.TextInput(attrs={
            "class": "jalali-date-input", "placeholder": "مثلاً ۱۴۰۵/۰۴/۱۲", "autocomplete": "off",
        }))
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            return None
        try:
            return jalali_str_to_gregorian(value)
        except ValueError as e:
            raise forms.ValidationError(str(e))

    def prepare_value(self, value):
        if isinstance(value, (datetime.date, datetime.datetime)):
            return gregorian_to_jalali_str(value)
        return value


class StudyForm(forms.ModelForm):
    class Meta:
        model = Study
        fields = ["title", "field", "date", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: تحلیل روند قیمت مواد اولیه"}),
            "field": forms.TextInput(attrs={"placeholder": "مثلاً: مطالعه بازار"}),
            "date": forms.TextInput(attrs={
                "class": "jalali-date-input",
                "placeholder": "انتخاب تاریخ",
                "readonly": "readonly",
            }),
        }


class InitiativeForm(forms.ModelForm):
    start_date = JalaliDateField(label="تاریخ شروع")
    end_date = JalaliDateField(label="تاریخ پایان")

    class Meta:
        model = Initiative
        fields = ["title", "owner", "start_date", "end_date", "progress", "status", "objectives"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: دیجیتالی‌سازی گزارش‌های ماهانه"}),
            "owner": forms.TextInput(attrs={"placeholder": "مثلاً: واحد مطالعات"}),
            "progress": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "objectives": forms.SelectMultiple(attrs={"size": 8}),
        }

    def __init__(self, *args, business_unit=None, **kwargs):
        super().__init__(*args, **kwargs)
        bu = business_unit or (self.instance.business_unit if self.instance and self.instance.pk else None)
        self.fields["objectives"].queryset = (
            StrategicObjective.objects.filter(business_unit=bu) if bu else StrategicObjective.objects.none()
        )
        self.fields["objectives"].required = False


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            "title", "cause", "consequence", "owner", "category",
            "inherent_likelihood", "inherent_impact",
            "likelihood", "impact",
            "target_likelihood", "target_impact",
            "response_strategy", "trend", "kri", "mitigation", "linked_objective", "related_scenario",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: افزایش شدید نرخ ارز"}),
            "cause": forms.Textarea(attrs={"rows": 2, "placeholder": "منشأ/علت بروز ریسک"}),
            "consequence": forms.Textarea(attrs={"rows": 2, "placeholder": "هر خط یک پیامد"}),
            "owner": forms.TextInput(attrs={"placeholder": "مثلاً: مدیریت مالی"}),
            "kri": forms.TextInput(attrs={"placeholder": "مثلاً: نرخ تسعیر ماهانه ارز"}),
            "mitigation": forms.Textarea(attrs={"rows": 3, "placeholder": "هر خط یک اقدام کنترلی"}),
            "related_scenario": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["linked_objective"].required = False
        self.fields["linked_objective"].empty_label = "— بدون ارتباط —"
        self.fields["related_scenario"].required = False


class SWOTItemForm(forms.ModelForm):
    class Meta:
        model = SWOTItem
        fields = [
            "category", "text", "weight",
            "source_pestel", "source_porter", "source_stakeholder", "source_scenario",
            "source_7s", "source_value_chain",
        ]
        widgets = {
            "category": forms.HiddenInput(),
            "source_pestel": forms.RadioSelect(),
            "source_porter": forms.RadioSelect(),
            "source_stakeholder": forms.RadioSelect(),
            "source_scenario": forms.RadioSelect(),
            "source_7s": forms.RadioSelect(),
            "source_value_chain": forms.RadioSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ["source_pestel", "source_porter", "source_stakeholder", "source_scenario", "source_7s", "source_value_chain"]:
            self.fields[f].required = False


class TOWSStrategyForm(forms.ModelForm):
    CATEGORY_LETTERS = {"so": ["s", "o"], "st": ["s", "t"], "wo": ["w", "o"], "wt": ["w", "t"]}

    class Meta:
        model = TOWSStrategy
        fields = ["category", "text", "order", "source_items"]
        widgets = {
            "category": forms.HiddenInput(),
            "source_items": forms.SelectMultiple(attrs={"size": 6}),
        }

    def __init__(self, *args, business_unit=None, **kwargs):
        super().__init__(*args, **kwargs)
        bu = business_unit or (self.instance.business_unit if self.instance and self.instance.pk else None)
        cat = None
        if self.data:
            cat = self.data.get("category")
        if not cat and self.instance and self.instance.pk:
            cat = self.instance.category
        letters = self.CATEGORY_LETTERS.get(cat, [])
        qs = SWOTItem.objects.filter(business_unit=bu, category__in=letters) if (bu and letters) else SWOTItem.objects.none()
        self.fields["source_items"].queryset = qs
        self.fields["source_items"].required = False


class StrategicObjectiveForm(forms.ModelForm):
    class Meta:
        model = StrategicObjective
        fields = ["code", "perspective", "theme", "title", "kpi", "status", "order", "feeds_into", "source_tows", "linked_kpis"]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "مثلاً: F1"}),
            "title": forms.TextInput(attrs={"placeholder": "عنوان هدف استراتژیک"}),
            "kpi": forms.TextInput(attrs={"placeholder": "مثلاً: رشد ۱۲٪ حاشیه سود ناخالص"}),
            "feeds_into": forms.CheckboxSelectMultiple(),
            "linked_kpis": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, business_unit=None, **kwargs):
        super().__init__(*args, **kwargs)
        bu = business_unit or (self.instance.business_unit if self.instance and self.instance.pk else None)

        feeds_qs = StrategicObjective.objects.filter(business_unit=bu) if bu else StrategicObjective.objects.none()
        if self.instance and self.instance.pk:
            feeds_qs = feeds_qs.exclude(pk=self.instance.pk)
        self.fields["feeds_into"].queryset = feeds_qs
        self.fields["feeds_into"].required = False
        self.fields["feeds_into"].label_from_instance = lambda obj: f"{obj.code} — {obj.title}"

        self.fields["theme"].queryset = StrategyTheme.objects.filter(business_unit=bu) if bu else StrategyTheme.objects.none()
        self.fields["theme"].required = False

        tows_qs = TOWSStrategy.objects.filter(business_unit=bu) if bu else TOWSStrategy.objects.none()
        self.fields["source_tows"] = forms.ModelChoiceField(
            queryset=tows_qs, required=False, label="راهبرد TOWS مبنا (اختیاری)",
            widget=forms.RadioSelect(),
        )
        self.fields["source_tows"].label_from_instance = lambda obj: obj.text

        self.fields["linked_kpis"].queryset = CompanyKPI.objects.all()
        self.fields["linked_kpis"].required = False
        self.fields["linked_kpis"].label_from_instance = lambda obj: f"{obj.code} — {obj.name}"


class StrategyThemeForm(forms.ModelForm):
    class Meta:
        model = StrategyTheme
        fields = ["business_unit", "name", "order"]
        widgets = {
            "business_unit": forms.HiddenInput(),
            "name": forms.TextInput(attrs={"placeholder": "مثلاً: تعالی عملیاتی و کیفیت"}),
        }


class CompetitorForm(forms.ModelForm):
    class Meta:
        model = Competitor
        fields = ["name", "market_share", "strengths", "weaknesses", "recent_move", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "مثلاً: تولیدکنندگان داخلی OEM"}),
            "market_share": forms.NumberInput(attrs={"min": 0, "max": 100}),
            "strengths": forms.Textarea(attrs={"rows": 3, "placeholder": "هر خط یک نقطه قوت"}),
            "weaknesses": forms.Textarea(attrs={"rows": 3, "placeholder": "هر خط یک نقطه ضعف"}),
            "recent_move": forms.TextInput(attrs={"placeholder": "مثلاً: افزایش ظرفیت تولید در فصل اخیر"}),
        }


class PestelFactorForm(forms.ModelForm):
    class Meta:
        model = PestelFactor
        fields = [
            "category", "kind", "text", "order",
            "impact_level", "probability", "uncertainty", "horizon", "trend",
        ]
        widgets = {
            "text": forms.TextInput(attrs={"placeholder": "متن عامل / فرصت / تهدید"}),
        }


class PorterForceForm(forms.ModelForm):
    class Meta:
        model = PorterForce
        fields = ["level", "reasons", "conclusion"]
        widgets = {
            "reasons": forms.Textarea(attrs={"rows": 5, "placeholder": "هر خط یک دلیل"}),
            "conclusion": forms.Textarea(attrs={"rows": 2, "placeholder": "نتیجه‌گیری"}),
        }


class McKinsey7SForm(forms.ModelForm):
    class Meta:
        model = McKinsey7S
        fields = ["status", "strengths", "weaknesses"]
        widgets = {
            "status": forms.Textarea(attrs={"rows": 3, "placeholder": "وضعیت فعلی این مؤلفه"}),
            "strengths": forms.Textarea(attrs={"rows": 3, "placeholder": "هر خط یک نقطه قوت"}),
            "weaknesses": forms.Textarea(attrs={"rows": 3, "placeholder": "هر خط یک نقطه ضعف/ریسک"}),
        }


class ValueChainActivityForm(forms.ModelForm):
    class Meta:
        model = ValueChainActivity
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(attrs={"rows": 6, "placeholder": "هر خط یک اقدام/محتوا"}),
        }


class StakeholderForm(forms.ModelForm):
    class Meta:
        model = Stakeholder
        fields = [
            "department", "name", "channel", "need", "need_flag", "expectation_flag",
            "risk_text", "risk_occurrence", "risk_severity", "risk_detection", "risk_score",
            "opportunity_text", "opportunity_importance", "opportunity_impact", "opportunity_score",
            "action", "domain", "status",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "مثلاً: شبکه نمایندگی‌ها"}),
            "department": forms.TextInput(attrs={"placeholder": "مثلاً: مدیریت آپشن"}),
            "channel": forms.TextInput(attrs={"placeholder": "مثلاً: مکاتبات، تلفن"}),
            "domain": forms.TextInput(attrs={"placeholder": "مثلاً: فرآیند"}),
            "need": forms.Textarea(attrs={"rows": 2}),
            "risk_text": forms.Textarea(attrs={"rows": 2}),
            "opportunity_text": forms.Textarea(attrs={"rows": 2}),
            "action": forms.Textarea(attrs={"rows": 2}),
        }


class CrossImpactFactorForm(forms.ModelForm):
    class Meta:
        model = CrossImpactFactor
        fields = ["text", "quadrant", "order", "linked_pestel"]
        widgets = {
            "text": forms.TextInput(attrs={"placeholder": "نام عامل"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["linked_pestel"].required = False


class ScenarioForm(forms.ModelForm):
    class Meta:
        model = Scenario
        fields = ["title", "narrative", "is_selected"]
        widgets = {
            "narrative": forms.Textarea(attrs={"rows": 10, "placeholder": "روایت کامل سناریو"}),
        }


class ScenarioAxesForm(forms.ModelForm):
    class Meta:
        model = ScenarioAxes
        fields = ["axis1_name", "axis1_positive", "axis1_negative", "axis2_name", "axis2_positive", "axis2_negative"]


class CompanyObjectiveForm(forms.ModelForm):
    class Meta:
        model = CompanyObjective
        fields = ["code", "group_title", "title", "description", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
        }


class CompanyKPIForm(forms.ModelForm):
    class Meta:
        model = CompanyKPI
        fields = [
            "code", "domain", "name", "unit", "target_1404", "actual_1404",
            "target_1405", "actual_1405", "progress_1405", "objectives", "is_monitoring", "notes", "order",
        ]
        widgets = {
            "objectives": forms.CheckboxSelectMultiple(),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["objectives"].required = False
        self.fields["objectives"].queryset = CompanyObjective.objects.all()


class DocumentForm(forms.ModelForm):
    approved_at = JalaliDateField(required=False, label="تاریخ تصویب")

    class Meta:
        model = Document
        fields = ["title", "code", "category", "description", "file", "approved_at", "order"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
            "code": forms.TextInput(attrs={"placeholder": "مثلاً: DOC-1405-14"}),
        }


class StrategicKPIForm(forms.ModelForm):
    class Meta:
        model = StrategicKPI
        fields = ["name", "unit", "target", "actual", "trend", "status", "owner", "period", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "مثلاً: حاشیه سود ناخالص"}),
            "owner": forms.TextInput(attrs={"placeholder": "مثلاً: معاونت مالی"}),
            "period": forms.TextInput(attrs={"placeholder": "مثلاً: فصلی"}),
        }


class LegalRequirementForm(forms.ModelForm):
    class Meta:
        model = LegalRequirement
        fields = [
            "title", "source", "is_legal", "is_organizational", "revision_date",
            "related_documents", "scope", "risk_text", "opportunity_text", "notes", "department",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: دستورالعمل تأمین اضطراری قطعات"}),
            "source": forms.TextInput(attrs={"placeholder": "مثلاً: شرکت سایپا، استاندارد"}),
            "revision_date": forms.TextInput(attrs={"placeholder": "مثلاً: ۱۴۰۴/۰۷/۰۲ یا ۲۰۱۵"}),
            "scope": forms.TextInput(attrs={"placeholder": "مثلاً: سازمان، سایپا یدک"}),
            "department": forms.TextInput(attrs={"placeholder": "مثلاً: معاونت بازرگانی"}),
            "related_documents": forms.Textarea(attrs={"rows": 2}),
            "risk_text": forms.Textarea(attrs={"rows": 2}),
            "opportunity_text": forms.Textarea(attrs={"rows": 2}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class EnvironmentalFactorForm(forms.ModelForm):
    class Meta:
        model = EnvironmentalFactor
        fields = [
            "category", "factor_text", "detail", "effect_type", "scoring_guide",
            "avg_score", "freq_high", "freq_very_high", "freq_total", "order",
        ]
        widgets = {
            "category": forms.TextInput(attrs={"placeholder": "مثلاً: عوامل اقتصادی، قدرت چانه‌زنی تأمین‌کنندگان"}),
            "factor_text": forms.TextInput(attrs={"placeholder": "شرح عامل تأثیرگذار"}),
            "detail": forms.Textarea(attrs={"rows": 3}),
            "effect_type": forms.TextInput(attrs={"placeholder": "فرصت / تهدید / فرصت‌تهدید"}),
            "scoring_guide": forms.TextInput(attrs={"placeholder": "راهنمای امتیازدهی"}),
        }
