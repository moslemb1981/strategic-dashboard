"""ابزار مشترک پشتیبان‌گیری و بازگردانی نقشه‌ی استراتژیک یک کسب‌وکار (JSON).
فایل با «_» شروع می‌شود، پس خودش فرمان مدیریتی حساب نمی‌شود."""
import datetime
import json
import os

from django.db import transaction

from strategic.models import (
    BusinessUnit, StrategicObjective, StrategyTheme, CompanyKPI, OperationalKPI,
    ObjectiveKPIWeight, ObjectiveOperationalKPIWeight, FunctionalStrategy, Risk, StrategicKPI,
    Initiative,
)


def snapshot(bu):
    """وضعیت کامل نقشه‌ی یک کسب‌وکار را به یک دیکشنری قابل ذخیره تبدیل می‌کند."""
    objs = list(StrategicObjective.objects.filter(business_unit=bu).select_related("theme").order_by("order", "code"))
    data = {
        "version": 1,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "bu": {"id": bu.pk, "name": bu.name, "archetype": bu.archetype},
        "themes": [{"name": t.name, "order": t.order} for t in StrategyTheme.objects.filter(business_unit=bu)],
        "objectives": [],
    }
    for o in objs:
        data["objectives"].append({
            "code": o.code, "perspective": o.perspective, "theme": o.theme.name if o.theme else None,
            "title": o.title, "kpi": o.kpi, "status": o.status, "order": o.order,
            "feeds": [x.code for x in o.feeds_into.all()],
            "tows": o.source_tows_id,
            "company_kpis": [[w.kpi.code, w.weight] for w in ObjectiveKPIWeight.objects.filter(objective=o).select_related("kpi")],
            "op_kpis": [[w.kpi.code, w.weight] for w in ObjectiveOperationalKPIWeight.objects.filter(objective=o).select_related("kpi")],
            "initiatives": list(o.initiatives.values_list("pk", flat=True)),
            "risks": list(Risk.objects.filter(linked_objective=o).values_list("pk", flat=True)),
            "functional_strategies": list(o.functional_strategies.values_list("pk", flat=True)),
            "strategic_kpis": list(StrategicKPI.objects.filter(objective=o).values_list("pk", flat=True)),
        })
    return data


def save_snapshot(bu, folder="backups", prefix="brokerage_map"):
    os.makedirs(folder, exist_ok=True)
    data = snapshot(bu)
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(folder, f"{prefix}_{stamp}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    return path, data


def restore(bu, data):
    """نقشه‌ی فعلی کسب‌وکار را حذف و از روی snapshot دوباره می‌سازد (لینک پروژه‌ها، ریسک‌ها و ... هم برمی‌گردد)."""
    with transaction.atomic():
        current = list(StrategicObjective.objects.filter(business_unit=bu).values_list("pk", flat=True))
        bu.archetype = data["bu"]["archetype"]
        bu.save()
        themes = {}
        for t in data["themes"]:
            obj = StrategyTheme.objects.filter(business_unit=bu, name=t["name"]).first() or StrategyTheme(business_unit=bu, name=t["name"])
            obj.order = t["order"]
            obj.save()
            themes[t["name"]] = obj
        new = {}
        for d in data["objectives"]:
            new[d["code"]] = StrategicObjective.objects.create(
                code=d["code"], perspective=d["perspective"], theme=themes.get(d["theme"]), title=d["title"],
                kpi=d["kpi"], status=d["status"], order=d["order"], business_unit=bu,
                source_tows_id=d["tows"] if d["tows"] and bu.tows_strategies.filter(pk=d["tows"]).exists() else None,
            )
        for d in data["objectives"]:
            o = new[d["code"]]
            o.feeds_into.set([new[c] for c in d["feeds"] if c in new])
            for code, w in d["company_kpis"]:
                k = CompanyKPI.objects.filter(code=code).first()
                if k:
                    ObjectiveKPIWeight.objects.create(objective=o, kpi=k, weight=w)
            for code, w in d["op_kpis"]:
                k = OperationalKPI.objects.filter(code=code).first()
                if k:
                    ObjectiveOperationalKPIWeight.objects.create(objective=o, kpi=k, weight=w)
            StrategicKPI.objects.filter(pk__in=d["strategic_kpis"]).update(objective=o)
            Risk.objects.filter(pk__in=d["risks"]).update(linked_objective=o)
            for ini in Initiative.objects.filter(pk__in=d["initiatives"]):
                ini.objectives.add(o)
            for fs in FunctionalStrategy.objects.filter(pk__in=d["functional_strategies"]):
                fs.linked_objectives.add(o)
        StrategicObjective.objects.filter(pk__in=current).delete()
    return len(new)
