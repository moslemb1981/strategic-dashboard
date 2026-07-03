import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Study, Initiative, Risk, SWOTItem, StrategicObjective, Competitor, PestelFactor,
)
from .forms import (
    StudyForm, InitiativeForm, RiskForm, SWOTItemForm, StrategicObjectiveForm,
    CompetitorForm, PestelFactorForm,
)

logger = logging.getLogger("strategic")


def _has_perm(request, perm):
    """Checks a Django model permission (e.g. 'strategic.add_study').
    Superusers always pass. On failure, flashes a message the user sees."""
    if request.user.has_perm(perm):
        return True
    messages.error(request, "شما اجازه انجام این عملیات را ندارید. برای دسترسی ویرایش با مدیر سیستم هماهنگ کنید.")
    logger.warning("PERMISSION DENIED: user=%s perm=%s", request.user, perm)
    return False


def _log_action(request, action, label):
    logger.info("%s: user=%s item=%r", action, request.user, label)


@login_required
def home(request):
    objectives = list(StrategicObjective.objects.all())
    obj_total = len(objectives)
    obj_score = 0
    if obj_total:
        weight = {"on": 1, "watch": 0.5, "risk": 0}
        obj_score = round(sum(weight.get(o.status, 0) for o in objectives) / obj_total * 100)

    initiatives = list(Initiative.objects.all())
    init_total = len(initiatives)
    init_behind = sum(1 for i in initiatives if i.status == "needs_attention")
    init_on_track = init_total - init_behind
    init_avg_progress = round(sum(i.progress for i in initiatives) / init_total) if init_total else 0

    studies = list(Study.objects.all())
    study_total = len(studies)
    study_done = sum(1 for s in studies if s.status == "done")
    study_pct = round(study_done / study_total * 100) if study_total else 0

    risks = list(Risk.objects.all())
    risk_total = len(risks)
    risk_high = sum(1 for r in risks if r.zone == "red")
    risk_pct = round(risk_high / risk_total * 100) if risk_total else 0

    # فید فعالیت‌های اخیر — از هر ۷ مدل، آخرین رکوردها را ترکیب می‌کند
    activity = []
    for s in Study.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-book", "text": f"مطالعه «{s.title}» ثبت شد", "tag": "کتابخانه مطالعات", "dt": s.created_at})
    for i in Initiative.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-route", "text": f"ابتکار «{i.title}» ثبت شد", "tag": "نقشه راه", "dt": i.created_at})
    for r in Risk.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-triangle-exclamation", "text": f"ریسک «{r.title}» ثبت شد", "tag": "نقشه ریسک", "dt": r.created_at})
    for o in StrategicObjective.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-map", "text": f"هدف «{o.code} — {o.title}» ثبت شد", "tag": "نقشه استراتژیک", "dt": o.created_at})
    for it in SWOTItem.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-table-cells", "text": f"مورد SWOT «{it.text}» ثبت شد", "tag": "SWOT", "dt": it.created_at})
    for c in Competitor.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-chart-line", "text": f"بازیگر «{c.name}» ثبت شد", "tag": "هوش رقابتی", "dt": c.created_at})
    for f in PestelFactor.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-earth-americas", "text": f"عامل «{f.text}» ثبت شد", "tag": "PESTEL", "dt": f.created_at})

    activity.sort(key=lambda a: a["dt"], reverse=True)
    activity = activity[:6]

    return render(request, "strategic/home.html", {
        "active_page": "home",
        "obj_score": obj_score, "obj_total": obj_total,
        "init_total": init_total, "init_on_track": init_on_track, "init_behind": init_behind, "init_avg_progress": init_avg_progress,
        "study_total": study_total, "study_done": study_done, "study_pct": study_pct,
        "risk_total": risk_total, "risk_high": risk_high, "risk_pct": risk_pct,
        "competitor_count": Competitor.objects.count(),
        "pestel_count": PestelFactor.objects.count(),
        "swot_count": SWOTItem.objects.count(),
        "activity": activity,
    })


