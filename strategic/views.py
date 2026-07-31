import logging
import re
import io

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import FileResponse, Http404, HttpResponse
from django.urls import reverse
from django.db.models import Q

from .models import (
    Study, Initiative, Risk, SWOTItem, TOWSStrategy, StrategicObjective, Competitor, PestelFactor,
    BusinessUnit, StrategyTheme, PorterForce, OrgIdentity, OrgValue, QualityPolicyPoint, McKinsey7S,
    ValueChainActivity, Stakeholder, CrossImpactFactor, CrossImpactLink, Scenario, ScenarioAxes,
    CompanyObjective, CompanyKPI, Document, StrategicKPI,
)
from .forms import (
    StudyForm, InitiativeForm, RiskForm, SWOTItemForm, TOWSStrategyForm, StrategicObjectiveForm,
    CompetitorForm, PestelFactorForm, StrategyThemeForm, PorterForceForm, McKinsey7SForm, ValueChainActivityForm,
    StakeholderForm, CrossImpactFactorForm, ScenarioForm, ScenarioAxesForm, CompanyObjectiveForm, CompanyKPIForm, DocumentForm,
    StrategicKPIForm,
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
    # برای کاربر بدون‌لاگین، موارد ریسک و SWOT (حساس) از فید حذف می‌شوند
    activity = []
    for s in Study.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-book", "text": f"مطالعه «{s.title}» ثبت شد", "tag": "کتابخانه مطالعات", "dt": s.created_at})
    for i in Initiative.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-route", "text": f"ابتکار «{i.title}» ثبت شد", "tag": "نقشه راه", "dt": i.created_at})
    if request.user.is_authenticated:
        for r in Risk.objects.order_by("-created_at")[:5]:
            activity.append({"icon": "fa-triangle-exclamation", "text": f"ریسک «{r.title}» ثبت شد", "tag": "نقشه ریسک", "dt": r.created_at})
    for o in StrategicObjective.objects.order_by("-created_at")[:5]:
        activity.append({"icon": "fa-map", "text": f"هدف «{o.code} — {o.title}» ثبت شد", "tag": "نقشه استراتژیک", "dt": o.created_at})
    if request.user.is_authenticated:
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
        "cross_impact_count": CrossImpactFactor.objects.count(),
        "scenario_selected": Scenario.objects.filter(is_selected=True).first(),
        "company_objective_count": CompanyObjective.objects.count(),
        "company_kpi_count": CompanyKPI.objects.count(),
        "document_count": Document.objects.count(),
        "stakeholder_count": Stakeholder.objects.count(),
        "porter_count": PorterForce.objects.count(),
        "mckinsey7s_count": McKinsey7S.objects.count(),
        "value_chain_count": ValueChainActivity.objects.count(),
        "swot_count": SWOTItem.objects.count(),
        "activity": activity,
    })


# ---------------- Research library ----------------

