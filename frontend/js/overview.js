/* ============================================================
   overview.js - Main JS for Overview page of Retail Price Intelligence Dashboard
   ============================================================ */

const CATEGORY_COLORS = {
    laptop: '#667eea',
    phone:  '#11998e',
    camera: '#f7971e'
};

const PLOTLY_BASE = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor:  'rgba(0,0,0,0)',
    font: { color: 'rgba(255,255,255,0.6)', family: 'Space Grotesk' },
    xaxis: {
        gridcolor: 'rgba(255,255,255,0.03)',
        tickfont:  { size: 10, color: 'rgba(255,255,255,0.5)' }
    },
    yaxis: {
        gridcolor: 'rgba(255,255,255,0.05)',
        tickfont:  { size: 10, color: 'rgba(255,255,255,0.5)' }
    }
};

function fmt(n) {
    if (n == null) return '—';
    return Number(n).toLocaleString();
}

/* ── 1. KPI Row 1 ── */
async function loadKpiCards() {
    const [listings, products, sellers] = await Promise.all([
        getTotalListings(),
        getTotalProducts(),
        getTotalSellers()
    ]);
    if (listings) document.getElementById('val-listings').textContent = fmt(listings.total);
    if (products) document.getElementById('val-products').textContent = fmt(products.total);
    if (sellers)  document.getElementById('val-sellers').textContent  = fmt(sellers.total);
}

/* ── 2. KPI Row 2: Discount cards ── */
async function loadDiscountCards() {
    const data = await getDiscounts();
    if (!data || data.length === 0) {
        ['val-discounted','val-avg-discount','val-max-discount'].forEach(id => {
            document.getElementById(id).textContent = '0';
        });
        return;
    }
    const total   = data.length;
    const avg     = (data.reduce((s,d) => s + (d.discount_pct||0), 0) / total).toFixed(1);
    const max     = Math.max(...data.map(d => d.discount_pct||0));
    document.getElementById('val-discounted').textContent   = fmt(total);
    document.getElementById('val-avg-discount').textContent = `${avg}%`;
    document.getElementById('val-max-discount').textContent = `${max}%`;
}

/* ── 3. Average Price Bar Chart ── */
async function loadAvgPriceChart() {
    const data = await getCategorySummary();
    if (!data || data.length === 0) return;

    Plotly.newPlot('chart-avg-price', [{
        x:    data.map(d => d.category),
        y:    data.map(d => parseFloat(d.avg_price)),
        type: 'bar',
        marker: { color: data.map(d => CATEGORY_COLORS[d.category] || '#999') },
        hovertemplate: '<b>%{x}</b><br>Avg: $%{y:,.2f}<extra></extra>'
    }], {
        ...PLOTLY_BASE,
        margin: { t: 20, b: 50, l: 60, r: 20 },
        yaxis: { ...PLOTLY_BASE.yaxis, tickprefix: '$' },
        showlegend: false
    }, { responsive: true, displayModeBar: false });
}

/* ── 4. Donut Chart ── */
async function loadDonutChart() {
    const data = await getListingsByCategory();
    if (!data || data.length === 0) return;

    const total = data.reduce((a, b) => a + b.listings, 0);

    Plotly.newPlot('chart-donut', [{
        labels:        data.map(d => d.category),
        values:        data.map(d => d.listings),
        type:          'pie',
        hole:          0.60,
        rotation:      90,
        marker: {
            colors: data.map(d => CATEGORY_COLORS[d.category] || '#999'),
            line: { color: '#0e1117', width: 3 }
        },
        textinfo:      'percent',
        textposition:  'inside',
        textfont:      { size: 12, color: 'white' },
        hovertemplate: '<b>%{label}</b><br>%{value} listings (%{percent})<extra></extra>',
        sort: false
    }], {
        ...PLOTLY_BASE,
        height: 280,
        margin: { t: 10, b: 10, l: 10, r: 10 },
        showlegend: true,
        legend: {
            orientation: 'h',
            yanchor: 'top', y: -0.05,
            xanchor: 'center', x: 0.5,
            font: { color: 'rgba(255,255,255,0.7)', size: 11 }
        },
        annotations: [{
            text: `<b>${fmt(total)}`,
            x: 0.5, y: 0.5,
            font: { size: 16, color: 'white' },
            showarrow: false
        }]
    }, { responsive: true, displayModeBar: false });
}

