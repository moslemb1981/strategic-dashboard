# -*- coding: utf-8 -*-
"""پردازشگرهای context مشترک بین همه‌ی قالب‌ها."""


def locked_sections(request):
    """مجموعه‌ی کلیدهای بخش‌هایی که برای کاربر مهمان قفل شده‌اند — برای نمایش
    آیکن قفل جلوی آیتم مربوطه در منوی کناری (base.html)، مستقل از این‌که کاربر
    فعلی وارد شده باشد یا نه (خود مدیر هم باید علامت قفل را در منو ببیند)."""
    from strategic.models import SectionVisibility
    try:
        keys = set(
            SectionVisibility.objects.filter(is_public=False).values_list("key", flat=True)
        )
    except Exception:
        # جدول ممکن است هنوز مهاجرت نشده باشد (مثلاً هنگام اجرای اولین migrate)
        keys = set()
    return {"locked_section_keys": keys}


def org_branding(request):
    """نام محصول و نام سازمان/اداره/مدیریت برای همه‌ی قالب‌ها (از settings / .env)."""
    from django.conf import settings
    return {
        "product_name": settings.PRODUCT_NAME,
        "product_tagline": settings.PRODUCT_TAGLINE,
        "org_name": settings.ORG_NAME,
        "org_office": settings.ORG_OFFICE_NAME,
        "org_management": settings.ORG_MANAGEMENT_NAME,
    }
