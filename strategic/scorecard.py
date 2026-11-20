# -*- coding: utf-8 -*-
"""کارنامه عملکرد ماهانه‌ی معاونت‌ها (حوزه‌ها) و مدیریت‌ها.

مالک کارنامه (owner_key): «u<id>» = معاونت/حوزه (OrgUnit از نوع deputy)، «m<id>» = مدیریت (Management).
  - کارنامه معاونت: اهداف OKR مدیریت‌های زیرمجموعه‌ی آن، به‌تفکیک مدیریت.
  - کارنامه مدیریت (مستقل یا زیرمجموعه‌ی معاونت): اهداف OKR همان مدیریت.
امتیاز کل = جمع وزنی چهار بخش: اهداف OKR، شاخص‌های سازمان (ثبت دستی)، پروژه‌ها، رابط.
همه‌ی اعداد OKR زنده از همان منطق صفحه OKR/دیدبان خوانده می‌شود (views._okr_wavg).
"""
import os

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import FileResponse, Http404
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Initiative, LiaisonParam, LiaisonScore, LiaisonTopic, Management, OKRObjective, OrgUnit,
    ScorecardConfig, ScorecardEntry, ScorecardOwnerConfig, ScorecardPeriod, ScorecardProject,
    ScorecardProjectMonth,
)
from . import views as V

MONTHS = ["فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
          "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"]
EDIT_PERM = "strategic.change_scorecardconfig"


# ---------------------------------------------------------------- کمکی‌ها

def _num(v):
    """عدد برای نمایش: صحیح بدون اعشار، وگرنه تا یک رقم اعشار."""
    if v is None:
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(round(f)) if abs(f - round(f)) < 0.05 else round(f, 1)


def _cls(p):
    """رنگ وضعیت: قرمز <۸۰، زرد ۸۰ تا ۹۰، سبز ≥۹۰، خاکستری بدون داده."""
    if p is None:
        return "n"
    return "r" if p < 80 else ("y" if p < 90 else "g")


def _status_text(p):
    return {"r": "نیازمند بهبود", "y": "در حال پیشرفت", "g": "مطلوب", "n": "بدون داده"}[_cls(p)]


def _period(request, cfg):
    try:
        y = int(request.GET.get("y") or cfg.period_year)
        m = int(request.GET.get("m") or cfg.period_month)
    except ValueError:
        y, m = cfg.period_year, cfg.period_month
    if not 1 <= m <= 12:
        y, m = cfg.period_year, cfg.period_month
    return y, m


def can_edit(user):
    return user.is_authenticated and user.has_perm(EDIT_PERM)


def _owner(key):
    """(نوع، شیء، عنوان، برچسب سربرگ، برچسب مسئول) یا None."""
    key = str(key or "")
    if len(key) < 2 or not key[1:].isdigit():
        return None
    pk = int(key[1:])
    if key[0] == "u":
        u = OrgUnit.objects.filter(pk=pk, kind="deputy").first()
        if not u:
            return None
        hr = "حوزه" if u.name.startswith("حوزه") else "معاونت"
        return {"key": key, "kind": "u", "obj": u, "name": u.name, "role": hr,
                "head_label": "نام معاون" if hr == "معاونت" else "نام مدیر حوزه"}
    if key[0] == "m":
        m = Management.objects.select_related("org_unit").filter(pk=pk).first()
        if not m:
            return None
        ind = m.org_unit.kind == "ceo_direct"
        role = "مدیریت مستقل" if ind else f"مدیریت (زیرمجموعه {m.org_unit.name})"
        return {"key": key, "kind": "m", "obj": m, "name": m.name, "role": role, "head_label": "نام مدیر"}
    return None


def all_owners():
    """فهرست همه‌ی واحدهایی که کارنامه دارند (برای صفحه فهرست): معاونت‌ها، مدیریت‌های مستقل، سایر مدیریت‌ها."""
    out = []
    for u in OrgUnit.objects.filter(kind="deputy", has_scorecard=True).order_by("order", "name"):
        out.append(_owner(f"u{u.pk}"))
    for m in Management.objects.filter(has_scorecard=True).select_related("org_unit").order_by(
            "org_unit__kind", "org_unit__order", "order", "name"):
        out.append(_owner(f"m{m.pk}"))
    return [o for o in out if o]


