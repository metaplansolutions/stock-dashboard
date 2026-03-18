/**
 * app.js — Client-side interactions for Stock Dashboard
 *
 * NOTE: No innerHTML is used with untrusted content.
 * All dynamic DOM nodes are built with createElement / textContent.
 */

"use strict";

/* ------------------------------------------------------------------ helpers */

function fmtMoney(n) {
  return "$" + Number(n).toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

async function fetchJSON(url, options) {
  const resp = await fetch(url, options);
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.error || "Request failed: " + resp.status);
  }
  return resp.json();
}

/** Build a stat tile using safe DOM methods — no innerHTML. */
function makeStatTile(label, value, cssClass) {
  const wrapper = document.createElement("div");

  const lbl = document.createElement("div");
  lbl.style.cssText = "color:#888;font-size:12px;text-transform:uppercase;";
  lbl.textContent = label;

  const val = document.createElement("div");
  if (cssClass) val.className = cssClass;
  val.style.cssText = "font-size:18px;font-weight:700;";
  val.textContent = value;

  wrapper.appendChild(lbl);
  wrapper.appendChild(val);
  return wrapper;
}

/* -------------------------------------------------------------- dashboard */

async function loadTicker(ticker) {
  ticker = ticker.toUpperCase().trim();
  if (!ticker) return;

  const priceEl = document.getElementById("current-price");
  const labelEl = document.getElementById("price-ticker-label");
  const statsEl = document.getElementById("quick-stats");

  if (priceEl) priceEl.textContent = "Loading\u2026";

  try {
    const data = await fetchJSON("/api/prices/" + encodeURIComponent(ticker));
    const prices = data.prices;

    if (!prices || prices.length === 0) {
      if (priceEl) priceEl.textContent = "No data";
      return;
    }

    const latest = prices[prices.length - 1];
    if (priceEl) priceEl.textContent = fmtMoney(latest.close);
    if (labelEl) labelEl.textContent = ticker;

    // Chart
    if (typeof renderPriceChart === "function") {
      renderPriceChart(ticker, prices);
    }

    // Quick stats — all built with safe DOM methods
    if (statsEl) {
      const first = prices[0];
      const change = latest.close - first.close;
      const changePct = (change / first.close) * 100;
      const high = Math.max(...prices.map((p) => p.high || p.close));
      const low  = Math.min(...prices.map((p) => p.low  || p.close));
      const sign = change >= 0 ? "+" : "";
      const cls  = change >= 0 ? "positive" : "negative";

      // Clear existing children safely
      while (statsEl.firstChild) statsEl.removeChild(statsEl.firstChild);

      statsEl.appendChild(
        makeStatTile(
          "Period Change",
          sign + fmtMoney(change) + " (" + sign + changePct.toFixed(2) + "%)",
          cls
        )
      );
      statsEl.appendChild(makeStatTile("Period High", fmtMoney(high), "positive"));

      const lowTile = makeStatTile("Period Low", fmtMoney(low), null);
      lowTile.querySelector("div:last-child").style.color = "#e0e0e0";
      statsEl.appendChild(lowTile);

      statsEl.appendChild(
        makeStatTile("Data Points", String(prices.length), null)
      );
    }
  } catch (e) {
    if (priceEl) priceEl.textContent = "Error";
    console.error("loadTicker error:", e);
  }
}

function initDashboard() {
  const form = document.getElementById("ticker-form");
  if (!form) return;

  // Load default ticker on page ready
  const input = document.getElementById("ticker-input");
  if (input && input.value) loadTicker(input.value);

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    if (input) loadTicker(input.value);
  });
}

/* -------------------------------------------------------------- portfolio */

function initPortfolio() {
  // Remove holding buttons
  document.querySelectorAll(".btn-remove-holding").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      if (!id) return;
      try {
        await fetchJSON("/api/holdings/" + encodeURIComponent(id), {
          method: "DELETE",
        });
        location.reload();
      } catch (e) {
        // Use textContent on a visible element rather than alert where possible,
        // but alert is safe here as the message originates from our own server.
        window.alert("Could not remove holding: " + e.message);
      }
    });
  });

  // Add holding form
  const form = document.getElementById("add-holding-form");
  if (!form) return;
  const msg = document.getElementById("add-holding-msg");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const ticker = document.getElementById("h-ticker").value.toUpperCase().trim();
    const shares = document.getElementById("h-shares").value;
    const price  = document.getElementById("h-price").value;
    const date   = document.getElementById("h-date").value;

    if (!ticker || !shares || !price) {
      if (msg) msg.textContent = "Ticker, shares and price are required.";
      return;
    }

    try {
      await fetchJSON("/api/holdings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, shares, price, date }),
      });
      location.reload();
    } catch (e) {
      if (msg) msg.textContent = "Error: " + e.message;
    }
  });
}

/* -------------------------------------------------------------- watchlist */

function initWatchlist() {
  // Remove watchlist buttons
  document.querySelectorAll(".btn-remove-watchlist").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      try {
        await fetchJSON("/api/watchlist/" + encodeURIComponent(id), {
          method: "DELETE",
        });
        location.reload();
      } catch (e) {
        window.alert("Could not remove: " + e.message);
      }
    });
  });

  // Add watchlist form
  const form = document.getElementById("add-watchlist-form");
  if (!form) return;
  const msg = document.getElementById("add-watchlist-msg");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const ticker = document.getElementById("w-ticker").value.toUpperCase().trim();
    const above  = document.getElementById("w-above").value || null;
    const below  = document.getElementById("w-below").value || null;

    if (!ticker) {
      if (msg) msg.textContent = "Ticker is required.";
      return;
    }

    try {
      await fetchJSON("/api/watchlist", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ticker,
          alert_above: above,
          alert_below: below,
        }),
      });
      location.reload();
    } catch (e) {
      if (msg) msg.textContent = "Error: " + e.message;
    }
  });
}

/* -------------------------------------------------------------- auto-init */

document.addEventListener("DOMContentLoaded", () => {
  initPortfolio();
  initWatchlist();
  // Dashboard page calls initDashboard() from its own inline script
  // so Chart.js is guaranteed to be loaded first.
});
