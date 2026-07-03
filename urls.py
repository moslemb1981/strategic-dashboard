from django.urls import path
from . import views

app_name = "strategic"

urlpatterns = [
    path("", views.home, name="home"),
    path("research/", views.research, name="research"),
    path("roadmap/", views.roadmap, name="roadmap"),
    path("market/", views.market, name="market"),
    path("pestel/", views.pestel, name="pestel"),
    path("stratmap/", views.stratmap, name="stratmap"),
    path("swot/", views.swot, name="swot"),
    path("risk/", views.risk, name="risk"),
]

# در urls.py اصلی پروژه (D:\sysapp\strategic\strategic\urls.py یا مشابه) این خط را اضافه کنید:
#
# from django.urls import include, path
# urlpatterns = [
#     ...
#     path("strategic/", include("strategic.urls")),
# ]
