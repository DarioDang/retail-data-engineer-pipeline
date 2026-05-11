/* ============================================================
   price.js — Price Analysis page (fixed)
   Key fix: category headers use .cat-header class, NOT inline
   border-left/right which caused the bracket rendering bug.
   ============================================================ */

const CAT_COLORS = { laptop:'#667eea', phone:'#11998e', camera:'#f7971e' };

const CAT_ICONS = {
    laptop: 'static/laptop-icon.png',
    phone:  'static/mobile-icon.png',
    camera: 'static/camera-icon.png'
};

const CAT_SECTION_ICONS = {
    laptop: 'static/laptop-cat-icon.png',
    phone:  'static/mobile-cat-icon.png',
    camera: 'static/camera-cat-icon.png'
};

const PRODUCT_ICONS = {
    'Dell XPS 13':        'static/dellxps-icon.png',
    'MacBook Air M3':     'static/macbookM3-icon.png',
    'HP Spectre x360':    'static/hpx360-icon.png',
    'iPhone 15':          'static/iphone15-icon.png',
    'Samsung Galaxy S24': 'static/samsungs24-icon.png',
    'Samsung Galaxy A54': 'static/samsungA54-icon.png',
    'GoPro Hero 13':      'static/gopro-icon.png',
    'DJI Osmo Action':    'static/dji-icon.png',
};

const PLOTLY_BASE = {
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor:  'rgba(0,0,0,0)',
    font: { color:'rgba(255,255,255,0.6)', family:'Space Grotesk' },
    xaxis: { gridcolor:'rgba(255,255,255,0.03)', tickfont:{ size:10, color:'rgba(255,255,255,0.5)' } },
    yaxis: { gridcolor:'rgba(255,255,255,0.05)', tickfont:{ size:10, color:'rgba(255,255,255,0.5)' } }
};

let selectedCategory = 'All';
let allData = {};

/* ── Category filter ── */
function setCategory(cat) {
    selectedCategory = cat;
    const map = { All:'all', laptop:'laptop', phone:'phone', camera:'camera' };
    ['All','laptop','phone','camera'].forEach(c => {
        const btn = document.getElementById(`btn-${map[c]}`);
        btn.className = 'filter-btn';
        if (c === cat) btn.classList.add(`active-${map[c]}`);
    });
    renderDealCards();
    renderProductCharts();
    renderBoxPlot();
    renderCarousel();
    renderSpreadAndSellerCount();
}

/* ════════════════════════════════════════════════════════════
   1. BEST DEAL SPARKLINE CARDS
   ════════════════════════════════════════════════════════════ */