def _weights(cfg, key):
    oc = ScorecardOwnerConfig.objects.filter(owner_key=key).first()
    base = cfg.weights
    if not oc:
        return base
    mine = [oc.weight_1, oc.weight_2, oc.weight_3, oc.weight_4]
    return [mine[i] if mine[i] is not None else base[i] for i in range(4)]


def _norm_weights(vals):
    """وزن‌های ۰..۱۰۰ → فهرست هم‌اندازه با جمع ۱۰۰. اگر همه ثبت شده باشند (و جمع > ۰) به‌نسبت، وگرنه مساوی."""
    n = len(vals)
    if n == 0:
        return [], True
    if all(v is not None for v in vals) and sum(vals) > 0:
        s = float(sum(vals))
        return [v * 100.0 / s for v in vals], int(round(s)) == 100
    return [100.0 / n] * n, True


# ---------------------------------------------------------------- محاسبه

def _okr_part(owner, cfg):
    kind, obj = owner["kind"], owner["obj"]
    mgmts = [obj] if kind == "m" else list(obj.managements.order_by("order", "name"))
    groups = []
    for m in mgmts:
        objs = list(
            OKRObjective.objects.filter(level="management", management_ref=m)
            .prefetch_related("key_results__operational_kpi", "key_results__company_kpi")
            .order_by("order", "code")
        )
        if objs:
            groups.append({"m": m, "objs": objs})
    # وزن مدیریت‌ها (فقط برای کارنامه معاونت) و وزن اهداف هر مدیریت
    if kind == "u":
        mw, ok_m = _norm_weights([g["m"].scorecard_weight for g in groups])
    else:
        mw, ok_m = [100.0], True
    warn = not ok_m
    total_w = total_s = 0.0
    out = []
    for g, gw in zip(groups, mw):
        ow, ok_o = _norm_weights([o.scorecard_weight for o in g["objs"]])
        warn = warn or not ok_o
        items = []
        gs = gws = 0.0
        for o, w in zip(g["objs"], ow):
            krs = list(o.key_results.all())
            pct = V._okr_wavg(krs)
            eff = gw * w / 100.0
            include = pct is not None or cfg.empty_as_zero
            if include:
                total_s += eff * (pct or 0)
                total_w += eff
                gs += w * (pct or 0)
                gws += w
            items.append({
                "code": o.code, "title": o.title, "n_kr": len(krs), "weight": _num(eff), "pct": pct,
                "cls": _cls(pct),
                "krs": [{
                    "code": k.code, "title": k.title, "kpi": k.kpi_code or "",
                    "trend_id": k.operational_kpi_id or (k.company_kpi.source_operational_kpi_id if k.company_kpi_id else None), "unit": (k.kpi.unit if k.kpi else ""),
                    "target": V._okr_fmt(k.target), "actual": V._okr_fmt(k.actual), "pct": k.pct, "cls": _cls(k.pct),
                } for k in krs],
            })
        gp = round(gs / gws) if gws else None
        out.append({"name": g["m"].name, "weight": _num(gw), "pct": gp, "cls": _cls(gp), "items": items})
    score = round(total_s / total_w) if total_w else None
    return {"groups": out, "score": score, "warn": warn, "n_obj": sum(len(g["items"]) for g in out)}


def _projects(key, y, m):
    rows = []
    links = (ScorecardProject.objects.filter(owner_key=key).select_related("initiative")
             .prefetch_related("months").order_by("order", "id"))
    for l in links:
        mr = next((x for x in l.months.all() if x.year == y and x.month == m), None)
        plan = mr.plan if mr else 100.0
        actual = mr.actual if mr else float(l.initiative.progress or 0)
        prev = mr.prev if mr else None
        pct = min(100, round(actual / plan * 100)) if plan else 0
        rows.append({
            "id": l.pk, "code": l.initiative.code, "title": l.initiative.title,
            "manager": l.initiative.project_manager, "plan": _num(plan), "actual": _num(actual),
            "prev": _num(prev), "note": (mr.note if mr else "") or "", "pct": pct, "cls": _cls(pct),
            "has_row": bool(mr), "plan_raw": plan, "actual_raw": actual,
        })
    score = round(sum(r["pct"] for r in rows) / len(rows)) if rows else None
    return rows, score


