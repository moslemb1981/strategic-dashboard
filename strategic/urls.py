from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

app_name = "strategic"

urlpatterns = [
    path("", views.home, name="home"),
    path("identity/", views.org_identity, name="org_identity"),
    path("identity/value/delete/<int:pk>/", views.org_value_delete, name="org_value_delete"),
    path("identity/policy/delete/<int:pk>/", views.policy_point_delete, name="policy_point_delete"),

    path("research/", views.research, name="research"),
    path("research/delete/<int:pk>/", views.study_delete, name="study_delete"),

    path("roadmap/", views.roadmap, name="roadmap"),
    path("roadmap/delete/<int:pk>/", views.initiative_delete, name="initiative_delete"),

    path("market/", views.market, name="market"),
    path("market/delete/<int:pk>/", views.competitor_delete, name="competitor_delete"),

    path("pestel/", views.pestel, name="pestel"),
    path("pestel/delete/<int:pk>/", views.pestel_delete, name="pestel_delete"),
    path("porter/", views.porter, name="porter"),
    path("stratmap/", views.stratmap, name="stratmap"),
    path("stratmap/print/", views.stratmap_print, name="stratmap_print"),
    path("stratmap/delete/<int:pk>/", views.objective_delete, name="objective_delete"),
    path("stratmap/theme/add/", views.theme_add, name="theme_add"),
    path("stratmap/theme/delete/<int:pk>/", views.theme_delete, name="theme_delete"),
    path("business-unit/add/", views.business_unit_add, name="business_unit_add"),

    path("swot/", views.swot, name="swot"),
    path("swot/print/", views.swot_print, name="swot_print"),
    path("swot/delete/<int:pk>/", views.swot_delete, name="swot_delete"),
    path("swot/tows/delete/<int:pk>/", views.tows_delete, name="tows_delete"),

    path("risk/", views.risk, name="risk"),
    path("risk/delete/<int:pk>/", views.risk_delete, name="risk_delete"),

    path("login/", auth_views.LoginView.as_view(template_name="strategic/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="strategic:login"), name="logout"),
]