function renderDealCards() {
    const stats    = allData.stats || [];
    const trendRaw = allData.trend || [];
    const container = document.getElementById('deal-cards-row');

    const cheapest = stats.map(r => ({
        product:  r.product_name,
        category: r.category,
        seller:   r.cheapest_seller,
        price:    parseFloat(r.cheapest_price),
        avg:      parseFloat(r.avg_price),
        savings:  parseFloat(r.savings_pct) || 0
    }));

    const filtered = selectedCategory === 'All'
        ? cheapest
        : cheapest.filter(r => r.category === selectedCategory);

    let deals = [], labels = [];

    if (selectedCategory === 'All') {
        ['laptop','phone','camera'].forEach(cat => {
            const best = filtered.filter(r => r.category === cat).sort((a,b) => b.savings - a.savings)[0];
            if (best) { deals.push(best); labels.push(cat.toUpperCase()); }
        });
    } else {
        deals  = filtered.sort((a,b) => b.savings - a.savings).slice(0, 3);
        labels = ['BEST DEAL','2ND DEAL','3RD DEAL'].slice(0, deals.length);
    }

    if (deals.length === 0) {
        container.innerHTML = '<p style="color:gray;padding:50px 0;text-align:center;grid-column:1/-1;">No data</p>';
        return;
    }

    // Update grid columns based on deal count
    container.style.gridTemplateColumns = `repeat(${Math.min(deals.length, 3)}, 1fr)`;

    container.innerHTML = deals.map((deal, i) => {
        const cat   = deal.category;
        const color = CAT_COLORS[cat] || '#38ef7d';
        const icon  = CAT_ICONS[cat]  || 'static/all-icon.png';
        const hex   = color.replace('#','');
        const r = parseInt(hex.slice(0,2),16);
        const g = parseInt(hex.slice(2,4),16);
        const b = parseInt(hex.slice(4,6),16);
        const delay = i * 0.15;

        const productTrend = trendRaw
            .filter(d => d.product_name === deal.product)
            .sort((a,b) => a.snapshot_date > b.snapshot_date ? 1 : -1);

        const points = productTrend.length >= 2
            ? productTrend.map(d => parseFloat(d.avg_price))
            : [60,55,70,50,65,45,60];

        const minP = Math.min(...points), maxP = Math.max(...points);
        const W = 200, H = 40;
        const coords = points.map((p, idx) => {
            const x = Math.round(idx * W / (points.length - 1));
            const y = H - Math.round((p - minP) / Math.max(maxP - minP, 1) * (H-8)) - 4;
            return `${x},${y}`;
        });
        const polyline = coords.join(' ');
        const fillPoly = polyline + ` ${W},${H} 0,${H}`;
        const last     = coords[coords.length - 1];

        return `
        <div class="best-deal-card" style="border-left-color:${color};"
             onmouseover="this.style.transform='translateY(-6px)';this.style.boxShadow='0 12px 28px rgba(${r},${g},${b},0.3)';"
             onmouseout="this.style.transform='';this.style.boxShadow='';">
            <p class="card-rank" style="color:${color};">
                <img src="${icon}" alt=""/> ${labels[i]}
            </p>
            <p class="card-product">${deal.product}</p>
            <p class="card-seller">via ${deal.seller}</p>
            <div class="card-divider" style="background:linear-gradient(90deg,transparent,rgba(${r},${g},${b},0.3),transparent);"></div>
            <div class="card-sparkline" style="animation:sparkFloat 4s ease-in-out ${delay}s infinite;">
                <svg viewBox="0 0 ${W} ${H}" width="100%" height="${H}" xmlns="http://www.w3.org/2000/svg">
                    <defs>
                        <linearGradient id="sg${i}" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stop-color="rgba(${r},${g},${b},0.25)"/>
                            <stop offset="100%" stop-color="rgba(${r},${g},${b},0)"/>
                        </linearGradient>
                    </defs>
                    <polygon points="${fillPoly}" fill="url(#sg${i})"/>
                    <polyline points="${polyline}" fill="none"
                        stroke="rgba(${r},${g},${b},0.9)" stroke-width="1.8"
                        stroke-linecap="round" stroke-linejoin="round"
                        stroke-dasharray="400" stroke-dashoffset="400"
                        style="animation:sparkDraw 1.2s ease ${delay}s forwards;"/>
                    <circle cx="${last.split(',')[0]}" cy="${last.split(',')[1]}" r="3" fill="${color}"/>
                </svg>
            </div>
            <p class="card-price">NZD ${deal.price.toLocaleString('en-NZ',{minimumFractionDigits:2,maximumFractionDigits:2})}</p>
            <p class="card-savings">⬇ Save ${deal.savings}%</p>
        </div>`;
    }).join('');
}

/* ════════════════════════════════════════════════════════════
   2. PER-PRODUCT LINE CHARTS
   Fix: use .cat-header class only, no inline border-left/right
   ════════════════════════════════════════════════════════════ */
