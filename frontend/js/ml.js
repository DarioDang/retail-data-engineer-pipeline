/* =============================================================
   ml.js - ML Price Forecasting page (v3)
   Per-category sections, per-product panels
============================================================= */

/* ── API helpers ─────────────────────────────────────────── */
async function getForecastProducts()    { return apiFetch('/api/forecast/products'); }
async function getForecastSummary()     { return apiFetch('/api/forecast/summary'); }
async function getForecastByProduct(p)  { return apiFetch(`/api/forecast/${encodeURIComponent(p)}`); }
async function getForecastBestSeller(p) { return apiFetch(`/api/forecast/${encodeURIComponent(p)}/best`); }

/* ── Category mapping ────────────────────────────────────── */
const CATEGORIES = [
    {
        key:      'laptop',
        label:    'LAPTOP CATEGORY',
        icon:     'static/laptop-cat-icon.png',
        color:    '#667eea',
        products: ['Dell XPS 13', 'HP Spectre x360', 'MacBook Air M3'],
    },
    {
        key:      'phone',
        label:    'PHONE CATEGORY',
        icon:     'static/mobile-cat-icon.png',
        color:    '#38ef7d',
        products: ['iPhone 15', 'Samsung Galaxy S24', 'Samsung Galaxy A54'],
    },
    {
        key:      'camera',
        label:    'CAMERA CATEGORY',
        icon:     'static/camera-cat-icon.png',
        color:    '#f7971e',
        products: ['GoPro Hero 13', 'DJI Osmo Action'],
    },
];

const PRODUCT_ICONS = {
    'Dell XPS 13':        'static/dellxps-icon.png',
    'HP Spectre x360':    'static/hpx360-icon.png',
    'MacBook Air M3':     'static/macbookM3-icon.png',
    'iPhone 15':          'static/iphone15-icon.png',
    'Samsung Galaxy S24': 'static/samsungs24-icon.png',
    'Samsung Galaxy A54': 'static/samsungA54-icon.png',
    'GoPro Hero 13':      'static/gopro-icon.png',
    'DJI Osmo Action':    'static/dji-icon.png',
};

/* ── Plotly shared config ────────────────────────────────── */
const PLOTLY_CONFIG = { responsive: true, displayModeBar: false };

const LAYOUT_BASE = {
    paper_bgcolor: 'transparent',
    plot_bgcolor:  'transparent',
    font: { family: 'Space Grotesk, sans-serif', color: 'rgba(255,255,255,0.6)', size: 10 },
    xaxis: {
        gridcolor: 'rgba(255,255,255,0.04)', linecolor: 'rgba(255,255,255,0.06)',
        tickcolor: 'rgba(255,255,255,0.15)', tickformat: '%b %d',
        showgrid: true, nticks: 7,
    },
    yaxis: {
        gridcolor: 'rgba(255,255,255,0.04)', linecolor: 'rgba(255,255,255,0.06)',
        tickcolor: 'rgba(255,255,255,0.15)', tickprefix: '$', showgrid: true,
    },
    margin:     { t: 10, r: 12, b: 40, l: 60 },
    hovermode:  'x unified',
    hoverlabel: { bgcolor: '#1E2130', bordercolor: '#FF6B6B', font: { family:'Space Grotesk', size:11 } },
    showlegend: false,
};

const SELLER_COLORS = [
    '#38ef7d','#667eea','#f7971e','#f953c6',
    '#11998e','#fddb92','#FF6B6B','#a8edea','#8BC6EC','#feb692',
];

/* ── State ───────────────────────────────────────────────── */
let _viewMode        = 'best';
let _allData         = {};
let _bestData        = {};
let _expandedProduct = null;

