from django.apps import AppConfig


class StrategicConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "strategic"

    def ready(self):
        from .license_check import check_license
        check_license()
        # جلوگیری از ورود دوباره‌ی حروف عربی (ي، ك) هنگام ذخیره‌ی هر رکورد
        from django.db import models as _m
        from django.db.models.signals import pre_save

        _map = str.maketrans({"ي": "ی", "ى": "ی", "ك": "ک"})

        def _normalize(sender, instance, **kwargs):
            if sender._meta.app_label != "strategic":
                return
            for f in sender._meta.concrete_fields:
                if isinstance(f, (_m.CharField, _m.TextField)) and not f.choices:
                    v = getattr(instance, f.attname, None)
                    if isinstance(v, str) and ("ي" in v or "ك" in v or "ى" in v):
                        setattr(instance, f.attname, v.translate(_map))

        pre_save.connect(_normalize, dispatch_uid="strategic_normalize_persian", weak=False)