def _liaison(key, y, m):
    earned = {s.param_id: s.earned for s in LiaisonScore.objects.filter(owner_key=key, year=y, month=m)}
    topics, te, tb = [], 0.0, 0.0
    for t in LiaisonTopic.objects.prefetch_related("params").order_by("order", "id"):
        ps, e = [], 0.0
        for p in t.params.all().order_by("order", "id"):
            v = min(float(p.max_score), max(0.0, float(earned.get(p.pk, 0) or 0)))
            e += v
            ps.append({"id": p.pk, "text": p.text, "max": p.max_score, "earned": _num(earned.get(p.pk, 0)) or 0})
        topics.append({"id": t.pk, "title": t.title, "base": t.base_score, "earned": _num(e), "params": ps,
                       "psum": sum(p["max"] for p in ps)})
        te += e
        tb += t.base_score
    score = round(te / tb * 100) if tb else None
    return {"topics": topics, "earned": _num(te), "base": _num(tb), "score": score}



def _fa(x):
    return str(x).translate(str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹"))


def gauge_svg(v):
    """گیج نیم‌دایره‌ای امتیاز کل (SVG ثابت)."""
    import math
    from django.utils.safestring import mark_safe
    cx, cy, r = 110, 108, 84
    col = {"r": "var(--red)", "y": "var(--yel)", "g": "var(--grn)", "n": "var(--mut)"}[_cls(v)]

    def pt(p, rr):
        a = math.pi * (1 - p / 100.0)
        return cx + rr * math.cos(a), cy - rr * math.sin(a)

    def arc(f, t, rr, c, w, o):
        a, b = pt(f, rr), pt(t, rr)
        return (f'<path d="M{a[0]:.1f} {a[1]:.1f} A{rr} {rr} 0 0 1 {b[0]:.1f} {b[1]:.1f}" '
                f'stroke="{c}" stroke-width="{w}" fill="none" opacity="{o}"/>')

    vv = max(0, min(100, v or 0))
    o = '<svg viewBox="0 0 220 150" style="width:100%;max-width:16rem" font-family="Vazirmatn">'
    o += arc(0, 80, r, "var(--red)", 12, .22) + arc(80, 90, r, "var(--yel)", 12, .3) + arc(90, 100, r, "var(--grn)", 12, .3)
    if vv > 0:
        o += arc(0, vv, r, col, 12, 1)
    for t in (0, 80, 90, 100):
        a, b, l = pt(t, r - 12), pt(t, r + 9), pt(t, r + 19)
        o += (f'<line x1="{a[0]:.1f}" y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}" stroke="var(--mut)" stroke-width="1"/>'
              f'<text x="{l[0]:.1f}" y="{l[1] + 3:.1f}" text-anchor="middle" font-size="8" fill="var(--mut)">{_fa(t)}</text>')
    m = pt(vv, r)
    o += f'<circle cx="{m[0]:.1f}" cy="{m[1]:.1f}" r="8" fill="var(--paper)" stroke="{col}" stroke-width="3"/>'
    o += (f'<text x="{cx}" y="{cy - 8}" text-anchor="middle" font-size="44" font-weight="700" fill="var(--fg)">{_fa(v) if v is not None else "—"}</text>'
          f'<text x="{cx}" y="{cy + 10}" text-anchor="middle" font-size="10" fill="var(--mut)">از ۱۰۰ امتیاز</text></svg>')
    return mark_safe(o)


def build(key, y, m, cfg=None):
    cfg = cfg or ScorecardConfig.get()
    owner = _owner(key)
    if not owner:
        return None
    okr = _okr_part(owner, cfg)
    pj_rows, pj_score = _projects(key, y, m)
    lia = _liaison(key, y, m)
    period = ScorecardPeriod.objects.filter(year=y, month=m).first()
    org = period.org_score if period else None
    entry = ScorecardEntry.objects.filter(owner_key=key, year=y, month=m).first()
    w = _weights(cfg, key)
    scores = [okr["score"], _num(org), pj_score, lia["score"]]
    tw = sum(w)
    total = round(sum(w[i] * (scores[i] or 0) for i in range(4)) / tw) if tw else 0
    rows = [{"title": cfg.titles[i], "weight": w[i], "score": scores[i], "cls": _cls(scores[i])} for i in range(4)]
    return {
        "owner": owner, "cfg": cfg, "year": y, "month": m, "month_name": MONTHS[m - 1], "okr": okr,
        "projects": pj_rows, "pj_score": pj_score, "lia": lia, "org_score": _num(org),
        "prev": _num(entry.prev_score) if entry else None, "rows": rows, "wsum": tw,
        "total": total, "cls": _cls(total), "status": _status_text(total),
        "prepared": (period.prepared_date if period else "") or "",
        "notes": [x.strip() for x in (cfg.notes or "").splitlines() if x.strip()],
        "sigs": cfg.sig_list,
        "photo_v": (owner["obj"].head_photo.name or "")[-12:], "gauge": gauge_svg(total), "head_name": owner["obj"].head_name, "has_photo": bool(owner["obj"].head_photo),
    }


# ---------------------------------------------------------------- صفحه‌ها

@V.guest_gate("executive_show")
def scorecard_home(request):
    cfg = ScorecardConfig.get()
    y, m = _period(request, cfg)
    cards = []
    for o in all_owners():
        d = build(o["key"], y, m, cfg)
        cards.append({"owner": o, "total": d["total"], "cls": d["cls"], "status": d["status"],
                      "okr": d["okr"]["score"], "n": d["okr"]["n_obj"], "head": d["head_name"]})
    groups = [
        ("معاونت‌ها و حوزه‌ها", [c for c in cards if c["owner"]["kind"] == "u"]),
        ("مدیریت‌های مستقل", [c for c in cards if c["owner"]["kind"] == "m" and c["owner"]["obj"].org_unit.kind == "ceo_direct"]),
        ("مدیریت‌های زیرمجموعه معاونت‌ها", [c for c in cards if c["owner"]["kind"] == "m" and c["owner"]["obj"].org_unit.kind != "ceo_direct"]),
    ]
    return render(request, "strategic/scorecard_home.html", {
        "groups": [(t, l) for t, l in groups if l], "y": y, "m": m, "month_name": MONTHS[m - 1],
        "can_edit": can_edit(request.user), "active_page": "scorecard",
    })


@V.guest_gate("executive_show")
def scorecard_view(request, key):
    cfg = ScorecardConfig.get()
    y, m = _period(request, cfg)
    d = build(key, y, m, cfg)
    if not d:
        raise Http404("کارنامه پیدا نشد")
    if not (d["owner"]["obj"].has_scorecard):
        messages.info(request, "برای این واحد کارنامه فعال نشده است (در تنظیمات کارنامه فعال می‌شود).")
    pj_moved = (d["okr"]["n_obj"] + len(d["okr"]["groups"]) * (1 if d["owner"]["kind"] == "u" else 0)
                + 2.5 * len(d["projects"])) > cfg.project_page_limit
    d.update({"can_edit": can_edit(request.user), "pj_moved": pj_moved})
    return render(request, "strategic/scorecard.html", d)


@xframe_options_sameorigin
@V.guest_gate("executive_show")
def scorecard_kpi_chart(request, pk):
    """صفحه‌ی مینیمال حاوی همان پنجره‌ی نمودار روند شاخص (با پرچم پروژه‌ها و تحلیل ماهانه) برای نمایش در کارنامه."""
    return render(request, "strategic/scorecard_kpi_chart.html", {"kpi_id": pk})


@V.guest_gate("executive_show")
def scorecard_photo(request, key):
    o = _owner(key)
    if not o or not o["obj"].head_photo:
        raise Http404
    try:
        f = o["obj"].head_photo.open("rb")
    except (FileNotFoundError, ValueError):
        raise Http404
    return FileResponse(f)


PHOTO_W, PHOTO_H = 400, 460  # پیکسل (نسبت ۸۷ به ۱۰۰ مطابق قاب کارنامه)


def _store_photo(obj, f):
    """ذخیره عکس مسئول: بریدن به نسبت قاب و کوچک‌کردن به ۴۰۰×۴۶۰ (JPEG)؛ بدون Pillow همان فایل ذخیره می‌شود."""
    from django.core.files.base import ContentFile
    if not (f.content_type or "").startswith("image/") or f.size > 5 * 1024 * 1024:
        return False
    if obj.head_photo:
        obj.head_photo.delete(save=False)
    try:
        import io
        from PIL import Image, ImageOps
        im = ImageOps.exif_transpose(Image.open(f)).convert("RGB")
        im = ImageOps.fit(im, (PHOTO_W, PHOTO_H), Image.LANCZOS, centering=(0.5, 0.3))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=88)
        obj.head_photo.save("head.jpg", ContentFile(buf.getvalue()), save=False)
    except Exception:
        f.seek(0)
        obj.head_photo = f
    obj.save()
    return True