# ---------------- Research library ----------------

@login_required
def research(request):
    if request.method == "POST":
        if _has_perm(request, "strategic.add_study"):
            form = StudyForm(request.POST)
            if form.is_valid():
                form.save()
                _log_action(request, "CREATE Study", str(form.instance))
                return redirect("strategic:research")
        else:
            form = StudyForm()
    else:
        form = StudyForm()

    studies = Study.objects.all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    if q:
        studies = studies.filter(title__icontains=q)
    if status:
        studies = studies.filter(status=status)

    return render(request, "strategic/research.html", {
        "active_page": "research", "studies": studies, "form": form, "q": q, "status": status,
    })


@login_required
def study_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_study"):
        _obj = get_object_or_404(Study, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE Study", _label)
    return redirect("strategic:research")


# ---------------- Roadmap / initiatives ----------------

@login_required
def roadmap(request):
    if request.method == "POST":
        if _has_perm(request, "strategic.add_initiative"):
            form = InitiativeForm(request.POST)
            if form.is_valid():
                form.save()
                _log_action(request, "CREATE Initiative", str(form.instance))
                return redirect("strategic:roadmap")
        else:
            form = InitiativeForm()
    else:
        form = InitiativeForm()

    initiatives = Initiative.objects.all()
    return render(request, "strategic/roadmap.html", {
        "active_page": "roadmap", "initiatives": initiatives, "form": form,
    })


@login_required
def initiative_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_initiative"):
        _obj = get_object_or_404(Initiative, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE Initiative", _label)
    return redirect("strategic:roadmap")


# ---------------- Market / competitive intelligence ----------------

@login_required
def market(request):
    if request.method == "POST":
        if _has_perm(request, "strategic.add_competitor"):
            form = CompetitorForm(request.POST)
            if form.is_valid():
                form.save()
                _log_action(request, "CREATE Competitor", str(form.instance))
                return redirect("strategic:market")
        else:
            form = CompetitorForm()
    else:
        form = CompetitorForm()

    competitors = Competitor.objects.all()
    return render(request, "strategic/market.html", {
        "active_page": "market", "competitors": competitors, "form": form,
    })


@login_required
def competitor_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_competitor"):
        _obj = get_object_or_404(Competitor, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE Competitor", _label)
    return redirect("strategic:market")


# ---------------- PESTEL ----------------

@login_required
def pestel(request):
    if request.method == "POST":
        if _has_perm(request, "strategic.add_pestelfactor"):
            form = PestelFactorForm(request.POST)
            if form.is_valid():
                form.save()
                _log_action(request, "CREATE PestelFactor", str(form.instance))
                return redirect("strategic:pestel")
        else:
            form = PestelFactorForm()
    else:
        form = PestelFactorForm()

    factors = PestelFactor.objects.all()
    grouped = []
    for key, label in PestelFactor.CATEGORY_CHOICES:
        color, soft, icon = PestelFactor.CATEGORY_STYLE[key]
        grouped.append({
            "key": key, "label": label, "color": color, "soft": soft, "icon": icon,
            "items": [f for f in factors if f.category == key],
        })

    return render(request, "strategic/pestel.html", {
        "active_page": "pestel", "grouped": grouped, "form": form,
    })


@login_required
def pestel_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_pestelfactor"):
        _obj = get_object_or_404(PestelFactor, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE PestelFactor", _label)
    return redirect("strategic:pestel")


# ---------------- Strategic map (BSC) ----------------

PERSPECTIVES = [
    ("financial", "مالی", "var(--primary-soft)", "var(--primary-dark)", 2),
    ("customer", "مشتری", "var(--accent-soft)", "#7A4711", 4),
    ("process", "فرآیندهای داخلی", "var(--success-soft)", "var(--success)", 6),
    ("learning", "یادگیری و رشد", "var(--purple-soft)", "var(--purple)", 8),
]
THEMES = [
    ("operational", "تعالی عملیاتی و کیفیت", "var(--success)", 2),
    ("growth", "رشد بازار و سودآوری", "var(--primary)", 3),
    ("digital", "نوآوری و تحول دیجیتال", "var(--purple)", 4),
]


@login_required
def stratmap(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_strategicobjective" if obj_id else "strategic.add_strategicobjective"
        if _has_perm(request, perm):
            instance = get_object_or_404(StrategicObjective, pk=obj_id) if obj_id else None
            form = StrategicObjectiveForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE StrategicObjective" if obj_id else "CREATE StrategicObjective", str(form.instance))
                return redirect("strategic:stratmap")
        else:
            form = StrategicObjectiveForm()
    else:
        form = StrategicObjectiveForm()

    objectives = list(StrategicObjective.objects.all())

    grid = []
    for p_key, p_label, p_bg, p_color, p_row in PERSPECTIVES:
        cells = []
        for t_key, t_label, t_color, t_col in THEMES:
            cells.append({
                "grid_col": t_col,
                "objectives": [o for o in objectives if o.perspective == p_key and o.theme == t_key],
            })
        grid.append({"label": p_label, "bg": p_bg, "color": p_color, "grid_row": p_row, "cells": cells})

    themes_header = [{"label": l, "color": c} for _, l, c, _ in THEMES]

    return render(request, "strategic/stratmap.html", {
        "active_page": "stratmap", "grid": grid, "themes_header": themes_header, "form": form,
    })


@login_required
def objective_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_strategicobjective"):
        _obj = get_object_or_404(StrategicObjective, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE StrategicObjective", _label)
    return redirect("strategic:stratmap")


# ---------------- SWOT ----------------

@login_required
def swot(request):
    if request.method == "POST":
        if _has_perm(request, "strategic.add_swotitem"):
            form = SWOTItemForm(request.POST)
            if form.is_valid():
                form.save()
                _log_action(request, "CREATE SWOTItem", str(form.instance))
                return redirect("strategic:swot")
        else:
            form = SWOTItemForm()
    else:
        form = SWOTItemForm()

    return render(request, "strategic/swot.html", {
        "active_page": "swot",
        "s_items": SWOTItem.objects.filter(category="s"),
        "w_items": SWOTItem.objects.filter(category="w"),
        "o_items": SWOTItem.objects.filter(category="o"),
        "t_items": SWOTItem.objects.filter(category="t"),
        "form": form,
    })


@login_required
def swot_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_swotitem"):
        _obj = get_object_or_404(SWOTItem, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE SWOTItem", _label)
    return redirect("strategic:swot")


# ---------------- Risk register ----------------

@login_required
def risk(request):
    if request.method == "POST":
        if _has_perm(request, "strategic.add_risk"):
            form = RiskForm(request.POST)
            if form.is_valid():
                form.save()
                _log_action(request, "CREATE Risk", str(form.instance))
                return redirect("strategic:risk")
        else:
            form = RiskForm()
    else:
        form = RiskForm()

    risks = list(Risk.objects.all())

    matrix = []
    for impact in range(4, 0, -1):
        row = []
        for likelihood in range(1, 5):
            s = likelihood + impact
            zone = "green" if s <= 4 else ("amber" if s <= 6 else "red")
            items = [r.title for r in risks if r.likelihood == likelihood and r.impact == impact]
            row.append({"zone": zone, "items": items})
        matrix.append(row)

    risks_sorted = sorted(risks, key=lambda r: -(r.likelihood + r.impact))

    return render(request, "strategic/risk.html", {
        "active_page": "risk", "matrix": matrix, "risks": risks_sorted, "form": form,
    })


@login_required
def risk_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_risk"):
        _obj = get_object_or_404(Risk, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE Risk", _label)
    return redirect("strategic:risk")
