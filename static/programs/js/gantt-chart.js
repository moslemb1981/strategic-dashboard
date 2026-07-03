/**
 * گانت چارت - پیاده‌سازی با Highcharts
 * پشتیبانی از تاریخ شمسی و وابستگی‌ها
 */

// رنگ‌های پیش‌فرض برای مراحل مختلف
const GANTT_COLORS = {
    completed: '#2ecc71',     // سبز - تکمیل شده
    in_progress: '#3498db',   // آبی - در حال انجام
    behind: '#e74c3c',        // قرمز - تأخیر داشته
    not_started: '#95a5a6',   // خاکستری - شروع نشده
    high_priority: '#f39c12', // نارنجی - اولویت بالا
    milestone: '#9b59b6'      // بنفش - نقطه عطف
};

/**
 * رندر نمودار گانت برای یک برنامه
 */
function renderGanttChart(ganttData) {
    // تخریب چارت قبلی اگر وجود دارد
    if (window.ganttChart) {
        window.ganttChart.destroy();
    }
    
    // ایجاد چارت گانت
    window.ganttChart = Highcharts.ganttChart('gantt-container', {
        chart: {
            type: 'gantt',
            height: 600,
            scrollablePlotArea: {
                minWidth: 600
            },
            style: {
                fontFamily: 'IRANSans, Tahoma, sans-serif'
            }
        },
        
        title: {
            text: ganttData.title || 'نمودار گانت برنامه',
            align: 'right',
            style: {
                fontSize: '16px',
                fontWeight: 'bold'
            }
        },
        
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%e %b',
                week: '%e %b',
                month: '%b %Y',
                year: '%Y'
            },
            labels: {
                style: {
                    fontSize: '11px'
                }
            },
            min: ganttData.startTimestamp,
            max: ganttData.endTimestamp
        },
        
        yAxis: {
            type: 'category',
            grid: {
                enabled: true,
                borderColor: '#e0e0e0',
                borderWidth: 1
            },
            labels: {
                style: {
                    fontSize: '12px',
                    fontWeight: 'normal'
                }
            },
            categories: ganttData.categories || [],
            title: {
                text: 'مراحل',
                style: {
                    fontSize: '14px',
                    fontWeight: 'bold'
                }
            }
        },
        
        tooltip: {
            useHTML: true,
            formatter: function() {
                const point = this.point;
                const startDate = point.start ? new Date(point.start).toLocaleDateString('fa-IR') : 'تعریف نشده';
                const endDate = point.end ? new Date(point.end).toLocaleDateString('fa-IR') : 'تعریف نشده';
                const progress = point.custom && point.custom.progress ? point.custom.progress : 0;
                
                return `
                    <div style="direction: rtl; text-align: right;">
                        <strong>${point.name}</strong><br>
                        <small>مرحله ${point.custom && point.custom.order ? point.custom.order : ''}</small>
                        <hr style="margin: 5px 0;">
                        <div>
                            <strong>تاریخ شروع:</strong> ${startDate}<br>
                            <strong>تاریخ پایان:</strong> ${endDate}<br>
                            <strong>مدت:</strong> ${point.custom && point.custom.duration ? point.custom.duration : 0} روز<br>
                            <strong>پیشرفت:</strong> ${progress}%<br>
                            <strong>وزن:</strong> ${point.custom && point.custom.weight ? point.custom.weight : 0}
                        </div>
                        ${point.custom && point.custom.description ? 
                            `<hr style="margin: 5px 0;">
                             <div><small>${point.custom.description}</small></div>` : ''}
                    </div>
                `;
            }
        },
        
        plotOptions: {
            series: {
                animation: {
                    duration: 1000
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.name}',
                    style: {
                        fontSize: '11px',
                        fontWeight: 'normal',
                        textOutline: 'none'
                    }
                },
                point: {
                    events: {
                        click: function(event) {
                            // مدیریت کلیک روی مرحله
                            handleStageClick(this.custom && this.custom.stage_id);
                        }
                    }
                }
            }
        },
        
        series: [{
            name: 'مراحل',
            data: ganttData.series || [],
            colorByPoint: true,
            colors: [
                GANTT_COLORS.completed,
                GANTT_COLORS.in_progress,
                GANTT_COLORS.behind,
                GANTT_COLORS.not_started
            ],
            pointPadding: 0.25,
            groupPadding: 0,
            borderColor: '#fff',
            borderWidth: 1
        }],
        
        // وابستگی‌ها
        plotOptions: {
            series: {
                connectEnds: false,
                connectNulls: false
            }
        },
        
        // نوار پیشرفت در داخل هر مرحله
        defs: {
            hatchLeft: {
                tagName: 'pattern',
                id: 'hatch-left',
                patternUnits: 'userSpaceOnUse',
                width: 4,
                height: 4,
                children: [{
                    tagName: 'path',
                    d: 'M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2',
                    strokeWidth: 1,
                    stroke: 'rgba(0,0,0,0.2)'
                }]
            }
        },
        
        // نقاط عطف
        plotOptions: {
            gantt: {
                milestone: {
                    symbol: 'diamond'
                }
            }
        },
        
        // نوار وضعیت در پایین
        navigator: {
            enabled: true,
            series: {
                type: 'gantt',
                pointPadding: 0,
                groupPadding: 0,
                color: 'rgba(94, 124, 224, 0.5)'
            },
            yAxis: {
                min: 0,
                max: 3,
                reversed: true,
                categories: []
            }
        },
        
        scrollbar: {
            enabled: true
        },
        
        rangeSelector: {
            enabled: true,
            selected: 1,
            buttons: [{
                type: 'month',
                count: 1,
                text: '۱ ماه'
            }, {
                type: 'month',
                count: 3,
                text: '۳ ماه'
            }, {
                type: 'year',
                count: 1,
                text: '۱ سال'
            }, {
                type: 'all',
                text: 'همه'
            }],
            buttonTheme: {
                width: 60
            },
            inputEnabled: false
        },
        
        credits: {
            enabled: false
        },
        
        exporting: {
            enabled: true,
            buttons: {
                contextButton: {
                    menuItems: [
                        'viewFullscreen',
                        'printChart',
                        'separator',
                        'downloadPNG',
                        'downloadJPEG',
                        'downloadPDF',
                        'downloadSVG'
                    ]
                }
            }
        },
        
        lang: {
            months: [
                'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
            ],
            weekdays: [
                'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'
            ],
            shortMonths: [
                'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
            ],
            downloadPDF: 'دانلود PDF',
            downloadPNG: 'دانلود PNG',
            downloadJPEG: 'دانلود JPEG',
            downloadSVG: 'دانلود SVG',
            printChart: 'چاپ نمودار',
            viewFullscreen: 'تمام صفحه'
        }
    });
    
    // اضافه کردن وابستگی‌ها اگر وجود دارند
    if (ganttData.dependencies && ganttData.dependencies.length > 0) {
        addDependenciesToChart(ganttData.dependencies);
    }
}

