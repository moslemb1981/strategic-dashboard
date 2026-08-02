from django.contrib import admin
from .models import (
    Study, Initiative, Risk, SWOTItem, TOWSStrategy, StrategicObjective,
    Competitor, PestelFactor, BusinessUnit, StrategyTheme, PorterForce,
    OrgIdentity, OrgValue, QualityPolicyPoint, McKinsey7S, ValueChainActivity, Stakeholder, CrossImpactFactor, CrossImpactLink, Scenario, ScenarioAxes, CompanyObjective, CompanyKPI, Document, StrategicKPI, LegalRequirement, EnvironmentalFactor,
)


@admin.register(BusinessUnit)
class BusinessUnitAdmin(admin.ModelAdmin):
    list_display = ("name", "archetype", "order")
    list_editable = ("order",)
    search_fields = ("name",)


@admin.register(StrategyTheme)
class StrategyThemeAdmin(admin.ModelAdmin):
    list_display = ("name", "business_unit", "order")
    list_editable = ("order",)
    list_filter = ("business_unit",)
    search_fields = ("name",)


@admin.register(Study)
class StudyAdmin(admin.ModelAdmin):
    list_display = ("title", "field", "status", "date", "created_at")
    list_filter = ("status", "field")
    search_fields = ("title", "field")


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "start_date", "end_date", "progress", "status")
    list_filter = ("status",)
    search_fields = ("title", "owner")


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "inherent_score", "residual_score", "target_score", "zone", "trend", "response_strategy")
    list_filter = ("category", "trend", "response_strategy")
    search_fields = ("title", "owner", "kri")


@admin.register(SWOTItem)
class SWOTItemAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "weight", "business_unit", "created_at")
    list_editable = ("weight",)
    list_filter = ("business_unit", "category")
    search_fields = ("text",)


@admin.register(TOWSStrategy)
class TOWSStrategyAdmin(admin.ModelAdmin):
    list_display = ("category", "text", "order")
    list_editable = ("order",)
    list_filter = ("business_unit", "category")
    search_fields = ("text",)
    ordering = ("category", "order")


@admin.register(StrategicObjective)
class StrategicObjectiveAdmin(admin.ModelAdmin):
    list_display = ("code", "perspective", "theme", "title", "kpi", "status", "order")
    list_display_links = ("code", "title")
    list_editable = ("status", "order")
    list_filter = ("business_unit", "perspective", "theme", "status")
    search_fields = ("code", "title", "kpi")
    ordering = ("perspective", "theme", "order", "code")
    filter_horizontal = ("feeds_into",)


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ("name", "market_share", "recent_move", "order")
    list_editable = ("market_share", "order")
    search_fields = ("name",)
    ordering = ("order", "-market_share")


@admin.register(PestelFactor)
class PestelFactorAdmin(admin.ModelAdmin):
    list_display = ("category", "kind", "text", "impact_level", "probability", "uncertainty", "order")
    list_filter = ("category", "kind", "uncertainty", "horizon")
    list_editable = ("order",)
    search_fields = ("text",)
    ordering = ("category", "kind", "order")


@admin.register(PorterForce)
class PorterForceAdmin(admin.ModelAdmin):
    list_display = ("force", "level", "updated_at")
    list_editable = ("level",)


@admin.register(OrgIdentity)
class OrgIdentityAdmin(admin.ModelAdmin):
    list_display = ("__str__", "signed_by", "signed_date")


@admin.register(OrgValue)
class OrgValueAdmin(admin.ModelAdmin):
    list_display = ("text", "is_center", "order")
    list_editable = ("order", "is_center")


@admin.register(QualityPolicyPoint)
class QualityPolicyPointAdmin(admin.ModelAdmin):
    list_display = ("number", "text", "order")
    list_editable = ("order",)


@admin.register(McKinsey7S)
class McKinsey7SAdmin(admin.ModelAdmin):
    list_display = ("component", "updated_at")


@admin.register(ValueChainActivity)
class ValueChainActivityAdmin(admin.ModelAdmin):
    list_display = ("activity", "updated_at")


@admin.register(Stakeholder)
class StakeholderAdmin(admin.ModelAdmin):
    list_display = ("name", "department", "risk_score", "opportunity_score", "status")
    list_filter = ("department", "status")
    search_fields = ("name", "need", "risk_text", "opportunity_text")


@admin.register(CrossImpactFactor)
class CrossImpactFactorAdmin(admin.ModelAdmin):
    list_display = ("text", "quadrant", "order")
    list_filter = ("quadrant",)
    list_editable = ("order",)


@admin.register(CrossImpactLink)
class CrossImpactLinkAdmin(admin.ModelAdmin):
    list_display = ("from_factor", "to_factor", "score")
    list_filter = ("score",)


@admin.register(Scenario)
class ScenarioAdmin(admin.ModelAdmin):
    list_display = ("quadrant", "title", "is_selected", "updated_at")


@admin.register(ScenarioAxes)
class ScenarioAxesAdmin(admin.ModelAdmin):
    list_display = ("axis1_name", "axis2_name")


@admin.register(CompanyObjective)
class CompanyObjectiveAdmin(admin.ModelAdmin):
    list_display = ("code", "group_title", "title", "order")
    list_editable = ("order",)


@admin.register(CompanyKPI)
class CompanyKPIAdmin(admin.ModelAdmin):
    list_display = ("code", "domain", "name", "target_1405", "actual_1405", "order")
    list_filter = ("domain", "is_monitoring")
    list_editable = ("order",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "category", "approved_at", "uploaded_at")
    list_filter = ("category",)


@admin.register(StrategicKPI)
class StrategicKPIAdmin(admin.ModelAdmin):
    list_display = ("name", "objective", "target", "actual", "status")
    list_filter = ("status", "trend")


@admin.register(LegalRequirement)
class LegalRequirementAdmin(admin.ModelAdmin):
    list_display = ("title", "source", "department", "is_legal", "is_organizational")
    list_filter = ("is_legal", "is_organizational", "department")
    search_fields = ("title", "source", "department")


@admin.register(EnvironmentalFactor)
class EnvironmentalFactorAdmin(admin.ModelAdmin):
    list_display = ("order", "category", "factor_text", "avg_score", "effect_type")
    list_filter = ("category", "effect_type")
    search_fields = ("factor_text", "detail")
    ordering = ("-avg_score",)
