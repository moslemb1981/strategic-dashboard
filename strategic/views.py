from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Study, Initiative, Risk, SWOTItem, StrategicObjective
from .forms import StudyForm, InitiativeForm, RiskForm, SWOTItemForm, StrategicObjectiveForm


@login_required
def home(request):
    return render(request, "strategic/home.html", {"active_page": "home"})


@login_required
def research(request):
    if request.method == "POST":
        form = StudyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("strategic:research")
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
        "active_page": "research",
        "studies": studies,
        "form": form,
        "q": q,
        "status": status,
    })


@login_required
def study_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(Study, pk=pk).delete()
    return redirect("strategic:research")


@login_required
def roadmap(request):
    if request.method == "POST":
        form = InitiativeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("strategic:roadmap")
    else:
        form = InitiativeForm()

    initiatives = Initiative.objects.all()
    return render(request, "strategic/roadmap.html", {
        "active_page": "roadmap",
        "initiatives": initiatives,
        "form": form,
    })


@login_required
def initiative_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(Initiative, pk=pk).delete()
    return redirect("strategic:roadmap")


@login_required
def market(request):
    return render(request, "strategic/market.html", {"active_page": "market"})


@login_required
def pestel(request):
    return render(request, "strategic/pestel.html", {"active_page": "pestel"})


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
        instance = get_object_or_404(StrategicObjective, pk=obj_id) if obj_id else None
        form = StrategicObjectiveForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            return redirect("strategic:stratmap")
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
        "active_page": "stratmap",
        "grid": grid,
        "themes_header": themes_header,
        "form": form,
    })


@login_required
def objective_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(StrategicObjective, pk=pk).delete()
    return redirect("strategic:stratmap")


@login_required
def swot(request):
    if request.method == "POST":
        form = SWOTItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("strategic:swot")
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
    if request.method == "POST":
        get_object_or_404(SWOTItem, pk=pk).delete()
    return redirect("strategic:swot")


@login_required
def risk(request):
    if request.method == "POST":
        form = RiskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("strategic:risk")
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
        "active_page": "risk",
        "matrix": matrix,
        "risks": risks_sorted,
        "form": form,
    })


@login_required
def risk_delete(request, pk):
    if request.method == "POST":
        get_object_or_404(Risk, pk=pk).delete()
    return redirect("strategic:risk")