/**
 * رندر نمودار گانت برای کارگروه
 */
function renderWorkgroupGanttChart(ganttData) {
    // تخریب چارت قبلی اگر وجود دارد
    if (window.workgroupGanttChart) {
        window.workgroupGanttChart.destroy();
    }
    
    const viewMode = document.getElementById('viewMode').value;
    const isProgramView = viewMode === 'program';
    
    // تنظیمات بر اساس حالت نمایش
    const yAxisConfig = {
        type: 'category',
        grid: {
            enabled: true,
            borderColor: '#e0e0e0',
            borderWidth: 1
        },
        labels: {
            style: {
                fontSize: '12px',
                fontWeight: 'normal'
            }
        },
        categories: ganttData.categories || [],
        title: {
            text: isProgramView ? 'برنامه‌ها' : 'مراحل',
            style: {
                fontSize: '14px',
                fontWeight: 'bold'
            }
        }
    };
    
    // ایجاد چارت گانت کارگروه
    window.workgroupGanttChart = Highcharts.ganttChart('workgroup-gantt-container', {
        chart: {
            type: 'gantt',
            height: 600,
            scrollablePlotArea: {
                minWidth: 800
            },
            style: {
                fontFamily: 'IRANSans, Tahoma, sans-serif'
            }
        },
        
        title: {
            text: ganttData.title || 'نمودار گانت کارگروه',
            align: 'right',
            style: {
                fontSize: '16px',
                fontWeight: 'bold'
            }
        },
        
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                day: '%e %b',
                week: '%e %b',
                month: '%b %Y',
                year: '%Y'
            },
            labels: {
                style: {
                    fontSize: '11px'
                }
            }
        },
        
        yAxis: yAxisConfig,
        
        tooltip: {
            useHTML: true,
            formatter: function() {
                const point = this.point;
                const startDate = point.start ? new Date(point.start).toLocaleDateString('fa-IR') : 'تعریف نشده';
                const endDate = point.end ? new Date(point.end).toLocaleDateString('fa-IR') : 'تعریف نشده';
                
                if (isProgramView) {
                    return `
                        <div style="direction: rtl; text-align: right;">
                            <strong>${point.name}</strong><br>
                            <small>${point.custom && point.custom.workgroup ? point.custom.workgroup : ''}</small>
                            <hr style="margin: 5px 0;">
                            <div>
                                <strong>تاریخ شروع:</strong> ${startDate}<br>
                                <strong>تاریخ پایان:</strong> ${endDate}<br>
                                <strong>وزن کل:</strong> ${point.custom && point.custom.total_weight ? point.custom.total_weight : 0}<br>
                                <strong>اولویت:</strong> ${point.custom && point.custom.priority ? getPriorityText(point.custom.priority) : 'نامشخص'}<br>
                                <strong>پیشرفت کل:</strong> ${point.custom && point.custom.overall_progress ? point.custom.overall_progress : 0}%
                            </div>
                        </div>
                    `;
                } else {
                    return `
                        <div style="direction: rtl; text-align: right;">
                            <strong>${point.name}</strong><br>
                            <small>${point.custom && point.custom.program ? point.custom.program : ''}</small>
                            <hr style="margin: 5px 0;">
                            <div>
                                <strong>تاریخ شروع:</strong> ${startDate}<br>
                                <strong>تاریخ پایان:</strong> ${endDate}<br>
                                <strong>وزن:</strong> ${point.custom && point.custom.weight ? point.custom.weight : 0}<br>
                                <strong>پیشرفت:</strong> ${point.custom && point.custom.progress ? point.custom.progress : 0}%
                            </div>
                        </div>
                    `;
                }
            }
        },
        
        plotOptions: {
            series: {
                animation: {
                    duration: 1000
                },
                dataLabels: {
                    enabled: true,
                    format: '{point.name}',
                    style: {
                        fontSize: '11px',
                        fontWeight: 'normal',
                        textOutline: 'none'
                    }
                },
                point: {
                    events: {
                        click: function(event) {
                            if (isProgramView && this.custom && this.custom.program_id) {
                                // رفتن به صفحه گانت برنامه
                                window.location.href = `/program/${this.custom.program_id}/gantt/`;
                            }
                        }
                    }
                }
            }
        },
        
        series: [{
            name: isProgramView ? 'برنامه‌ها' : 'مراحل',
            data: ganttData.series || [],
            colorByPoint: true,
            pointPadding: 0.2,
            groupPadding: 0,
            borderColor: '#fff',
            borderWidth: 1
        }],
        
        // رنگ‌بندی بر اساس اولویت
        colors: (function() {
            if (isProgramView) {
                return ganttData.series ? ganttData.series.map(point => {
                    const priority = point.custom && point.custom.priority;
                    switch(priority) {
                        case 1: return '#e74c3c'; // قرمز - اولویت بالا
                        case 2: return '#f39c12'; // نارنجی - اولویت متوسط
                        case 3: return '#3498db'; // آبی - اولویت پایین
                        default: return '#95a5a6'; // خاکستری
                    }
                }) : [];
            }
            return [];
        })(),
        
        navigator: {
            enabled: true,
            series: {
                type: 'gantt',
                pointPadding: 0,
                groupPadding: 0,
                color: 'rgba(94, 124, 224, 0.5)'
            },
            yAxis: {
                min: 0,
                max: 3,
                reversed: true,
                categories: []
            }
        },
        
        scrollbar: {
            enabled: true
        },
        
        rangeSelector: {
            enabled: true,
            selected: 1,
            buttons: [{
                type: 'month',
                count: 1,
                text: '۱ ماه'
            }, {
                type: 'month',
                count: 3,
                text: '۳ ماه'
            }, {
                type: 'year',
                count: 1,
                text: '۱ سال'
            }, {
                type: 'all',
                text: 'همه'
            }],
            buttonTheme: {
                width: 60
            },
            inputEnabled: false
        },
        
        credits: {
            enabled: false
        },
        
        exporting: {
            enabled: true,
            buttons: {
                contextButton: {
                    menuItems: [
                        'viewFullscreen',
                        'printChart',
                        'separator',
                        'downloadPNG',
                        'downloadJPEG',
                        'downloadPDF',
                        'downloadSVG'
                    ]
                }
            }
        },
        
        lang: {
            months: [
                'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
            ],
            weekdays: [
                'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'
            ],
            shortMonths: [
                'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
                'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
            ],
            downloadPDF: 'دانلود PDF',
            downloadPNG: 'دانلود PNG',
            downloadJPEG: 'دانلود JPEG',
            downloadSVG: 'دانلود SVG',
            printChart: 'چاپ نمودار',
            viewFullscreen: 'تمام صفحه'
        }
    });
}

