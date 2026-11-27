"use strict";
let pin = "", activeTab = "orders", updating = false;
const reportDate = $("#report-date");
$("#today").textContent = "Cambodia · " + cambodiaToday();
reportDate.value = cambodiaToday();
$("#login-form").addEventListener("submit", async event => {
  event.preventDefault();
  const candidate = new FormData(event.target).get("pin");
  try {
    await api("/api/staff/orders","GET",null,candidate);
    pin = candidate; event.target.reset();
    $("#login-screen").hidden = true; $("#dashboard").hidden = false; $("#sign-out").hidden = false;
    await refreshAll();
  } catch(error) { message($("#login-message"),error.message,true); }
});
$("#sign-out").addEventListener("click", () => {
  pin = ""; $("#dashboard").hidden = true; $("#login-screen").hidden = false; $("#sign-out").hidden = true;
  $("#orders").innerHTML=""; $("#availability").innerHTML=""; message($("#login-message"),"");
});
document.querySelectorAll("[data-tab]").forEach(button => button.addEventListener("click", () => {
  activeTab = button.dataset.tab;
  document.querySelectorAll("[data-tab]").forEach(b => b.classList.toggle("active", b === button));
  document.querySelectorAll(".staff-tab").forEach(tab => tab.hidden = tab.id !== "tab-" + activeTab);
  refreshAll();
}));
function renderOrders(orders) {
  $("#open-count").textContent = orders.filter(o => o.status !== "Completed").length;
  $("#ready-count").textContent = orders.filter(o => o.status === "Ready for pickup").length;
  $("#orders").innerHTML = orders.map(o => {
    const next = statuses[statuses.indexOf(o.status)+1];
    return `<article class="panel kitchen-card"><header><div><h3>${safe(o.customer_name)}</h3><span class="reference">${safe(o.reference)}</span></div><span class="pill ${statusClass(o.status)}">${safe(o.status)}</span></header><div class="phone">${safe(o.phone)} · ${safe(o.pickup_time)}</div><div class="lines">${o.items.map(i=>`<div><span>${i.quantity} × ${safe(i.name)}</span><strong>${money(i.quantity*i.unit_price_cents)}</strong></div>`).join("")}</div>${o.notes?`<p class="note">Note: ${safe(o.notes)}</p>`:""}<div class="cart-total"><span>Total</span><strong>${money(o.total_cents)}</strong></div>${next?`<button class="button full" data-ref="${safe(o.reference)}" data-next="${safe(next)}">${next==="Preparing"?"Start preparing":next==="Ready for pickup"?"Mark ready":"Complete order"} <span>→</span></button>`:'<span class="pill completed">✓ Completed</span>'}</article>`;
  }).join("") || '<div class="panel empty"><span class="empty-icon">☷</span>No orders yet. New customer orders will appear here.</div>';
}
function renderAvailability(menu) {
  $("#menu-count").textContent = menu.filter(d => d.available).length + " / " + menu.length;
  $("#availability").innerHTML = menu.map(d=>`<div class="availability-row"><img src="/images/${safe(d.image)}" alt=""><div><strong>${safe(d.name)}</strong><small>${safe(d.category)} · ${money(d.price_cents)}</small></div><span class="pill ${d.available?"":"unavailable"}">${d.available?"Available":"Sold out"}</span><button class="secondary-button" data-dish="${d.id}" data-available="${!d.available}">${d.available?"Mark sold out":"Make available"}</button></div>`).join("");
}
async function renderReport() {
  if (!pin) return;
  try {
    const report = await api("/api/staff/report?date=" + encodeURIComponent(reportDate.value),"GET",null,pin);
    $("#sales-total").textContent=money(report.sales_cents); $("#sales-orders").textContent=report.orders; $("#sales-items").textContent=report.items_sold;
    $("#top-dishes").innerHTML=report.top_dishes.map(([name,quantity],i)=>`<div class="top-row"><span class="rank">${String(i+1).padStart(2,"0")}</span><strong>${safe(name)}</strong><small>${quantity} sold</small></div>`).join("") || '<div class="empty">No completed sales on this date yet.</div>';
  } catch(error) { message($("#staff-message"),error.message,true); }
}
async function refreshAll() {
  if (!pin || updating) return;
  try {
    const [orders,menu] = await Promise.all([api("/api/staff/orders","GET",null,pin),api("/api/menu")]);
    if (!pin) return;
    renderOrders(orders); renderAvailability(menu);
    if (activeTab === "report") await renderReport();
  } catch(error) { message($("#staff-message"),error.message,true); }
}
document.addEventListener("click", async event => {
  const button = event.target.closest("[data-ref],[data-dish]");
  if (!button || !pin || updating) return;
  updating = true; button.disabled = true;
  try {
    if (button.dataset.ref) {
      await api("/api/staff/status","POST",{reference:button.dataset.ref,status:button.dataset.next},pin);
      message($("#staff-message"),"Order status updated.");
    } else {
      await api("/api/staff/availability","POST",{id:Number(button.dataset.dish),available:button.dataset.available==="true"},pin);
      message($("#staff-message"),"Menu availability updated.");
    }
  } catch(error) { message($("#staff-message"),error.message,true); }
  finally { updating = false; button.disabled = false; await refreshAll(); }
});
$("#refresh").addEventListener("click",refreshAll);
reportDate.addEventListener("change",renderReport);
setInterval(refreshAll,5000);