function renderProductCharts() {
    const trendRaw  = allData.trend || [];
    const fromDate  = document.getElementById('date-from').value;
    const toDate    = document.getElementById('date-to').value;
    const container = document.getElementById('product-charts-container');

    const filtered = trendRaw.filter(d =>
        d.snapshot_date >= fromDate && d.snapshot_date <= toDate &&
        (selectedCategory === 'All' || d.category === selectedCategory)
    );

    const cats = selectedCategory === 'All' ? ['laptop','phone','camera'] : [selectedCategory];
    let html = '';

    cats.forEach(cat => {
        const products = [...new Set(filtered.filter(d => d.category === cat).map(d => d.product_name))];
        if (!products.length) return;

        const color    = CAT_COLORS[cat] || '#FF6B6B';
        const catIcon  = CAT_SECTION_ICONS[cat] || '';
        const colClass = products.length === 1 ? 'cols-1' : products.length === 2 ? 'cols-2' : 'cols-3';

        /* Key fix: use data-color attribute instead of inline border */
        html += `
        <div class="cat-header" data-color="${color}">
            <div class="cat-header-line" style="background:linear-gradient(90deg,transparent,rgba(255,255,255,0.08));"></div>
            <img src="${catIcon}" alt="${cat}"/>
            <span class="cat-header-label" style="color:${color};">${cat.toUpperCase()} CATEGORY</span>
            <div class="cat-header-line" style="background:linear-gradient(90deg,rgba(255,255,255,0.08),transparent);"></div>
        </div>
        <div class="product-charts-row ${colClass}">
            ${products.map(p => `<div class="product-chart-card" id="pcard-${p.replace(/\s+/g,'-')}"></div>`).join('')}
        </div>`;
    });

    container.innerHTML = html || '<p style="color:gray;text-align:center;padding:40px 0;">No data for selected range.</p>';

    // Render each product chart
    cats.forEach(cat => {
        const products = [...new Set(filtered.filter(d => d.category === cat).map(d => d.product_name))];
        products.forEach(product => {
            const divId = `pcard-${product.replace(/\s+/g,'-')}`;
            const el = document.getElementById(divId);
            if (!el) return;

            const rows = filtered.filter(d => d.product_name === product)
                                 .sort((a,b) => a.snapshot_date > b.snapshot_date ? 1 : -1);
            if (!rows.length) return;

            const color = CAT_COLORS[cat] || '#FF6B6B';
            const hex   = color.replace('#','');
            const r = parseInt(hex.slice(0,2),16);
            const g = parseInt(hex.slice(2,4),16);
            const b = parseInt(hex.slice(4,6),16);
            const icon = PRODUCT_ICONS[product] || '';

            let badge = '–', badgeColor = 'gray';
            if (rows.length >= 2) {
                const first = parseFloat(rows[0].avg_price);
                const last  = parseFloat(rows[rows.length-1].avg_price);
                const pct   = ((last - first) / first) * 100;
                badge      = (pct <= 0 ? '▼ ' : '▲ ') + Math.abs(pct).toFixed(1) + '%';
                badgeColor = pct <= 0 ? '#2ECC71' : '#FF6B6B';
            }

            el.innerHTML = `
                <div class="product-chart-title">
                    ${icon ? `<img src="${icon}" alt=""/>` : ''}
                    <span>${product}</span>
                    <span class="product-chart-badge" style="color:${badgeColor};">${badge}</span>
                </div>
                <div id="${divId}-plot" style="height:280px;"></div>`;

            const dates  = rows.map(d => d.snapshot_date);
            const prices = rows.map(d => parseFloat(d.avg_price));
            const yMin   = Math.min(...prices), yMax = Math.max(...prices);
            const pad    = (yMax - yMin) * 0.15 || yMax * 0.05;

            Plotly.newPlot(`${divId}-plot`, [{
                x: dates, y: prices,
                type:'scatter', mode:'lines+markers',
                line:   { 
                    color, 
                    width:2.5,
                    shape:'spline',
                    smoothing:1.2
                },
                marker: { size:8, color, line: { width: 2, color } },
                fill:'tozeroy', fillcolor:`rgba(${r},${g},${b},0.12)`,
                hovertemplate:`<b>${product}</b><br>%{x}<br>$%{y:,.2f}<extra></extra>`
            }], {
                ...PLOTLY_BASE,
                height: 320,
                margin: { t:10, b:90, l:70, r:30 },
                xaxis: {
                    ...PLOTLY_BASE.xaxis,
                    type: 'category',
                    tickangle: -45,
                    tickvals: dates,
                    range: [-0.5, dates.length - 0.5]
                },
                yaxis: {
                    ...PLOTLY_BASE.yaxis,
                    tickprefix: '$',
                    range: [yMin - pad, yMax + pad]
                },
                showlegend: false,
                plot_bgcolor: 'rgba(255,255,255,0.01)',
                paper_bgcolor: 'rgba(0,0,0,0)'
            }, { responsive:true, displayModeBar:false });
        });
    });
}

/* ════════════════════════════════════════════════════════════
   3. BOX PLOT
   ════════════════════════════════════════════════════════════ */