/**
 * اضافه کردن خطوط وابستگی به نمودار
 */
function addDependenciesToChart(dependencies) {
    if (!window.ganttChart || !dependencies || dependencies.length === 0) {
        return;
    }
    
    // ایجاد سری جدید برای وابستگی‌ها
    const dependencySeries = {
        type: 'line',
        name: 'وابستگی‌ها',
        data: [],
        color: '#7cb5ec',
        lineWidth: 2,
        dashStyle: 'Dash',
        marker: {
            enabled: false
        },
        enableMouseTracking: false
    };
    
    // تبدیل وابستگی‌ها به نقاط خط
    dependencies.forEach(dep => {
        dependencySeries.data.push({
            x: dep.fromX,
            y: dep.fromY,
            x2: dep.toX,
            y2: dep.toY
        });
    });
    
    window.ganttChart.addSeries(dependencySeries);
}

/**
 * مدیریت کلیک روی مرحله
 */
function handleStageClick(stageId) {
    if (!stageId) return;
    
    // نمایش اطلاعات بیشتر یا ویرایش مرحله
    const modal = new bootstrap.Modal(document.getElementById('stageDetailsModal'));
    // در اینجا می‌توان اطلاعات مرحله را بارگذاری کرد
    console.log('Clicked on stage:', stageId);
}

