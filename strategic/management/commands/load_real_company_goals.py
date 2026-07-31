# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from strategic.models import CompanyObjective, CompanyKPI

# منبع: «اهداف شرکت سایپا یدک ۱۴۰۵» — شیت‌های «اهداف کلان» و «شاخص‌ها»
# این اهداف/شاخص‌ها سطح کل شرکت‌اند (نه یکی از ۵ کسب‌وکار) و مستقیماً به
# نقشه استراتژیک ۳ ساله گروه سایپا (شرکت مادر) وصل می‌شوند.

OBJECTIVES = [
    {'code': 'O1', 'group_title': 'میزان فروش قطعات یدکی \n( افزایش سهم بازار قطعات یدکی)', 'title': 'افزایش فروش از فروشگاهها، تعمیرگاهها و مشتریان جدید', 'description': 'هدف ، توسعه  فروش مشتقیم به مشتریان نهائی است. این روش مکل فروش از طریق شبکه خواهد بود.', 'order': 0},
    {'code': 'O2', 'group_title': 'میزان فروش قطعات یدکی \n( افزایش سهم بازار قطعات یدکی)', 'title': 'تنوع قطعات و خدمات', 'description': 'تنوع قطعات یدکی و حضور در سگمنتهای مختلف بازر می تواند به فروش بیشتر کمک نماید خصوصا در حوزه آپشن.', 'order': 1},
    {'code': 'O3', 'group_title': 'میزان فروش قطعات یدکی \n( افزایش سهم بازار قطعات یدکی)', 'title': 'قیمت گذاری هوشمند', 'description': 'با توجه به نوسانات شدید ارز و لحظه ای شدن قیمتها، هوشمند سازی قیمت گذاری یک الزام می باشد.', 'order': 2},
    {'code': 'O4', 'group_title': 'میزان فروش قطعات یدکی \n( افزایش سهم بازار قطعات یدکی)', 'title': 'شفافیت و تسهیل برگشت از فروش/ خرید', 'description': 'یکی از نقاط قابل بهبود جهت رقابت با رقبا، سهولت فرایند برگشت از خرید است تا خریداران نگرانی کمتری در حین خرید داشته باشند.', 'order': 3},
    {'code': 'O5', 'group_title': 'ارزيابي كيفيت خدمات پس از فروش', 'title': 'توسعه قابلیتهای ارائه خدمات تخصصی به خودروهای برقی و هیبریدی', 'description': 'در صورتیکه سایپا تصمیم به تولید  خودروهای برقی و هیبریدی بگیرد، آمادگی برای ارائه خدمات به خودروهای مذکور برای سایپا یدک الزامی خواهد بود.', 'order': 4},
    {'code': 'O6', 'group_title': 'ارزيابي كيفيت خدمات پس از فروش', 'title': 'مدیریت بهینه موجودی قطعات', 'description': 'با توجه به مشکلات تامین و محدود بودن موجودی قطعات, به منظور حفظ خدمات حیاطی در شرایط خاص, موجودی قطعات بصورت هوشمند و مستقل از اهداف فروش، مدیریت خواهد شد.', 'order': 5},
    {'code': 'O7', 'group_title': 'ارزيابي كيفيت خدمات پس از فروش', 'title': 'ارائه بسته های خدمت متنوع', 'description': 'تنوع دهی به خدمات، می تواند در توسعه فروش قطعات یدکی و رضایت مشتریان اثر قابل توجهی داشته باشد.', 'order': 6},
    {'code': 'O8', 'group_title': 'ارزيابي كيفيت خدمات پس از فروش', 'title': 'تامین به موقع خدمت گارانتی و ارسال مسئولانه قطعه به نماینده', 'description': 'ارائه خدمات گارنتی مناسب (از منظر QCD) و تامین به موقع قطعات ، اثر بسیاز زیادی در بهبود خدمات گارانتی دارد.', 'order': 7},
    {'code': 'O9', 'group_title': 'افزایش سود', 'title': 'درآمد اتصال قطعه سازان و واردکنندگان به شبکه و مشتری', 'description': 'هدف کسب درآمد و سود از طریق توسعه پلتفرمی است که  قطعه سازان و واردکنندگان را به مشتری نهائی وصل می کند.', 'order': 8},
    {'code': 'O10', 'group_title': 'افزایش سود', 'title': 'قیمت گذاری هوشمند', 'description': 'با توجه به نوسانات شدید ارز و لحظه ای شدن قیمتها، هوشمند سازی قیمت گذاری یک الزام می باشد.', 'order': 9},
    {'code': 'O11', 'group_title': 'افزایش سود', 'title': 'درامد مستقیم از فروشگاهها و تعمیرکاران آزاد', 'description': 'از طریق ورود مستقیم به بازار و ارائه قطعات به مشتریان نهائی و تعمیرکاران آزاد سطح کشور می باشد.', 'order': 10},
    {'code': 'O12', 'group_title': 'افزایش بهره وری و OHE', 'title': 'توسعه رویکرد شایستگی مشاغل، جانشین پروری و شایسته گزینی', 'description': 'توسعه شایستگیها، جانشین پروری و شایسته گزینی از روشهای متداول افزایش بهره وری نیروی انسانی است.', 'order': 11},
    {'code': 'O13', 'group_title': 'افزایش بهره وری و OHE', 'title': 'توسعه فرهنگ بهبود مستمر', 'description': 'نهادینه سازی و توسعه فرهنگ بهبود مستمر در طراحی و اجرای فرایندها، از محورهای اصلی ارتقاء بهرهوری در سایپا یدک می باشد.', 'order': 12},
    {'code': 'O14', 'group_title': 'ارتقای جایگاه برند', 'title': 'ارائه خدمات سفارشی سازی شده', 'description': 'ارائه خدمات سفارشی سازی شده متنالسب با نیاز گروه های خاص مشتریان، می تواند نقش موثری در ارتقاء برند داشته باشد.', 'order': 13},
    {'code': 'O15', 'group_title': 'ارتقای جایگاه برند', 'title': 'تنوع قطعات و خدمات', 'description': 'تنوع قطعات یدکی و حضور در سگمنتهای مختلف بازر می تواند به ارتقاء برند و  فروش بیشتر کمک نماید .', 'order': 14},
    {'code': 'O16', 'group_title': 'ارتقای جایگاه برند', 'title': 'توسعه روابط با مشتریان', 'description': 'CRM خوب و یکی از ابزر ارتقاء برند می باشد.', 'order': 15},
    {'code': 'O17', 'group_title': 'توسعه مدیریت دانش', 'title': 'پایگاه داده مشتریان و مدیریت دانش', 'description': 'ایجاد و مدیریت مناسب پایگاه داده های مرتبط با مشتریان و مدیریت آنها از ابزار مهم مدیرت دانش می باشد.', 'order': 16},
    {'code': 'O18', 'group_title': 'توسعه مدیریت دانش', 'title': 'توسعه رویکرد شایستگی مشاغل، جانشین پروری و شایسته گزینی', 'description': 'توسعه شایستگیها، جانشین پروری و شایسته گزینی از روشهای متداول، حدیریت دانش و افزایش بهره وری  است.', 'order': 17},
    {'code': 'O19', 'group_title': 'توسعه مدیریت دانش', 'title': 'انتقال دانش به ذینفعان اصلی', 'description': 'انتشار و به اشتراک گذاری دانش به همه ذینفعان ، میتواند در حفظ و انتشار دانش کمک قابل توجهی نماید.', 'order': 18},
    {'code': 'O20', 'group_title': 'ارتقای رضایت و نگهداشت کارکنان', 'title': 'توسعه رویکرد شایستگی مشاغل، جانشین پروری و شایسته گزینی', 'description': 'مطابق با نتایج نظر سنجی و رضایت شغلی منابع انسانی، توجه به موضوع شایسه سالاری و رشد سازمانی می تواند تا حد قابل توجهی رضایت کارمنان را بالا ببرد.', 'order': 19},
    {'code': 'O21', 'group_title': 'مدیریت مصرف حاملهای انرژی و آب', 'title': 'الزامات زیست محیطی', 'description': '', 'order': 20},
    {'code': 'O22', 'group_title': 'مدیریت مصرف حاملهای انرژی و آب', 'title': 'مدیریت بهینه مصرف انرژی و ملزومات و مواد مصرفی', 'description': '', 'order': 21},
]