function renderBoxPlot() {
    const data = allData.priceRange || [];
    const filtered = selectedCategory === 'All' ? data : data.filter(d => d.category === selectedCategory);
    const products = [...new Set(filtered.map(d => d.product_name))];

    Plotly.react('chart-box',
        products.map(product => {
            const rows = filtered.filter(d => d.product_name === product);
            return {
                y:    rows.map(d => parseFloat(d.price)),
                name: product, type:'box',
                marker:{ color: CAT_COLORS[rows[0]?.category] || '#999' },
                hovertemplate:`<b>${product}</b><br>$%{y:,.2f}<extra></extra>`
            };
        }),
        {
            ...PLOTLY_BASE, height:400,
            margin:{ t:30, b:80, l:60, r:20 },
            xaxis:{ ...PLOTLY_BASE.xaxis, tickangle:-45 },
            yaxis:{ ...PLOTLY_BASE.yaxis, tickprefix:'$', title:{ text:'Price (NZD)', font:{ color:'rgba(255,255,255,0.4)' } } },
            showlegend:false
        },
        { responsive:true, displayModeBar:false }
    );
}

/* ════════════════════════════════════════════════════════════
   4. CAROUSEL DATA
   ════════════════════════════════════════════════════════════ */
function renderCarousel() {
    const stats     = allData.stats     || [];
    const stats7d   = allData.stats7d   || [];
    const yesterday = allData.yesterday || [];
    const week      = allData.week      || [];

    const fStats   = selectedCategory === 'All' ? stats   : stats.filter(d => d.category === selectedCategory);
    const f7d      = selectedCategory === 'All' ? stats7d : stats7d.filter(d => d.category === selectedCategory);
    const fYest    = selectedCategory === 'All' ? yesterday : yesterday.filter(d => d.category === selectedCategory);
    const fWeek    = selectedCategory === 'All' ? week      : week.filter(d => d.category === selectedCategory);

    const expRow   = f7d.length   ? f7d.reduce((a,b)   => parseFloat(a.max_price_7d) > parseFloat(b.max_price_7d) ? a : b) : null;
    const cheapRow = f7d.length   ? f7d.reduce((a,b)   => parseFloat(a.avg_price_7d) < parseFloat(b.avg_price_7d) ? a : b) : null;
    const compRow  = fStats.length? fStats.reduce((a,b) => parseInt(a.seller_count) > parseInt(b.seller_count) ? a : b) : null;
    const dealRow  = fStats.length? fStats.reduce((a,b) => parseFloat(a.cheapest_price) < parseFloat(b.cheapest_price) ? a : b) : null;

    function set(valId, subId, val, sub) {
        [valId, valId+'2'].forEach(id => { const el=document.getElementById(id); if(el) el.textContent=val; });
        [subId, subId+'2'].forEach(id => { const el=document.getElementById(id); if(el) el.textContent=sub; });
    }

    const fmtNZD = n => `NZD ${parseFloat(n).toLocaleString('en-NZ',{minimumFractionDigits:2,maximumFractionDigits:2})}`;

    set('ic-val-expensive',  'ic-sub-expensive',  expRow   ? fmtNZD(expRow.max_price_7d)   : 'N/A', expRow   ? `${expRow.product_name} (7d)`  : '—');
    set('ic-val-cheapest',   'ic-sub-cheapest',   cheapRow ? fmtNZD(cheapRow.avg_price_7d)  : 'N/A', cheapRow ? `${cheapRow.product_name} (7d)`: '—');
    set('ic-val-competitive','ic-sub-competitive',compRow  ? `${compRow.seller_count} sellers` : 'N/A', compRow ? compRow.product_name : '—');
    set('ic-val-best-deal',  'ic-sub-best-deal',  dealRow  ? fmtNZD(dealRow.cheapest_price)  : 'N/A', dealRow ? dealRow.cheapest_seller : '—');

    const jumpRow  = fYest.length ? fYest.reduce((a,b) => parseFloat(a.pct_change) > parseFloat(b.pct_change) ? a : b) : null;
    const dropRow  = fYest.length ? fYest.reduce((a,b) => parseFloat(a.pct_change) < parseFloat(b.pct_change) ? a : b) : null;
    const alertRow = fWeek.length ? fWeek.reduce((a,b) => parseFloat(a.pct_change_week) > parseFloat(b.pct_change_week) ? a : b) : null;
    const weekRow  = fWeek.length ? fWeek.reduce((a,b) => parseFloat(a.pct_change_week) < parseFloat(b.pct_change_week) ? a : b) : null;

    function setText(id, val) { const el=document.getElementById(id); if(el) el.textContent=val; }
    setText('ic-val-jump',   jumpRow  ? `▲ ${parseFloat(jumpRow.pct_change).toFixed(1)}%`              : 'N/A');
    setText('ic-sub-jump',   jumpRow  ? jumpRow.product_name                                             : 'Need 2+ days');
    setText('ic-val-drop',   dropRow  ? `▼ ${Math.abs(parseFloat(dropRow.pct_change)).toFixed(1)}%`     : 'N/A');
    setText('ic-sub-drop',   dropRow  ? dropRow.product_name                                             : 'Need 2+ days');
    setText('ic-val-alert',  alertRow ? `▲ ${parseFloat(alertRow.pct_change_week).toFixed(1)}%`         : 'N/A');
    setText('ic-sub-alert',  alertRow ? `${alertRow.product_name} vs last week`                          : 'Need 7+ days');
    setText('ic-val-weekly', weekRow  ? `▼ ${Math.abs(parseFloat(weekRow.pct_change_week)).toFixed(1)}%`: 'N/A');
    setText('ic-sub-weekly', weekRow  ? `${weekRow.product_name} vs last week`                           : 'Need 7+ days');

    const ratedRow    = fStats.filter(d=>d.avg_rating).reduce((a,b) => parseFloat(a.avg_rating||0) > parseFloat(b.avg_rating||0) ? a : b, fStats[0]) || null;
    const reviewedRow = fStats.filter(d=>d.avg_reviews).reduce((a,b) => parseInt(a.avg_reviews||0) > parseInt(b.avg_reviews||0) ? a : b, fStats[0]) || null;
    const rangeRow    = fStats.length ? fStats.reduce((a,b) => (parseFloat(a.max_price)-parseFloat(a.min_price)) > (parseFloat(b.max_price)-parseFloat(b.min_price)) ? a : b) : null;

    setText('ic-val-rated',    ratedRow    ? `★ ${parseFloat(ratedRow.avg_rating).toFixed(1)}`    : 'N/A');
    setText('ic-sub-rated',    ratedRow    ? ratedRow.product_name                                 : '—');
    setText('ic-val-reviewed', reviewedRow ? parseInt(reviewedRow.avg_reviews).toLocaleString()   : 'N/A');
    setText('ic-sub-reviewed', reviewedRow ? reviewedRow.product_name                             : '—');
    setText('ic-val-range',    rangeRow    ? fmtNZD(parseFloat(rangeRow.max_price)-parseFloat(rangeRow.min_price)) : 'N/A');
    setText('ic-sub-range',    rangeRow    ? rangeRow.product_name                                : '—');
    setText('ic-val-sellers',  compRow     ? `${compRow.seller_count} sellers`                    : 'N/A');
    setText('ic-sub-sellers',  compRow     ? compRow.product_name                                 : '—');
}

