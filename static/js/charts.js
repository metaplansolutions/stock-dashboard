/**
 * charts.js — Chart.js helpers for Stock Dashboard
 *
 * Palette (accessible, no red/green):
 *   blue   #4fc3f7  — primary line / positive
 *   orange #ff9800  — secondary / negative
 *   gray   #888     — grid / labels
 */

"use strict";

let priceChartInstance = null;

/**
 * Render (or update) the price line chart on the dashboard.
 *
 * @param {string} ticker   - Ticker symbol shown in the title.
 * @param {Array}  prices   - Array of {date, close} objects.
 */
function renderPriceChart(ticker, prices) {
  const canvas = document.getElementById("price-chart");
  if (!canvas) return;

  const labels = prices.map((p) => {
    // Trim time portion if present
    const d = p.date.split("T")[0].split(" ")[0];
    return d;
  });
  const closes = prices.map((p) => p.close);

  // Destroy previous instance before re-creating
  if (priceChartInstance) {
    priceChartInstance.destroy();
    priceChartInstance = null;
  }

  priceChartInstance = new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: ticker + " Close",
          data: closes,
          borderColor: "#4fc3f7",
          backgroundColor: "rgba(79, 195, 247, 0.08)",
          borderWidth: 2,
          pointRadius: 2,
          pointHoverRadius: 5,
          fill: true,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: { color: "#e0e0e0", font: { size: 13 } },
        },
        tooltip: {
          backgroundColor: "#1a1a2e",
          borderColor: "#333",
          borderWidth: 1,
          titleColor: "#4fc3f7",
          bodyColor: "#e0e0e0",
          callbacks: {
            label: (ctx) => " $" + ctx.parsed.y.toFixed(2),
          },
        },
      },
      scales: {
        x: {
          ticks: {
            color: "#888",
            maxTicksLimit: 8,
            maxRotation: 30,
            font: { size: 11 },
          },
          grid: { color: "#222" },
        },
        y: {
          ticks: {
            color: "#888",
            font: { size: 11 },
            callback: (v) => "$" + v.toFixed(0),
          },
          grid: { color: "#222" },
        },
      },
    },
  });
}
