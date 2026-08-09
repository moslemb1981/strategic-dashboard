# -*- coding: utf-8 -*-
"""اتصال دو محور سناریو به پیشران معادلشان در ماتریس اثر متقابل."""
from django.core.management.base import BaseCommand
from strategic.models import ScenarioAxes, CrossImpactFactor


class Command(BaseCommand):
    help = "دو محور عدم‌قطعیت سناریو را به پیشران معادلشان در ماتریس اثر متقابل وصل می‌کند."

    def handle(self, *args, **options):
        axes, _ = ScenarioAxes.objects.get_or_create(pk=1)
        axis1_source = CrossImpactFactor.objects.filter(text="تأمین منابع مالی").first()
        axis2_source = CrossImpactFactor.objects.filter(text="ارتباطات بین‌المللی").first()

        linked = 0
        if axis1_source:
            axes.axis1_source = axis1_source
            linked += 1
        if axis2_source:
            axes.axis2_source = axis2_source
            linked += 1
        axes.save()

        self.stdout.write(self.style.SUCCESS(f"ثبت شد: {linked} محور به پیشران ماتریس اثر متقابل وصل شد."))
