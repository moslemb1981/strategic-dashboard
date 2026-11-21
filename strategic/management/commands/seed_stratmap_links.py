from django.core.management.base import BaseCommand
from strategic.models import StrategicObjective

# هر ردیف: (کد مبدا, [کدهای مقصد])
# جریان طبیعی BSC: یادگیری و رشد -> فرآیندهای داخلی -> مشتری -> مالی
# سه ستون مطابق سه محور استراتژیک (تعالی عملیاتی / رشد بازار / نوآوری دیجیتال)
LINKS = [
    ("L1", ["P1"]),
    ("L2", ["P2"]),
    ("L3", ["P3"]),
    ("P1", ["C1", "F1"]),
    ("P2", ["C2"]),
    ("P3", ["C3"]),
    ("C1", ["F1", "F2"]),
    ("C2", ["F2"]),
    ("C3", ["F1"]),
]


class Command(BaseCommand):
    help = "رابطه‌های نمونه (این هدف به کدام هدف کمک می‌کند) را بین ۱۲ هدف نمونه برقرار می‌کند تا سیم‌های نقشه استراتژیک قابل مشاهده باشند."

    def handle(self, *args, **options):
        by_code = {o.code: o for o in StrategicObjective.objects.all()}
        missing = set()
        count = 0
        for src_code, dst_codes in LINKS:
            src = by_code.get(src_code)
            if not src:
                missing.add(src_code)
                continue
            for dst_code in dst_codes:
                dst = by_code.get(dst_code)
                if not dst:
                    missing.add(dst_code)
                    continue
                src.feeds_into.add(dst)
                count += 1

        self.stdout.write(self.style.SUCCESS(f"{count} رابطه برقرار شد."))
        if missing:
            self.stdout.write(self.style.WARNING(
                f"این کدها پیدا نشدند (شاید تغییر کرده باشند): {', '.join(sorted(missing))}"
            ))
