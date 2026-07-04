import datetime
from django import forms
from .models import (
    Study, Initiative, Risk, SWOTItem, TOWSStrategy, StrategicObjective, Competitor, PestelFactor,
    StrategyTheme, BusinessUnit,
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
        fields = ["title", "owner", "start_date", "end_date", "progress", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: دیجیتالی‌سازی گزارش‌های ماهانه"}),
            "owner": forms.TextInput(attrs={"placeholder": "مثلاً: واحد مطالعات"}),
            "progress": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = [
            "title", "owner", "category",
            "inherent_likelihood", "inherent_impact",
            "likelihood", "impact",
            "target_likelihood", "target_impact",
            "response_strategy", "trend", "kri", "mitigation", "linked_objective",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: افزایش شدید نرخ ارز"}),
            "owner": forms.TextInput(attrs={"placeholder": "مثلاً: مدیریت مالی"}),
            "kri": forms.TextInput(attrs={"placeholder": "مثلاً: نرخ تسعیر ماهانه ارز"}),
            "mitigation": forms.Textarea(attrs={"rows": 3, "placeholder": "هر خط یک اقدام کنترلی"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["linked_objective"].required = False
        self.fields["linked_objective"].empty_label = "— بدون ارتباط —"


class SWOTItemForm(forms.ModelForm):
    class Meta:
        model = SWOTItem
        fields = ["category", "text", "weight"]
        widgets = {"category": forms.HiddenInput()}


class TOWSStrategyForm(forms.ModelForm):
    class Meta:
        model = TOWSStrategy
        fields = ["category", "text", "order"]
        widgets = {"category": forms.HiddenInput()}


class StrategicObjectiveForm(forms.ModelForm):
    class Meta:
        model = StrategicObjective
        fields = ["code", "perspective", "theme", "title", "kpi", "status", "order", "feeds_into"]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "مثلاً: F1"}),
            "title": forms.TextInput(attrs={"placeholder": "عنوان هدف استراتژیک"}),
            "kpi": forms.TextInput(attrs={"placeholder": "مثلاً: رشد ۱۲٪ حاشیه سود ناخالص"}),
            "feeds_into": forms.SelectMultiple(attrs={"size": 6}),
        }

    def __init__(self, *args, business_unit=None, **kwargs):
        super().__init__(*args, **kwargs)
        bu = business_unit or (self.instance.business_unit if self.instance and self.instance.pk else None)

        feeds_qs = StrategicObjective.objects.filter(business_unit=bu) if bu else StrategicObjective.objects.none()
        if self.instance and self.instance.pk:
            feeds_qs = feeds_qs.exclude(pk=self.instance.pk)
        self.fields["feeds_into"].queryset = feeds_qs
        self.fields["feeds_into"].required = False

        self.fields["theme"].queryset = StrategyTheme.objects.filter(business_unit=bu) if bu else StrategyTheme.objects.none()
        self.fields["theme"].required = False


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
        fields = ["category", "text", "order"]
        widgets = {
            "text": forms.TextInput(attrs={"placeholder": "عامل محیطی جدید"}),
        }
