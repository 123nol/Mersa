document.addEventListener('DOMContentLoaded', function () {
  var data = window.DASHBOARD_DATA || {};

  // Line chart for performance (created vs closed)
  try {
    var ctx = document.getElementById('performaneLine');
    if (ctx && typeof Chart !== 'undefined') {
      new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
          labels: data.labels || [],
          datasets: [
            {
              label: 'Created',
              data: data.created || [],
              borderColor: 'rgba(75,192,192,1)',
              backgroundColor: 'rgba(75,192,192,0.2)',
              fill: true,
              tension: 0.3,
            },
            {
              label: 'Closed',
              data: data.closed || [],
              borderColor: 'rgba(54,162,235,1)',
              backgroundColor: 'rgba(54,162,235,0.2)',
              fill: true,
              tension: 0.3,
            },
          ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: { padding: { top: 8, right: 8, bottom: 24, left: 8 } },
            plugins: {
              legend: { display: true, position: 'top' },
            },
            scales: {
              x: { display: true, ticks: { padding: 6 } },
              y: { display: true, beginAtZero: true, ticks: { padding: 8, precision: 0 } },
            },
        },
      });
    }
  } catch (e) {
    console.error('Error rendering performance chart', e);
  }

  // Status summary pie/doughnut
  try {
    var ctx2 = document.getElementById('status-summary');
    if (ctx2 && typeof Chart !== 'undefined') {
      // Ensure legend labels are white across Chart.js versions
      try {
        if (Chart.defaults) {
          if (Chart.defaults.plugins && Chart.defaults.plugins.legend && Chart.defaults.plugins.legend.labels) {
            Chart.defaults.plugins.legend.labels.color = '#fff';
          }
          if (Chart.defaults.global && Chart.defaults.global.legend && Chart.defaults.global.legend.labels) {
            Chart.defaults.global.legend.labels.fontColor = '#fff';
          }
        }
      } catch (e) {
        // ignore
      }
      var status = data.status || { closed: 0, open: 0, overdue: 0 };
      new Chart(ctx2.getContext('2d'), {
        type: 'doughnut',
        data: {
          labels: ['Closed', 'Open', 'Overdue'],
          datasets: [
            {
              data: [status.closed || 0, status.open || 0, status.overdue || 0],
              backgroundColor: ['#36A2EB', '#FFCE56', '#FF6384'],
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              align: 'center',
              labels: {
                color: '#fff',
                usePointStyle: true,
                boxWidth: 12,
                padding: 6
              }
            }
          },
          layout: { padding: { top: 8, right: 8, bottom: 8, left: 8 } },
        },
      });
    }
  } catch (e) {
    console.error('Error rendering status chart', e);
  }

  // Visitors widgets using ProgressBar.js if available
  try {
    var pct = parseInt(data.visitors_percentage || 0, 10);
    var total = parseInt(data.visitors_total || 0, 10);
    var mine = parseInt(data.my_visits || 0, 10);

    // Total visitors circle
    if (typeof ProgressBar !== 'undefined') {
      var totalEl = document.getElementById('totalVisitors');
      if (totalEl) {
        var circle = new ProgressBar.Circle(totalEl, {
          strokeWidth: 6,
          trailWidth: 1,
          color: '#00bfa5',
          trailColor: '#eee',
          duration: 1400,
          easing: 'easeInOut'
        });
        circle.animate(Math.min(Math.max(pct / 100, 0), 1));
      }

      var myEl = document.getElementById('visitperday');
      if (myEl) {
        var myRatio = 0;
        if (total > 0) myRatio = Math.min(Math.max(mine / total, 0), 1);
        var circle2 = new ProgressBar.Circle(myEl, {
          strokeWidth: 6,
          trailWidth: 1,
          color: '#3f51b5',
          trailColor: '#eee',
          duration: 1400,
          easing: 'easeInOut'
        });
        circle2.animate(myRatio);
      }
    }

    // Update textual values
    var pctEl = document.getElementById('totalVisitorsPercent');
    if (pctEl) pctEl.textContent = pct + '%';
    var myVisitsEl = document.getElementById('myVisits');
    if (myVisitsEl) myVisitsEl.textContent = String(mine);

  } catch (e) {
    console.error('Error rendering visitors widgets', e);
  }

});