KPIS = [
    {'code': 'I1', 'domain': 'C', 'name': 'فروش کل (برند یک + آپشن + بسته خدمت)', 'unit': 'میلیاردتومان',
     'target_1404': '16500', 'actual_1404': '9425.22', 'target_1405': '27000', 'suggested_target': '20160',
     'related_codes': ['O1', 'O2', 'O3', 'O7'], 'is_monitoring': False, 'notes': '', 'order': 0},
    {'code': 'I2', 'domain': 'C', 'name': 'فروش ریالی قطعات یدکی سایپایدک - برند یک', 'unit': 'میلیارد تومان',
     'target_1404': '15000', 'actual_1404': '8676.14', 'target_1405': '25000', 'suggested_target': '18600',
     'related_codes': ['O1', 'O2', 'O3'], 'is_monitoring': False, 'notes': '', 'order': 1},
    {'code': 'I3', 'domain': 'D', 'name': 'فروش تعدادی قطعات یدکی سایپایدک - برند یک', 'unit': 'عدد',
     'target_1404': '48343665', 'actual_1404': '37409119', 'target_1405': '60000000', 'suggested_target': '55000000',
     'related_codes': ['O1', 'O2', 'O3'], 'is_monitoring': False, 'notes': '', 'order': 2},
    {'code': 'I4', 'domain': 'C', 'name': 'فروش ریالی کارت طلایی اختیاری', 'unit': 'میلیاردتومان',
     'target_1404': '900', 'actual_1404': '447.75', 'target_1405': '1200', 'suggested_target': '910',
     'related_codes': ['O7'], 'is_monitoring': False, 'notes': '', 'order': 3},
    {'code': 'I5', 'domain': 'D', 'name': 'فروش تعدادی کارت طلایی اختیاری', 'unit': 'عدد',
     'target_1404': '230000', 'actual_1404': '132915', 'target_1405': '280000', 'suggested_target': '250000',
     'related_codes': ['O7'], 'is_monitoring': False, 'notes': '', 'order': 4},
    {'code': 'I6', 'domain': 'C', 'name': 'فروش ریالی قطعات آپشن', 'unit': 'میلیاردتومان',
     'target_1404': '600', 'actual_1404': '301.27', 'target_1405': '900', 'suggested_target': '650',
     'related_codes': ['O1', 'O2', 'O3'], 'is_monitoring': False, 'notes': '', 'order': 5},
    {'code': 'I7', 'domain': 'D', 'name': 'فروش تعدادی قطعات آپشن', 'unit': 'عدد',
     'target_1404': '1550000', 'actual_1404': '545984', 'target_1405': '1000000', 'suggested_target': '1000000',
     'related_codes': ['O1', 'O2', 'O3'], 'is_monitoring': False, 'notes': '', 'order': 6},
    {'code': 'I8', 'domain': 'Q', 'name': 'متوسط زمان پذیرش تا ترخیص در شبکه', 'unit': 'روز',
     'target_1404': '1', 'actual_1404': '1.19', 'target_1405': '1', 'suggested_target': '1',
     'related_codes': ['O6', 'O7', 'O8'], 'is_monitoring': False, 'notes': '', 'order': 7},
    {'code': 'I9', 'domain': 'Q', 'name': 'متوسط زمان خواب خودروها در شبکه (با برند گروه در شبکه)', 'unit': 'روز',
     'target_1404': '3', 'actual_1404': '6.5', 'target_1405': '3', 'suggested_target': '8',
     'related_codes': ['O6', 'O8'], 'is_monitoring': False, 'notes': '', 'order': 8},
    {'code': 'I10', 'domain': 'Q', 'name': 'متوسط زمان خواب خودروها در شبکه (با برند همکاران تجاری در شبکه)', 'unit': 'روز',
     'target_1404': '7', 'actual_1404': '6', 'target_1405': '4', 'suggested_target': '10',
     'related_codes': ['O6', 'O8'], 'is_monitoring': False, 'notes': '', 'order': 9},
    {'code': 'I11', 'domain': 'Q', 'name': 'متوسط زمان رسیدگی به شکایات مشتریان از خدمات پس از فروش', 'unit': 'روز',
     'target_1404': '8', 'actual_1404': '8.12', 'target_1405': '6', 'suggested_target': '8',
     'related_codes': ['O6', 'O8'], 'is_monitoring': False, 'notes': '', 'order': 10},
    {'code': 'I12', 'domain': 'D', 'name': 'نسبت خودرو های مشمول پرداخت هزینه خواب به تعداد پذیرش گارانتی', 'unit': 'درصد',
     'target_1404': '0.5', 'actual_1404': '0.49', 'target_1405': '0.4', 'suggested_target': '0.5',
     'related_codes': ['O6', 'O8'], 'is_monitoring': False, 'notes': '', 'order': 11},
    {'code': 'I13', 'domain': 'Q', 'name': 'نرخ برگشت از تعمیرات در شبکه  (2 ماه یا 3000 کیلومتر)', 'unit': 'ppm',
     'target_1404': '10000', 'actual_1404': '10292', 'target_1405': '9000', 'suggested_target': '10000',
     'related_codes': ['O8'], 'is_monitoring': False, 'notes': '', 'order': 12},
    {'code': 'I14', 'domain': 'Q', 'name': 'رضایت مشتریان از خدمات پس از فروش (میانگین وزنی سه خودروساز)', 'unit': 'درصد',
     'target_1404': '82', 'actual_1404': '78.33', 'target_1405': '85.5', 'suggested_target': '80',
     'related_codes': ['O16', 'O8'], 'is_monitoring': False, 'notes': '', 'order': 13},
    {'code': 'I15', 'domain': 'C', 'name': 'فروش خالص ریالی قطعات یدکی برند دو (شرکت همراه خودرو)', 'unit': 'میلیاردتومان',
     'target_1404': '800', 'actual_1404': '257.78', 'target_1405': '1000', 'suggested_target': '800',
     'related_codes': ['O2', 'O15'], 'is_monitoring': False, 'notes': '', 'order': 14},
    {'code': 'I16', 'domain': 'C', 'name': 'نرخ گردش موجودي شركت', 'unit': 'دفعه',
     'target_1404': '4.8', 'actual_1404': '3.46', 'target_1405': '3', 'suggested_target': '4.8',
     'related_codes': ['O6'], 'is_monitoring': False, 'notes': '', 'order': 15},
    {'code': 'I17', 'domain': 'D', 'name': 'دوره وصل مطالبات شبکه', 'unit': 'روز',
     'target_1404': '72', 'actual_1404': '65', 'target_1405': '50', 'suggested_target': '65',
     'related_codes': [], 'is_monitoring': True, 'notes': '', 'order': 16},
    {'code': 'I18', 'domain': 'Q', 'name': 'اثربخشي کلی نیروی انسانی(OHE)(تجمعی)', 'unit': 'میلیارد تومان/نفر',
     'target_1404': '7.7', 'actual_1404': '3.07', 'target_1405': '12.78', 'suggested_target': '6',
     'related_codes': ['O12', 'O13'], 'is_monitoring': False, 'notes': '', 'order': 17},
    {'code': 'I19', 'domain': 'D', 'name': 'تامین صادراتی', 'unit': 'هزار دلار',
     'target_1404': '35.06', 'actual_1404': '35.06', 'target_1405': '60', 'suggested_target': '60',
     'related_codes': ['O9'], 'is_monitoring': False, 'notes': '', 'order': 18},
    {'code': 'I20', 'domain': 'C', 'name': 'ميزان صادرات', 'unit': 'هزار دلار',
     'target_1404': '', 'actual_1404': '', 'target_1405': 'مطابق با ابلاغيه مديريت صادرات گروه', 'suggested_target': '1000',
     'related_codes': ['O1'], 'is_monitoring': False, 'notes': '', 'order': 19},
    {'code': 'I21', 'domain': 'C', 'name': 'ميزان تأمين مالی (از بازار سرمايه و بازار پول)', 'unit': 'ميليارد تومان',
     'target_1404': '0', 'actual_1404': '0', 'target_1405': '0', 'suggested_target': '500',
     'related_codes': [], 'is_monitoring': True, 'notes': '', 'order': 20},
    {'code': 'I22', 'domain': 'Q', 'name': 'کیفیت خدمات پس از فروش', 'unit': 'امتیاز',
     'target_1404': '-', 'actual_1404': '677', 'target_1405': '720', 'suggested_target': '700',
     'related_codes': ['O8'], 'is_monitoring': False, 'notes': '', 'order': 21},
    {'code': 'I23', 'domain': 'M', 'name': 'بازرسی و ارتقای سطح سلامت نظام اداری', 'unit': 'درصد',
     'target_1404': '100', 'actual_1404': '90', 'target_1405': '100', 'suggested_target': '100',
     'related_codes': [], 'is_monitoring': True, 'notes': '', 'order': 22},
    {'code': 'I24', 'domain': 'M', 'name': 'توسعه منابع انسانی (HRD)', 'unit': 'امتياز',
     'target_1404': '100', 'actual_1404': '89', 'target_1405': '100', 'suggested_target': '100',
     'related_codes': ['O13'], 'is_monitoring': False, 'notes': '', 'order': 23},
    {'code': 'I25', 'domain': 'C', 'name': 'امتیاز عملکرد حوزه اقتصادی', 'unit': 'درصد',
     'target_1404': '100', 'actual_1404': '91', 'target_1405': '100', 'suggested_target': '100',
     'related_codes': [], 'is_monitoring': True, 'notes': '', 'order': 24},
    {'code': 'I26', 'domain': 'M', 'name': 'امتیازعملکرد حوزه حقوقی', 'unit': 'درصد',
     'target_1404': '100', 'actual_1404': '95', 'target_1405': '100', 'suggested_target': '100',
     'related_codes': [], 'is_monitoring': True, 'notes': '', 'order': 25},
]