/* ── Init ────────────────────────────────────────────────── */
async function initMLPage() {
    const [products, summary] = await Promise.all([
        getForecastProducts(),
        getForecastSummary(),
    ]);

    const availableProducts = products || [];

    renderModelInfoBanner(summary || []);
    renderAllProductsChart(summary || []);
    renderSkeletonSections(availableProducts);

    /* Fetch all products in parallel */
    await Promise.all(availableProducts.map(async p => {
        const [forecast, best] = await Promise.all([
            getForecastByProduct(p),
            getForecastBestSeller(p),
        ]);
        _allData[p]  = forecast || [];
        _bestData[p] = best    || null;
    }));

    /* Render real content */
    renderCategorySections(availableProducts);
}

/* ── Model info banner ───────────────────────────────────── */
function renderModelInfoBanner(summary) {
    const runDates  = summary.map(s => s.forecast_run_date).filter(Boolean);
    const latestRun = runDates.length
        ? new Date(Math.max(...runDates.map(d => new Date(d))))
              .toLocaleDateString('en-NZ', { day:'2-digit', month:'short', year:'numeric' })
        : '—';
    document.getElementById('mib-series-count').textContent = `${summary.length} series`;
    document.getElementById('mib-run-date').textContent      = latestRun;
}

/* ── Skeleton while loading ──────────────────────────────── */
function renderSkeletonSections(products) {
    const container = document.getElementById('forecast-sections');
    container.innerHTML = CATEGORIES.map(cat => {
        const catProducts = cat.products.filter(p => products.includes(p));
        if (catProducts.length === 0) return '';
        return `
            <div class="category-section">
                <div class="category-header">
                    <img class="category-icon" src="${cat.icon}" alt="${cat.label}"/>
                    <span class="category-label" style="color:${cat.color};">${cat.label}</span>
                </div>
                <div class="product-panels-grid">
                    ${catProducts.map(p => `
                        <div class="product-panel">
                            <p class="pp-name">${p}</p>
                            <div class="fpc-skeleton"></div>
                        </div>
                    `).join('')}
                </div>
            </div>`;
    }).join('');
}

/* ── Render real category sections ───────────────────────── */
function renderCategorySections(availableProducts) {
    const container = document.getElementById('forecast-sections');
    container.innerHTML = CATEGORIES.map(cat => {
        const catProducts = cat.products.filter(p => availableProducts.includes(p));
        if (catProducts.length === 0) return '';
        return `
            <div class="category-section">
                <div class="category-header">
                    <img class="category-icon" src="${cat.icon}" alt="${cat.label}"/>
                    <span class="category-label" style="color:${cat.color};">${cat.label}</span>
                    <div class="category-divider" style="background:${cat.color};"></div>
                </div>
                <div class="product-panels-grid" id="grid-${cat.key}">
                    ${catProducts.map(p => buildProductPanel(p, cat.color)).join('')}
                </div>
            </div>`;
    }).join('');

    /* Draw all charts */
    requestAnimationFrame(() => {
        availableProducts.forEach(p => drawProductChart(p));
    });
}

