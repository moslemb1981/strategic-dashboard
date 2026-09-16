# -*- coding: utf-8 -*-
"""نگاشت مرکزی «بخش‌های سامانه» به مدل‌های Django مرتبط — تنها منبع حقیقت
برای سیستم دسترسی. هر بخش که کاربر بتونه دسترسی ویرایش بگیره، اینجا با
یه کلید یکتا و فهرست مدل‌های مرتبطش تعریف می‌شه.

این فایل جایگزین منطق پراکنده‌ی قبلی (setup_user_roles.py / seed_groups.py)
شده — تنها منبع تعریف بخش‌ها همینجاست.
"""

# کلید → (عنوان فارسی، فهرست اسم کلاس مدل‌ها، آیا محدودیت کسب‌وکار دارد)
SECTIONS = {
    "documents": ("اسناد و دستورالعمل‌ها", ["Document"], False),
    "org_values": ("ارکان جهت‌ساز سازمان", ["OrgValue"], False),
    "legal_requirements": ("الزامات قانونی", ["LegalRequirement"], False),
    "stakeholders": ("تحلیل ذینفعان", ["Stakeholder"], False),
    "audit_findings": ("نتایج ممیزی‌ها", ["AuditFinding"], False),
    "raw_factors": ("آرشیو عوامل اولیه", ["RawIdentifiedFactor"], False),
    "environmental_factors": ("بانک عوامل محیطی", ["EnvironmentalFactor"], False),
    "pestel": ("تحلیل Pestel", ["PestelFactor"], False),
    "porter": ("تحلیل Porter", ["PorterForce"], False),
    "mckinsey7s": ("تحلیل McKinsey 7S", ["McKinsey7S"], False),
    "value_chain": ("زنجیره ارزش پورتر", ["ValueChainActivity"], False),
    "cross_impact": ("ماتریس اثر متقابل", ["CrossImpactFactor", "CrossImpactLink"], False),
    "scenarios": ("سناریوهای راهبردی", ["Scenario", "ScenarioAxes", "ScenarioResponseStrategy", "ScenarioHighlight"], False),
    "swot": ("تحلیل SWOT", ["SWOTItem", "TOWSStrategy"], True),
    "stratmap": ("نقشه استراتژیک", ["StrategicObjective"], True),
    "risk": ("نقشه ریسک", ["Risk"], False),
    "company_goals": ("اهداف کلان و KPI شرکت", ["CompanyObjective", "CompanyKPI"], False),
    "operational_kpis": ("بانک شاخص‌های عملیاتی", ["OperationalKPI"], False),
    "roadmap": ("پروژه‌های تحول", ["Initiative"], True),
    "market_intel": ("هوش بازار", ["Competitor", "CustomerSatisfactionBenchmark", "DomesticRawMaterial", "MarketIntelReport"], False),
}

BU_SCOPED_SECTION_KEYS = [key for key, (_, _, bu_scoped) in SECTIONS.items() if bu_scoped]


def permissions_for_section(section_key):
    """کدنام‌های مجوز Django (add/change/delete) برای هر مدل این بخش را برمی‌گرداند."""
    _, model_names, _ = SECTIONS[section_key]
    codenames = []
    for model_name in model_names:
        lower = model_name.lower()
        for prefix in ("add", "change", "delete"):
            codenames.append(f"{prefix}_{lower}")
    return codenames
