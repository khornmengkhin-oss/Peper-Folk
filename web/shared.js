"use strict";
const $ = (selector) => document.querySelector(selector);
const money = (cents) => "$" + (cents / 100).toFixed(2);
const safe = (value) => String(value ?? "").replace(/[&<>"']/g, (char) => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[char]);
const statuses = ["Received", "Preparing", "Ready for pickup", "Completed"];
const statusClass = (status) => status.toLowerCase().replaceAll(" ", "-");
function message(element, text, error = false) {
  element.textContent = text; element.hidden = !text; element.classList.toggle("error", error);
}
async function api(path, method = "GET", data = null, pin = "") {
  const headers = {"Accept":"application/json"};
  if (data !== null) headers["Content-Type"] = "application/json";
  if (pin) headers["X-Staff-Pin"] = pin;
  const response = await fetch(path, {method, headers, body: data === null ? null : JSON.stringify(data), cache:"no-store"});
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || "Something went wrong.");
  return result;
}
function cambodiaToday() {
  return new Intl.DateTimeFormat("en-CA",{timeZone:"Asia/Phnom_Penh",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
}
