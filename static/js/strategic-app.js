// ---------- SWOT (demo data, in-memory — a real model/DB backing can follow the Study model pattern) ----------
let swot = {
  s: [{t:'برند شناخته‌شده در بازار قطعات یدکی', imp:'high'}, {t:'شبکه توزیع سراسری فعال', imp:'high'}, {t:'سابقه طولانی همکاری با نمایندگی‌ها', imp:'med'}],
  w: [{t:'فرآیندهای تصمیم‌گیری کند در برخی واحدها', imp:'med'}, {t:'وابستگی به تأمین‌کنندگان محدود', imp:'high'}],
  o: [{t:'رشد بازار آفترمارکت خودروهای در حال سرویس', imp:'high'}, {t:'امکان دیجیتالی‌سازی زنجیره تأمین', imp:'med'}],
  t: [{t:'نوسان نرخ ارز و مواد اولیه', imp:'high'}, {t:'رشد بازار غیررسمی و قطعات تقلبی', imp:'high'}],
};
const swotPrefix = {s:'S', w:'W', o:'O', t:'T'};
const impactLabel = {high:'بالا', med:'متوسط'};
function renderSwot(){
  const el = document.getElementById('swot-s');
  if(!el) return;
  ['s','w','o','t'].forEach(k=>{
    document.getElementById('swot-'+k).innerHTML = swot[k].map((item,i)=>
      `<li><span class="code">${swotPrefix[k]}${i+1}</span><span class="txt">${item.t}</span><span class="impact-pill ${item.imp}">${impactLabel[item.imp]}</span><button onclick="removeSwot('${k}',${i})"><i class="fa-solid fa-xmark"></i></button></li>`
    ).join('') || '<li style="opacity:.6">موردی ثبت نشده</li>';
  });
}
function addSwot(k){
  const input = document.getElementById('in-'+k);
  const val = input.value.trim();
  if(!val) return;
  swot[k].push({t:val, imp:'med'});
  input.value = '';
  renderSwot();
}
function removeSwot(k, i){ swot[k].splice(i,1); renderSwot(); }
document.addEventListener('DOMContentLoaded', renderSwot);
