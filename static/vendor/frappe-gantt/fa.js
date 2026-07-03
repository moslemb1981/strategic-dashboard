// static/vendor/frappe-gantt/fa.js
// فایل زبان فارسی برای frappe-gantt

const fa_lang = {
    name: 'fa',
    weekdays: ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'],
    weekdaysShort: ['ی', 'د', 'س', 'چ', 'پ', 'ج', 'ش'],
    weekdaysMin: ['ی', 'د', 'س', 'چ', 'پ', 'ج', 'ش'],
    months: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'],
    monthsShort: ['فر', 'ار', 'خر', 'تی', 'مر', 'شه', 'مه', 'آب', 'آذ', 'دی', 'به', 'اس'],
    weekStart: 6,
    yearStart: 1,
    formats: {
        LT: 'HH:mm',
        LTS: 'HH:mm:ss',
        L: 'YYYY/MM/DD',
        LL: 'D MMMM YYYY',
        LLL: 'D MMMM YYYY HH:mm',
        LLLL: 'dddd, D MMMM YYYY HH:mm'
    },
    relativeTime: {
        future: 'در %s',
        past: '%s پیش',
        s: 'چند ثانیه',
        m: 'یک دقیقه',
        mm: '%d دقیقه',
        h: 'یک ساعت',
        hh: '%d ساعت',
        d: 'یک روز',
        dd: '%d روز',
        M: 'یک ماه',
        MM: '%d ماه',
        y: 'یک سال',
        yy: '%d سال'
    },
    ordinal: function(n) {
        return n;
    }
};

// اضافه کردن به Gantt
if (typeof Gantt !== 'undefined') {
    Gantt.month_names = Gantt.month_names || {};
    Gantt.month_names['fa'] = fa_lang.monthsShort;
    
    Gantt.day_names = Gantt.day_names || {};
    Gantt.day_names['fa'] = fa_lang.weekdaysMin;
    
    Gantt.lang = 'fa';
}