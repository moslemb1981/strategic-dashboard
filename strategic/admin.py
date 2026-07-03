from django.contrib import admin
from .models import Study, Initiative, Risk, SWOTItem, StrategicObjective, Competitor, PestelFactor


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
    list_display = ("title", "owner", "likelihood", "impact", "zone")
    list_filter = ("likelihood", "impact")
    search_fields = ("title", "owner")


@admin.register(SWOTItem)
class SWOTItemAdmin(admin.ModelAdmin):
    list_display = ("text", "category", "impact", "created_at")
    list_filter = ("category", "impact")
    search_fields = ("text",)


@admin.register(StrategicObjective)
class StrategicObjectiveAdmin(admin.ModelAdmin):
    list_display = ("code", "perspective", "theme", "title", "kpi", "status", "order")
    list_display_links = ("code", "title")
    list_editable = ("status", "order")
    list_filter = ("perspective", "theme", "status")
    search_fields = ("code", "title", "kpi")
    ordering = ("perspective", "theme", "order", "code")


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ("name", "market_share", "recent_move", "order")
    list_editable = ("market_share", "order")
    search_fields = ("name",)
    ordering = ("order", "-market_share")


@admin.register(PestelFactor)
class PestelFactorAdmin(admin.ModelAdmin):
    list_display = ("category", "text", "order")
    list_filter = ("category",)
    list_editable = ("order",)
    search_fields = ("text",)
    ordering = ("category", "order")
