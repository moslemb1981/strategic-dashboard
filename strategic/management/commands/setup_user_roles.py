# -*- coding: utf-8 -*-
"""ساخت سه نقش پیش‌فرض (Group) برای مدیریت کاربران:
- «ویرایشگر»: مجوز افزودن/ویرایش روی مدل‌های اصلی محتوایی سامانه (بدون حذف، بدون مدیریت کاربران)
- «کارشناس (فقط مشاهده)»: بدون هیچ مجوز افزودن/ویرایش/حذف — فقط مشاهده (پیش‌فرض ورود به سامانه)
- ادمین کامل از طریق is_superuser مدیریت می‌شود (نیازی به گروه ندارد)

این دستور idempotent است — اجرای دوباره‌اش مشکلی ایجاد نمی‌کند."""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from strategic.models import (
    Initiative, Stakeholder, Risk, StrategicObjective, CompanyObjective, CompanyKPI,
)


class Command(BaseCommand):
    help = "سه نقش پیش‌فرض (ویرایشگر، کارشناس فقط‌مشاهده) را می‌سازد یا به‌روزرسانی می‌کند."

    def handle(self, *args, **options):
        from strategic.models import OperationalKPI

        editable_models = [
            Initiative, Stakeholder, Risk, StrategicObjective,
            CompanyObjective, CompanyKPI, OperationalKPI,
        ]

        editor_group, _ = Group.objects.get_or_create(name="ویرایشگر")
        editor_perms = []
        for model in editable_models:
            ct = ContentType.objects.get_for_model(model)
            for codename_prefix in ["add", "change"]:
                codename = f"{codename_prefix}_{model._meta.model_name}"
                try:
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    editor_perms.append(perm)
                except Permission.DoesNotExist:
                    pass
        editor_group.permissions.set(editor_perms)

        viewer_group, _ = Group.objects.get_or_create(name="کارشناس (فقط مشاهده)")
        viewer_group.permissions.clear()

        self.stdout.write(self.style.SUCCESS(
            f"آماده شد: گروه «ویرایشگر» با {len(editor_perms)} مجوز، گروه «کارشناس (فقط مشاهده)» بدون مجوز ویرایش."
        ))