/**
 * تبدیل متن اولویت
 */
function getPriorityText(priority) {
    switch(priority) {
        case 1: return 'بالا';
        case 2: return 'متوسط';
        case 3: return 'پایین';
        default: return 'نامشخص';
    }
}

/**
 * فرمت تاریخ برای Highcharts
 */
function formatDateForHighcharts(jalaliDate) {
    // این تابع باید تاریخ شمسی را به timestamp تبدیل کند
    // در حال حاضر از timestamp دریافتی از بک‌اند استفاده می‌کنیم
    return Date.parse(jalaliDate);
}

/**
 * تنظیمات عمومی برای Highcharts
 */
Highcharts.setOptions({
    lang: {
        loading: 'در حال بارگذاری...',
        months: [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ],
        weekdays: [
            'یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'
        ],
        shortMonths: [
            'فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور',
            'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'
        ],
        exportButtonTitle: "خروجی",
        printButtonTitle: "چاپ",
        rangeSelectorFrom: "از",
        rangeSelectorTo: "تا",
        rangeSelectorZoom: "بازه",
        downloadCSV: 'دانلود CSV',
        downloadXLS: 'دانلود XLS',
        viewData: 'مشاهده داده‌ها',
        hideData: 'مخفی کردن داده‌ها'
    }
});