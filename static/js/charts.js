(function () {
  const inkMuted = "#8C99AD";
  const gridColor = "rgba(255, 255, 255, 0.06)";
  const palette = ["#3DDC97", "#F2A65A", "#7FB8F0", "#C792EA", "#EF6F6C", "#F2D06F", "#7FE0D8", "#8C99AD"];

  const categoryCanvas = document.getElementById("categoryChart");
  if (categoryCanvas && categoryLabels.length) {
    new Chart(categoryCanvas, {
      type: "doughnut",
      data: {
        labels: categoryLabels,
        datasets: [{
          data: categoryValues,
          backgroundColor: palette,
          borderColor: "#182232",
          borderWidth: 2,
        }],
      },
      options: {
        cutout: "62%",
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: inkMuted, font: { family: "Inter", size: 12 }, boxWidth: 10, padding: 14 },
          },
        },
      },
    });
  }

  const monthCanvas = document.getElementById("monthChart");
  if (monthCanvas && monthLabels.length) {
    new Chart(monthCanvas, {
      type: "bar",
      data: {
        labels: monthLabels,
        datasets: [{
          label: "Spend",
          data: monthValues,
          backgroundColor: "#3DDC97",
          borderRadius: 4,
          maxBarThickness: 36,
        }],
      },
      options: {
        plugins: { legend: { display: false } },
        scales: {
          x: { ticks: { color: inkMuted, font: { family: "JetBrains Mono", size: 11 } }, grid: { display: false } },
          y: { ticks: { color: inkMuted, font: { family: "JetBrains Mono", size: 11 } }, grid: { color: gridColor } },
        },
      },
    });
  }
})();