/* ── Build one product panel ─────────────────────────────── */
function buildProductPanel(productName, categoryColor) {
    const best       = _bestData[productName];
    const rows       = _allData[productName] || [];
    const hasBest    = best && best.seller;
    const tier       = hasBest ? (best.confidence_tier || 'B') : 'B';
    const mape       = hasBest ? best.mape : null;
    const avg        = hasBest ? `$${Number(best.avg_predicted_price).toFixed(2)}` : '—';
    const minP       = hasBest ? `$${Number(best.min_predicted_price).toFixed(0)}` : '—';
    const maxP       = hasBest ? `$${Number(best.max_predicted_price).toFixed(0)}` : '—';
    const sellerName = hasBest ? best.seller : 'No data';
    const tierClass  = tier === 'A' ? 'a' : 'b';
    const mapeColor  = mape == null ? '' : (mape < 5 ? 'green' : mape < 15 ? 'orange' : 'red');
    const slug       = slugify(productName);
    const hasData    = rows.length > 0;

    return `
        <div class="product-panel ${hasData ? '' : 'no-data'}"
             id="panel-${slug}"
             onclick="${hasData ? `toggleExpand('${productName.replace(/'/g,"\\'")}')` : ''}">

            ${hasData ? '<span class="pp-expand-hint">⤢</span>' : ''}

            <!-- Header -->
            <div class="pp-header">
                <div style="display:flex; align-items:center; gap:8px;">
                    <img src="${PRODUCT_ICONS[productName] || 'static/price-analysis.png'}" 
                        alt="${productName}" 
                        style="width:20px; height:20px; object-fit:contain;"/>
                    <p class="pp-name">${productName}</p>
                </div>
            </div>

            <!-- Stats -->
            <div class="pp-stats">
                <div class="pp-stat">
                    <span class="pp-stat-label">Avg Forecast</span>
                    <span class="pp-stat-value green">${avg}</span>
                </div>
                <div class="pp-stat">
                    <span class="pp-stat-label">Range</span>
                    <span class="pp-stat-value orange">${minP} – ${maxP}</span>
                </div>
                <div class="pp-stat">
                    <span class="pp-stat-label">MAPE</span>
                    <span class="pp-stat-value ${mapeColor}">${mape != null ? mape + '%' : '—'}</span>
                </div>
            </div>

            <!-- Chart or empty state -->
            ${hasData
                ? `<div class="pp-chart" id="chart-${slug}"></div>
                   <div class="pp-seller-note">
                       <span class="pp-seller-dot" style="background:${categoryColor};"></span>
                       ${sellerName}
                   </div>`
                : `<div class="pp-empty">
                       <span style="font-size:28px;">📭</span>
                       <p>Insufficient retail listings</p>
                       <p style="font-size:10px;margin-top:4px;color:rgba(255,255,255,0.2);">
                           This model was superseded by newer generations
                       </p>
                   </div>`
            }
        </div>`;
}

/* ── Draw Plotly chart for one product ───────────────────── */
function drawProductChart(productName) {
    const slug      = slugify(productName);
    const container = document.getElementById(`chart-${slug}`);
    if (!container) return;

    const rows = _allData[productName] || [];
    if (rows.length === 0) return;

    const isExpanded = _expandedProduct === productName;
    const traces     = buildTraces(rows);

    Plotly.newPlot(container, traces, {
        ...LAYOUT_BASE,
        showlegend: isExpanded,
        legend: isExpanded ? {
            bgcolor: 'rgba(0,0,0,0)', bordercolor: 'rgba(255,255,255,0.08)',
            borderwidth: 1, font: { size: 9 }, orientation: 'h', x: 0, y: -0.3,
        } : {},
    }, PLOTLY_CONFIG);
}

/* ── Build traces for one product ────────────────────────── */
function buildTraces(rows) {
    const today      = new Date().toISOString().split('T')[0];
    const bySeller   = groupBySeller(rows);
    const sellers    = Object.keys(bySeller);
    const traces     = [];

    const visibleSellers = _viewMode === 'best'
        ? [sellers.reduce((best, s) => {
                const m = bySeller[s][0]?.mape ?? 999;
                return m < (bySeller[best]?.[0]?.mape ?? 999) ? s : best;
            }, sellers[0])]
        : sellers;

    visibleSellers.forEach((seller, idx) => {
        const sRows  = bySeller[seller].sort((a,b) => new Date(a.forecast_date) - new Date(b.forecast_date));
        const dates  = sRows.map(r => r.forecast_date);
        const yhats  = sRows.map(r => r.predicted_price);
        const lowers = sRows.map(r => r.price_lower);
        const uppers = sRows.map(r => r.price_upper);
        const tier   = sRows[0]?.confidence_tier || 'B';
        const mape   = sRows[0]?.mape;
        const color  = SELLER_COLORS[idx % SELLER_COLORS.length];

        /* Confidence band */
        traces.push({
            x: [...dates, ...dates.slice().reverse()],
            y: [...uppers, ...lowers.slice().reverse()],
            fill: 'toself', fillcolor: hexToRgba(color, 0.1),
            line: { color: 'transparent' },
            hoverinfo: 'skip', showlegend: false, type: 'scatter',
        });

        /* Forecast line */
        traces.push({
            x: dates, y: yhats,
            mode: 'lines+markers',
            name: `${seller} (Tier ${tier}, MAPE ${mape}%)`,
            line:   { color, width: 2, dash: 'dot' },
            marker: { color, size: 4 },
            hovertemplate: `<b>${seller}</b><br>%{x}<br>$%{y:.2f}<extra></extra>`,
        });
    });

    /* Today marker */
    traces.push({
        x: [today, today], y: [0, 1], yaxis:'y', xaxis:'x',
        mode: 'lines', line: { color:'rgba(255,107,107,0.35)', width:1, dash:'dash' },
        hoverinfo: 'skip', showlegend: false, type: 'scatter',
    });

    return traces;
}

/* ── Toggle expand/collapse ──────────────────────────────── */
function toggleExpand(productName) {
    const slug    = slugify(productName);
    const panel   = document.getElementById(`panel-${slug}`);
    const chartEl = document.getElementById(`chart-${slug}`);

    if (_expandedProduct === productName) {
        _expandedProduct = null;
        panel.classList.remove('expanded');
        chartEl.classList.remove('expanded');
    } else {
        if (_expandedProduct) {
            const ps = slugify(_expandedProduct);
            document.getElementById(`panel-${ps}`)?.classList.remove('expanded');
            document.getElementById(`chart-${ps}`)?.classList.remove('expanded');
            drawProductChart(_expandedProduct);
        }
        _expandedProduct = productName;
        panel.classList.add('expanded');
        chartEl.classList.add('expanded');
    }

    requestAnimationFrame(() => drawProductChart(productName));
}

/* ── View mode toggle ────────────────────────────────────── */
function setViewMode(mode) {
    _viewMode = mode;
    document.getElementById('btn-best').classList.toggle('active', mode === 'best');
    document.getElementById('btn-all').classList.toggle('active',  mode === 'all');
    Object.keys(_allData).forEach(p => drawProductChart(p));
}

/* ── All-products bar chart ──────────────────────────────── */
function renderAllProductsChart(summary) {
    if (!summary || summary.length === 0) return;
    const byProduct = {};
    summary.forEach(row => {
        if (!byProduct[row.product_name]) byProduct[row.product_name] = [];
        byProduct[row.product_name].push(row.avg_predicted_price);
    });
    const products = Object.keys(byProduct).sort();
    const avgs     = products.map(p => {
        const v = byProduct[p];
        return v.reduce((a,b) => a+b, 0) / v.length;
    });

    Plotly.newPlot('chart-all-products', [{
        x: products, y: avgs, type: 'bar',
        marker: { color: products.map((_,i) => SELLER_COLORS[i % SELLER_COLORS.length]), opacity:0.85, line:{ width:0 } },
        hovertemplate: '<b>%{x}</b><br>Avg forecast: $%{y:.2f}<extra></extra>',
    }], {
        ...LAYOUT_BASE,
        xaxis: { ...LAYOUT_BASE.xaxis, tickangle:-20 },
        margin: { t:10, r:20, b:80, l:70 },
        showlegend: false, bargap: 0.3,
    }, PLOTLY_CONFIG);
}

/* ── Utils ───────────────────────────────────────────────── */
function groupBySeller(rows) {
    return rows.reduce((acc, row) => {
        if (!acc[row.seller]) acc[row.seller] = [];
        acc[row.seller].push(row);
        return acc;
    }, {});
}

function slugify(str) { return str.toLowerCase().replace(/[^a-z0-9]/g, '-'); }

function hexToRgba(hex, alpha) {
    const r = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    if (!r) return `rgba(255,107,107,${alpha})`;
    return `rgba(${parseInt(r[1],16)},${parseInt(r[2],16)},${parseInt(r[3],16)},${alpha})`;
}