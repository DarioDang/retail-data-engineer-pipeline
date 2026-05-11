/* ============================================================
   seller.js — Seller Intelligence (full 4-section version)
   Section 1: Horizontal bar + donut   (existing)
   Section 2: Bubble chart             (NEW — rating-by-seller)
   Section 3: Reputation scorecard     (existing)
   Section 4: Cheapest per category    (NEW — cheapest-seller-per-category)
   ============================================================ */

const CAT_COLORS = { laptop:'#667eea', phone:'#11998e', camera:'#f7971e' };

const RATING_COLORS = {
    verified: '#38ef7d',
    unrated:  '#667eea',
    limited:  '#FF6B6B'
};

const PLOTLY_BASE = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor:  'rgba(0,0,0,0)',
    font: { color:'rgba(255,255,255,0.6)', family:'Space Grotesk' }
};

/* ════════════════════════════════════════════════════════════
   1. SELLER COUNT — Plotly horizontal bar chart
   ════════════════════════════════════════════════════════════ */
function renderSellerBars(data) {
    const container = document.getElementById('seller-bars');
    if (!data || !data.length) {
        container.innerHTML = '<p style="color:gray;text-align:center;padding:40px 0;">No data</p>';
        return;
    }

    const sorted   = [...data].sort((a,b) => parseInt(a.seller_count) - parseInt(b.seller_count));
    const maxCount = Math.max(...sorted.map(d => parseInt(d.seller_count)));

    Plotly.newPlot('seller-bars', [{
        x:            sorted.map(d => parseInt(d.seller_count)),
        y:            sorted.map(d => d.product_name),
        type:         'bar',
        orientation:  'h',
        marker: {
            color:   sorted.map(d => CAT_COLORS[d.category] || '#999'),
            opacity: 0.85,
            line:    { width: 0 }
        },
        text:         sorted.map(d => d.seller_count),
        textposition: 'outside',
        textfont:     { color:'rgba(255,255,255,0.6)', size:11, family:'Space Grotesk' },
        customdata:   sorted.map(d => {
            const pct   = parseInt(d.seller_count) / maxCount;
            const level = pct >= 0.7 ? '🔥 HIGH' : pct >= 0.4 ? '⚡ MED' : '🌱 LOW';
            return `${d.category} · ${level}`;
        }),
        hovertemplate: '<b>%{y}</b><br>%{customdata}<br>Sellers: %{x}<extra></extra>'
    }], {
        ...PLOTLY_BASE,
        height: 340,
        margin: { t:10, b:30, l:140, r:60 },
        xaxis: {
            gridcolor: 'rgba(255,255,255,0.05)',
            tickfont:  { size:10, color:'rgba(255,255,255,0.4)' },
            zeroline:  false,
            title:     { text:'Number of Sellers', font:{ size:11, color:'rgba(255,255,255,0.3)' } }
        },
        yaxis: {
            tickfont:   { size:11, color:'white', family:'Space Grotesk' },
            gridcolor:  'rgba(0,0,0,0)',
            automargin: true
        },
        showlegend: false,
        bargap: 0.3
    }, { responsive:true, displayModeBar:false });

    document.getElementById('cat-legend').innerHTML =
        Object.entries(CAT_COLORS).map(([cat, color]) => `
        <div class="cat-legend-item">
            <div class="cat-dot" style="background:${color};"></div>
            <span>${cat}</span>
        </div>`).join('');
}

/* ════════════════════════════════════════════════════════════
   2. RATING STATUS DONUT + LEGEND
   ════════════════════════════════════════════════════════════ */
