/**
 * تاریخ‌پیکر شمسی (جلالی)
 * پیاده‌سازی ساده و سبک برای انتخاب تاریخ
 */

class JalaliDatepicker {
    constructor(inputElement, options = {}) {
        this.input = inputElement;
        this.options = {
            format: 'YYYY/MM/DD',
            autoClose: true,
            showToday: true,
            showClear: true,
            position: 'bottom-right',
            ...options
        };
        
        this.date = null;
        this.calendarContainer = null;
        this.isOpen = false;
        
        this.init();
    }
    
    init() {
        // ایجاد تقویم
        this.createCalendar();
        
        // رویداد کلیک روی input
        this.input.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        this.input.addEventListener('focus', () => {
            this.show();
        });
        
        // بستن تقویم با کلیک خارج
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.calendarContainer.contains(e.target) && e.target !== this.input) {
                this.hide();
            }
        });
        
        // مقدار اولیه از input
        if (this.input.value) {
            this.setDateFromString(this.input.value);
        }
    }
    
    createCalendar() {
        // ایجاد کانتینر اصلی
        this.calendarContainer = document.createElement('div');
        this.calendarContainer.className = 'jalali-datepicker';
        this.calendarContainer.style.cssText = `
            position: absolute;
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            padding: 10px;
            z-index: 9999;
            font-family: 'IRANSans', Tahoma, sans-serif;
            direction: rtl;
            display: none;
            min-width: 280px;
        `;
        
        // هدر تقویم
        const header = document.createElement('div');
        header.className = 'datepicker-header';
        header.style.cssText = `
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        `;
        
        // دکمه‌های ماه قبل/بعد
        const prevBtn = this.createButton('‹', 'قبلی', () => this.prevMonth());
        const nextBtn = this.createButton('›', 'بعدی', () => this.nextMonth());
        
        // نمایش ماه و سال
        const monthYear = document.createElement('div');
        monthYear.className = 'month-year';
        monthYear.style.cssText = `
            font-weight: bold;
            font-size: 14px;
        `;
        
        // بخش روزهای هفته
        const weekDays = document.createElement('div');
        weekDays.className = 'week-days';
        weekDays.style.cssText = `
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
            margin-bottom: 5px;
            text-align: center;
            font-size: 12px;
            color: #666;
        `;
        
        const daysOfWeek = ['ش', 'ی', 'د', 'س', 'چ', 'پ', 'ج'];
        daysOfWeek.forEach(day => {
            const dayElement = document.createElement('div');
            dayElement.textContent = day;
            weekDays.appendChild(dayElement);
        });
        
        // کانتینر روزها
        const daysContainer = document.createElement('div');
        daysContainer.className = 'days-container';
        daysContainer.style.cssText = `
            display: grid;
            grid-template-columns: repeat(7, 1fr);
            gap: 5px;
        `;
        
        // فوتر تقویم
        const footer = document.createElement('div');
        footer.className = 'datepicker-footer';
        footer.style.cssText = `
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #eee;
            display: flex;
            justify-content: space-between;
        `;
        
        // دکمه امروز
        if (this.options.showToday) {
            const todayBtn = this.createButton('امروز', 'امروز', () => this.setToday());
            todayBtn.className = 'btn-today';
            todayBtn.style.cssText = `
                padding: 5px 10px;
                font-size: 12px;
            `;
            footer.appendChild(todayBtn);
        }
        
        // دکمه پاک کردن
        if (this.options.showClear) {
            const clearBtn = this.createButton('پاک کردن', 'پاک کردن', () => this.clear());
            clearBtn.className = 'btn-clear';
            clearBtn.style.cssText = `
                padding: 5px 10px;
                font-size: 12px;
                color: #dc3545;
            `;
            footer.appendChild(clearBtn);
        }
        
        // مونتاژ اجزا
        header.appendChild(prevBtn);
        header.appendChild(monthYear);
        header.appendChild(nextBtn);
        
        this.calendarContainer.appendChild(header);
        this.calendarContainer.appendChild(weekDays);
        this.calendarContainer.appendChild(daysContainer);
        this.calendarContainer.appendChild(footer);
        
        // ذخیره ارجاع‌ها
        this.monthYearElement = monthYear;
        this.daysContainer = daysContainer;
        
        // اضافه کردن به DOM
        document.body.appendChild(this.calendarContainer);
        
        // بارگذاری اولیه
        this.renderCalendar();
    }
    
    createButton(text, title, onClick) {
        const button = document.createElement('button');
        button.textContent = text;
        button.title = title;
        button.style.cssText = `
            background: none;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            padding: 5px 10px;
            cursor: pointer;
            font-family: inherit;
            font-size: 12px;
        `;
        
        button.addEventListener('click', (e) => {
            e.stopPropagation();
            onClick();
        });
        
        button.addEventListener('mouseenter', () => {
            button.style.backgroundColor = '#f8f9fa';
        });
        
        button.addEventListener('mouseleave', () => {
            button.style.backgroundColor = '';
        });
        
        return button;
    }
    
    renderCalendar() {
        const now = new Date();
        const currentDate = this.date ? this.toGregorian(this.date) : now;
        
        // تنظیم ماه و سال
        const jalaliDate = this.date || this.toJalali(now);
        this.monthYearElement.textContent = `${this.getMonthName(jalaliDate.month)} ${jalaliDate.year}`;
        
        // پاک کردن روزهای قبلی
        this.daysContainer.innerHTML = '';
        
        // روز اول ماه
        const firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
        const jalaliFirstDay = this.toJalali(firstDayOfMonth);
        
        // تعداد روزهای ماه
        const daysInMonth = this.getDaysInJalaliMonth(jalaliDate.year, jalaliDate.month);
        
        // روز اول هفته (0 = شنبه، 6 = جمعه)
        const firstDayWeek = (jalaliFirstDay.day + 1) % 7;
        
        // روزهای خالی قبل
        for (let i = 0; i < firstDayWeek; i++) {
            const emptyDay = document.createElement('div');
            emptyDay.style.cssText = `
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
            `;
            this.daysContainer.appendChild(emptyDay);
        }
        
        // روزهای ماه
        for (let day = 1; day <= daysInMonth; day++) {
            const dayElement = document.createElement('div');
            dayElement.textContent = day;
            dayElement.style.cssText = `
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                border-radius: 4px;
                font-size: 13px;
                transition: all 0.2s;
            `;
            
            // بررسی اگر روز امروز است
            const today = this.toJalali(now);
            if (jalaliDate.year === today.year && 
                jalaliDate.month === today.month && 
                day === today.day) {
                dayElement.style.backgroundColor = '#007bff';
                dayElement.style.color = 'white';
            }
            
            // بررسی اگر روز انتخاب شده است
            if (this.date && 
                this.date.year === jalaliDate.year && 
                this.date.month === jalaliDate.month && 
                this.date.day === day) {
                dayElement.style.backgroundColor = '#28a745';
                dayElement.style.color = 'white';
            }
            
            dayElement.addEventListener('click', () => {
                this.selectDay(day);
            });
            
            dayElement.addEventListener('mouseenter', () => {
                if (!dayElement.style.backgroundColor) {
                    dayElement.style.backgroundColor = '#f8f9fa';
                }
            });
            
            dayElement.addEventListener('mouseleave', () => {
                if (!dayElement.style.backgroundColor.includes('007bff') && 
                    !dayElement.style.backgroundColor.includes('28a745')) {
                    dayElement.style.backgroundColor = '';
                }
            });
            
            this.daysContainer.appendChild(dayElement);
        }
    }
    
    selectDay(day) {
        const jalaliDate = this.date || this.toJalali(new Date());
        this.date = {
            year: jalaliDate.year,
            month: jalaliDate.month,
            day: day
        };
        
        // به‌روزرسانی input
        this.updateInput();
        
        // رندر مجدد
        this.renderCalendar();
        
        // بستن اگر autoClose فعال باشد
        if (this.options.autoClose) {
            setTimeout(() => this.hide(), 100);
        }
        
        // رویداد تغییر
        this.input.dispatchEvent(new Event('change'));
    }
    
    prevMonth() {
        if (!this.date) {
            this.date = this.toJalali(new Date());
        }
        
        if (this.date.month === 1) {
            this.date.year--;
            this.date.month = 12;
        } else {
            this.date.month--;
        }
        
        this.renderCalendar();
    }
    
    nextMonth() {
        if (!this.date) {
            this.date = this.toJalali(new Date());
        }
        
        if (this.date.month === 12) {
            this.date.year++;
            this.date.month = 1;
        } else {
            this.date.month++;
        }
        
        this.renderCalendar();
    }
    
    setToday() {
        this.date = this.toJalali(new Date());
        this.updateInput();
        this.renderCalendar();
        
        if (this.options.autoClose) {
            setTimeout(() => this.hide(), 100);
        }
        
        this.input.dispatchEvent(new Event('change'));
    }
    
    clear() {
        this.date = null;
        this.input.value = '';
        this.renderCalendar();
        this.input.dispatchEvent(new Event('change'));
    }
    
    updateInput() {
        if (this.date) {
            const formatted = this.formatDate(this.date);
            this.input.value = formatted;
        }
    }
    
    setDateFromString(dateString) {
        // فرض بر این است که فرمت YYYY/MM/DD است
        const parts = dateString.split('/');
        if (parts.length === 3) {
            this.date = {
                year: parseInt(parts[0]),
                month: parseInt(parts[1]),
                day: parseInt(parts[2])
            };
            this.renderCalendar();
        }
    }
    
    formatDate(date) {
        const year = date.year.toString().padStart(4, '0');
        const month = date.month.toString().padStart(2, '0');
        const day = date.day.toString().padStart(2, '0');
        
        return this.options.format
            .replace('YYYY', year)
            .replace('MM', month)
            .replace('DD', day);
    }
    
    getMonthName(month) {
        const months = [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ];
        return months[month - 1] || '';
    }
    
    getDaysInJalaliMonth(year, month) {
        // یک پیاده‌سازی ساده - برای دقت بیشتر نیاز به الگوریتم دقیق داریم
        if (month <= 6) return 31;
        if (month <= 11) return 30;
        // اسفند
        const isLeap = this.isJalaliLeapYear(year);
        return isLeap ? 30 : 29;
    }
    
    isJalaliLeapYear(year) {
        // الگوریتم تشخیص کبیسه بودن سال شمسی
        const remainder = (year + 2346) * 683;
        const fraction = (remainder % 2820) / 2820;
        return fraction < 0.179;
    }
    
    toJalali(gregorianDate) {
        // تبدیل تاریخ میلادی به شمسی (پیاده‌سازی ساده)
        // برای دقت بالا باید از کتابخانه کامل استفاده شود
        const gYear = gregorianDate.getFullYear();
        const gMonth = gregorianDate.getMonth() + 1;
        const gDay = gregorianDate.getDate();
        
        // این یک تبدیل ساده است - برای پروژه واقعی از کتابخانه استفاده کنید
        const jalaliYear = gYear - 621;
        let jalaliMonth, jalaliDay;
        
        // محاسبه ماه و روز (تقریبی)
        if (gMonth <= 3) {
            jalaliMonth = gMonth + 9;
            jalaliDay = gDay + 21;
        } else {
            jalaliMonth = gMonth - 3;
            jalaliDay = gDay + 20;
        }
        
        // تنظیم در صورت تجاوز از روزهای ماه
        if (jalaliDay > 31 && jalaliMonth <= 6) {
            jalaliDay -= 31;
            jalaliMonth++;
        } else if (jalaliDay > 30 && jalaliMonth > 6 && jalaliMonth < 12) {
            jalaliDay -= 30;
            jalaliMonth++;
        } else if (jalaliDay > 29 && jalaliMonth === 12) {
            const isLeap = this.isJalaliLeapYear(jalaliYear);
            jalaliDay -= isLeap ? 30 : 29;
            jalaliMonth = 1;
            jalaliYear++;
        }
        
        return {
            year: jalaliYear,
            month: jalaliMonth,
            day: jalaliDay
        };
    }
    
    toGregorian(jalaliDate) {
        // تبدیل تاریخ شمسی به میلادی (پیاده‌سازی ساده)
        const jYear = jalaliDate.year;
        const jMonth = jalaliDate.month;
        const jDay = jalaliDate.day;
        
        // این یک تبدیل ساده است
        const gregorianYear = jYear + 621;
        let gregorianMonth, gregorianDay;
        
        if (jMonth <= 9) {
            gregorianMonth = jMonth + 3;
            gregorianDay = jDay - 20;
        } else {
            gregorianMonth = jMonth - 9;
            gregorianDay = jDay - 21;
        }
        
        // تنظیم در صورت منفی بودن روز
        if (gregorianDay <= 0) {
            gregorianMonth--;
            if (gregorianMonth <= 0) {
                gregorianMonth += 12;
                gregorianYear--;
            }
            
            // اضافه کردن روزهای ماه قبل
            const daysInPrevMonth = this.getDaysInGregorianMonth(gregorianYear, gregorianMonth);
            gregorianDay += daysInPrevMonth;
        }
        
        return new Date(gregorianYear, gregorianMonth - 1, gregorianDay);
    }
    
    getDaysInGregorianMonth(year, month) {
        return new Date(year, month, 0).getDate();
    }
    
    show() {
        if (this.isOpen) return;
        
        this.isOpen = true;
        this.calendarContainer.style.display = 'block';
        
        // موقعیت‌یابی
        this.positionCalendar();
    }
    
    hide() {
        if (!this.isOpen) return;
        
        this.isOpen = false;
        this.calendarContainer.style.display = 'none';
    }
    
    toggle() {
        if (this.isOpen) {
            this.hide();
        } else {
            this.show();
        }
    }
    
    positionCalendar() {
        const rect = this.input.getBoundingClientRect();
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;
        
        let top, left;
        
        switch (this.options.position) {
            case 'top-left':
                top = rect.top + scrollTop - this.calendarContainer.offsetHeight - 5;
                left = rect.left + scrollLeft;
                break;
            case 'top-right':
                top = rect.top + scrollTop - this.calendarContainer.offsetHeight - 5;
                left = rect.left + scrollLeft + rect.width - this.calendarContainer.offsetWidth;
                break;
            case 'bottom-left':
                top = rect.top + scrollTop + rect.height + 5;
                left = rect.left + scrollLeft;
                break;
            case 'bottom-right':
            default:
                top = rect.top + scrollTop + rect.height + 5;
                left = rect.left + scrollLeft + rect.width - this.calendarContainer.offsetWidth;
        }
        
        // اطمینان از نمایش در viewport
        const viewportWidth = window.innerWidth;
        const viewportHeight = window.innerHeight;
        
        if (left + this.calendarContainer.offsetWidth > viewportWidth) {
            left = viewportWidth - this.calendarContainer.offsetWidth - 10;
        }
        
        if (left < 10) {
            left = 10;
        }
        
        if (top + this.calendarContainer.offsetHeight > viewportHeight + scrollTop) {
            top = rect.top + scrollTop - this.calendarContainer.offsetHeight - 5;
        }
        
        if (top < scrollTop + 10) {
            top = scrollTop + 10;
        }
        
        this.calendarContainer.style.top = `${top}px`;
        this.calendarContainer.style.left = `${left}px`;
    }
    
    destroy() {
        if (this.calendarContainer && this.calendarContainer.parentNode) {
            this.calendarContainer.parentNode.removeChild(this.calendarContainer);
        }
        
        this.input.removeEventListener('click', this.show);
        document.removeEventListener('click', this.hide);
    }
}

// راه‌اندازی خودکار برای تمام inputهای با کلاس jalali-datepicker
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.jalali-datepicker').forEach(input => {
        new JalaliDatepicker(input);
    });
});

// صادر کردن کلاس برای استفاده در ماژول‌ها
if (typeof module !== 'undefined' && module.exports) {
    module.exports = JalaliDatepicker;
} else {
    window.JalaliDatepicker = JalaliDatepicker;
}