@login_required
def scorecard_photo_edit(request, key):
    """افزودن / تغییر / حذف عکس مسئول مستقیم از صفحه کارنامه."""
    o = _owner(key)
    if not o:
        raise Http404
    ref = request.META.get("HTTP_REFERER")
    back = redirect(ref) if ref else redirect("strategic:scorecard_view", key=key)
    if request.method != "POST":
        return back
    if not request.user.has_perm(EDIT_PERM):
        messages.error(request, "برای تغییر عکس دسترسی ویرایش «کارنامه عملکرد» لازم است.")
        return back
    obj = o["obj"]
    if request.POST.get("action") == "del":
        if obj.head_photo:
            obj.head_photo.delete(save=False)
            obj.head_photo = ""
            obj.save()
        messages.success(request, "عکس حذف شد.")
    else:
        f = request.FILES.get("photo")
        if f and _store_photo(obj, f):
            messages.success(request, "عکس ذخیره شد.")
        else:
            messages.error(request, "فقط فایل تصویر تا ۵ مگابایت پذیرفته می‌شود.")
    return back


def _to_float(v, default=None):
    v = str(v if v is not None else "").strip()
    if not v:
        return default
    for i, d in enumerate("۰۱۲۳۴۵۶۷۸۹"):
        v = v.replace(d, str(i))
    v = v.replace("٫", ".").replace("،", ".")
    try:
        return float(v)
    except ValueError:
        return default


