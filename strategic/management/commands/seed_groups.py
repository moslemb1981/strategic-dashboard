from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from strategic.models import (
    Study, Initiative, Risk, SWOTItem, StrategicObjective, Competitor, PestelFactor,
)

MODELS = [Study, Initiative, Risk, SWOTItem, StrategicObjective, Competitor, PestelFactor]


class Command(BaseCommand):
    help = (
        "دو گروه کاربری می‌سازد: «ویرایشگران» (افزودن/ویرایش/حذف در همه ماژول‌ها) "
        "و «بینندگان» (فقط مشاهده، بدون امکان تغییر). اجرای دوباره امن است."
    )

    def handle(self, *args, **options):
        editors, _ = Group.objects.get_or_create(name="ویرایشگران")
        viewers, _ = Group.objects.get_or_create(name="بینندگان")

        edit_perms = []
        for model in MODELS:
            ct = ContentType.objects.get_for_model(model)
            for action in ("add", "change", "delete"):
                codename = f"{action}_{model._meta.model_name}"
                perm = Permission.objects.filter(content_type=ct, codename=codename).first()
                if perm:
                    edit_perms.append(perm)

        editors.permissions.set(edit_perms)
        viewers.permissions.clear()  # فقط مشاهده — هیچ مجوز افزودن/ویرایش/حذفی ندارد

        self.stdout.write(self.style.SUCCESS(
            f"گروه «ویرایشگران» با {len(edit_perms)} مجوز آماده شد.\n"
            f"گروه «بینندگان» بدون مجوز ویرایش آماده شد (فقط مشاهده).\n"
            f"حالا از پنل ادمین → Users، هر کاربر را به یکی از این دو گروه اضافه کنید."
        ))