class Command(BaseCommand):
    help = "اهداف کلان و شاخص‌های کلیدی واقعی سطح کل شرکت سایپا یدک (سال ۱۴۰۵) را ثبت/به‌روزرسانی می‌کند."

    def handle(self, *args, **options):
        obj_map = {}
        for o in OBJECTIVES:
            obj, _ = CompanyObjective.objects.update_or_create(
                code=o["code"],
                defaults=dict(
                    group_title=o["group_title"], title=o["title"],
                    description=o["description"], order=o["order"],
                ),
            )
            obj_map[o["code"]] = obj

        for k in KPIS:
            kpi, _ = CompanyKPI.objects.update_or_create(
                code=k["code"],
                defaults=dict(
                    domain=k["domain"], name=k["name"], unit=k["unit"],
                    target_1404=k["target_1404"], actual_1404=k["actual_1404"],
                    target_1405=k["target_1405"],
                    is_monitoring=k["is_monitoring"], notes=k["notes"], order=k["order"],
                ),
            )
            kpi.objectives.set([obj_map[c] for c in k["related_codes"] if c in obj_map])

        self.stdout.write(self.style.SUCCESS(
            f"{len(OBJECTIVES)} هدف کلان و {len(KPIS)} شاخص کلیدی سطح کل شرکت ثبت/به‌روزرسانی شد."
        ))