/* ════════════════════════════════════════════════════════════
   5. PRICE SPREAD + SELLER COUNT
   ════════════════════════════════════════════════════════════ */
function renderSpreadAndSellerCount() {
    const stats    = allData.stats || [];
    const filtered = selectedCategory === 'All' ? stats : stats.filter(d => d.category === selectedCategory);

    const spreadTraces = [];
    filtered.forEach(row => {
        const color = CAT_COLORS[row.category] || '#FF6B6B';
        const min = parseFloat(row.min_price), max = parseFloat(row.max_price), avg = parseFloat(row.avg_price);
        spreadTraces.push({ x:[row.product_name], y:[max-min], base:min, type:'bar', marker:{color,opacity:0.4}, showlegend:false, hovertemplate:`<b>${row.product_name}</b><br>Min:$${min.toLocaleString()}<br>Max:$${max.toLocaleString()}<extra></extra>` });
        spreadTraces.push({ x:[row.product_name], y:[avg], mode:'markers', type:'scatter', marker:{size:10,color,line:{width:2,color:'white'}}, showlegend:false, hovertemplate:`<b>${row.product_name}</b><br>Avg:$${avg.toLocaleString()}<extra></extra>` });
    });

    Plotly.react('chart-spread', spreadTraces, {
        ...PLOTLY_BASE,
        title:{ text:'PRICE SPREAD PER PRODUCT', x:0.5, font:{size:13,color:'#F5F73E'} },
        barmode:'overlay', height:400, margin:{t:50,b:80,l:60,r:20},
        xaxis:{...PLOTLY_BASE.xaxis,tickangle:-45},
        yaxis:{...PLOTLY_BASE.yaxis,tickprefix:'$',title:{text:'Price (NZD)',font:{color:'rgba(255,255,255,0.4)'}}},
        showlegend:false
    }, {responsive:true,displayModeBar:false});

    Plotly.react('chart-seller-count', [{
        x:    filtered.map(d => d.product_name),
        y:    filtered.map(d => parseInt(d.seller_count)),
        type: 'bar',
        marker:{ color: filtered.map(d => CAT_COLORS[d.category]||'#999') },
        hovertemplate:'<b>%{x}</b><br>%{y} sellers<extra></extra>'
    }], {
        ...PLOTLY_BASE,
        title:{ text:'SELLER COUNT PER PRODUCT', x:0.5, font:{size:13,color:'#F5F73E'} },
        height:400, margin:{t:50,b:80,l:60,r:20},
        xaxis:{...PLOTLY_BASE.xaxis,tickangle:-45},
        yaxis:{...PLOTLY_BASE.yaxis,title:{text:'Number of Sellers',font:{color:'rgba(255,255,255,0.4)'}}},
        showlegend:false
    }, {responsive:true,displayModeBar:false});
}

