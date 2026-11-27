"use strict";
let menu = [], basket = {}, activeCategory = "All", trackingRef = "", placing = false;
const filters = $("#filters");
for (const category of ["All","Bowls","Mains","Sides","Drinks"]) {
  const button = document.createElement("button");
  button.textContent = category; button.dataset.category = category;
  button.classList.toggle("active", category === activeCategory);
  button.addEventListener("click", () => {
    activeCategory = category;
    filters.querySelectorAll("button").forEach(b => b.classList.toggle("active", b === button));
    renderMenu();
  });
  filters.append(button);
}
function renderMenu() {
  $("#menu-grid").innerHTML = menu.filter(d => activeCategory === "All" || d.category === activeCategory).map(d =>
    `<article class="menu-card ${d.available ? "" : "sold-out"}"><div class="image-wrap"><img src="/images/${safe(d.image)}" alt="${safe(d.name)}"><span class="category-pill">${d.available ? safe(d.category) : "Sold out"}</span></div><div class="menu-content"><h3>${safe(d.name)}</h3><p>${safe(d.description)}</p><div class="menu-bottom"><strong>${money(d.price_cents)}</strong><button class="add" data-add="${d.id}" ${d.available ? "" : "disabled"}>${d.available ? "+ Add" : "Unavailable"}</button></div></div></article>`).join("");
}
function renderBasket() {
  let total = 0, count = 0, unavailable = false;
  const rows = [];
  for (const d of menu) {
    const quantity = basket[d.id] || 0;
    if (!quantity) continue;
    total += d.price_cents * quantity; count += quantity;
    if (!d.available) unavailable = true;
    rows.push(`<div class="cart-item"><div><strong>${safe(d.name)}</strong><small>${d.available ? money(d.price_cents) + " each" : "Sold out · remove to continue"}</small></div><strong>${money(d.price_cents*quantity)}</strong><div class="quantity"><button aria-label="Remove one ${safe(d.name)}" data-minus="${d.id}">−</button><span>${quantity}</span><button aria-label="Add one ${safe(d.name)}" data-add="${d.id}" ${d.available && quantity < 20 ? "" : "disabled"}>+</button></div></div>`);
  }
  $("#cart-items").innerHTML = rows.join("") || '<div class="empty"><span class="empty-icon">☷</span>Your basket is empty.<br>Pick something delicious.</div>';
  $("#total").textContent = money(total); $("#cart-count").textContent = count;
  $("#place-order").disabled = !count || unavailable || placing;
}
async function loadMenu() {
  try { menu = await api("/api/menu"); renderMenu(); renderBasket(); message($("#menu-error"), ""); }
  catch (error) { message($("#menu-error"), "Could not load menu. Make sure Python server is running.", true); }
}
document.addEventListener("click", event => {
  const button = event.target.closest("[data-add],[data-minus]");
  if (!button || button.disabled) return;
  const id = Number(button.dataset.add || button.dataset.minus);
  const dish = menu.find(d => d.id === id);
  const amount = basket[id] || 0;
  if (button.dataset.add && dish?.available && amount < 20) basket[id] = amount + 1;
  if (button.dataset.minus) basket[id] = Math.max(0, amount - 1);
  renderBasket();
});
$("#checkout").addEventListener("submit", async event => {
  event.preventDefault();
  if (placing) return;
  const data = Object.fromEntries(new FormData(event.target));
  data.items = Object.entries(basket).filter(([,q]) => q > 0).map(([id,quantity]) => ({id:Number(id),quantity}));
  placing = true; renderBasket(); message($("#checkout-message"), "Sending your order…");
  try {
    const order = await api("/api/orders","POST",data);
    basket = {}; event.target.reset();
    message($("#checkout-message"), "Order received! Reference: " + order.reference + ". Save this private reference.");
    $("#track-reference").value = order.reference;
    trackingRef = order.reference; showTracking(order);
    document.querySelector("#track").scrollIntoView({behavior:"smooth"});
  } catch (error) { message($("#checkout-message"),error.message,true); await loadMenu(); }
  finally { placing = false; renderBasket(); }
});
function showTracking(order) {
  const position = statuses.indexOf(order.status);
  $("#tracking-result").innerHTML = `<span class="pill ${statusClass(order.status)}">${safe(order.status)}</span><strong>${safe(order.reference)}</strong><div class="steps">${statuses.map((s,i)=>`<div class="step ${i<=position?"done":""}"><span></span>${safe(s)}</div>`).join("")}</div><ul>${order.items.map(i=>`<li><span>${i.quantity} × ${safe(i.name)}</span><strong>${money(i.quantity*i.unit_price_cents)}</strong></li>`).join("")}</ul><strong>Total: ${money(order.total_cents)}</strong><p>${safe(order.pickup_time)} · Pay at pickup</p>`;
}
async function updateTracking(ref, showError = false) {
  try { const order = await api("/api/track?ref=" + encodeURIComponent(ref)); showTracking(order); message($("#tracking-message"),""); }
  catch (error) { if (showError) { message($("#tracking-message"),error.message,true); $("#tracking-result").textContent = "No order found for this reference."; trackingRef = ""; } }
}
$("#track-form").addEventListener("submit", event => { event.preventDefault(); trackingRef = $("#track-reference").value.trim(); updateTracking(trackingRef,true); });
loadMenu();
setInterval(() => { loadMenu(); if (trackingRef) updateTracking(trackingRef); }, 6000);
