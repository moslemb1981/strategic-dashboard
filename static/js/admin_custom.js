// static/js/admin_custom.js

(function($) {
    $(document).ready(function() {
        // پیدا کردن جدول اصلی در صفحه ادمین
        var changelistTable = $('#changelist table');

        if (changelistTable.length) {
            // تنظیم اندازه فونت کلی جدول به 0.85em
            changelistTable.css('font-size', '0.85em');

            // تنظیمات برای جلوگیری از شکستن متن و تنظیم عرض ستون‌ها
            changelistTable.find('thead th, tbody td').css({
                'white-space': 'nowrap', // جلوگیری از شکستن خط در محتوای سلول
                'vertical-align': 'middle',
                'padding': '6px 4px', // کمی فشرده‌تر کردن padding
            });

            // تنظیم عرض تقریبی برای ستون‌های مختلف به صورت دستی
            // این مقادیر را می‌توانید بر اساس نیاز خودتان تنظیم کنید
            changelistTable.find('th.column-unique_code, td.field-unique_code').css('width', '100px');
            changelistTable.find('th.column-title, td.field-title').css('width', '200px'); // عنوان شاخص، کمی پهن‌تر
            changelistTable.find('th.column-owner, td.field-owner').css('width', '150px');
            changelistTable.find('th.column-unit, td.field-unit').css('width', '120px');
            changelistTable.find('th.column-direction, td.field-direction').css('width', '100px');
            changelistTable.find('th.column-monitoring_period_type, td.field-monitoring_period_type').css('width', '160px');
            changelistTable.find('th.column-updated_at, td.field-updated_at').css('width', '130px');

            // اگر ستون‌های دیگری دارید، می‌توانید به همین ترتیب عرضشان را تنظیم کنید
            // مثال: اگر ستون 'level' دارید
            // changelistTable.find('th.column-level, td.field-level').css('width', '100px');

            // برای اطمینان از اینکه همه سلول‌ها عرض ثابت داشته باشند، می‌توانیم
            // یک rule کلی برای سلول‌ها تعریف کنیم که اگر محتوا زیاد بود، با ... نمایش داده شود
            // این کار را با overflow و text-overflow انجام می‌دهیم
            changelistTable.find('td').css({
                'max-width': '0', // این برای جلوگیری از کشیده شدن بیش از حد سلول‌ها لازم است
                'overflow': 'hidden',
                'text-overflow': 'ellipsis'
            });

            // ممکن است لازم باشد عرض سرتیترها (th) را هم تنظیم کنید تا با سلول‌ها همخوانی داشته باشد
            changelistTable.find('th').css({
                 'overflow': 'hidden',
                 'text-overflow': 'ellipsis'
            });
        }
    });
})(django.jQuery);