function renderRatingDonut(data) {
    if (!data || !data.length) return;

    const total  = data.reduce((s,d) => s + parseInt(d.count), 0);
    const labels = data.map(d => d.rating_status);
    const values = data.map(d => parseInt(d.count));
    const colors = data.map(d => RATING_COLORS[d.rating_status] || '#999');

    Plotly.newPlot('chart-donut', [{
        labels, values,
        type: 'pie', hole: 0.60, rotation: 90,
        marker: { colors, line: { color:'#0e1117', width:3 } },
        textinfo: 'none',
        hovertemplate: '<b>%{label}</b><br>%{value} listings (%{percent})<extra></extra>',
        sort: false
    }], {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor:  'rgba(0,0,0,0)',
        font: { color:'rgba(255,255,255,0.6)', family:'Space Grotesk' },
        height: 260,
        margin: { t:10, b:10, l:20, r:20 },
        showlegend: false,
        annotations: [{
            text:      `<b>${total.toLocaleString()}</b><br>listings`,
            x: 0.5, y: 0.5,
            font:      { size:16, color:'white', family:'Space Grotesk' },
            showarrow: false
        }]
    }, { responsive:true, displayModeBar:false });

    const sorted = [...data].sort((a,b) => parseInt(b.count) - parseInt(a.count));
    document.getElementById('rating-legend').innerHTML = sorted.map(row => {
        const color = RATING_COLORS[row.rating_status] || '#999';
        const pct   = (parseInt(row.count) / total * 100).toFixed(1);
        const label = row.rating_status.charAt(0).toUpperCase() + row.rating_status.slice(1);
        return `
        <div class="rating-legend-row">
            <div class="rating-legend-label">
                <div class="rating-legend-dot" style="background:${color};"></div>
                <span class="rating-legend-name">${label}</span>
            </div>
            <div class="rating-bar-track">
                <div class="rating-bar-fill" style="width:${pct}%; background:${color};"></div>
            </div>
            <span class="rating-pct">${pct}%</span>
        </div>`;
    }).join('');
}

/* ════════════════════════════════════════════════════════════
   3. NEW — SELLER TRUST CHART
   ════════════════════════════════════════════════════════════ */
function renderCompetitionVsPrice(sellerData, statsData) {
    if (!sellerData || !sellerData.length) return;

    const sorted = [...sellerData].sort((a,b) =>
        parseInt(b.seller_count) - parseInt(a.seller_count)
    );

    /* Match avg price from stats if available */
    const prices = sorted.map(row => {
        const match = (statsData||[]).find(s => s.product_name === row.product_name);
        return match ? parseFloat(match.avg_price) : null;
    });

    const hasPrices = prices.some(p => p !== null);

    const traces = [{
        x:    sorted.map(d => d.product_name),
        y:    sorted.map(d => parseInt(d.seller_count)),
        type: 'bar',
        name: 'Seller Count',
        yaxis: 'y',
        marker: {
            color:   sorted.map(d => CAT_COLORS[d.category] || '#999'),
            opacity: 0.8,
            line:    { width: 0 }
        },
        hovertemplate: '<b>%{x}</b><br>Sellers: %{y}<extra></extra>'
    }];

    if (hasPrices) {
        traces.push({
            x:    sorted.map(d => d.product_name),
            y:    prices,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Avg Price (NZD)',
            yaxis: 'y2',
            line:   { color:'#FF6B6B', width:2, dash:'dot' },
            marker: { size:8, color:'#FF6B6B', line:{ width:2, color:'white' } },
            hovertemplate: '<b>%{x}</b><br>Avg Price: $%{y:,.0f}<extra></extra>'
        });
    }

    Plotly.newPlot('chart-bubble', traces, {
        ...PLOTLY_BASE,
        height: 400,
        margin: { t:50, b:110, l:60, r:80 },
        barmode: 'group',
        legend: {
            orientation: 'h',
            x: 1.0,
            y: 1.12,
            xanchor: 'right',
            yanchor: 'top',
            font: { color:'rgba(255,255,255,0.6)', size:11 },
            bgcolor: 'rgba(0,0,0,0)',
            borderwidth: 0
        },
        xaxis: {
            tickangle:  -40,
            tickfont:   { size:10, color:'rgba(255,255,255,0.6)' },
            gridcolor:  'rgba(255,255,255,0)',
            automargin: true
        },
        yaxis: {
            title:     { text:'Seller Count', font:{ size:11, color:'rgba(255,255,255,0.3)' }, standoff:10 },
            gridcolor: 'rgba(255,255,255,0.05)',
            tickfont:  { size:10, color:'rgba(255,255,255,0.5)' },
            zeroline:  false
        },
        yaxis2: hasPrices ? {
            title: {
                text: 'Avg Price (NZD)',
                font: { size:11, color:'rgba(238, 44, 5, 0.52)' },
                standoff: 15      /* pushes title away from tick labels */
            },
            overlaying: 'y',
            side:       'right',
            tickprefix: '$',
            tickfont:   { size:10, color:'rgba(238, 39, 39, 0.74)' },
            gridcolor:  'rgba(0,0,0,0)',
            zeroline:   false,
            tickformat: ',.0f'   
        } : undefined,
        showlegend: hasPrices,
        /* Subtle bar rounding via shape */
        bargap:     0.25,
        bargroupgap: 0.1
    }, { responsive:true, displayModeBar:false });
}

