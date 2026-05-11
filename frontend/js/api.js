/* =============================================================
    api.js - Fetch layer for Retail Price Intelligence Dashboard
    Phase 02: HTML/CSS/JS frontend

    One function per FASTAPI endpoint.
    Change API_BASE once to switch between local and production.
============================================================= */

const API_BASE = "http://localhost:8000"; // Change to production URL when deployed

/* ── Helper ───────────────────────────────────────────────────
    All fetch calls go through this function.
      - Return parsed JSON on success
      - Logs the error and returns null on failure 
      - Caller always checks: if (data) return;
────────────────────────────────────────────────────────────── */

async function apiFetch(endpoint) {
     try {
        const res = await fetch(`${API_BASE}${endpoint}`);
        if (!res.ok) throw new Error(`HTTP ${res.status} on ${endpoint}`);
        return await res.json();
     } catch (err) {
        console.error(`[API] failed: ${endpoint}`, err);
        return null;
     }
}

/* ════════════════════════════════════════════════════════════
   OVERVIEW endpoints
   ════════════════════════════════════════════════════════════ */

/* Total number of price snapshot rows 
   Return: {total: 3425} */
async function getTotalListings() {
    return apiFetch('/api/overview/total-listings');
}

async function getTotalProducts() {
    return apiFetch('/api/overview/total-products');
}

/* Count of distinct sellers in dim_store 
    Return: {total: 42} */
async function getTotalSellers() {
    return apiFetch('/api/overview/total-sellers');
}

/* Top 15 sellers by listing count 
    Return: [{seller: "PB Tech", listings: 24 }, ...] */
async function getListingsBySeller() {
    return apiFetch('/api/overview/listings-by-seller');
}

/* Listing count grouped by category
   Returns: [{ category: "laptop", listings: 120 }, ...] */
async function getListingsByCategory() {
    return apiFetch('/api/overview/listings-by-category');
}

/* ════════════════════════════════════════════════════════════
    PRICE ANALYSIS endpoints
════════════════════════════════════════════════════════════ */

/* Average price per prodyct per snapshot date 
    Return: [{snapshot_date: "2024-01-01", product_name: "MacBook Pro 16", avg_price: 3500}, ...] */
async function getAvgPriceOverTime() {
    return apiFetch('/api/price/avg-price-over-time');
}

/* Full price stats per product with rating and reviews
   Returns: [{ product_name: "...", category: "...", seller_count: 5,
               min_price: 999, max_price: 1499, avg_price: 1199,
               cheapest_seller: "...", cheapest_price: 999,
               savings_pct: 16.68, avg_rating: 4.5, avg_reviews: 2300 }, ...] */
async function getStatsPerProduct() {
    return apiFetch('/api/price/stats-per-product');
}

/* Every individual price listing per product (for box plot)
   Returns: [{ product_name: "...", category: "...", price: 1199.0 }, ...] */
async function getPriceRangeByProduct() {
    return apiFetch('/api/price/price-range-by-product');
}

/* All listings with a discount, ordered highest discount first
   Returns: [{ product_name: "...", seller: "...", price: 799,
               old_price: 999, discount_pct: 20.0 }, ...] */
async function getDiscounts() {
    return apiFetch('/api/price/discounts');
}

/* Latest price vs previous day per product (LAG window function)
   Returns: [{ product_name: "...", category: "...", avg_price: 1250,
               prev_price: 1299, pct_change: -3.77,
               snapshot_date: "2026-05-09" }, ...] */
async function getPriceChangeVsYesterday() {
    return apiFetch('/api/price/change-vs-yesterday');
}

/* Today's price vs oldest available date per product
   Returns: [{ product_name: "...", category: "...",
               today_price: 1250, week_price: 1299,
               pct_change_week: -3.77 }, ...] */
async function getPriceChangeVsLastWeek() {
    return apiFetch('/api/price/change-vs-last-week');
}


/* Max, min, avg price per product over last 7 snapshot days
   Returns: [{ product_name: "...", category: "...",
               max_price_7d: 1499, min_price_7d: 999,
               avg_price_7d: 1199.5, latest_date: "2026-05-09" }, ...] */
async function getPriceStatsLast7Days() {
    return apiFetch('/api/price/stats-last-7-days');
}

/* ════════════════════════════════════════════════════════════
   SELLER INTELLIGENCE endpoints
   ════════════════════════════════════════════════════════════ */
/* How many sellers list each product
   Returns: [{ product_name: "...", category: "...", seller_count: 7 }, ...] */
async function getSellerCountPerProduct() {
    return apiFetch('/api/seller/seller-count-per-product');
}

/* Cheapest seller and price vs average per product 
   Returns: [{ product_name: "...", category: "...",
               cheapest_seller: "PB Tech", cheapest_price: 999,
               avg_price: 1199, savings_pct: 16.68 }, ...] */
async function getCheapestSellerPerProduct() {
    return apiFetch('/api/seller/cheapest-seller-per-product');
}

/* Top 15 sellers by average rating (min 2 listings)
   Returns: [{ seller: "...", avg_rating: 4.7,
               total_reviews: 8400, total_listings: 12 }, ...] */
async function getRatingBySeller() {
    return apiFetch('/api/seller/rating-by-seller');
}

/* Count of listings per rating_status bucket
   Returns: [{ rating_status: "Excellent", count: 45 }, ...] */
async function getRatingStatusDistribution() {
    return apiFetch('/api/seller/rating-status-distribution');
}

/* Aggregated stats per category
   Returns: [{ category: "Laptop", product_count: 3,
               seller_count: 12, total_listings: 180,
               min_price: 799, max_price: 3499, avg_price: 1650 }, ...] */
async function getCategorySummary() {
    return apiFetch('/api/seller/category-summary');
}

/* Cheapest seller per category from staging table (latest snapshot)
   Returns: [{ category: "laptop", product_name: "...", seller: "...",
               min_price: 999, avg_price: 1199, savings_pct: 16.7 }, ...] */
async function getCheapestSellerPerCategory() {
    return apiFetch('/api/seller/cheapest-seller-per-category');
}

/* Last update timestamp of the data */
async function getLastUpdated() {
    return apiFetch('/api/overview/last-updated');
}

/* ════════════════════════════════════════════════════════════
   HEALTH CHECK
   ═════════════════════════════════════════════════════ */
 
/* Confirms the FastAPI server is reachable
   Returns: { status: "ok", version: "1.0.0" } */
async function checkHealth() {
    return apiFetch('/health');
}