/* ── 5. Price Trend Line Chart ── */
async function loadTrendChart() {
    const data = await getAvgPriceOverTime();
    if (!data || data.length === 0) return;

    const allDates  = [...new Set(data.map(d => d.snapshot_date))].sort();
    const totalDays = allDates.length;
    const fromSel   = document.getElementById('date-from');
    const toSel     = document.getElementById('date-to');

    allDates.forEach(d => {
        const label = new Date(d).toLocaleDateString('en-NZ', { day:'2-digit', month:'short', year:'numeric' });
        fromSel.innerHTML += `<option value="${d}">${label}</option>`;
        toSel.innerHTML   += `<option value="${d}">${label}</option>`;
    });

    fromSel.selectedIndex = Math.max(0, allDates.length - 7);
    toSel.selectedIndex   = allDates.length - 1;

    if (totalDays < 14) {
        document.getElementById('trend-note').textContent =
            `Weekly view activates after 14 days of data — currently ${totalDays}d`;
    }

    function renderTrend() {
        const fromDate = fromSel.value;
        const toDate   = toSel.value;
        const filtered = data.filter(d => d.snapshot_date >= fromDate && d.snapshot_date <= toDate);

        const byCategory = {};
        filtered.forEach(d => {
            if (!byCategory[d.category]) byCategory[d.category] = {};
            if (!byCategory[d.category][d.snapshot_date]) byCategory[d.category][d.snapshot_date] = [];
            byCategory[d.category][d.snapshot_date].push(d.avg_price);
        });

        const traces = Object.entries(byCategory).map(([cat, byDate]) => {
            const dates  = Object.keys(byDate).sort();
            const prices = dates.map(d =>
                (byDate[d].reduce((a,b) => a+b, 0) / byDate[d].length).toFixed(2)
            );
            return {
                x: dates, y: prices, name: cat,
                type: 'scatter', mode: 'lines+markers',
                line:   { 
                    color: CATEGORY_COLORS[cat] || '#999', 
                    width: 2.5,
                    shape: 'spline',
                    smoothing: 1.2},
                marker: { 
                    size: 8, 
                    color: CATEGORY_COLORS[cat] || '#999', 
                    line: { width: 2, color: 'white' } 
                },
                hovertemplate: `<b>${cat}</b><br>%{x}<br>$%{y}<extra></extra>`
            };
        });

        /* Enough bottom margin so x-axis labels don't overlap legend */
        Plotly.react('chart-trend', traces, {
            ...PLOTLY_BASE,
            height: 440,
            margin: { t: 60, b: 100, l: 60, r: 20 },
            showlegend: true,
            legend: {
                orientation: 'h',
                yanchor: 'bottom', y: 1.02,
                xanchor: 'left',   x: 0,
                font: { color: 'rgba(255,255,255,0.6)', size: 11 }
            },
            xaxis: {
                ...PLOTLY_BASE.xaxis,
                type: 'category',
                tickangle: -45
            },
            yaxis: {
                ...PLOTLY_BASE.yaxis,
                tickprefix: '$'
            },
            title: {
                text: `${totalDays < 14 ? 'DAILY' : 'WEEKLY'} VIEW`,
                x: 0.5, xanchor: 'center',
                font: { size: 14, color: '#F5F73E' }
            }
        }, { responsive: true, displayModeBar: false });
    }

    renderTrend();
    fromSel.addEventListener('change', renderTrend);
    toSel.addEventListener('change',   renderTrend);
}

/* ── 6. Last Updated Timestamp ── */
async function loadLastUpdated() {
    const data = await getLastUpdated();
    if (!data || !data[0]?.last_updated) return;

    const dateStr = data[0].last_updated.split('T')[0];

    /* Parse date parts directly — avoids UTC vs local timezone shift */
    const [year, month, day] = dateStr.split('-').map(Number);
    const updated = new Date(year, month - 1, day);

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffDays = Math.floor((today - updated) / (1000 * 60 * 60 * 24));

    let color, ageText;
    if (diffDays === 0)      { color = '#38ef7d'; ageText = 'Today'; }
    else if (diffDays === 1) { color = '#f7971e'; ageText = 'Yesterday'; }
    else                     { color = '#FF6B6B'; ageText = `${diffDays}d ago`; }

    const label = updated.toLocaleDateString('en-NZ', {
        day: '2-digit', month: 'short', year: 'numeric'
    });

    /* Update dot — background + CSS variable for pulse glow color */
    const dotEl = document.getElementById('status-dot');
    dotEl.style.background = color;
    dotEl.style.setProperty('--pulse-color', color + '66');

    /* Update date and age text */
    document.getElementById('last-updated-date').textContent = label;
    document.getElementById('last-updated-date').style.color = color;
    document.getElementById('last-updated-age').textContent  = ageText;
}

/* ── INIT ── */
document.addEventListener('DOMContentLoaded', () => {
    loadKpiCards();
    loadDiscountCards();
    loadAvgPriceChart();
    loadDonutChart();
    loadTrendChart();
    loadLastUpdated();
});