/* ════════════════════════════════════════════════════════════
   4. SELLER REPUTATION SCORECARD — 3 columns
   ════════════════════════════════════════════════════════════ */
function renderSellerScorecard(data) {
    const container = document.getElementById('seller-scorecard');
    if (!data || !data.length) {
        container.innerHTML = '<p style="color:gray;text-align:center;grid-column:1/-1;">No data yet.</p>';
        return;
    }

    const top3 = [...data]
        .sort((a,b) => parseFloat(b.avg_rating) - parseFloat(a.avg_rating))
        .slice(0, 3);

    const maxReviews  = Math.max(...top3.map(d => parseInt(d.total_reviews  || 0)));
    const maxListings = Math.max(...top3.map(d => parseInt(d.total_listings || 0)));
    const colors      = ['#38ef7d', '#f7971e', '#667eea'];

    container.innerHTML = top3.map((row, idx) => {
        const rating   = parseFloat(row.avg_rating);
        const reviews  = parseInt(row.total_reviews  || 0);
        const listings = parseInt(row.total_listings || 0);
        const color    = colors[idx];
        const hex      = color.replace('#','');
        const r = parseInt(hex.slice(0,2),16);
        const g = parseInt(hex.slice(2,4),16);
        const b = parseInt(hex.slice(4,6),16);
        const delay    = `${idx * 0.2}s`;

        const trustScore = Math.min(100, Math.round(
            (rating / 5.0) * 60 + (reviews / Math.max(maxReviews, 1)) * 40
        ));

        const reviewPct  = maxReviews  > 0 ? (reviews  / maxReviews  * 100).toFixed(0) : 0;
        const listingPct = maxListings > 0 ? (listings / maxListings * 100).toFixed(0) : 0;
        const ratingPct  = (rating / 5 * 100).toFixed(0);
        const revPerList = listings > 0 ? Math.round(reviews / listings) : 0;
        const ratingLabel = rating >= 4.5 ? 'EXCELLENT' : rating >= 4.0 ? 'GOOD' : 'FAIR';
        const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));

        const insight = revPerList > 5000
            ? '🔥 Highly engaged — customers love this seller'
            : revPerList > 500
            ? '⚡ Active — strong review presence'
            : '🌱 Growing — building reputation';

        return `
        <div class="scorecard-card" style="border-left:3px solid ${color};"
             onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 12px 32px rgba(${r},${g},${b},0.25)';"
             onmouseout="this.style.transform='';this.style.boxShadow='';">
            <div class="scorecard-accent" style="background:${color};"></div>
            <div class="scorecard-shimmer" style="animation-delay:${delay};"></div>
            <div class="scorecard-header">
                <div class="scorecard-rank" style="background:${color};">${idx + 1}</div>
                <span class="scorecard-name">${row.seller}</span>
                <span class="scorecard-trust"
                      style="background:rgba(${r},${g},${b},0.15);border:1px solid ${color};color:${color};animation-delay:${delay};">
                    TRUST ${trustScore}%
                </span>
            </div>
            <div style="display:flex;align-items:center;gap:8px;padding:2px 0;">
                <span style="color:${color};font-size:14px;letter-spacing:1px;">${stars}</span>
                <span style="color:${color};font-size:14px;font-weight:800;">${rating.toFixed(1)}</span>
                <span style="color:rgba(255,255,255,0.25);font-size:10px;">/ 5.0</span>
                <span style="margin-left:auto;background:rgba(${r},${g},${b},0.12);border:1px solid rgba(${r},${g},${b},0.3);color:${color};font-size:9px;font-weight:700;letter-spacing:1px;padding:2px 8px;border-radius:6px;">${ratingLabel}</span>
            </div>
            <div class="scorecard-metric">
                <div class="scorecard-metric-header">
                    <span class="scorecard-metric-label">Avg Rating</span>
                    <span class="scorecard-metric-value" style="color:${color};">★ ${rating.toFixed(1)} / 5.0</span>
                </div>
                <div class="scorecard-bar-track">
                    <div class="scorecard-bar-fill" style="width:${ratingPct}%;background:linear-gradient(90deg,${color},${color}44,${color});animation-delay:${delay};"></div>
                </div>
            </div>
            <div class="scorecard-metric">
                <div class="scorecard-metric-header">
                    <span class="scorecard-metric-label">Review Volume</span>
                    <span class="scorecard-metric-value" style="color:rgba(255,255,255,0.7);">${reviews.toLocaleString()}</span>
                </div>
                <div class="scorecard-bar-track">
                    <div class="scorecard-bar-fill" style="width:${reviewPct}%;background:linear-gradient(90deg,${color},${color}44,${color});animation-delay:${delay};"></div>
                </div>
            </div>
            <div class="scorecard-metric">
                <div class="scorecard-metric-header">
                    <span class="scorecard-metric-label">Total Listings</span>
                    <span class="scorecard-metric-value" style="color:rgba(255,255,255,0.7);">${listings.toLocaleString()}</span>
                </div>
                <div class="scorecard-bar-track">
                    <div class="scorecard-bar-fill" style="width:${listingPct}%;background:linear-gradient(90deg,${color},${color}44,${color});animation-delay:${delay};"></div>
                </div>
            </div>
            <div class="scorecard-metric">
                <div class="scorecard-metric-header">
                    <span class="scorecard-metric-label">Reviews per Listing</span>
                    <span class="scorecard-metric-value" style="color:rgba(255,255,255,0.7);">${revPerList.toLocaleString()}</span>
                </div>
            </div>
            <div class="scorecard-insight" style="color:rgba(255,255,255,0.4);">${insight}</div>
        </div>`;
    }).join('');
}

