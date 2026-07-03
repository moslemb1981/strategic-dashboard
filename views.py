from django.shortcuts import render


def home(request):
    return render(request, "strategic/home.html", {"active_page": "home"})


def research(request):
    return render(request, "strategic/research.html", {"active_page": "research"})


def roadmap(request):
    return render(request, "strategic/roadmap.html", {"active_page": "roadmap"})


def market(request):
    return render(request, "strategic/market.html", {"active_page": "market"})


def pestel(request):
    return render(request, "strategic/pestel.html", {"active_page": "pestel"})


def stratmap(request):
    return render(request, "strategic/stratmap.html", {"active_page": "stratmap"})


def swot(request):
    return render(request, "strategic/swot.html", {"active_page": "swot"})


def risk(request):
    return render(request, "strategic/risk.html", {"active_page": "risk"})