def research(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_study" if obj_id else "strategic.add_study"
        if _has_perm(request, perm):
            instance = get_object_or_404(Study, pk=obj_id) if obj_id else None
            form = StudyForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE Study" if obj_id else "CREATE Study", str(form.instance))
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


# ---------------- ذینفعان ----------------

def stakeholders(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_stakeholder" if obj_id else "strategic.add_stakeholder"
        if _has_perm(request, perm):
            instance = get_object_or_404(Stakeholder, pk=obj_id) if obj_id else None
            form = StakeholderForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE Stakeholder" if obj_id else "CREATE Stakeholder", str(form.instance))
                return redirect("strategic:stakeholders")
        else:
            form = StakeholderForm()
    else:
        form = StakeholderForm()

    items = Stakeholder.objects.all().prefetch_related("swot_items__business_unit")
    q = request.GET.get("q", "").strip()
    dept = request.GET.get("dept", "").strip()
    if q:
        items = items.filter(
            Q(name__icontains=q) | Q(need__icontains=q) |
            Q(risk_text__icontains=q) | Q(opportunity_text__icontains=q)
        )
    if dept:
        items = items.filter(department=dept)

    all_items = list(Stakeholder.objects.all())
    top_risks = sorted([i for i in all_items if i.risk_score], key=lambda i: i.risk_score, reverse=True)[:6]
    top_opportunities = sorted(
        [i for i in all_items if i.opportunity_score], key=lambda i: i.opportunity_score, reverse=True
    )[:6]
    departments = sorted({i.department for i in all_items if i.department})

    return render(request, "strategic/stakeholders.html", {
        "active_page": "stakeholders", "items": items, "form": form, "q": q, "dept": dept,
        "departments": departments, "top_risks": top_risks, "top_opportunities": top_opportunities,
        "total_count": len(all_items),
    })


@login_required
def stakeholder_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_stakeholder"):
        obj = get_object_or_404(Stakeholder, pk=pk)
        label = str(obj)
        obj.delete()
        _log_action(request, "DELETE Stakeholder", label)
    return redirect("strategic:stakeholders")


@login_required
def study_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_study"):
        _obj = get_object_or_404(Study, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE Study", _label)
    return redirect("strategic:research")


# ---------------- Roadmap / initiatives ----------------

def roadmap(request):
    business_units = list(BusinessUnit.objects.all())
    bu_id = request.POST.get("business_unit") or request.GET.get("bu")
    current_bu = None
    if bu_id:
        current_bu = next((b for b in business_units if str(b.pk) == str(bu_id)), None)
    if not current_bu and business_units:
        current_bu = business_units[0]

    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_initiative" if obj_id else "strategic.add_initiative"
        if _has_perm(request, perm):
            instance = get_object_or_404(Initiative, pk=obj_id) if obj_id else None
            form = InitiativeForm(request.POST, instance=instance, business_unit=current_bu)
            if form.is_valid():
                obj = form.save(commit=False)
                if not obj_id and current_bu:
                    obj.business_unit = current_bu
                obj.save()
                form.save_m2m()
                _log_action(request, "UPDATE Initiative" if obj_id else "CREATE Initiative", str(obj))
                bu_param = f"?bu={current_bu.pk}" if current_bu else ""
                return redirect(reverse("strategic:roadmap") + bu_param)
        else:
            form = InitiativeForm(business_unit=current_bu)
    else:
        form = InitiativeForm(business_unit=current_bu)

    initiatives = (
        Initiative.objects.filter(business_unit=current_bu).prefetch_related("objectives")
        if current_bu else Initiative.objects.none()
    )
    return render(request, "strategic/roadmap.html", {
        "active_page": "roadmap", "initiatives": initiatives, "form": form,
        "business_units": business_units, "current_bu": current_bu,
    })


@login_required
def initiative_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_initiative"):
        _obj = get_object_or_404(Initiative, pk=pk)
        _label = str(_obj)
        bu_pk = _obj.business_unit_id
        _obj.delete()
        _log_action(request, "DELETE Initiative", _label)
        if bu_pk:
            return redirect(reverse("strategic:roadmap") + f"?bu={bu_pk}")
    return redirect("strategic:roadmap")


# ---------------- Market / competitive intelligence ----------------

def market(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_competitor" if obj_id else "strategic.add_competitor"
        if _has_perm(request, perm):
            instance = get_object_or_404(Competitor, pk=obj_id) if obj_id else None
            form = CompetitorForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE Competitor" if obj_id else "CREATE Competitor", str(form.instance))
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

def pestel(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_pestelfactor" if obj_id else "strategic.add_pestelfactor"
        if _has_perm(request, perm):
            instance = get_object_or_404(PestelFactor, pk=obj_id) if obj_id else None
            form = PestelFactorForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE PestelFactor" if obj_id else "CREATE PestelFactor", str(form.instance))
                return redirect("strategic:pestel")
        else:
            form = PestelFactorForm()
    else:
        form = PestelFactorForm()

    LETTERS = {"political": "P", "economic": "E", "social": "S",
               "technological": "T", "environmental": "E", "legal": "L"}

    factors = PestelFactor.objects.all().prefetch_related("swot_items__business_unit")
    grouped = []
    for key, label in PestelFactor.CATEGORY_CHOICES:
        color, soft, icon = PestelFactor.CATEGORY_STYLE[key]
        cat_items = [f for f in factors if f.category == key]
        grouped.append({
            "key": key, "label": label, "color": color, "soft": soft, "icon": icon,
            "letter": LETTERS[key],
            "factors": [f for f in cat_items if f.kind == "factor"],
            "opportunities": [f for f in cat_items if f.kind == "opportunity"],
            "threats": [f for f in cat_items if f.kind == "threat"],
            "summary": cat_items[:6],
        })

    top_factors = sorted(factors, key=lambda f: f.priority_score, reverse=True)[:8]

    return render(request, "strategic/pestel.html", {
        "active_page": "pestel", "grouped": grouped, "form": form, "top_factors": top_factors,
    })


@login_required
def pestel_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_pestelfactor"):
        _obj = get_object_or_404(PestelFactor, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE PestelFactor", _label)
    return redirect("strategic:pestel")


# ---------------- تحلیل اثرات متقابل (MICMAC) ----------------

def cross_impact(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_crossimpactfactor" if obj_id else "strategic.add_crossimpactfactor"
        if _has_perm(request, perm):
            instance = get_object_or_404(CrossImpactFactor, pk=obj_id) if obj_id else None
            form = CrossImpactFactorForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE CrossImpactFactor" if obj_id else "CREATE CrossImpactFactor", str(form.instance))
                return redirect("strategic:cross_impact")
        else:
            form = CrossImpactFactorForm()
    else:
        form = CrossImpactFactorForm()

    factors = list(CrossImpactFactor.objects.all())
    quadrants = {key: [] for key, _ in CrossImpactFactor.QUADRANT_CHOICES}
    for f in factors:
        quadrants[f.quadrant].append(f)

    return render(request, "strategic/cross_impact.html", {
        "active_page": "cross_impact", "quadrants": quadrants, "form": form,
        "pestel_factors": PestelFactor.objects.all(),
    })


@login_required
def cross_impact_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_crossimpactfactor"):
        obj = get_object_or_404(CrossImpactFactor, pk=pk)
        label = str(obj)
        obj.delete()
        _log_action(request, "DELETE CrossImpactFactor", label)
    return redirect("strategic:cross_impact")


def _compute_influence_dependence(factors):
    """برای هر عامل، اثرگذاری (مجموع سطر) و وابستگی (مجموع ستون) را از روی ماتریس مستقیم حساب می‌کند."""
    links = {(l.from_factor_id, l.to_factor_id): l.score for l in CrossImpactLink.objects.all()}
    results = []
    for f in factors:
        influence = sum(links.get((f.pk, other.pk), 0) for other in factors if other.pk != f.pk)
        dependence = sum(links.get((other.pk, f.pk), 0) for other in factors if other.pk != f.pk)
        results.append({"factor": f, "influence": influence, "dependence": dependence})
    return results


def _suggest_quadrant(influence, dependence, median_influence, median_dependence):
    if influence >= median_influence and dependence < median_dependence:
        return "driver"
    if influence >= median_influence and dependence >= median_dependence:
        return "relay"
    if influence < median_influence and dependence < median_dependence:
        return "watch"
    return "resultant"


@login_required
def cross_impact_matrix(request):
    factors = list(CrossImpactFactor.objects.all().order_by("quadrant", "order"))

    if request.method == "POST" and _has_perm(request, "strategic.change_crossimpactfactor"):
        action = request.POST.get("action")
        if action == "save_matrix":
            for f in factors:
                for g in factors:
                    if f.pk == g.pk:
                        continue
                    key = f"score_{f.pk}_{g.pk}"
                    val = request.POST.get(key)
                    if val is not None and val != "":
                        CrossImpactLink.objects.update_or_create(
                            from_factor=f, to_factor=g, defaults={"score": int(val)},
                        )
            _log_action(request, "UPDATE CrossImpactLink matrix", "ماتریس اثرات مستقیم به‌روزرسانی شد")
            return redirect("strategic:cross_impact_matrix")

        elif action == "apply_suggestions":
            results = _compute_influence_dependence(factors)
            influences = sorted(r["influence"] for r in results)
            dependences = sorted(r["dependence"] for r in results)
            n = len(results)
            median_influence = influences[n // 2] if n else 0
            median_dependence = dependences[n // 2] if n else 0
            for r in results:
                suggested = _suggest_quadrant(r["influence"], r["dependence"], median_influence, median_dependence)
                r["factor"].quadrant = suggested
                r["factor"].save(update_fields=["quadrant"])
            _log_action(request, "APPLY CrossImpact suggestions", "پیشنهادهای محاسبه‌شده اعمال شد")
            return redirect("strategic:cross_impact")

    results = _compute_influence_dependence(factors)
    influences = sorted(r["influence"] for r in results)
    dependences = sorted(r["dependence"] for r in results)
    n = len(results)
    median_influence = influences[n // 2] if n else 0
    median_dependence = dependences[n // 2] if n else 0
    for r in results:
        r["suggested"] = _suggest_quadrant(r["influence"], r["dependence"], median_influence, median_dependence)
        r["suggested_label"] = dict(CrossImpactFactor.QUADRANT_CHOICES)[r["suggested"]]
        r["current_label"] = dict(CrossImpactFactor.QUADRANT_CHOICES)[r["factor"].quadrant]
        r["changed"] = r["suggested"] != r["factor"].quadrant

    links = {(l.from_factor_id, l.to_factor_id): l.score for l in CrossImpactLink.objects.all()}
    matrix_rows = []
    for f in factors:
        cells = []
        for g in factors:
            if f.pk == g.pk:
                cells.append({"to_factor": g, "is_diag": True, "score": None})
            else:
                cells.append({"to_factor": g, "is_diag": False, "score": links.get((f.pk, g.pk), 0)})
        matrix_rows.append({"from_factor": f, "cells": cells})

    return render(request, "strategic/cross_impact_matrix.html", {
        "active_page": "cross_impact", "factors": factors, "results": results, "matrix_rows": matrix_rows,
    })


# ---------------- Porter's Five Forces ----------------

def porter(request):
    # مطمئن می‌شویم هر ۵ نیرو همیشه یک رکورد دارند
    for key, _ in PorterForce.FORCE_CHOICES:
        PorterForce.objects.get_or_create(force=key)

    if request.method == "POST":
        force_id = request.POST.get("obj_id")
        if _has_perm(request, "strategic.change_porterforce"):
            instance = get_object_or_404(PorterForce, pk=force_id)
            form = PorterForceForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE PorterForce", str(instance))
                return redirect("strategic:porter")

    forces = list(PorterForce.objects.all().prefetch_related("swot_items__business_unit"))
    level_rank = {"low": 1, "medium": 2, "high": 3, "very_high": 4}
    forces.sort(key=lambda f: list(dict(PorterForce.FORCE_CHOICES).keys()).index(f.force))
    overall = round(sum(level_rank.get(f.level, 2) for f in forces) / len(forces), 1) if forces else 0

    return render(request, "strategic/porter.html", {
        "active_page": "porter", "forces": forces, "overall": overall, "form": PorterForceForm(),
    })


# ---------------- McKinsey 7S ----------------

def mckinsey7s(request):
    for key, _ in McKinsey7S.COMPONENT_CHOICES:
        McKinsey7S.objects.get_or_create(component=key)

    if request.method == "POST":
        comp_id = request.POST.get("obj_id")
        if _has_perm(request, "strategic.change_mckinsey7s"):
            instance = get_object_or_404(McKinsey7S, pk=comp_id)
            form = McKinsey7SForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE McKinsey7S", str(instance))
                return redirect("strategic:mckinsey7s")

    components = list(McKinsey7S.objects.all().prefetch_related("swot_items__business_unit"))
    order = list(dict(McKinsey7S.COMPONENT_CHOICES).keys())
    components.sort(key=lambda c: order.index(c.component))

    return render(request, "strategic/mckinsey7s.html", {
        "active_page": "mckinsey7s", "components": components, "form": McKinsey7SForm(),
    })


# ---------------- زنجیره ارزش پورتر (تحلیل محیطی) ----------------

def value_chain(request):
    for key, _ in ValueChainActivity.ACTIVITY_CHOICES:
        ValueChainActivity.objects.get_or_create(activity=key)

    if request.method == "POST":
        act_id = request.POST.get("obj_id")
        if _has_perm(request, "strategic.change_valuechainactivity"):
            instance = get_object_or_404(ValueChainActivity, pk=act_id)
            form = ValueChainActivityForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE ValueChainActivity", str(instance))
                return redirect("strategic:value_chain")

    activities = list(ValueChainActivity.objects.all().prefetch_related("swot_items__business_unit"))
    order = list(dict(ValueChainActivity.ACTIVITY_CHOICES).keys())
    activities.sort(key=lambda a: order.index(a.activity))
    primary = [a for a in activities if a.activity_type == "primary"]
    support = [a for a in activities if a.activity_type == "support"]

    return render(request, "strategic/value_chain.html", {
        "active_page": "value_chain", "primary": primary, "support": support, "form": ValueChainActivityForm(),
    })


# ---------------- Strategic map (BSC) ----------------

THEME_PALETTE = ["#0f8a6a", "#1183c9", "#7b5cd6", "#d08a1f", "#17a3a3", "#d6402f", "#8a5a44", "#5a6474"]


def stratmap(request):
    business_units = list(BusinessUnit.objects.all())
    bu_id = request.POST.get("business_unit") or request.GET.get("bu")
    current_bu = None
    if bu_id:
        current_bu = next((b for b in business_units if str(b.pk) == str(bu_id)), None)
    if not current_bu and business_units:
        current_bu = business_units[0]

    themes = list(StrategyTheme.objects.filter(business_unit=current_bu)) if current_bu else []
    theme_color = {}
    for i, t in enumerate(themes):
        t.color = THEME_PALETTE[i % len(THEME_PALETTE)]
        theme_color[t.pk] = t.color

    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_strategicobjective" if obj_id else "strategic.add_strategicobjective"
        if _has_perm(request, perm):
            instance = get_object_or_404(StrategicObjective, pk=obj_id) if obj_id else None
            form = StrategicObjectiveForm(request.POST, instance=instance, business_unit=current_bu)
            if form.is_valid():
                obj = form.save(commit=False)
                if not obj_id and current_bu:
                    obj.business_unit = current_bu
                obj.save()
                form.save_m2m()
                _log_action(request, "UPDATE StrategicObjective" if obj_id else "CREATE StrategicObjective", str(obj))
                bu_param = f"?bu={current_bu.pk}" if current_bu else ""
                return redirect(reverse("strategic:stratmap") + bu_param)
        else:
            form = StrategicObjectiveForm(business_unit=current_bu)
    else:
        form = StrategicObjectiveForm(business_unit=current_bu)

    objectives = list(
        StrategicObjective.objects.filter(business_unit=current_bu).select_related("theme").prefetch_related("feeds_into", "linked_kpis")
        if current_bu else StrategicObjective.objects.none()
    )
    for o in objectives:
        o.theme_color = theme_color.get(o.theme_id, "var(--ink-faint)")
        o.theme_name = o.theme.name if o.theme_id else "بدون محور"

    PERSP_KEYS = {"financial": "fin", "customer": "cust", "process": "proc", "learning": "learn"}
    bands = []
    for p_key, p_label in StrategicObjective.PERSPECTIVE_CHOICES:
        bands.append({
            "key": p_key, "css": PERSP_KEYS[p_key], "label": p_label,
            "nodes": [o for o in objectives if o.perspective == p_key],
        })

    links = []
    for o in objectives:
        for target in o.feeds_into.all():
            links.append([f"obj-{o.pk}", f"obj-{target.pk}"])

    org_identity, _ = OrgIdentity.objects.get_or_create(pk=1)

    def _pct_color(pct):
        if pct is None:
            return "#9aa1ab"
        if pct < 80:
            return "#B0413E"
        if pct < 90:
            return "#C97A2B"
        return "#3E7A52"

    kpis_by_objective = {}
    circles_by_objective = {}
    for k in StrategicKPI.objects.filter(objective__in=objectives).select_related("objective"):
        kpis_by_objective.setdefault(k.objective_id, []).append({
            "type": "custom", "id": k.pk, "name": k.name, "unit": k.unit, "target": k.target, "actual": k.actual,
            "trend": k.trend, "status": k.status, "owner": k.owner, "period": k.period,
        })
        circles_by_objective.setdefault(k.objective_id, []).append({
            "name": k.name, "target": k.target, "actual": k.actual, "unit": k.unit,
            "pct": k.progress_pct, "color": _pct_color(k.progress_pct),
        })

    for o in objectives:
        for k in o.linked_kpis.all():
            kpis_by_objective.setdefault(o.pk, []).append({
                "type": "shared", "id": k.pk, "name": f"{k.code} — {k.name}", "unit": k.unit,
                "target": k.target_1405, "actual": k.actual_1405,
                "trend": "flat", "status": "on_track", "owner": "", "period": "",
            })
            circles_by_objective.setdefault(o.pk, []).append({
                "name": f"{k.code} — {k.name}", "target": k.target_1405, "actual": k.actual_1405, "unit": k.unit,
                "pct": k.manual_progress_value, "color": _pct_color(k.manual_progress_value),
            })

    for o in objectives:
        o.kpi_count = len(kpis_by_objective.get(o.pk, []))
        o.kpi_circles = circles_by_objective.get(o.pk, [])

    return render(request, "strategic/stratmap.html", {
        "active_page": "stratmap", "bands": bands, "form": form,
        "links": links, "business_units": business_units, "current_bu": current_bu,
        "themes": themes, "theme_form": StrategyThemeForm(), "org_vision": org_identity.vision,
        "kpis_by_objective": kpis_by_objective, "kpi_form": StrategicKPIForm(),
    })


@login_required
def strategic_kpi_save(request):
    if request.method == "POST":
        obj_id = request.POST.get("kpi_id")
        objective_id = request.POST.get("objective_id")
        perm = "strategic.change_strategickpi" if obj_id else "strategic.add_strategickpi"
        if _has_perm(request, perm):
            instance = get_object_or_404(StrategicKPI, pk=obj_id) if obj_id else None
            form = StrategicKPIForm(request.POST, instance=instance)
            if form.is_valid():
                kpi = form.save(commit=False)
                if not obj_id:
                    kpi.objective_id = objective_id
                kpi.save()
                _log_action(request, "UPDATE StrategicKPI" if obj_id else "CREATE StrategicKPI", str(kpi))
    ref = request.POST.get("next") or reverse("strategic:stratmap")
    return redirect(ref)


@login_required
def strategic_kpi_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_strategickpi"):
        obj = get_object_or_404(StrategicKPI, pk=pk)
        label = str(obj)
        obj.delete()
        _log_action(request, "DELETE StrategicKPI", label)
    ref = request.POST.get("next") or reverse("strategic:stratmap")
    return redirect(ref)


def stratmap_print(request):
    business_units = list(BusinessUnit.objects.all())
    bu_id = request.GET.get("bu")
    current_bu = None
    if bu_id:
        current_bu = next((b for b in business_units if str(b.pk) == str(bu_id)), None)
    if not current_bu and business_units:
        current_bu = business_units[0]

    objectives = list(
        StrategicObjective.objects.filter(business_unit=current_bu).select_related("theme").prefetch_related("feeds_into")
        if current_bu else StrategicObjective.objects.none()
    )
    links = []
    for o in objectives:
        o.theme_name = o.theme.name if o.theme_id else ""
        targets = list(o.feeds_into.all())
        o.feeds_codes = [t.code for t in targets]
        for t in targets:
            links.append([f"pcard-{o.pk}", f"pcard-{t.pk}"])

    bands = []
    PERSP_KEYS = {"financial": "fin", "customer": "cust", "process": "proc", "learning": "learn"}
    for p_key, p_label in StrategicObjective.PERSPECTIVE_CHOICES:
        bands.append({"label": p_label, "css": PERSP_KEYS[p_key], "nodes": [o for o in objectives if o.perspective == p_key]})

    return render(request, "strategic/stratmap_print.html", {"current_bu": current_bu, "bands": bands, "links": links})


@login_required
def theme_add(request):
    if request.method == "POST" and _has_perm(request, "strategic.add_strategytheme"):
        bu_id = request.POST.get("business_unit")
        bu = get_object_or_404(BusinessUnit, pk=bu_id)
        name = request.POST.get("name", "").strip()
        if name:
            StrategyTheme.objects.create(business_unit=bu, name=name, order=bu.themes.count())
            _log_action(request, "CREATE StrategyTheme", f"{bu.name} — {name}")
        return redirect(reverse("strategic:stratmap") + f"?bu={bu.pk}")
    return redirect("strategic:stratmap")


@login_required
def theme_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_strategytheme"):
        _obj = get_object_or_404(StrategyTheme, pk=pk)
        bu_pk = _obj.business_unit_id
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE StrategyTheme", _label)
        return redirect(reverse("strategic:stratmap") + f"?bu={bu_pk}")
    return redirect("strategic:stratmap")


@login_required
def objective_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_strategicobjective"):
        _obj = get_object_or_404(StrategicObjective, pk=pk)
        _label = str(_obj)
        bu_pk = _obj.business_unit_id
        _obj.delete()
        _log_action(request, "DELETE StrategicObjective", _label)
        if bu_pk:
            return redirect(reverse("strategic:stratmap") + f"?bu={bu_pk}")
    return redirect("strategic:stratmap")


@login_required
def business_unit_add(request):
    if request.method == "POST" and _has_perm(request, "strategic.add_businessunit"):
        name = request.POST.get("name", "").strip()
        archetype = request.POST.get("archetype", "other")
        next_page = request.POST.get("next", "strategic:stratmap")
        if name:
            bu = BusinessUnit.objects.create(name=name, archetype=archetype, order=BusinessUnit.objects.count())
            _log_action(request, "CREATE BusinessUnit", name)
            return redirect(reverse(next_page) + f"?bu={bu.pk}")
        return redirect(next_page)
    return redirect("strategic:stratmap")


# ---------------- SWOT ----------------

@login_required
def swot(request):
    business_units = list(BusinessUnit.objects.all())
    bu_id = request.POST.get("business_unit") or request.GET.get("bu")
    current_bu = None
    if bu_id:
        current_bu = next((b for b in business_units if str(b.pk) == str(bu_id)), None)
    if not current_bu and business_units:
        current_bu = business_units[0]
    bu_param = f"?bu={current_bu.pk}" if current_bu else ""

    if request.method == "POST":
        cat = request.POST.get("category", "")
        obj_id = request.POST.get("obj_id")
        if cat in ("s", "w", "o", "t"):
            perm = "strategic.change_swotitem" if obj_id else "strategic.add_swotitem"
            if _has_perm(request, perm):
                instance = get_object_or_404(SWOTItem, pk=obj_id) if obj_id else None
                form = SWOTItemForm(request.POST, instance=instance)
                if form.is_valid():
                    obj = form.save(commit=False)
                    if not obj_id:
                        obj.business_unit = current_bu
                    obj.save()
                    _log_action(request, "UPDATE SWOTItem" if obj_id else "CREATE SWOTItem", str(obj))
                    return redirect(reverse("strategic:swot") + bu_param)
        elif cat in ("so", "st", "wo", "wt"):
            perm = "strategic.change_towsstrategy" if obj_id else "strategic.add_towsstrategy"
            if _has_perm(request, perm):
                t_instance = get_object_or_404(TOWSStrategy, pk=obj_id) if obj_id else None
                tform = TOWSStrategyForm(request.POST, instance=t_instance, business_unit=current_bu)
                if tform.is_valid():
                    tobj = tform.save(commit=False)
                    if not obj_id:
                        tobj.business_unit = current_bu
                    tobj.save()
                    tform.save_m2m()
                    _log_action(request, "UPDATE TOWSStrategy" if obj_id else "CREATE TOWSStrategy", str(tobj))
                    return redirect(reverse("strategic:swot") + bu_param)

    if current_bu:
        s_items = list(SWOTItem.objects.filter(category="s", business_unit=current_bu))
        w_items = list(SWOTItem.objects.filter(category="w", business_unit=current_bu))
        o_items = list(SWOTItem.objects.filter(category="o", business_unit=current_bu))
        t_items = list(SWOTItem.objects.filter(category="t", business_unit=current_bu))
    else:
        s_items = w_items = o_items = t_items = []

    def avg_w(items):
        return round(sum(i.weight for i in items) / len(items), 1) if items else 0

    s_score, w_score, o_score, t_score = avg_w(s_items), avg_w(w_items), avg_w(o_items), avg_w(t_items)

    def norm(score):
        return (score - 3) / 2 if score else 0

    internal = norm(s_score) - norm(w_score)
    external = norm(o_score) - norm(t_score)
    pos_x = 50 + internal * 42
    pos_y = 50 - external * 42
    if internal >= 0 and external >= 0:
        posture, posture_color = "راهبرد تهاجمی (SO)", "var(--s)"
    elif internal >= 0 and external < 0:
        posture, posture_color = "راهبرد تنوع (ST)", "var(--w)"
    elif internal < 0 and external >= 0:
        posture, posture_color = "راهبرد بازنگری (WO)", "var(--o)"
    else:
        posture, posture_color = "راهبرد تدافعی (WT)", "var(--t)"

    tows = {}
    for key, _ in TOWSStrategy.CATEGORY_CHOICES:
        tows[key] = list(
            TOWSStrategy.objects.filter(category=key, business_unit=current_bu)
            .prefetch_related("source_items", "objectives")
        ) if current_bu else []

    swot_items_data = []
    for letter, items in (("S", s_items), ("W", w_items), ("O", o_items), ("T", t_items)):
        for i, it in enumerate(items, start=1):
            it.code = f"{letter}{i}"
            swot_items_data.append({"id": it.pk, "cat": it.category, "code": it.code, "text": it.text})

    return render(request, "strategic/swot.html", {
        "active_page": "swot",
        "business_units": business_units, "current_bu": current_bu,
        "s_items": s_items, "w_items": w_items, "o_items": o_items, "t_items": t_items,
        "s_score": s_score, "w_score": w_score, "o_score": o_score, "t_score": t_score,
        "pos_x": pos_x, "pos_y": pos_y, "posture": posture, "posture_color": posture_color,
        "internal_dominant": "قوت‌ها بر ضعف‌ها" if internal >= 0 else "ضعف‌ها بر قوت‌ها",
        "external_dominant": "فرصت‌ها بر تهدیدها" if external >= 0 else "تهدیدها بر فرصت‌ها",
        "tows": tows, "swot_items_data": swot_items_data,
        "form": SWOTItemForm(),
        "tows_form": TOWSStrategyForm(business_unit=current_bu),
        "pestel_factors": PestelFactor.objects.all(),
        "porter_forces": PorterForce.objects.all(),
        "stakeholders_list": Stakeholder.objects.all(),
        "scenarios_list": Scenario.objects.all(),
        "s7_components": McKinsey7S.objects.all(),
        "vc_activities": ValueChainActivity.objects.all(),
    })


@login_required
def swot_print(request):
    business_units = list(BusinessUnit.objects.all())
    bu_id = request.GET.get("bu")
    current_bu = None
    if bu_id:
        current_bu = next((b for b in business_units if str(b.pk) == str(bu_id)), None)
    if not current_bu and business_units:
        current_bu = business_units[0]

    if current_bu:
        s_items = list(SWOTItem.objects.filter(category="s", business_unit=current_bu))
        w_items = list(SWOTItem.objects.filter(category="w", business_unit=current_bu))
        o_items = list(SWOTItem.objects.filter(category="o", business_unit=current_bu))
        t_items = list(SWOTItem.objects.filter(category="t", business_unit=current_bu))
        tows = {key: list(TOWSStrategy.objects.filter(category=key, business_unit=current_bu))
                for key, _ in TOWSStrategy.CATEGORY_CHOICES}
    else:
        s_items = w_items = o_items = t_items = []
        tows = {}

    return render(request, "strategic/swot_print.html", {
        "current_bu": current_bu,
        "s_items": s_items, "w_items": w_items, "o_items": o_items, "t_items": t_items,
        "tows": tows,
    })


@login_required
def swot_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_swotitem"):
        _obj = get_object_or_404(SWOTItem, pk=pk)
        _label = str(_obj)
        bu_pk = _obj.business_unit_id
        _obj.delete()
        _log_action(request, "DELETE SWOTItem", _label)
        if bu_pk:
            return redirect(reverse("strategic:swot") + f"?bu={bu_pk}")
    return redirect("strategic:swot")


@login_required
def tows_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_towsstrategy"):
        _obj = get_object_or_404(TOWSStrategy, pk=pk)
        _label = str(_obj)
        bu_pk = _obj.business_unit_id
        _obj.delete()
        _log_action(request, "DELETE TOWSStrategy", _label)
        if bu_pk:
            return redirect(reverse("strategic:swot") + f"?bu={bu_pk}")
    return redirect("strategic:swot")


# ---------------- Risk register ----------------

@login_required
def risk(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_risk" if obj_id else "strategic.add_risk"
        if _has_perm(request, perm):
            instance = get_object_or_404(Risk, pk=obj_id) if obj_id else None
            form = RiskForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE Risk" if obj_id else "CREATE Risk", str(form.instance))
                return redirect("strategic:risk")
        else:
            form = RiskForm()
    else:
        form = RiskForm()

    risks = list(Risk.objects.all())
    risks_sorted = sorted(risks, key=lambda r: -r.residual_score)
    for idx, r in enumerate(risks_sorted, start=1):
        r.display_no = idx  # runtime-only, used for bubble/row numbering

    ZONE_COLOR = {"low": "#2fa96b", "med": "#e3b23c", "high": "#e2792e", "crit": "#d6402f"}

    # ماتریس ۵×۵ (احتمال × شدت اثر) بر اساس امتیاز باقیمانده
    matrix = []
    for impact in range(5, 0, -1):
        row = []
        for likelihood in range(1, 6):
            s = likelihood * impact
            zone = Risk._zone_of(s)
            cell_risks = [r for r in risks_sorted if r.likelihood == likelihood and r.impact == impact]
            row.append({"zone": zone, "color": ZONE_COLOR[zone], "score": s,
                        "likelihood": likelihood, "impact": impact, "risks": cell_risks})
        matrix.append(row)

    top_risks = risks_sorted[:5]

    categories = []
    for key, label in Risk.CATEGORY_CHOICES:
        n = sum(1 for r in risks if r.category == key)
        categories.append({"key": key, "label": label, "color": Risk.CATEGORY_COLOR[key], "count": n})
    max_cat = max([c["count"] for c in categories], default=0) or 1
    for c in categories:
        c["pct"] = round(c["count"] / max_cat * 100)

    total = len(risks)
    high_or_crit = sum(1 for r in risks if r.residual_score >= 10)
    above_appetite = sum(1 for r in risks if r.residual_score > 9)
    avg_score = round(sum(r.residual_score for r in risks) / total, 1) if total else 0
    avg_effectiveness = round(sum(r.effectiveness_pct for r in risks) / total) if total else 0

    risks_json = [
        {"pk": r.pk, "likelihood": r.likelihood, "impact": r.impact,
         "inherent_likelihood": r.inherent_likelihood, "inherent_impact": r.inherent_impact}
        for r in risks_sorted
    ]

    return render(request, "strategic/risk.html", {
        "active_page": "risk", "matrix": matrix, "risks": risks_sorted, "top_risks": top_risks,
        "form": form, "categories": categories, "max_cat": max_cat,
        "total": total, "high_or_crit": high_or_crit, "above_appetite": above_appetite,
        "avg_score": avg_score, "avg_effectiveness": avg_effectiveness, "risks_json": risks_json,
    })


@login_required
def risk_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_risk"):
        _obj = get_object_or_404(Risk, pk=pk)
        _label = str(_obj)
        _obj.delete()
        _log_action(request, "DELETE Risk", _label)
    return redirect("strategic:risk")


# ---------------- چشم‌انداز، مأموریت و ارزش‌های سازمانی ----------------
# ویرایش این بخش فقط برای ادمین اصلی (Superuser) مجاز است، نه گروه «ویرایشگران».

def org_identity(request):
    identity, _ = OrgIdentity.objects.get_or_create(pk=1)

    if request.method == "POST" and request.user.is_superuser:
        form_kind = request.POST.get("form_kind")

        if form_kind == "identity":
            identity.vision = request.POST.get("vision", "").strip()
            identity.mission = request.POST.get("mission", "").strip()
            identity.signed_by = request.POST.get("signed_by", "").strip()
            identity.signed_role = request.POST.get("signed_role", "").strip()
            identity.signed_date = request.POST.get("signed_date", "").strip()
            identity.save()
            _log_action(request, "UPDATE OrgIdentity", "چشم‌انداز/مأموریت")
            return redirect("strategic:org_identity")

        elif form_kind == "value":
            obj_id = request.POST.get("obj_id")
            text = request.POST.get("text", "").strip()
            is_center = bool(request.POST.get("is_center"))
            if text:
                if obj_id:
                    OrgValue.objects.filter(pk=obj_id).update(text=text, is_center=is_center)
                else:
                    OrgValue.objects.create(text=text, is_center=is_center, order=OrgValue.objects.count())
                _log_action(request, "UPDATE OrgValue" if obj_id else "CREATE OrgValue", text)
            return redirect("strategic:org_identity")

        elif form_kind == "policy":
            obj_id = request.POST.get("obj_id")
            number = request.POST.get("number") or 0
            text = request.POST.get("text", "").strip()
            if text:
                if obj_id:
                    QualityPolicyPoint.objects.filter(pk=obj_id).update(number=number, text=text)
                else:
                    QualityPolicyPoint.objects.create(number=number, text=text, order=QualityPolicyPoint.objects.count())
                _log_action(request, "UPDATE QualityPolicyPoint" if obj_id else "CREATE QualityPolicyPoint", text)
            return redirect("strategic:org_identity")

    values = list(OrgValue.objects.all())
    outer_values = [v for v in values if not v.is_center]
    center_value = next((v for v in values if v.is_center), None)
    policy_points = list(QualityPolicyPoint.objects.all())

    return render(request, "strategic/org_identity.html", {
        "active_page": "org_identity", "identity": identity,
        "outer_values": outer_values, "center_value": center_value,
        "policy_points": policy_points,
    })


def org_value_delete(request, pk):
    if request.method == "POST" and request.user.is_superuser:
        obj = get_object_or_404(OrgValue, pk=pk)
        label = str(obj)
        obj.delete()
        _log_action(request, "DELETE OrgValue", label)
    return redirect("strategic:org_identity")


def policy_point_delete(request, pk):
    if request.method == "POST" and request.user.is_superuser:
        obj = get_object_or_404(QualityPolicyPoint, pk=pk)
        label = str(obj)
        obj.delete()
        _log_action(request, "DELETE QualityPolicyPoint", label)
    return redirect("strategic:org_identity")


# ---------------- سناریوهای راهبردی ----------------

def scenarios(request):
    for key, _ in Scenario.QUADRANT_CHOICES:
        Scenario.objects.get_or_create(quadrant=key)
    axes, _ = ScenarioAxes.objects.get_or_create(pk=1)

    if request.method == "POST":
        form_kind = request.POST.get("form_kind")
        if form_kind == "scenario":
            obj_id = request.POST.get("obj_id")
            if _has_perm(request, "strategic.change_scenario"):
                instance = get_object_or_404(Scenario, pk=obj_id)
                form = ScenarioForm(request.POST, instance=instance)
                if form.is_valid():
                    if form.cleaned_data.get("is_selected"):
                        Scenario.objects.exclude(pk=instance.pk).update(is_selected=False)
                    form.save()
                    _log_action(request, "UPDATE Scenario", str(instance))
                    return redirect("strategic:scenarios")
        elif form_kind == "axes":
            if _has_perm(request, "strategic.change_scenarioaxes"):
                form = ScenarioAxesForm(request.POST, instance=axes)
                if form.is_valid():
                    form.save()
                    _log_action(request, "UPDATE ScenarioAxes", "محورهای سناریو")
                    return redirect("strategic:scenarios")

    scenario_map = {s.quadrant: s for s in Scenario.objects.all().prefetch_related("swot_items__business_unit")}
    return render(request, "strategic/scenarios.html", {
        "active_page": "scenarios", "scenario_map": scenario_map, "axes": axes,
        "scenario_form": ScenarioForm(), "axes_form": ScenarioAxesForm(instance=axes),
    })


# ---------------- اهداف کلان و شاخص‌های سطح کل شرکت ----------------

def company_goals(request):
    if request.method == "POST":
        form_kind = request.POST.get("form_kind")
        obj_id = request.POST.get("obj_id")

        if form_kind == "objective":
            perm = "strategic.change_companyobjective" if obj_id else "strategic.add_companyobjective"
            if _has_perm(request, perm):
                instance = get_object_or_404(CompanyObjective, pk=obj_id) if obj_id else None
                form = CompanyObjectiveForm(request.POST, instance=instance)
                if form.is_valid():
                    form.save()
                    _log_action(request, "UPDATE CompanyObjective" if obj_id else "CREATE CompanyObjective", str(form.instance))
                    return redirect("strategic:company_goals")

        elif form_kind == "kpi":
            perm = "strategic.change_companykpi" if obj_id else "strategic.add_companykpi"
            if _has_perm(request, perm):
                instance = get_object_or_404(CompanyKPI, pk=obj_id) if obj_id else None
                form = CompanyKPIForm(request.POST, instance=instance)
                if form.is_valid():
                    form.save()
                    _log_action(request, "UPDATE CompanyKPI" if obj_id else "CREATE CompanyKPI", str(form.instance))
                    return redirect("strategic:company_goals")

    objectives = list(CompanyObjective.objects.all().prefetch_related("kpis"))
    grouped = []
    seen_groups = {}
    for o in objectives:
        key = o.group_title
        if key not in seen_groups:
            seen_groups[key] = {"group_title": key, "objectives": []}
            grouped.append(seen_groups[key])
        seen_groups[key]["objectives"].append(o)

    kpis = list(CompanyKPI.objects.all().prefetch_related("objectives"))

    return render(request, "strategic/company_goals.html", {
        "active_page": "company_goals", "grouped": grouped, "kpis": kpis,
        "objective_form": CompanyObjectiveForm(),
        "kpi_form": CompanyKPIForm(),
    })


@login_required
def company_objective_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_companyobjective"):
        obj = get_object_or_404(CompanyObjective, pk=pk)
        label = str(obj)
        obj.delete()
        _log_action(request, "DELETE CompanyObjective", label)
    return redirect("strategic:company_goals")


@login_required
def company_kpi_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_companykpi"):
        obj = get_object_or_404(CompanyKPI, pk=pk)
        label = str(obj)
        obj.delete()
        _log_action(request, "DELETE CompanyKPI", label)
    return redirect("strategic:company_goals")


# ---------------- اسناد و دستورالعمل‌ها ----------------

@login_required
def documents(request):
    if request.method == "POST":
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_document" if obj_id else "strategic.add_document"
        if _has_perm(request, perm):
            instance = get_object_or_404(Document, pk=obj_id) if obj_id else None
            form = DocumentForm(request.POST, request.FILES, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE Document" if obj_id else "CREATE Document", str(form.instance))
                return redirect("strategic:documents")
        else:
            form = DocumentForm()
    else:
        form = DocumentForm()

    docs = Document.objects.all()
    upstream = [d for d in docs if d.category == "upstream"]
    guideline = [d for d in docs if d.category == "guideline"]

    return render(request, "strategic/documents.html", {
        "active_page": "documents", "upstream": upstream, "guideline": guideline, "form": form,
    })


@login_required
def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    try:
        f = doc.file.open("rb")
    except (FileNotFoundError, ValueError):
        raise Http404("فایل یافت نشد")
    is_pdf = doc.file_ext == "pdf"
    response = FileResponse(f, as_attachment=not is_pdf, filename=doc.file.name.split("/")[-1])
    return response


@login_required
def document_delete(request, pk):
    if request.method == "POST" and _has_perm(request, "strategic.delete_document"):
        obj = get_object_or_404(Document, pk=pk)
        label = str(obj)
        obj.file.delete(save=False)
        obj.delete()
        _log_action(request, "DELETE Document", label)
    return redirect("strategic:documents")


# ---------------- ورود/خروجی اکسل شاخص‌های کلیدی شرکت (فقط مدیر سیستم) ----------------

_KPI_EXCEL_HEADERS = [
    "کد", "حوزه (Q/D/C/M)", "شاخص", "واحد سنجش", "هدف ۱۴۰۴", "عملکرد ۱۴۰۴",
    "هدف ۱۴۰۵", "عملکرد ۱۴۰۵", "درصد تحقق", "صرفاً پایشی (بله/خیر)",
    "اهداف مرتبط (مثلاً O1-O2-O3)", "ملاحظات", "ترتیب نمایش",
]


@login_required
def company_kpi_export(request):
    if not request.user.is_superuser:
        messages.error(request, "این عملیات فقط برای مدیر سیستم مجاز است.")
        return redirect("strategic:company_goals")

    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "شاخص‌های کلیدی"
    ws.sheet_view.rightToLeft = True

    header_fill = PatternFill(start_color="1B2430", end_color="1B2430", fill_type="solid")
    header_font = Font(color="FFFFFF", bold=True)
    for col, title in enumerate(_KPI_EXCEL_HEADERS, start=1):
        cell = ws.cell(row=1, column=col, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for row_i, k in enumerate(CompanyKPI.objects.all().prefetch_related("objectives"), start=2):
        related = "-".join(o.code for o in k.objectives.all())
        values = [
            k.code, k.domain, k.name, k.unit, k.target_1404, k.actual_1404,
            k.target_1405, k.actual_1405, k.progress_1405, "بله" if k.is_monitoring else "خیر",
            related, k.notes, k.order,
        ]
        for col, val in enumerate(values, start=1):
            ws.cell(row=row_i, column=col, value=val)

    widths = [8, 14, 34, 12, 10, 12, 10, 12, 12, 14, 22, 24, 10]
    for col, w in enumerate(widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = w

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    _log_action(request, "EXPORT CompanyKPI Excel", f"{CompanyKPI.objects.count()} ردیف")
    response = HttpResponse(
        buf.read(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="shakhes-haye-kelidi.xlsx"'
    return response


@login_required
def company_kpi_import(request):
    if not request.user.is_superuser:
        messages.error(request, "این عملیات فقط برای مدیر سیستم مجاز است.")
        return redirect("strategic:company_goals")

    if request.method != "POST" or not request.FILES.get("excel_file"):
        messages.error(request, "فایلی انتخاب نشده است.")
        return redirect("strategic:company_goals")

    import openpyxl

    try:
        wb = openpyxl.load_workbook(request.FILES["excel_file"], data_only=True)
        ws = wb.active
    except Exception:
        messages.error(request, "فایل اکسل قابل خواندن نیست. لطفاً فرمت را بررسی کنید.")
        return redirect("strategic:company_goals")

    def _s(v):
        return "" if v is None else str(v).strip()

    created, updated, skipped = 0, 0, 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue
        code = _s(row[0])
        if not code:
            skipped += 1
            continue
        domain = _s(row[1])[:1].upper() or "Q"
        if domain not in dict(CompanyKPI.DOMAIN_CHOICES):
            domain = "Q"
        name = _s(row[2])
        unit = _s(row[3]) if len(row) > 3 else ""
        target_1404 = _s(row[4]) if len(row) > 4 else ""
        actual_1404 = _s(row[5]) if len(row) > 5 else ""
        target_1405 = _s(row[6]) if len(row) > 6 else ""
        actual_1405 = _s(row[7]) if len(row) > 7 else ""
        progress_1405 = _s(row[8]) if len(row) > 8 else ""
        is_monitoring = _s(row[9]).startswith("بل") if len(row) > 9 else False
        related_raw = _s(row[10]) if len(row) > 10 else ""
        notes = _s(row[11]) if len(row) > 11 else ""
        try:
            order = int(row[12]) if len(row) > 12 and row[12] not in (None, "") else 0
        except (TypeError, ValueError):
            order = 0

        kpi, was_created = CompanyKPI.objects.update_or_create(
            code=code,
            defaults=dict(
                domain=domain, name=name, unit=unit,
                target_1404=target_1404, actual_1404=actual_1404,
                target_1405=target_1405, actual_1405=actual_1405,
                progress_1405=progress_1405, is_monitoring=is_monitoring,
                notes=notes, order=order,
            ),
        )
        related_codes = re.findall(r"O\d+", related_raw)
        if related_codes:
            objs = list(CompanyObjective.objects.filter(code__in=related_codes))
            kpi.objectives.set(objs)

        created += 1 if was_created else 0
        updated += 0 if was_created else 1

    _log_action(request, "IMPORT CompanyKPI Excel", f"{created} جدید، {updated} به‌روزشده، {skipped} رد‌شده")
    messages.success(request, f"وارد کردن انجام شد: {created} شاخص جدید، {updated} شاخص به‌روزرسانی‌شده، {skipped} ردیف نامعتبر رد شد.")
    return redirect("strategic:company_goals")