@login_required
def scorecard_edit(request, key):
    """ثبت دستی ماهانه‌ی یک کارنامه: امتیاز ماه گذشته، امتیاز رابط، پروژه‌های کارنامه و اعداد آن‌ها."""
    cfg = ScorecardConfig.get()
    y, m = _period(request, cfg)
    owner = _owner(key)
    if not owner:
        raise Http404
    if not request.user.has_perm(EDIT_PERM):
        messages.error(request, "برای ثبت کارنامه دسترسی ویرایش «کارنامه عملکرد» لازم است.")
        return redirect("strategic:scorecard_view", key=key)

    if request.method == "POST":
        P = request.POST
        with transaction.atomic():
            prev = _to_float(P.get("prev_score"))
            ent, _c = ScorecardEntry.objects.get_or_create(owner_key=key, year=y, month=m)
            ent.prev_score = prev
            ent.save()
            for p in LiaisonParam.objects.all():
                v = _to_float(P.get(f"lia_{p.pk}"))
                if v is None:
                    LiaisonScore.objects.filter(owner_key=key, year=y, month=m, param=p).delete()
                else:
                    LiaisonScore.objects.update_or_create(
                        owner_key=key, year=y, month=m, param=p, defaults={"earned": max(0.0, v)})
            for l in ScorecardProject.objects.filter(owner_key=key):
                if P.get(f"pj_{l.pk}_del"):
                    l.delete()
                    continue
                plan = _to_float(P.get(f"pj_{l.pk}_plan"), 100.0)
                actual = _to_float(P.get(f"pj_{l.pk}_actual"), 0.0)
                ScorecardProjectMonth.objects.update_or_create(
                    link=l, year=y, month=m,
                    defaults={"plan": plan, "actual": actual, "prev": _to_float(P.get(f"pj_{l.pk}_prev")),
                              "note": (P.get(f"pj_{l.pk}_note") or "").strip()[:300]})
            n_added = 0
            have = set(ScorecardProject.objects.filter(owner_key=key).values_list("initiative_id", flat=True))
            order = ScorecardProject.objects.filter(owner_key=key).count()
            for iid in P.getlist("add_init"):
                if iid.isdigit() and int(iid) not in have:
                    ini = Initiative.objects.filter(pk=int(iid)).first()
                    if ini:
                        order += 1
                        ScorecardProject.objects.create(owner_key=key, initiative=ini, order=order)
                        n_added += 1
        V._log_action(request, "SCORECARD edit", f"{key} {y}/{m}")
        messages.success(request, "ثبت شد." + (f" {n_added} پروژه به کارنامه اضافه شد." if n_added else ""))
        return redirect(f"{request.path}?y={y}&m={m}")

    d = build(key, y, m, cfg)
    linked = set(ScorecardProject.objects.filter(owner_key=key).values_list("initiative_id", flat=True))
    all_init = [{"id": i.pk, "code": i.code, "title": i.title, "div": i.division or i.owner,
                 "wg": i.work_group, "pr": i.progress, "pm": i.project_manager, "t": i.item_type,
                 "on": i.pk in linked}
                for i in Initiative.objects.order_by("code", "id")]
    d.update({"divs": sorted({i["div"] for i in all_init if i["div"]}), "wgs": sorted({i["wg"] for i in all_init if i["wg"]}), "all_init": all_init, "can_edit": True, "active_page": "scorecard"})
    return render(request, "strategic/scorecard_edit.html", d)


