from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize([
        "strategic/models.py",
        "strategic/views.py",
        "strategic/forms.py",
        "strategic/admin.py",
        "strategic/permission_sections.py",
        "strategic/market_intel_sheets.py",
        "strategic/middleware.py",
        "strategic/context_processors.py",
        "strategic/jalali_utils.py",
        "strategic/license_check.py",
        "strategic/apps.py",
        "strategic/urls.py",
    ], language_level="3")
)
