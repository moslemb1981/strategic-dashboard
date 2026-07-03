from django import forms
from .models import Study, Initiative, Risk, SWOTItem, StrategicObjective


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
    class Meta:
        model = Initiative
        fields = ["title", "owner", "start_date", "end_date", "progress", "status"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: دیجیتالی‌سازی گزارش‌های ماهانه"}),
            "owner": forms.TextInput(attrs={"placeholder": "مثلاً: واحد مطالعات"}),
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "progress": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }


class RiskForm(forms.ModelForm):
    class Meta:
        model = Risk
        fields = ["title", "owner", "likelihood", "impact", "mitigation"]
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: افزایش شدید نرخ ارز"}),
            "owner": forms.TextInput(attrs={"placeholder": "مثلاً: مدیریت مالی"}),
            "mitigation": forms.Textarea(attrs={"rows": 2, "placeholder": "اقدام کاهشی پیشنهادی"}),
        }


class SWOTItemForm(forms.ModelForm):
    class Meta:
        model = SWOTItem
        fields = ["category", "text", "impact"]
        widgets = {"category": forms.HiddenInput()}


class StrategicObjectiveForm(forms.ModelForm):
    class Meta:
        model = StrategicObjective
        fields = ["code", "perspective", "theme", "title", "kpi", "status", "order"]
        widgets = {
            "code": forms.TextInput(attrs={"placeholder": "مثلاً: F1"}),
            "title": forms.TextInput(attrs={"placeholder": "عنوان هدف استراتژیک"}),
            "kpi": forms.TextInput(attrs={"placeholder": "مثلاً: رشد ۱۲٪ حاشیه سود ناخالص"}),
        }
