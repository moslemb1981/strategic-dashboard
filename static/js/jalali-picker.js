(function () {
  "use strict";

  var MONTH_NAMES = ["فروردین","اردیبهشت","خرداد","تیر","مرداد","شهریور","مهر","آبان","آذر","دی","بهمن","اسفند"];
  var WEEK_DAYS = ["ش","ی","د","س","چ","پ","ج"]; // شنبه تا جمعه
  var PERSIAN_DIGITS = "۰۱۲۳۴۵۶۷۸۹";

  function toPersianDigits(str) {
    return String(str).replace(/[0-9]/g, function (d) { return PERSIAN_DIGITS[d]; });
  }
  function toEnglishDigits(str) {
    return String(str).replace(/[۰-۹]/g, function (d) { return String(PERSIAN_DIGITS.indexOf(d)); });
  }
  function pad2(n) { return n < 10 ? "0" + n : "" + n; }

  // ---- Jalaali <-> Gregorian conversion (standard public algorithm) ----
  function div(a, b) { return ~~(a / b); }
  function mod(a, b) { return a - ~~(a / b) * b; }

  var breaks = [-61, 9, 38, 199, 426, 686, 756, 818, 1111, 1181, 1210, 1635, 2060, 2097, 2192, 2262, 2324, 2394, 2456, 3178];

  function jalCal(jy) {
    var bl = breaks.length, gy = jy + 621, leapJ = -14, jp = breaks[0], jm, jump, leap, leapG, march, n, i;
    for (i = 1; i < bl; i += 1) {
      jm = breaks[i];
      jump = jm - jp;
      if (jy < jm) break;
      leapJ = leapJ + div(jump, 33) * 8 + div(mod(jump, 33), 4);
      jp = jm;
    }
    n = jy - jp;
    leapJ = leapJ + div(n, 33) * 8 + div(mod(n, 33) + 3, 4);
    if (mod(jump, 33) === 4 && jump - n === 4) leapJ += 1;
    leapG = div(gy, 4) - div((div(gy, 100) + 1) * 3, 4) - 150;
    march = 20 + leapJ - leapG;
    if (jump - n < 6) n = n - jump + div(jump + 4, 33) * 33;
    leap = mod(mod(n + 1, 33) - 1, 4);
    if (leap === -1) leap = 4;
    return { leap: leap, gy: gy, march: march };
  }
  function isLeapJalaaliYear(jy) { return jalCal(jy).leap === 0; }

  function g2d(gy, gm, gd) {
    var d = div((gy + div(gm - 8, 6) + 100100) * 1461, 4) + div(153 * mod(gm + 9, 12) + 2, 5) + gd - 34840408;
    d = d - div(div(gy + 100100 + div(gm - 8, 6), 100) * 3, 4) + 752;
    return d;
  }
  function d2g(jdn) {
    var j = 4 * jdn + 139361631;
    j = j + div(div(4 * jdn + 183187720, 146097) * 3, 4) * 4 - 3908;
    var i = div(mod(j, 1461), 4) * 5 + 308;
    var gd = div(mod(i, 153), 5) + 1;
    var gm = mod(div(i, 153), 12) + 1;
    var gy = div(j, 1461) - 100100 + div(8 - gm, 6);
    return { gy: gy, gm: gm, gd: gd };
  }
  function j2d(jy, jm, jd) {
    var r = jalCal(jy);
    return g2d(r.gy, 3, r.march) + (jm - 1) * 31 - div(jm, 7) * (jm - 7) + jd - 1;
  }
  function d2j(jdn) {
    var gy = d2g(jdn).gy, jy = gy - 621, r = jalCal(jy), jdn1f = g2d(gy, 3, r.march), jd, jm, k;
    k = jdn - jdn1f;
    if (k >= 0) {
      if (k <= 185) { jm = 1 + div(k, 31); jd = mod(k, 31) + 1; return { jy: jy, jm: jm, jd: jd }; }
      k -= 186;
    } else {
      jy -= 1; k += 179;
      if (r.leap === 1) k += 1;
    }
    jm = 7 + div(k, 30); jd = mod(k, 30) + 1;
    return { jy: jy, jm: jm, jd: jd };
  }
  function toJalaali(gy, gm, gd) { return d2j(g2d(gy, gm, gd)); }
  function toGregorian(jy, jm, jd) { return d2g(j2d(jy, jm, jd)); }
  function jalaaliMonthLength(jy, jm) {
    if (jm <= 6) return 31;
    if (jm <= 11) return 30;
    return isLeapJalaaliYear(jy) ? 30 : 29;
  }
  function todayJalaali() {
    var now = new Date();
    return toJalaali(now.getFullYear(), now.getMonth() + 1, now.getDate());
  }

  // ---- Popup UI ----
  var STYLE_ID = "jalali-picker-style";
  if (!document.getElementById(STYLE_ID)) {
    var style = document.createElement("style");
    style.id = STYLE_ID;
    style.textContent =
      ".jp-popup{position:absolute;z-index:500;background:#fff;border:1px solid #E2DED2;border-radius:10px;" +
      "box-shadow:0 8px 24px rgba(0,0,0,.16);padding:10px;width:230px;direction:rtl;font-family:inherit;}" +
      ".jp-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;}" +
      ".jp-nav{border:none;background:#F5F4EF;border-radius:6px;padding:5px 10px;cursor:pointer;font-size:11px;color:#1B2430;}" +
      ".jp-nav:hover{background:#E3EBF2;}" +
      ".jp-title{font-size:12px;font-weight:700;color:#1B2430;}" +
      ".jp-grid{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;}" +
      ".jp-wd{text-align:center;font-size:9.5px;color:#8B93A1;padding:4px 0;}" +
      ".jp-day{border:none;background:none;border-radius:6px;padding:6px 0;font-size:11px;cursor:pointer;color:#1B2430;}" +
      ".jp-day:hover{background:#E3EBF2;}" +
      ".jp-day.jp-today{background:#F5E6D3;font-weight:700;}" +
      ".jp-day.jp-blank{cursor:default;}" +
      ".jp-footer{text-align:center;margin-top:6px;}" +
      ".jp-today-btn{border:none;background:none;color:#2E5C8A;font-size:10.5px;cursor:pointer;text-decoration:underline;}";
    document.head.appendChild(style);
  }

  var activePopup = null;
  var outsideHandler = null;

  function closePopup() {
    if (activePopup) { activePopup.remove(); activePopup = null; }
    if (outsideHandler) { document.removeEventListener("click", outsideHandler); outsideHandler = null; }
  }

  function openPopup(input) {
    closePopup();
    var today = todayJalaali();
    var raw = toEnglishDigits(input.value || "").trim();
    var m = raw.match(/^(\d{4})[\/\-](\d{1,2})[\/\-](\d{1,2})$/);
    var viewYear = today.jy, viewMonth = today.jm, selYear = null, selMonth = null, selDay = null;
    if (m) {
      viewYear = parseInt(m[1], 10); viewMonth = parseInt(m[2], 10);
      selYear = viewYear; selMonth = viewMonth; selDay = parseInt(m[3], 10);
    }

    var pop = document.createElement("div");
    pop.className = "jp-popup";

    function render() {
      pop.innerHTML = "";

      var header = document.createElement("div");
      header.className = "jp-header";
      var nextBtn = document.createElement("button");
      nextBtn.type = "button"; nextBtn.className = "jp-nav"; nextBtn.textContent = "بعد ›";
      var prevBtn = document.createElement("button");
      prevBtn.type = "button"; prevBtn.className = "jp-nav"; prevBtn.textContent = "‹ قبل";
      var title = document.createElement("span");
      title.className = "jp-title";
      title.textContent = MONTH_NAMES[viewMonth - 1] + " " + toPersianDigits(viewYear);
      header.appendChild(nextBtn);
      header.appendChild(title);
      header.appendChild(prevBtn);
      pop.appendChild(header);

      var grid = document.createElement("div");
      grid.className = "jp-grid";
      WEEK_DAYS.forEach(function (w) {
        var el = document.createElement("div"); el.className = "jp-wd"; el.textContent = w; grid.appendChild(el);
      });

      var g = toGregorian(viewYear, viewMonth, 1);
      var jsDay = new Date(g.gy, g.gm - 1, g.gd).getDay(); // 0=یکشنبه..6=شنبه در جاوااسکریپت
      var offset = (jsDay + 1) % 7; // تبدیل به شنبه=۰

      for (var b = 0; b < offset; b++) {
        var blank = document.createElement("div"); blank.className = "jp-day jp-blank"; grid.appendChild(blank);
      }
      var len = jalaaliMonthLength(viewYear, viewMonth);
      for (var d = 1; d <= len; d++) {
        var cell = document.createElement("button");
        cell.type = "button"; cell.className = "jp-day";
        if (viewYear === today.jy && viewMonth === today.jm && d === today.jd) cell.classList.add("jp-today");
        cell.textContent = toPersianDigits(d);
        (function (day) {
          cell.addEventListener("click", function (e) {
            e.stopPropagation();
            var jStr = toPersianDigits(viewYear) + "/" + toPersianDigits(pad2(viewMonth)) + "/" + toPersianDigits(pad2(day));
            input.value = jStr;
            input.dispatchEvent(new Event("change", { bubbles: true }));
            closePopup();
          });
        })(d);
        grid.appendChild(cell);
      }
      pop.appendChild(grid);

      var footer = document.createElement("div");
      footer.className = "jp-footer";
      var todayBtn = document.createElement("button");
      todayBtn.type = "button"; todayBtn.className = "jp-today-btn"; todayBtn.textContent = "برو به امروز";
      todayBtn.addEventListener("click", function (e) { e.stopPropagation(); viewYear = today.jy; viewMonth = today.jm; render(); });
      footer.appendChild(todayBtn);
      pop.appendChild(footer);

      nextBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        viewMonth += 1; if (viewMonth > 12) { viewMonth = 1; viewYear += 1; }
        render();
      });
      prevBtn.addEventListener("click", function (e) {
        e.stopPropagation();
        viewMonth -= 1; if (viewMonth < 1) { viewMonth = 12; viewYear -= 1; }
        render();
      });
    }
    render();

    document.body.appendChild(pop);
    var rect = input.getBoundingClientRect();
    pop.style.top = (window.scrollY + rect.bottom + 4) + "px";
    pop.style.left = (window.scrollX + rect.left) + "px";
    activePopup = pop;

    setTimeout(function () {
      outsideHandler = function (e) {
        if (!pop.contains(e.target) && e.target !== input) closePopup();
      };
      document.addEventListener("click", outsideHandler);
    }, 0);
  }

  function initJalaliPickers() {
    document.querySelectorAll(".jalali-date-input").forEach(function (input) {
      if (input.dataset.jpInit) return;
      input.dataset.jpInit = "1";
      input.setAttribute("readonly", "readonly");
      input.style.cursor = "pointer";
      input.addEventListener("click", function (e) { e.stopPropagation(); openPopup(input); });
    });
  }

  document.addEventListener("DOMContentLoaded", initJalaliPickers);
  window.initJalaliPickers = initJalaliPickers;
})();
