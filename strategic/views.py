import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .models import (
    Study, Initiative, Risk, SWOTItem, TOWSStrategy, StrategicObjective, Competitor, PestelFactor,
    BusinessUnit, StrategyTheme,
)
from .forms import (
    StudyForm, InitiativeForm, RiskForm, SWOTItemForm, TOWSStrategyForm, StrategicObjectiveForm,
    CompetitorForm, PestelFactorForm, StrategyThemeForm,
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
        obj_id = request.POST.get("obj_id")
        perm = "strategic.change_initiative" if obj_id else "strategic.add_initiative"
        if _has_perm(request, perm):
            instance = get_object_or_404(Initiative, pk=obj_id) if obj_id else None
            form = InitiativeForm(request.POST, instance=instance)
            if form.is_valid():
                form.save()
                _log_action(request, "UPDATE Initiative" if obj_id else "CREATE Initiative", str(form.instance))
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

@login_required
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

THEME_PALETTE = ["#0f8a6a", "#1183c9", "#7b5cd6", "#d08a1f", "#17a3a3", "#d6402f", "#8a5a44", "#5a6474"]


@login_required
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
        StrategicObjective.objects.filter(business_unit=current_bu).select_related("theme").prefetch_related("feeds_into")
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

    return render(request, "strategic/stratmap.html", {
        "active_page": "stratmap", "bands": bands, "form": form,
        "links": links, "business_units": business_units, "current_bu": current_bu,
        "themes": themes, "theme_form": StrategyThemeForm(),
    })


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
        if cat in ("s", "w", "o", "t"):
            if _has_perm(request, "strategic.add_swotitem"):
                form = SWOTItemForm(request.POST)
                if form.is_valid():
                    obj = form.save(commit=False)
                    obj.business_unit = current_bu
                    obj.save()
                    _log_action(request, "CREATE SWOTItem", str(obj))
                    return redirect(reverse("strategic:swot") + bu_param)
        elif cat in ("so", "st", "wo", "wt"):
            if _has_perm(request, "strategic.add_towsstrategy"):
                tform = TOWSStrategyForm(request.POST)
                if tform.is_valid():
                    tobj = tform.save(commit=False)
                    tobj.business_unit = current_bu
                    tobj.save()
                    _log_action(request, "CREATE TOWSStrategy", str(tobj))
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
        tows[key] = list(TOWSStrategy.objects.filter(category=key, business_unit=current_bu)) if current_bu else []

    return render(request, "strategic/swot.html", {
        "active_page": "swot",
        "business_units": business_units, "current_bu": current_bu,
        "s_items": s_items, "w_items": w_items, "o_items": o_items, "t_items": t_items,
        "s_score": s_score, "w_score": w_score, "o_score": o_score, "t_score": t_score,
        "pos_x": pos_x, "pos_y": pos_y, "posture": posture, "posture_color": posture_color,
        "internal_dominant": "قوت‌ها بر ضعف‌ها" if internal >= 0 else "ضعف‌ها بر قوت‌ها",
        "external_dominant": "فرصت‌ها بر تهدیدها" if external >= 0 else "تهدیدها بر فرصت‌ها",
        "tows": tows,
        "form": SWOTItemForm(),
        "tows_form": TOWSStrategyForm(),
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