/* ════════════════════════════════════════════════════════════
   5. NEW — CHEAPEST SELLER PER CATEGORY CARDS
   ════════════════════════════════════════════════════════════ */
function renderCheapestSellers(data) {
    const container = document.getElementById('cheapest-sellers');
    if (!data || !data.length) {
        container.innerHTML = '<p style="color:gray;text-align:center;grid-column:1/-1;">No pricing data yet.</p>';
        return;
    }

    const maxPrice = Math.max(...data.map(d => parseFloat(d.min_price)));

    container.innerHTML = data.map((row, i) => {
        const color = CAT_COLORS[row.category] || '#667eea';
        const hex   = color.replace('#','');
        const r = parseInt(hex.slice(0,2),16);
        const g = parseInt(hex.slice(2,4),16);
        const b = parseInt(hex.slice(4,6),16);
        const pct   = (parseFloat(row.min_price) / maxPrice * 100).toFixed(1);
        const delay = `${i * 0.3}s`;
        const price = parseFloat(row.min_price).toLocaleString('en-NZ',{minimumFractionDigits:2,maximumFractionDigits:2});
        const avg   = parseFloat(row.avg_price).toLocaleString('en-NZ',{minimumFractionDigits:2,maximumFractionDigits:2});

        return `
        <div class="cheap-card" style="border-left:3px solid ${color};"
             onmouseover="this.style.transform='translateY(-4px)';this.style.boxShadow='0 12px 32px rgba(${r},${g},${b},0.25)';"
             onmouseout="this.style.transform='';this.style.boxShadow='';">
            <div class="cheap-card-scan" style="animation-delay:${delay};"></div>
            <div class="cheap-card-shimmer" style="animation-delay:${delay};"></div>
            <div class="cheap-card-inner">
                <div class="cheap-top-row">
                    <span class="cheap-cat-label" style="color:${color};">${row.category.toUpperCase()}</span>
                    <span class="cheap-savings" style="animation-delay:${delay};">💚 Save ${row.savings_pct}%</span>
                </div>
                <div class="cheap-product">${row.product_name}</div>
                <div class="cheap-price" style="animation-delay:${delay};">NZD ${price}</div>
                <div class="cheap-seller">via ${row.seller}</div>
                <div class="cheap-bar-track">
                    <div class="cheap-bar-fill" style="width:${pct}%;background:linear-gradient(90deg,${color},${color}44,${color});animation-delay:${delay};"></div>
                </div>
                <div class="cheap-avg">Market avg: NZD ${avg}</div>
            </div>
        </div>`;
    }).join('');
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

/* ════════════════════════════════════════════════════════════
   INIT — fetch all 3 endpoints in parallel
   ════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {
    const [sellerCount, ratingStatus, ratingBySeller, cheapestPerCat, statsData] = await Promise.all([
        getSellerCountPerProduct(),
        getRatingStatusDistribution(),
        getRatingBySeller(),
        getCheapestSellerPerCategory(),
        getStatsPerProduct()
    ]);

    renderSellerBars(sellerCount);
    renderRatingDonut(ratingStatus);
    renderCompetitionVsPrice(sellerCount, statsData);
    renderSellerScorecard(ratingBySeller);
    renderCheapestSellers(cheapestPerCat);
    loadLastUpdated();
});