def _unit_rows():
    cfg0 = ScorecardConfig.get()
    rows = []
    for u in OrgUnit.objects.filter(kind="deputy").order_by("order", "name"):
        rows.append({"key": f"u{u.pk}", "label": u.name, "kind": "معاونت / حوزه", "o": u})
    for m in Management.objects.select_related("org_unit").order_by("org_unit__kind", "org_unit__order", "order", "name"):
        rows.append({"key": f"m{m.pk}", "label": m.name, "kind": "مدیریت — " + ("مستقل" if m.org_unit.kind == "ceo_direct" else m.org_unit.name), "o": m})
    for r in rows:
        r["w"] = _weights(cfg0, r["key"])  # وزن مؤثر (اختصاصی یا پیش‌فرض)
        r["custom"] = ScorecardOwnerConfig.objects.filter(owner_key=r["key"]).exists()
    return rows


@login_required
def scorecard_settings(request):
    """تنظیمات کارنامه: عنوان و وزن بخش‌ها، ماه، نمره شرکت مادر، جدول رابط، امضاها و واحدهای دارای کارنامه."""
    if not request.user.has_perm(EDIT_PERM):
        messages.error(request, "برای تنظیمات کارنامه دسترسی ویرایش «کارنامه عملکرد» لازم است.")
        return redirect("strategic:scorecard_home")
    cfg = ScorecardConfig.get()

    if request.method == "POST":
        P = request.POST
        old_def = list(cfg.weights)
        # اعتبارسنجی پیش از هر ذخیره‌سازی
        errs = []
        ws_ = [_to_float(P.get(f"weight_{i}")) for i in range(1, 5)]
        ws_ = [int(w) if w is not None else getattr(cfg, f"weight_{i}") for i, w in enumerate(ws_, 1)]
        if sum(ws_) != 100:
            errs.append(f"جمع وزن‌های جدول بالای کارنامه برابر {sum(ws_)} است و باید ۱۰۰ باشد.")
        for r in _unit_rows():
            k = r["key"]
            uw = [_to_float(P.get(f"o{k}_w{i}")) for i in range(1, 5)]
            if all(w is not None for w in uw) and sum(int(w) for w in uw) != 100:
                errs.append(f"جمع وزن‌های «{r['label']}» برابر {sum(int(w) for w in uw)} است و باید ۱۰۰ باشد.")
        for t in LiaisonTopic.objects.all():
            if P.get(f"t{t.pk}_del"):
                continue
            base = _to_float(P.get(f"t{t.pk}_base"))
            base = int(base) if base is not None else t.base_score
            tot = 0
            for pr in t.params.all():
                if P.get(f"p{pr.pk}_del"):
                    continue
                mx = _to_float(P.get(f"p{pr.pk}_max"))
                tot += int(mx) if mx is not None else pr.max_score
            for tid, text, mx in zip(P.getlist("np_topic"), P.getlist("np_text"), P.getlist("np_max")):
                if str(tid) == str(t.pk) and text.strip():
                    tot += int(_to_float(mx, 0) or 0)
            if tot != base:
                errs.append(f"در جدول رابط، جمع امتیاز پارامترهای «{t.title}» برابر {tot} است ولی امتیاز پایه {base} است؛ باید برابر باشند.")
        if errs:
            messages.error(request, "ذخیره انجام نشد. " + " ".join(errs))
            return redirect("strategic:scorecard_settings")
        with transaction.atomic():
            for i in range(1, 5):
                t = (P.get(f"title_{i}") or "").strip()
                if t:
                    setattr(cfg, f"title_{i}", t[:200])
                w = _to_float(P.get(f"weight_{i}"))
                if w is not None:
                    setattr(cfg, f"weight_{i}", max(0, min(int(w), 100)))
            cfg.liaison_title = (P.get("liaison_title") or cfg.liaison_title).strip()[:200]
            cfg.notes = (P.get("notes") or "").strip()
            import json
            sigs = []
            for t, r, n in zip(P.getlist("sg_t"), P.getlist("sg_r"), P.getlist("sg_n")):
                if t.strip() or r.strip() or n.strip():
                    sigs.append({"t": t.strip()[:100], "r": r.strip()[:150], "n": n.strip()[:100]})
            cfg.signatures = json.dumps(sigs, ensure_ascii=False)
            py, pm = _to_float(P.get("period_year")), _to_float(P.get("period_month"))
            if py and pm and 1 <= int(pm) <= 12:
                cfg.period_year, cfg.period_month = int(py), int(pm)
            cfg.empty_as_zero = bool(P.get("empty_as_zero"))
            lim = _to_float(P.get("project_page_limit"))
            if lim is not None:
                cfg.project_page_limit = max(1, int(lim))
            cfg.save()
            per, _c = ScorecardPeriod.objects.get_or_create(year=cfg.period_year, month=cfg.period_month)
            per.org_score = _to_float(P.get("org_score"))
            per.prepared_date = (P.get("prepared_date") or "").strip()[:20]
            per.save()

            # جدول رابط
            for t in LiaisonTopic.objects.all():
                if P.get(f"t{t.pk}_del"):
                    t.delete()
                    continue
                t.title = (P.get(f"t{t.pk}_title") or t.title).strip()[:200]
                b = _to_float(P.get(f"t{t.pk}_base"))
                if b is not None:
                    t.base_score = max(0, int(b))
                t.save()
            for p in LiaisonParam.objects.all():
                if P.get(f"p{p.pk}_del"):
                    p.delete()
                    continue
                p.text = (P.get(f"p{p.pk}_text") or p.text).strip()[:500]
                mx = _to_float(P.get(f"p{p.pk}_max"))
                if mx is not None:
                    p.max_score = max(0, int(mx))
                p.save()
            n = LiaisonTopic.objects.count()
            for title, base in zip(P.getlist("nt_title"), P.getlist("nt_base")):
                if title.strip():
                    n += 1
                    LiaisonTopic.objects.create(title=title.strip()[:200], base_score=int(_to_float(base, 0) or 0), order=n)
            for tid, text, mx in zip(P.getlist("np_topic"), P.getlist("np_text"), P.getlist("np_max")):
                t = LiaisonTopic.objects.filter(pk=tid).first() if str(tid).isdigit() else None
                if t and text.strip():
                    LiaisonParam.objects.create(topic=t, text=text.strip()[:500], max_score=int(_to_float(mx, 0) or 0),
                                                order=t.params.count() + 1)

            # واحدها
            for r in _unit_rows():
                k, o = r["key"], r["o"]
                o.has_scorecard = bool(P.get(f"o{k}_has"))
                o.head_name = (P.get(f"o{k}_head") or "").strip()[:150]
                f = request.FILES.get(f"o{k}_photo")
                o.save()
                if P.get(f"o{k}_photo_del") and o.head_photo:
                    o.head_photo.delete(save=False)
                    o.head_photo = ""
                    o.save()
                elif f and not _store_photo(o, f):
                    messages.error(request, f"عکس «{r['label']}» رد شد (فقط تصویر تا ۵ مگابایت).")
                ws = [_to_float(P.get(f"o{k}_w{i}")) for i in range(1, 5)]
                ws = [None if w is None else max(0, min(int(w), 100)) for w in ws]
                # خانه‌ها با وزن مؤثر پر می‌شوند؛ فقط اگر با پیش‌فرض (قبلی) فرق داشت وزن اختصاصی ثبت می‌شود
                if all(w is not None for w in ws) and ws != old_def:
                    oc, _c = ScorecardOwnerConfig.objects.get_or_create(owner_key=k)
                    for i, w in enumerate(ws, 1):
                        setattr(oc, f"weight_{i}", w)
                    oc.save()
                elif any(w is not None for w in ws) and not all(w is not None for w in ws):
                    oc, _c = ScorecardOwnerConfig.objects.get_or_create(owner_key=k)
                    for i, w in enumerate(ws, 1):
                        setattr(oc, f"weight_{i}", w)
                    oc.save()
                else:
                    ScorecardOwnerConfig.objects.filter(owner_key=k).delete()
        V._log_action(request, "SCORECARD settings", "")
        messages.success(request, "تنظیمات کارنامه ذخیره شد.")
        return redirect("strategic:scorecard_settings")

    per = ScorecardPeriod.objects.filter(year=cfg.period_year, month=cfg.period_month).first()
    return render(request, "strategic/scorecard_settings.html", {
        "cfg": cfg, "sigs": cfg.sig_list, "period": per, "months": list(enumerate(MONTHS, 1)),
        "topics": LiaisonTopic.objects.prefetch_related("params").order_by("order", "id"),
        "units": _unit_rows(), "active_page": "scorecard",
    })