/* ════════════════════════════════════════════════════════════
   CAROUSEL CONTROLLER
   ════════════════════════════════════════════════════════════ */
function initCarousel() {
    const track = document.getElementById('icTrack');
    const outer = document.getElementById('icOuter');
    const dots  = [0,1,2].map(i => document.getElementById(`ic-dot${i}`));
    let page=0, locked=false, timer=null;
    const TOTAL=3;

    function init() {
        const W = outer.offsetWidth;
        document.querySelectorAll('.ic-page').forEach(p => { p.style.width = p.style.minWidth = W+'px'; });
    }

    function setDots(p) { dots.forEach((d,i) => d.classList.toggle('active', i===p)); }

    function slideTo(p, animate) {
        const W = outer.offsetWidth;
        if (!animate) track.style.transition = 'none';
        track.style.transform = `translateX(-${p*W}px)`;
        if (!animate) { void track.offsetWidth; track.style.transition=''; }
    }

    function next() {
        if (locked) return;
        locked = true;
        const np = page+1;
        if (np < TOTAL) { page=np; setDots(page); slideTo(page,true); setTimeout(()=>{locked=false;},900); }
        else { slideTo(TOTAL,true); setDots(0); setTimeout(()=>{slideTo(0,false);page=0;locked=false;},900); }
    }

    outer.addEventListener('mouseenter', () => clearInterval(timer));
    outer.addEventListener('mouseleave', () => { timer=setInterval(next,4000); });
    init();
    timer = setInterval(next, 4000);
}

/* ════════════════════════════════════════════════════════════
   DATE FILTER
   ════════════════════════════════════════════════════════════ */
function setupDateFilter() {
    const allDates = [...new Set((allData.trend||[]).map(d => d.snapshot_date))].sort();
    const fromSel  = document.getElementById('date-from');
    const toSel    = document.getElementById('date-to');

    allDates.forEach(d => {
        const label = new Date(d).toLocaleDateString('en-NZ',{day:'2-digit',month:'short',year:'numeric'});
        fromSel.innerHTML += `<option value="${d}">${label}</option>`;
        toSel.innerHTML   += `<option value="${d}">${label}</option>`;
    });

    fromSel.selectedIndex = Math.max(0, allDates.length-7);
    toSel.selectedIndex   = allDates.length-1;
    fromSel.addEventListener('change', renderProductCharts);
    toSel.addEventListener('change',   renderProductCharts);
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
   INIT
   ════════════════════════════════════════════════════════════ */
document.addEventListener('DOMContentLoaded', async () => {
    const [stats, trend, priceRange, stats7d, yesterday, week] = await Promise.all([
        getStatsPerProduct(),
        getAvgPriceOverTime(),
        getPriceRangeByProduct(),
        getPriceStatsLast7Days(),
        getPriceChangeVsYesterday(),
        getPriceChangeVsLastWeek()
    ]);

    allData = {
        stats:      stats      || [],
        trend:      trend      || [],
        priceRange: priceRange || [],
        stats7d:    stats7d    || [],
        yesterday:  yesterday  || [],
        week:       week       || []
    };

    setupDateFilter();
    renderDealCards();
    renderProductCharts();
    renderBoxPlot();
    renderCarousel();
    renderSpreadAndSellerCount();
    initCarousel();
    loadLastUpdated();
});