# ---------------------------------------------------------------- وزن‌دهی اهداف (در بخش OKR)

def _equal(n):
    if not n:
        return []
    b = 100 // n
    r = 100 - b * n
    return [b + (1 if i < r else 0) for i in range(n)]


def _init_w(vals):
    """وزن‌های ثبت‌شده، یا تقسیم مساوی اگر همه خالی/غیرقابل‌استفاده باشند."""
    if vals and all(v is not None for v in vals) and sum(vals) > 0:
        return list(vals)
    return _equal(len(vals))


@login_required
def scorecard_weights(request):
    """وزن اهداف هر مدیریت (جمع ۱۰۰) و وزن مدیریت‌ها در معاونت (جمع ۱۰۰) برای کارنامه."""
    if not request.user.has_perm("strategic.change_okrobjective"):
        messages.error(request, "برای تغییر وزن‌ها دسترسی ویرایش OKR لازم است.")
        return redirect("strategic:okr")
    units = []
    for u in OrgUnit.objects.filter(kind__in=["deputy", "ceo_direct"]).order_by("kind", "order", "name"):
        mg = []
        for m in u.managements.order_by("order", "name"):
            objs = list(OKRObjective.objects.filter(level="management", management_ref=m).order_by("order", "code"))
            if objs:
                mg.append({"m": m, "objs": objs})
        if mg:
            units.append({"u": u, "mg": mg, "dep": u.kind == "deputy"})

    errors, posted = [], {}
    if request.method == "POST":
        P = request.POST
        # اعتبارسنجی: جمع وزن اهداف هر مدیریت و جمع وزن مدیریت‌های هر معاونت نباید از ۱۰۰ بیشتر شود
        for u in units:
            tot_m = 0
            for g in u["mg"]:
                m = g["m"]
                if u["dep"]:
                    v = _to_float(P.get(f"mw_{m.pk}"))
                    if v is not None:
                        posted[f"mw_{m.pk}"] = int(v)
                        tot_m += max(0, int(v))
                tot_o = 0
                for o in g["objs"]:
                    v = _to_float(P.get(f"ow_{o.pk}"))
                    if v is not None:
                        posted[f"ow_{o.pk}"] = int(v)
                        tot_o += max(0, int(v))
                if tot_o > 100:
                    errors.append(f"جمع وزن اهداف «{m.name}» ({u['u'].name}) برابر {tot_o} است و از ۱۰۰ بیشتر است.")
            if u["dep"] and tot_m > 100:
                errors.append(f"جمع وزن مدیریت‌های «{u['u'].name}» برابر {tot_m} است و از ۱۰۰ بیشتر است.")
        if not errors:
            with transaction.atomic():
                for u in units:
                    for g in u["mg"]:
                        m = g["m"]
                        if u["dep"] and f"mw_{m.pk}" in posted:
                            m.scorecard_weight = max(0, min(posted[f"mw_{m.pk}"], 100))
                            m.save(update_fields=["scorecard_weight"])
                        for o in g["objs"]:
                            if f"ow_{o.pk}" in posted:
                                o.scorecard_weight = max(0, min(posted[f"ow_{o.pk}"], 100))
                                o.save(update_fields=["scorecard_weight"])
            V._log_action(request, "SCORECARD weights", "")
            messages.success(request, "وزن‌ها ذخیره شد.")
            return redirect("strategic:scorecard_weights")
        messages.error(request, "ذخیره انجام نشد. " + " ".join(errors))

    for u in units:
        mws = _init_w([g["m"].scorecard_weight for g in u["mg"]]) if u["dep"] else [100] * len(u["mg"])
        for g, mw in zip(u["mg"], mws):
            g["mw"] = posted.get(f"mw_{g['m'].pk}", mw)
            ows = _init_w([o.scorecard_weight for o in g["objs"]])
            g["ow"] = [(o, posted.get(f"ow_{o.pk}", w)) for o, w in zip(g["objs"], ows)]
    return render(request, "strategic/scorecard_weights.html", {"units": units, "active_page": "okr"})
