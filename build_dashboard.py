import json
import pandas as pd

# Load the dataset
df = pd.read_csv("sales_marketing_dataset.csv")

# Convert to JSON records
records_json = df.to_json(orient="records")

html_content = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Sales Performance & Marketing Intelligence Dashboard</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    body {{
      font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      background-color: #0b0f19;
      color: #f1f5f9;
    }}
    .glass-card {{
      background: rgba(17, 24, 39, 0.7);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid rgba(255, 255, 255, 0.07);
    }}
    .glass-card-hover {{
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .glass-card-hover:hover {{
      border-color: rgba(99, 102, 241, 0.35);
      transform: translateY(-2px);
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
    }}
    .chart-tooltip {{
      position: absolute;
      pointer-events: none;
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid rgba(99, 102, 241, 0.3);
      border-radius: 0.5rem;
      padding: 0.5rem 0.75rem;
      font-size: 0.75rem;
      color: #f8fafc;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
      z-index: 50;
      opacity: 0;
      transition: opacity 0.15s ease-out;
      white-space: nowrap;
    }}
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: #0f172a;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #334155;
      border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #475569;
    }}
  </style>
</head>
<body class="min-h-screen bg-[#0b0f19] text-slate-100 antialiased selection:bg-indigo-500 selection:text-white">

  <!-- Chart Tooltip DOM Element -->
  <div id="chartTooltip" class="chart-tooltip"></div>

  <div class="max-w-[1700px] mx-auto p-4 md:p-6 lg:p-8 space-y-6">

    <!-- Top Navigation & Header -->
    <header class="glass-card rounded-2xl p-5 md:p-6 shadow-xl flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 border border-slate-800">
      <div class="flex items-center gap-4">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 text-white font-black text-2xl">
          ₹
        </div>
        <div>
          <div class="flex flex-wrap items-center gap-3">
            <h1 class="text-xl md:text-2xl font-bold tracking-tight text-white">Sales & Marketing Intelligence Dashboard</h1>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse mr-1.5"></span>
              Live Formula Verified (220 Records)
            </span>
          </div>
          <p class="text-xs md:text-sm text-slate-400 mt-1">
            Sales Formula: <span class="text-indigo-400 font-mono font-medium">Main Rate × Qty × (1 − Discount %)</span> | Currency: Indian Rupee (<span class="font-bold text-slate-300">₹</span>)
          </p>
        </div>
      </div>

      <!-- Action buttons & Export -->
      <div class="flex flex-wrap items-center gap-3 w-full lg:w-auto">
        <button onclick="exportToCSV()" class="flex-1 lg:flex-initial inline-flex items-center justify-center gap-2 px-4 py-2 text-xs md:text-sm font-semibold rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 hover:border-slate-600 transition-all shadow-sm">
          <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path>
          </svg>
          Export Filtered CSV
        </button>
        <button onclick="resetAllFilters()" class="inline-flex items-center justify-center gap-2 px-3 py-2 text-xs md:text-sm font-medium rounded-xl bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 transition-all">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
          </svg>
          Reset Filters
        </button>
      </div>
    </header>

    <!-- Global Interactive Filter Bar -->
    <div class="glass-card rounded-2xl p-4 md:p-5 shadow-lg border border-slate-800/80">
      <div class="flex items-center justify-between mb-3">
        <span class="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <svg class="w-4 h-4 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z"></path>
          </svg>
          Real-time Cross Filters
        </span>
        <span id="activeFilterCount" class="text-xs text-indigo-400 font-medium">All 220 Records Active</span>
      </div>

      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        <!-- Month Filter -->
        <div>
          <label class="block text-[11px] font-semibold text-slate-400 mb-1">Time Period</label>
          <select id="periodFilter" onchange="applyFilters()" class="w-full bg-slate-900/90 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none">
            <option value="all" selected>All Q1 2026</option>
            <option value="2026-01">January 2026</option>
            <option value="2026-02">February 2026</option>
            <option value="2026-03">March 2026</option>
          </select>
        </div>

        <!-- Region Filter -->
        <div>
          <label class="block text-[11px] font-semibold text-slate-400 mb-1">Region</label>
          <select id="regionFilter" onchange="applyFilters()" class="w-full bg-slate-900/90 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none">
            <option value="all" selected>All Regions</option>
            <option value="West">West</option>
            <option value="South">South</option>
            <option value="North">North</option>
            <option value="East">East</option>
            <option value="Central">Central</option>
          </select>
        </div>

        <!-- Category Filter -->
        <div>
          <label class="block text-[11px] font-semibold text-slate-400 mb-1">Category</label>
          <select id="categoryFilter" onchange="applyFilters()" class="w-full bg-slate-900/90 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none">
            <option value="all" selected>All Categories</option>
            <option value="Electronics">Electronics</option>
            <option value="Accessories">Accessories</option>
            <option value="Wearable">Wearable</option>
            <option value="Entertainment">Entertainment</option>
          </select>
        </div>

        <!-- Campaign Filter -->
        <div>
          <label class="block text-[11px] font-semibold text-slate-400 mb-1">Campaign</label>
          <select id="campaignFilter" onchange="applyFilters()" class="w-full bg-slate-900/90 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none">
            <option value="all" selected>All Campaigns</option>
            <option value="Social Media">Social Media</option>
            <option value="Google Ads">Google Ads</option>
            <option value="Instagram">Instagram</option>
            <option value="Email">Email</option>
            <option value="Influencer">Influencer</option>
            <option value="Organic">Organic</option>
          </select>
        </div>

        <!-- Customer Type Filter -->
        <div>
          <label class="block text-[11px] font-semibold text-slate-400 mb-1">Customer Type</label>
          <select id="customerFilter" onchange="applyFilters()" class="w-full bg-slate-900/90 text-slate-200 border border-slate-700 rounded-xl px-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none">
            <option value="all" selected>All Customers</option>
            <option value="New">New Customers</option>
            <option value="Returning">Returning Customers</option>
          </select>
        </div>

        <!-- Search Input -->
        <div>
          <label class="block text-[11px] font-semibold text-slate-400 mb-1">Product / Order Search</label>
          <div class="relative">
            <input type="text" id="searchInput" oninput="applyFilters()" placeholder="e.g. Laptop, ORD001..." class="w-full bg-slate-900/90 text-slate-200 border border-slate-700 rounded-xl pl-8 pr-3 py-2 text-xs focus:ring-2 focus:ring-indigo-500 focus:outline-none placeholder-slate-500">
            <svg class="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Executive KPI Summary Cards -->
    <div class="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-6 gap-4">
      <!-- KPI 1: Total Sales -->
      <div class="glass-card glass-card-hover rounded-2xl p-4 md:p-5 border-l-4 border-l-emerald-500">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Sales</span>
          <span class="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
          </span>
        </div>
        <div id="kpiTotalSales" class="text-xl md:text-2xl font-bold text-white mt-2">₹0</div>
        <div class="flex items-center gap-1.5 mt-1 text-[11px] text-slate-400">
          <span>Avg Order:</span>
          <span id="kpiAOV" class="text-slate-300 font-semibold">₹0</span>
        </div>
      </div>

      <!-- KPI 2: Total Profit -->
      <div class="glass-card glass-card-hover rounded-2xl p-4 md:p-5 border-l-4 border-l-blue-500">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Net Profit</span>
          <span class="p-2 rounded-xl bg-blue-500/10 text-blue-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </span>
        </div>
        <div id="kpiTotalProfit" class="text-xl md:text-2xl font-bold text-white mt-2">₹0</div>
        <div class="flex items-center gap-1.5 mt-1 text-[11px] text-slate-400">
          <span>Profit Margin:</span>
          <span id="kpiProfitMargin" class="text-blue-400 font-semibold">0.0%</span>
        </div>
      </div>

      <!-- KPI 3: Marketing Spend -->
      <div class="glass-card glass-card-hover rounded-2xl p-4 md:p-5 border-l-4 border-l-purple-500">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Mkt Spend</span>
          <span class="p-2 rounded-xl bg-purple-500/10 text-purple-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5.882V19.24a1.76 1.76 0 01-3.417.592l-2.147-6.15M18 13a3 3 0 100-6M5.436 13.683A4.001 4.001 0 017 6h1.832c4.1 0 7.625-1.234 9.168-3v14c-1.543-1.766-5.067-3-9.168-3H7a3.988 3.988 0 01-1.564-.317z"></path>
            </svg>
          </span>
        </div>
        <div id="kpiMarketingSpend" class="text-xl md:text-2xl font-bold text-white mt-2">₹0</div>
        <div class="flex items-center gap-1.5 mt-1 text-[11px] text-slate-400">
          <span>Cost/Sale:</span>
          <span id="kpiSpendPerOrder" class="text-purple-300 font-semibold">₹0</span>
        </div>
      </div>

      <!-- KPI 4: Blended ROAS -->
      <div class="glass-card glass-card-hover rounded-2xl p-4 md:p-5 border-l-4 border-l-amber-500">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">ROAS (Sales / Spend)</span>
          <span class="p-2 rounded-xl bg-amber-500/10 text-amber-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
            </svg>
          </span>
        </div>
        <div id="kpiROAS" class="text-xl md:text-2xl font-bold text-amber-400 mt-2">0.0x</div>
        <div class="flex items-center gap-1.5 mt-1 text-[11px] text-slate-400">
          <span>Return Efficiency:</span>
          <span id="kpiROASTier" class="text-emerald-400 font-semibold">High ROI</span>
        </div>
      </div>

      <!-- KPI 5: Orders & Units -->
      <div class="glass-card glass-card-hover rounded-2xl p-4 md:p-5 border-l-4 border-l-cyan-500">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Orders & Units</span>
          <span class="p-2 rounded-xl bg-cyan-500/10 text-cyan-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path>
            </svg>
          </span>
        </div>
        <div id="kpiTotalOrders" class="text-xl md:text-2xl font-bold text-white mt-2">0</div>
        <div class="flex items-center gap-1.5 mt-1 text-[11px] text-slate-400">
          <span>Total Units:</span>
          <span id="kpiTotalQuantity" class="text-cyan-300 font-semibold">0</span>
        </div>
      </div>

      <!-- KPI 6: Average Discount -->
      <div class="glass-card glass-card-hover rounded-2xl p-4 md:p-5 border-l-4 border-l-rose-500">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-slate-400 uppercase tracking-wider">Avg Discount</span>
          <span class="p-2 rounded-xl bg-rose-500/10 text-rose-400">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
            </svg>
          </span>
        </div>
        <div id="kpiAvgDiscount" class="text-xl md:text-2xl font-bold text-rose-400 mt-2">0.0%</div>
        <div class="flex items-center gap-1.5 mt-1 text-[11px] text-slate-400">
          <span>Discount Volume:</span>
          <span id="kpiDiscountedCount" class="text-slate-300 font-semibold">0 Orders</span>
        </div>
      </div>
    </div>

    <!-- Visual Analytics Tabs -->
    <div class="flex border-b border-slate-800 space-x-2">
      <button onclick="switchView('visuals')" id="tabVisuals" class="px-5 py-2.5 text-xs md:text-sm font-semibold rounded-t-xl bg-indigo-600 text-white transition-all">
        📊 Visual Analytics Suite (All 8 Charts)
      </button>
      <button onclick="switchView('ledger')" id="tabLedger" class="px-5 py-2.5 text-xs md:text-sm font-medium rounded-t-xl text-slate-400 hover:text-slate-200 transition-all">
        📋 Granular Data Ledger (Table & Export)
      </button>
    </div>

    <!-- MAIN VISUAL ANALYTICS CONTAINER -->
    <div id="viewVisuals" class="space-y-6">

      <!-- ROW 1: Daily Sales Trend & Regional Breakdown -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <!-- VISUAL 1: 📈 Daily Sales (Date vs Sales) -->
        <div class="lg:col-span-2 glass-card rounded-2xl p-5 border border-slate-800">
          <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-emerald-400 text-base">📈</span>
                <h3 class="text-base font-bold text-white">Daily Sales Trend (Date vs Sales)</h3>
              </div>
              <p class="text-xs text-slate-400">Timeline of sales revenue generated across Q1 2026</p>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span class="inline-block w-3 h-3 rounded-full bg-emerald-500"></span>
              <span class="text-slate-300">Sales (₹)</span>
              <span class="inline-block w-3 h-3 rounded-full bg-blue-500 ml-2"></span>
              <span class="text-slate-300">Profit (₹)</span>
            </div>
          </div>
          <!-- Canvas for Daily Sales -->
          <div class="relative w-full h-[280px]">
            <canvas id="dailySalesCanvas" class="w-full h-full cursor-crosshair"></canvas>
          </div>
        </div>

        <!-- VISUAL 6: 🌍 Sales by Region -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800 flex flex-col justify-between">
          <div>
            <div class="flex items-center gap-2 mb-1">
              <span class="text-blue-400 text-base">🌍</span>
              <h3 class="text-base font-bold text-white">Sales by Region</h3>
            </div>
            <p class="text-xs text-slate-400 mb-3">Geographical distribution across 5 key territories</p>
            
            <div class="relative w-full h-[200px] flex items-center justify-center">
              <canvas id="regionDonutCanvas" class="w-full h-full"></canvas>
            </div>
          </div>

          <div id="regionLegend" class="grid grid-cols-2 gap-2 mt-4 pt-3 border-t border-slate-800/80 text-xs">
            <!-- Populated via JS -->
          </div>
        </div>

      </div>

      <!-- ROW 2: Product Breakdown & Main Rate vs Sales -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- VISUAL 4: 📊 Sales by Product -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800">
          <div class="flex items-center justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-indigo-400 text-base">📊</span>
                <h3 class="text-base font-bold text-white">Sales by Product</h3>
              </div>
              <p class="text-xs text-slate-400">Ranked revenue performance and units sold per product</p>
            </div>
            <span class="text-xs font-semibold text-slate-400">Ranked by Revenue</span>
          </div>
          <div id="productRankingsContainer" class="space-y-3 max-h-[340px] overflow-y-auto pr-1">
            <!-- Populated via JS -->
          </div>
        </div>

        <!-- VISUAL 2: 💰 Main Rate vs Sales (Product Comparison) -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800">
          <div class="flex items-center justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-amber-400 text-base">💰</span>
                <h3 class="text-base font-bold text-white">Main Rate vs Sales (Product Comparison)</h3>
              </div>
              <p class="text-xs text-slate-400">Unit base price vs Total realized revenue</p>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span class="inline-block w-3 h-3 rounded bg-amber-400"></span>
              <span class="text-slate-300">Base Rate</span>
              <span class="inline-block w-3 h-3 rounded bg-indigo-500 ml-2"></span>
              <span class="text-slate-300">Total Sales</span>
            </div>
          </div>
          <div class="relative w-full h-[320px]">
            <canvas id="mainRateVsSalesCanvas" class="w-full h-full cursor-pointer"></canvas>
          </div>
        </div>

      </div>

      <!-- ROW 3: Marketing Spend vs Sales & Sales by Campaign -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- VISUAL 8: 📣 Marketing Spend vs Sales (ROAS & Efficiency) -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800">
          <div class="flex items-center justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-purple-400 text-base">📣</span>
                <h3 class="text-base font-bold text-white">Marketing Spend vs Sales</h3>
              </div>
              <p class="text-xs text-slate-400">Acquisition spend vs revenue delivered across campaigns</p>
            </div>
            <div class="flex items-center gap-2 text-xs">
              <span class="inline-block w-3 h-3 rounded bg-purple-500"></span>
              <span class="text-slate-300">Spend</span>
              <span class="inline-block w-3 h-3 rounded bg-emerald-500 ml-2"></span>
              <span class="text-slate-300">Sales</span>
            </div>
          </div>
          <div class="relative w-full h-[280px]">
            <canvas id="mktSpendVsSalesCanvas" class="w-full h-full cursor-pointer"></canvas>
          </div>
          <div id="roasSummaryCards" class="grid grid-cols-3 gap-2 mt-3 pt-3 border-t border-slate-800 text-xs">
            <!-- ROAS badges populated via JS -->
          </div>
        </div>

        <!-- VISUAL 5: 📢 Sales by Marketing Campaign -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800">
          <div class="flex items-center justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-rose-400 text-base">📢</span>
                <h3 class="text-base font-bold text-white">Sales by Marketing Campaign</h3>
              </div>
              <p class="text-xs text-slate-400">Channel revenue attribution & wallet share %</p>
            </div>
            <span class="text-xs font-semibold text-slate-400">Channel Share</span>
          </div>
          <div id="campaignDistributionContainer" class="space-y-3">
            <!-- Populated via JS -->
          </div>
        </div>

      </div>

      <!-- ROW 4: Discount Analysis & Profit Analysis -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">

        <!-- VISUAL 3: 🏷️ Discount Analysis (Discount % vs Sales) -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800">
          <div class="flex items-center justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-teal-400 text-base">🏷️</span>
                <h3 class="text-base font-bold text-white">Discount Analysis (Discount % vs Sales)</h3>
              </div>
              <p class="text-xs text-slate-400">Impact of promotional discount tiers on total sales & order volume</p>
            </div>
          </div>
          <div class="relative w-full h-[280px]">
            <canvas id="discountAnalysisCanvas" class="w-full h-full"></canvas>
          </div>
        </div>

        <!-- VISUAL 7: 💵 Profit Analysis -->
        <div class="glass-card rounded-2xl p-5 border border-slate-800">
          <div class="flex items-center justify-between mb-4">
            <div>
              <div class="flex items-center gap-2">
                <span class="text-green-400 text-base">💵</span>
                <h3 class="text-base font-bold text-white">Profit Analysis by Category</h3>
              </div>
              <p class="text-xs text-slate-400">Net Profit generated and profit margin % across categories</p>
            </div>
            <span class="text-xs text-green-400 font-semibold">Margin Retention</span>
          </div>
          <div class="relative w-full h-[280px]">
            <canvas id="profitAnalysisCanvas" class="w-full h-full"></canvas>
          </div>
        </div>

      </div>

    </div>

    <!-- GRANULAR DATA LEDGER CONTAINER -->
    <div id="viewLedger" class="hidden space-y-4">
      <div class="glass-card rounded-2xl p-5 border border-slate-800">
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
          <div>
            <h3 class="text-base font-bold text-white flex items-center gap-2">
              <span>📋</span> All Transaction Records (Complete Dataset)
            </h3>
            <p class="text-xs text-slate-400">13 Columns adhering to: <code class="text-indigo-400">Sales = Main Rate × Qty × (1 − Discount Rate)</code></p>
          </div>
          <div class="flex items-center gap-3">
            <span id="ledgerRecordCount" class="text-xs text-slate-400">Showing 1-15 of 220 records</span>
            <select id="pageSizeSelect" onchange="changePageSize()" class="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1 text-xs text-slate-200">
              <option value="15" selected>15 / page</option>
              <option value="30">30 / page</option>
              <option value="50">50 / page</option>
              <option value="100">100 / page</option>
            </select>
          </div>
        </div>

        <!-- Responsive Table -->
        <div class="overflow-x-auto rounded-xl border border-slate-800">
          <table class="w-full text-left text-xs whitespace-nowrap">
            <thead class="bg-slate-900/90 text-slate-400 uppercase tracking-wider font-semibold border-b border-slate-800">
              <tr>
                <th onclick="sortTable('Date')" class="p-3 cursor-pointer hover:text-white">Date ↕</th>
                <th onclick="sortTable('Order ID')" class="p-3 cursor-pointer hover:text-white">Order ID ↕</th>
                <th onclick="sortTable('Region')" class="p-3 cursor-pointer hover:text-white">Region ↕</th>
                <th onclick="sortTable('Product')" class="p-3 cursor-pointer hover:text-white">Product ↕</th>
                <th onclick="sortTable('Category')" class="p-3 cursor-pointer hover:text-white">Category ↕</th>
                <th onclick="sortTable('Customer Type')" class="p-3 cursor-pointer hover:text-white">Customer Type ↕</th>
                <th onclick="sortTable('Campaign')" class="p-3 cursor-pointer hover:text-white">Campaign ↕</th>
                <th onclick="sortTable('Quantity')" class="p-3 text-center cursor-pointer hover:text-white">Qty ↕</th>
                <th onclick="sortTable('Main Rate')" class="p-3 text-right cursor-pointer hover:text-white">Main Rate (₹) ↕</th>
                <th onclick="sortTable('Discount Rate')" class="p-3 text-right cursor-pointer hover:text-white">Discount % ↕</th>
                <th onclick="sortTable('Sales')" class="p-3 text-right cursor-pointer text-emerald-400 font-bold hover:text-emerald-300">Sales (₹) ↕</th>
                <th onclick="sortTable('Profit')" class="p-3 text-right cursor-pointer text-blue-400 font-bold hover:text-blue-300">Profit (₹) ↕</th>
                <th onclick="sortTable('Marketing Spend')" class="p-3 text-right cursor-pointer text-purple-400 hover:text-purple-300">Mkt Spend (₹) ↕</th>
              </tr>
            </thead>
            <tbody id="ledgerTableBody" class="divide-y divide-slate-800/60 bg-slate-950/40">
              <!-- Rendered via JS -->
            </tbody>
          </table>
        </div>

        <!-- Pagination Controls -->
        <div class="flex items-center justify-between pt-4">
          <button id="btnPrevPage" onclick="prevPage()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold disabled:opacity-40 disabled:cursor-not-allowed">
            Previous
          </button>
          <span id="pageIndicator" class="text-xs text-slate-400 font-medium">Page 1 of 15</span>
          <button id="btnNextPage" onclick="nextPage()" class="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold disabled:opacity-40 disabled:cursor-not-allowed">
            Next
          </button>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="text-center py-4 text-xs text-slate-500 border-t border-slate-900">
      Sales Performance Analysis + Marketing Dashboard | Built with HTML5 Canvas, Tailwind CSS & Vanilla JS
    </footer>

  </div>

  <!-- EMBEDDED DATASET & CORE CONTROLLER SCRIPT -->
  <script>
    // Embedded Complete Dataset ({len(df)} records)
    const rawDataset = {records_json};

    let filteredData = [...rawDataset];
    let currentPage = 1;
    let pageSize = 15;
    let sortColumn = "Date";
    let sortAsc = true;

    // Format Indian Rupee currency (₹)
    function formatINR(val) {{
      return new Intl.NumberFormat('en-IN', {{
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 0
      }}).format(val);
    }}

    // Compact format for charts (e.g. ₹1.2L, ₹45k)
    function formatCompactINR(val) {{
      if (val >= 10000000) return '₹' + (val / 10000000).toFixed(1) + ' Cr';
      if (val >= 100000) return '₹' + (val / 100000).toFixed(1) + 'L';
      if (val >= 1000) return '₹' + (val / 1000).toFixed(0) + 'k';
      return '₹' + val.toFixed(0);
    }}

    // Format Percent
    function formatPercent(val) {{
      return (val * 100).toFixed(1) + '%';
    }}

    // Switch between Visuals and Ledger view
    function switchView(viewName) {{
      const vVisuals = document.getElementById('viewVisuals');
      const vLedger = document.getElementById('viewLedger');
      const tVisuals = document.getElementById('tabVisuals');
      const tLedger = document.getElementById('tabLedger');

      if (viewName === 'visuals') {{
        vVisuals.classList.remove('hidden');
        vLedger.classList.add('hidden');
        tVisuals.className = "px-5 py-2.5 text-xs md:text-sm font-semibold rounded-t-xl bg-indigo-600 text-white transition-all";
        tLedger.className = "px-5 py-2.5 text-xs md:text-sm font-medium rounded-t-xl text-slate-400 hover:text-slate-200 transition-all";
        renderAllVisuals();
      }} else {{
        vVisuals.classList.add('hidden');
        vLedger.classList.remove('hidden');
        tLedger.className = "px-5 py-2.5 text-xs md:text-sm font-semibold rounded-t-xl bg-indigo-600 text-white transition-all";
        tVisuals.className = "px-5 py-2.5 text-xs md:text-sm font-medium rounded-t-xl text-slate-400 hover:text-slate-200 transition-all";
        renderLedgerTable();
      }}
    }}

    // Apply interactive filters
    function applyFilters() {{
      const period = document.getElementById('periodFilter').value;
      const region = document.getElementById('regionFilter').value;
      const category = document.getElementById('categoryFilter').value;
      const campaign = document.getElementById('campaignFilter').value;
      const customer = document.getElementById('customerFilter').value;
      const search = document.getElementById('searchInput').value.toLowerCase().trim();

      filteredData = rawDataset.filter(row => {{
        if (period !== 'all' && !row["Date"].startsWith(period)) return false;
        if (region !== 'all' && row["Region"] !== region) return false;
        if (category !== 'all' && row["Category"] !== category) return false;
        if (campaign !== 'all' && row["Campaign"] !== campaign) return false;
        if (customer !== 'all' && row["Customer Type"] !== customer) return false;
        if (search) {{
          const term = `${{row["Product"]}} ${{row["Order ID"]}} ${{row["Campaign"]}} ${{row["Region"]}}`.toLowerCase();
          if (!term.includes(search)) return false;
        }}
        return true;
      }});

      document.getElementById('activeFilterCount').innerText = `${{filteredData.length}} of ${{rawDataset.length}} Records Active`;

      updateKPICards();
      renderAllVisuals();
      currentPage = 1;
      renderLedgerTable();
    }}

    function resetAllFilters() {{
      document.getElementById('periodFilter').value = 'all';
      document.getElementById('regionFilter').value = 'all';
      document.getElementById('categoryFilter').value = 'all';
      document.getElementById('campaignFilter').value = 'all';
      document.getElementById('customerFilter').value = 'all';
      document.getElementById('searchInput').value = '';
      applyFilters();
    }}

    // Update KPI Cards
    function updateKPICards() {{
      const totalSales = filteredData.reduce((acc, r) => acc + r["Sales"], 0);
      const totalProfit = filteredData.reduce((acc, r) => acc + r["Profit"], 0);
      const totalSpend = filteredData.reduce((acc, r) => acc + r["Marketing Spend"], 0);
      const totalQty = filteredData.reduce((acc, r) => acc + r["Quantity"], 0);
      const orderCount = filteredData.length;

      const aov = orderCount > 0 ? totalSales / orderCount : 0;
      const margin = totalSales > 0 ? (totalProfit / totalSales) * 100 : 0;
      const spendPerOrder = orderCount > 0 ? totalSpend / orderCount : 0;
      const roas = totalSpend > 0 ? (totalSales / totalSpend) : 0;

      const totalDiscounts = filteredData.reduce((acc, r) => acc + r["Discount Rate"], 0);
      const avgDiscount = orderCount > 0 ? (totalDiscounts / orderCount) : 0;
      const discountedOrders = filteredData.filter(r => r["Discount Rate"] > 0).length;

      document.getElementById('kpiTotalSales').innerText = formatINR(totalSales);
      document.getElementById('kpiAOV').innerText = formatINR(aov);

      document.getElementById('kpiTotalProfit').innerText = formatINR(totalProfit);
      document.getElementById('kpiProfitMargin').innerText = margin.toFixed(1) + '%';

      document.getElementById('kpiMarketingSpend').innerText = formatINR(totalSpend);
      document.getElementById('kpiSpendPerOrder').innerText = formatINR(spendPerOrder);

      document.getElementById('kpiROAS').innerText = roas.toFixed(2) + 'x';
      const roasBadge = document.getElementById('kpiROASTier');
      if (roas >= 5) {{
        roasBadge.innerText = 'High ROAS (5x+)';
        roasBadge.className = 'text-emerald-400 font-semibold';
      }} else if (roas >= 3) {{
        roasBadge.innerText = 'Healthy (3x-5x)';
        roasBadge.className = 'text-amber-400 font-semibold';
      }} else {{
        roasBadge.innerText = 'Optimizable (<3x)';
        roasBadge.className = 'text-rose-400 font-semibold';
      }}

      document.getElementById('kpiTotalOrders').innerText = orderCount.toLocaleString('en-IN');
      document.getElementById('kpiTotalQuantity').innerText = totalQty.toLocaleString('en-IN') + ' Units';

      document.getElementById('kpiAvgDiscount').innerText = (avgDiscount * 100).toFixed(1) + '%';
      document.getElementById('kpiDiscountedCount').innerText = `${{discountedOrders}} / ${{orderCount}} Orders`;
    }}

    // Tooltip Helpers
    const tooltipEl = document.getElementById('chartTooltip');
    function showTooltip(e, html) {{
      tooltipEl.innerHTML = html;
      tooltipEl.style.opacity = '1';
      tooltipEl.style.left = (e.pageX + 12) + 'px';
      tooltipEl.style.top = (e.pageY - 28) + 'px';
    }}
    function hideTooltip() {{
      tooltipEl.style.opacity = '0';
    }}

    // ==========================================
    // CHART 1: DAILY SALES TREND (Date vs Sales)
    // ==========================================
    function renderDailySalesChart() {{
      const canvas = document.getElementById('dailySalesCanvas');
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      const width = rect.width;
      const height = rect.height;

      ctx.clearRect(0, 0, width, height);

      if (filteredData.length === 0) {{
        ctx.fillStyle = '#64748b';
        ctx.font = '13px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText('No data matching active filters', width / 2, height / 2);
        return;
      }}

      // Group by Date
      const dateMap = {{}};
      filteredData.forEach(r => {{
        if (!dateMap[r["Date"]]) dateMap[r["Date"]] = {{ sales: 0, profit: 0, count: 0 }};
        dateMap[r["Date"]].sales += r["Sales"];
        dateMap[r["Date"]].profit += r["Profit"];
        dateMap[r["Date"]].count += 1;
      }});

      const sortedDates = Object.keys(dateMap).sort();
      const padding = {{ top: 20, right: 30, bottom: 40, left: 65 }};
      const chartW = width - padding.left - padding.right;
      const chartH = height - padding.top - padding.bottom;

      const maxSales = Math.max(...sortedDates.map(d => dateMap[d].sales), 1000);
      const minSales = 0;

      // Draw Grid Lines & Y-axis labels
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';

      const gridSteps = 4;
      for (let i = 0; i <= gridSteps; i++) {{
        const yVal = minSales + (maxSales - minSales) * (i / gridSteps);
        const yPos = padding.top + chartH - (i / gridSteps) * chartH;
        ctx.beginPath();
        ctx.moveTo(padding.left, yPos);
        ctx.lineTo(width - padding.right, yPos);
        ctx.stroke();
        ctx.fillText(formatCompactINR(yVal), padding.left - 8, yPos + 3);
      }}

      // Calculate coordinates
      const points = sortedDates.map((date, idx) => {{
        const x = padding.left + (idx / (sortedDates.length - 1 || 1)) * chartW;
        const ySales = padding.top + chartH - ((dateMap[date].sales - minSales) / (maxSales - minSales)) * chartH;
        const yProfit = padding.top + chartH - ((dateMap[date].profit - minSales) / (maxSales - minSales)) * chartH;
        return {{ date, x, ySales, yProfit, sales: dateMap[date].sales, profit: dateMap[date].profit, count: dateMap[date].count }};
      }});

      // Draw Sales Area Gradient
      const gradSales = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartH);
      gradSales.addColorStop(0, 'rgba(16, 185, 129, 0.25)');
      gradSales.addColorStop(1, 'rgba(16, 185, 129, 0.0)');

      ctx.beginPath();
      ctx.moveTo(points[0].x, padding.top + chartH);
      points.forEach(pt => ctx.lineTo(pt.x, pt.ySales));
      ctx.lineTo(points[points.length - 1].x, padding.top + chartH);
      ctx.closePath();
      ctx.fillStyle = gradSales;
      ctx.fill();

      // Draw Sales Line
      ctx.beginPath();
      points.forEach((pt, idx) => {{
        if (idx === 0) ctx.moveTo(pt.x, pt.ySales);
        else ctx.lineTo(pt.x, pt.ySales);
      }});
      ctx.strokeStyle = '#10b981';
      ctx.lineWidth = 2.5;
      ctx.stroke();

      // Draw Profit Line
      ctx.beginPath();
      points.forEach((pt, idx) => {{
        if (idx === 0) ctx.moveTo(pt.x, pt.yProfit);
        else ctx.lineTo(pt.x, pt.yProfit);
      }});
      ctx.strokeStyle = '#3b82f6';
      ctx.lineWidth = 1.8;
      ctx.stroke();

      // Draw Points
      points.forEach(pt => {{
        ctx.beginPath();
        ctx.arc(pt.x, pt.ySales, 3.5, 0, Math.PI * 2);
        ctx.fillStyle = '#10b981';
        ctx.fill();
        ctx.lineWidth = 1.5;
        ctx.strokeStyle = '#0b0f19';
        ctx.stroke();
      }});

      // X Axis dates (sampling)
      ctx.fillStyle = '#64748b';
      ctx.textAlign = 'center';
      const labelInterval = Math.max(1, Math.floor(sortedDates.length / 6));
      sortedDates.forEach((d, idx) => {{
        if (idx % labelInterval === 0 || idx === sortedDates.length - 1) {{
          const pt = points[idx];
          const label = d.substring(5); // MM-DD
          ctx.fillText(label, pt.x, padding.top + chartH + 18);
        }}
      }});

      // Mousemove tooltip
      canvas.onmousemove = (e) => {{
        const b = canvas.getBoundingClientRect();
        const mx = e.clientX - b.left;
        let nearest = points[0];
        let minDist = Math.abs(points[0].x - mx);
        points.forEach(pt => {{
          const dist = Math.abs(pt.x - mx);
          if (dist < minDist) {{
            minDist = dist;
            nearest = pt;
          }}
        }});
        if (minDist < 30) {{
          showTooltip(e, `
            <div class="font-bold text-slate-200">${{nearest.date}}</div>
            <div class="text-emerald-400 font-semibold mt-1">Sales: ${{formatINR(nearest.sales)}}</div>
            <div class="text-blue-400 font-semibold">Profit: ${{formatINR(nearest.profit)}}</div>
            <div class="text-slate-400 text-[10px] mt-0.5">${{nearest.count}} Orders</div>
          `);
        }} else {{
          hideTooltip();
        }}
      }};
      canvas.onmouseleave = hideTooltip;
    }}

    // ==========================================
    // CHART 6: SALES BY REGION (Donut + Legend)
    // ==========================================
    function renderRegionDonut() {{
      const canvas = document.getElementById('regionDonutCanvas');
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      const width = rect.width;
      const height = rect.height;

      ctx.clearRect(0, 0, width, height);

      const regionMap = {{ "West": 0, "South": 0, "North": 0, "East": 0, "Central": 0 }};
      filteredData.forEach(r => {{
        if (regionMap[r["Region"]] !== undefined) {{
          regionMap[r["Region"]] += r["Sales"];
        }}
      }});

      const totalRegionalSales = Object.values(regionMap).reduce((a, b) => a + b, 0);

      const colors = {{
        "West": "#6366f1",
        "South": "#10b981",
        "North": "#f59e0b",
        "East": "#ec4899",
        "Central": "#06b6d4"
      }};

      const centerX = width / 2;
      const centerY = height / 2;
      const outerRadius = Math.min(centerX, centerY) - 15;
      const innerRadius = outerRadius * 0.62;

      let currentAngle = -Math.PI / 2;

      Object.entries(regionMap).forEach(([region, val]) => {{
        const sliceAngle = totalRegionalSales > 0 ? (val / totalRegionalSales) * (Math.PI * 2) : 0;
        ctx.beginPath();
        ctx.arc(centerX, centerY, outerRadius, currentAngle, currentAngle + sliceAngle);
        ctx.arc(centerX, centerY, innerRadius, currentAngle + sliceAngle, currentAngle, true);
        ctx.closePath();
        ctx.fillStyle = colors[region] || '#94a3b8';
        ctx.fill();
        ctx.lineWidth = 2;
        ctx.strokeStyle = '#0b0f19';
        ctx.stroke();
        currentAngle += sliceAngle;
      }});

      // Center Text
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 15px sans-serif';
      ctx.fillText(formatCompactINR(totalRegionalSales), centerX, centerY - 4);
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.fillText('All Regions', centerX, centerY + 14);

      // Render legend cards below
      const legendContainer = document.getElementById('regionLegend');
      legendContainer.innerHTML = '';
      Object.entries(regionMap).forEach(([region, val]) => {{
        const pct = totalRegionalSales > 0 ? ((val / totalRegionalSales) * 100).toFixed(1) : '0';
        const item = document.createElement('div');
        item.className = 'flex items-center justify-between p-1.5 rounded-lg bg-slate-900/60 border border-slate-800/80';
        item.innerHTML = `
          <div class="flex items-center gap-1.5">
            <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${{colors[region]}}"></span>
            <span class="font-medium text-slate-300">${{region}}</span>
          </div>
          <div class="text-right">
            <span class="font-bold text-white">${{pct}}%</span>
          </div>
        `;
        legendContainer.appendChild(item);
      }});
    }}

    // ==========================================
    // CHART 4: SALES BY PRODUCT (Ranked Bars)
    // ==========================================
    function renderProductRankings() {{
      const container = document.getElementById('productRankingsContainer');
      container.innerHTML = '';

      const productMap = {{}};
      filteredData.forEach(r => {{
        if (!productMap[r["Product"]]) productMap[r["Product"]] = {{ sales: 0, qty: 0, category: r["Category"] }};
        productMap[r["Product"]].sales += r["Sales"];
        productMap[r["Product"]].qty += r["Quantity"];
      }});

      const sortedProducts = Object.entries(productMap).sort((a, b) => b[1].sales - a[1].sales);
      const maxProductSales = sortedProducts.length > 0 ? sortedProducts[0][1].sales : 1;

      sortedProducts.forEach(([prod, data], idx) => {{
        const pctOfMax = (data.sales / maxProductSales) * 100;
        const item = document.createElement('div');
        item.className = 'p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80 hover:border-indigo-500/30 transition-all';
        item.innerHTML = `
          <div class="flex items-center justify-between text-xs mb-1.5">
            <div class="flex items-center gap-2">
              <span class="w-5 h-5 rounded-full bg-slate-800 text-slate-400 flex items-center justify-center font-bold text-[10px]">#${{idx + 1}}</span>
              <span class="font-semibold text-slate-200">${{prod}}</span>
              <span class="text-[10px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">${{data.category}}</span>
            </div>
            <div class="text-right">
              <span class="font-bold text-emerald-400">${{formatINR(data.sales)}}</span>
              <span class="text-slate-400 text-[10px] ml-1.5">(${{data.qty}} units)</span>
            </div>
          </div>
          <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div class="bg-gradient-to-r from-indigo-500 to-emerald-400 h-2 rounded-full transition-all duration-500" style="width: ${{pctOfMax}}%"></div>
          </div>
        `;
        container.appendChild(item);
      }});
    }}

    // ==========================================
    // CHART 2: MAIN RATE VS SALES (Product Comparison)
    // ==========================================
    function renderMainRateVsSalesChart() {{
      const canvas = document.getElementById('mainRateVsSalesCanvas');
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      const width = rect.width;
      const height = rect.height;

      ctx.clearRect(0, 0, width, height);

      const prodMap = {{}};
      filteredData.forEach(r => {{
        if (!prodMap[r["Product"]]) prodMap[r["Product"]] = {{ mainRate: r["Main Rate"], totalSales: 0, orders: 0 }};
        prodMap[r["Product"]].totalSales += r["Sales"];
        prodMap[r["Product"]].orders += 1;
      }});

      const prods = Object.keys(prodMap).sort((a, b) => prodMap[b].totalSales - prodMap[a].totalSales);
      if (prods.length === 0) return;

      const padding = {{ top: 25, right: 25, bottom: 65, left: 70 }};
      const chartW = width - padding.left - padding.right;
      const chartH = height - padding.top - padding.bottom;

      const maxSales = Math.max(...prods.map(p => prodMap[p].totalSales), 1000);
      const maxRate = Math.max(...prods.map(p => prodMap[p].mainRate), 1000);

      // Grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';

      for (let i = 0; i <= 4; i++) {{
        const yPos = padding.top + chartH - (i / 4) * chartH;
        ctx.beginPath();
        ctx.moveTo(padding.left, yPos);
        ctx.lineTo(width - padding.right, yPos);
        ctx.stroke();
        ctx.fillText(formatCompactINR((i / 4) * maxSales), padding.left - 8, yPos + 3);
      }}

      const groupW = chartW / prods.length;
      const barW = Math.max(5, groupW * 0.32);

      const hitBoxes = [];

      prods.forEach((prod, i) => {{
        const gx = padding.left + i * groupW + groupW / 2;
        const rateNorm = prodMap[prod].mainRate / maxRate;
        const salesNorm = prodMap[prod].totalSales / maxSales;

        const hRate = rateNorm * chartH;
        const hSales = salesNorm * chartH;

        const xRate = gx - barW - 1.5;
        const xSales = gx + 1.5;

        // Draw Main Rate Bar (Amber)
        ctx.fillStyle = '#f59e0b';
        ctx.fillRect(xRate, padding.top + chartH - hRate, barW, hRate);

        // Draw Sales Bar (Indigo)
        ctx.fillStyle = '#6366f1';
        ctx.fillRect(xSales, padding.top + chartH - hSales, barW, hSales);

        // X Labels (rotated slightly)
        ctx.save();
        ctx.translate(gx, padding.top + chartH + 12);
        ctx.rotate(-Math.PI / 4);
        ctx.textAlign = 'right';
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '10px sans-serif';
        ctx.fillText(prod, 0, 0);
        ctx.restore();

        hitBoxes.push({{
          gx, xRate, xSales, barW, prod,
          mainRate: prodMap[prod].mainRate,
          totalSales: prodMap[prod].totalSales,
          orders: prodMap[prod].orders
        }});
      }});

      canvas.onmousemove = (e) => {{
        const b = canvas.getBoundingClientRect();
        const mx = e.clientX - b.left;
        const hit = hitBoxes.find(h => Math.abs(h.gx - mx) < groupW / 2);
        if (hit) {{
          showTooltip(e, `
            <div class="font-bold text-white">${{hit.prod}}</div>
            <div class="text-amber-400 font-medium mt-1">Main Rate: ${{formatINR(hit.mainRate)}}</div>
            <div class="text-indigo-400 font-semibold">Realized Sales: ${{formatINR(hit.totalSales)}}</div>
            <div class="text-slate-400 text-[10px]">${{hit.orders}} Orders</div>
          `);
        }} else {{
          hideTooltip();
        }}
      }};
      canvas.onmouseleave = hideTooltip;
    }}

    // ==========================================
    // CHART 8: MARKETING SPEND VS SALES (ROAS)
    // ==========================================
    function renderMarketingSpendVsSales() {{
      const canvas = document.getElementById('mktSpendVsSalesCanvas');
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      const width = rect.width;
      const height = rect.height;

      ctx.clearRect(0, 0, width, height);

      const campMap = {{}};
      filteredData.forEach(r => {{
        if (!campMap[r["Campaign"]]) campMap[r["Campaign"]] = {{ sales: 0, spend: 0, orders: 0 }};
        campMap[r["Campaign"]].sales += r["Sales"];
        campMap[r["Campaign"]].spend += r["Marketing Spend"];
        campMap[r["Campaign"]].orders += 1;
      }});

      const camps = Object.keys(campMap).sort((a, b) => campMap[b].sales - campMap[a].sales);
      if (camps.length === 0) return;

      const padding = {{ top: 20, right: 20, bottom: 50, left: 65 }};
      const chartW = width - padding.left - padding.right;
      const chartH = height - padding.top - padding.bottom;

      const maxSales = Math.max(...camps.map(c => campMap[c].sales), 1000);

      // Y Grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';

      for (let i = 0; i <= 4; i++) {{
        const yPos = padding.top + chartH - (i / 4) * chartH;
        ctx.beginPath();
        ctx.moveTo(padding.left, yPos);
        ctx.lineTo(width - padding.right, yPos);
        ctx.stroke();
        ctx.fillText(formatCompactINR((i / 4) * maxSales), padding.left - 8, yPos + 3);
      }}

      const groupW = chartW / camps.length;
      const barW = Math.max(6, groupW * 0.35);
      const hitBoxes = [];

      camps.forEach((camp, i) => {{
        const gx = padding.left + i * groupW + groupW / 2;
        const hSales = (campMap[camp].sales / maxSales) * chartH;
        const hSpend = (campMap[camp].spend / maxSales) * chartH;

        const xSpend = gx - barW - 1;
        const xSales = gx + 1;

        // Spend bar
        ctx.fillStyle = '#a855f7';
        ctx.fillRect(xSpend, padding.top + chartH - hSpend, barW, hSpend);

        // Sales bar
        ctx.fillStyle = '#10b981';
        ctx.fillRect(xSales, padding.top + chartH - hSales, barW, hSales);

        // Label
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(camp, gx, padding.top + chartH + 18);

        hitBoxes.push({{
          gx, camp, sales: campMap[camp].sales, spend: campMap[camp].spend,
          roas: campMap[camp].spend > 0 ? (campMap[camp].sales / campMap[camp].spend).toFixed(1) : '∞'
        }});
      }});

      canvas.onmousemove = (e) => {{
        const b = canvas.getBoundingClientRect();
        const mx = e.clientX - b.left;
        const hit = hitBoxes.find(h => Math.abs(h.gx - mx) < groupW / 2);
        if (hit) {{
          showTooltip(e, `
            <div class="font-bold text-white">${{hit.camp}}</div>
            <div class="text-purple-400 font-medium mt-1">Mkt Spend: ${{formatINR(hit.spend)}}</div>
            <div class="text-emerald-400 font-semibold">Sales Revenue: ${{formatINR(hit.sales)}}</div>
            <div class="text-amber-300 font-bold mt-0.5">ROAS Multiplier: ${{hit.roas}}x</div>
          `);
        }} else {{
          hideTooltip();
        }}
      }};
      canvas.onmouseleave = hideTooltip;

      // Populate ROAS summary chips
      const roasContainer = document.getElementById('roasSummaryCards');
      roasContainer.innerHTML = '';
      camps.slice(0, 3).forEach(c => {{
        const rVal = campMap[c].spend > 0 ? (campMap[c].sales / campMap[c].spend).toFixed(1) : 'N/A';
        const card = document.createElement('div');
        card.className = 'p-2 rounded-lg bg-slate-900/60 border border-slate-800 text-center';
        card.innerHTML = `
          <div class="text-slate-400 text-[10px] truncate">${{c}}</div>
          <div class="text-xs font-bold text-amber-400 mt-0.5">${{rVal}}x ROAS</div>
        `;
        roasContainer.appendChild(card);
      }});
    }}

    // ==========================================
    // CHART 5: SALES BY MARKETING CAMPAIGN
    // ==========================================
    function renderCampaignDistribution() {{
      const container = document.getElementById('campaignDistributionContainer');
      container.innerHTML = '';

      const campMap = {{}};
      filteredData.forEach(r => {{
        if (!campMap[r["Campaign"]]) campMap[r["Campaign"]] = {{ sales: 0, orders: 0 }};
        campMap[r["Campaign"]].sales += r["Sales"];
        campMap[r["Campaign"]].orders += 1;
      }});

      const totalSales = Object.values(campMap).reduce((a, b) => a + b.sales, 0);
      const sortedCamps = Object.entries(campMap).sort((a, b) => b[1].sales - a[1].sales);

      const colorPalette = [
        'from-rose-500 to-pink-500',
        'from-blue-500 to-cyan-500',
        'from-purple-500 to-indigo-500',
        'from-amber-500 to-yellow-500',
        'from-emerald-500 to-teal-500',
        'from-slate-500 to-gray-500'
      ];

      sortedCamps.forEach(([camp, data], idx) => {{
        const share = totalSales > 0 ? (data.sales / totalSales) * 100 : 0;
        const color = colorPalette[idx % colorPalette.length];
        const row = document.createElement('div');
        row.className = 'p-2.5 rounded-xl bg-slate-900/60 border border-slate-800/80';
        row.innerHTML = `
          <div class="flex items-center justify-between text-xs mb-1">
            <div class="flex items-center gap-2">
              <span class="font-semibold text-slate-200">${{camp}}</span>
              <span class="text-[10px] text-slate-400">${{data.orders}} orders</span>
            </div>
            <div class="text-right">
              <span class="font-bold text-white">${{formatINR(data.sales)}}</span>
              <span class="text-indigo-400 text-[10px] ml-1.5 font-semibold">(${{share.toFixed(1)}}%)</span>
            </div>
          </div>
          <div class="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <div class="bg-gradient-to-r ${{color}} h-2 rounded-full" style="width: ${{share}}%"></div>
          </div>
        `;
        container.appendChild(row);
      }});
    }}

    // ==========================================
    // CHART 3: DISCOUNT ANALYSIS (Discount % vs Sales)
    // ==========================================
    function renderDiscountAnalysis() {{
      const canvas = document.getElementById('discountAnalysisCanvas');
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      const width = rect.width;
      const height = rect.height;

      ctx.clearRect(0, 0, width, height);

      const discMap = {{}};
      filteredData.forEach(r => {{
        const key = (r["Discount Rate"] * 100).toFixed(0) + '%';
        if (!discMap[key]) discMap[key] = {{ rate: r["Discount Rate"], sales: 0, count: 0, qty: 0 }};
        discMap[key].sales += r["Sales"];
        discMap[key].count += 1;
        discMap[key].qty += r["Quantity"];
      }});

      const tiers = Object.keys(discMap).sort((a, b) => discMap[a].rate - discMap[b].rate);
      if (tiers.length === 0) return;

      const padding = {{ top: 20, right: 20, bottom: 45, left: 65 }};
      const chartW = width - padding.left - padding.right;
      const chartH = height - padding.top - padding.bottom;

      const maxSales = Math.max(...tiers.map(t => discMap[t].sales), 1000);

      // Y Grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';

      for (let i = 0; i <= 4; i++) {{
        const yPos = padding.top + chartH - (i / 4) * chartH;
        ctx.beginPath();
        ctx.moveTo(padding.left, yPos);
        ctx.lineTo(width - padding.right, yPos);
        ctx.stroke();
        ctx.fillText(formatCompactINR((i / 4) * maxSales), padding.left - 8, yPos + 3);
      }}

      const slotW = chartW / tiers.length;
      const barW = Math.max(12, slotW * 0.55);
      const hitBoxes = [];

      tiers.forEach((tier, i) => {{
        const cx = padding.left + i * slotW + slotW / 2;
        const bH = (discMap[tier].sales / maxSales) * chartH;

        // Gradient bar
        const g = ctx.createLinearGradient(0, padding.top + chartH - bH, 0, padding.top + chartH);
        g.addColorStop(0, '#14b8a6');
        g.addColorStop(1, '#0f766e');

        ctx.fillStyle = g;
        ctx.fillRect(cx - barW / 2, padding.top + chartH - bH, barW, bH);

        // Label
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(tier, cx, padding.top + chartH + 16);

        hitBoxes.push({{
          cx, tier,
          sales: discMap[tier].sales,
          orders: discMap[tier].count,
          qty: discMap[tier].qty
        }});
      }});

      canvas.onmousemove = (e) => {{
        const b = canvas.getBoundingClientRect();
        const mx = e.clientX - b.left;
        const hit = hitBoxes.find(h => Math.abs(h.cx - mx) < slotW / 2);
        if (hit) {{
          showTooltip(e, `
            <div class="font-bold text-white">${{hit.tier}} Discount Bracket</div>
            <div class="text-teal-400 font-semibold mt-1">Generated Sales: ${{formatINR(hit.sales)}}</div>
            <div class="text-slate-300 text-xs">${{hit.orders}} Orders (${{hit.qty}} Units Sold)</div>
          `);
        }} else {{
          hideTooltip();
        }}
      }};
      canvas.onmouseleave = hideTooltip;
    }}

    // ==========================================
    // CHART 7: PROFIT ANALYSIS BY CATEGORY
    // ==========================================
    function renderProfitAnalysis() {{
      const canvas = document.getElementById('profitAnalysisCanvas');
      const ctx = canvas.getContext('2d');
      const dpr = window.devicePixelRatio || 1;
      const rect = canvas.getBoundingClientRect();
      canvas.width = rect.width * dpr;
      canvas.height = rect.height * dpr;
      ctx.scale(dpr, dpr);
      const width = rect.width;
      const height = rect.height;

      ctx.clearRect(0, 0, width, height);

      const catMap = {{}};
      filteredData.forEach(r => {{
        if (!catMap[r["Category"]]) catMap[r["Category"]] = {{ sales: 0, profit: 0 }};
        catMap[r["Category"]].sales += r["Sales"];
        catMap[r["Category"]].profit += r["Profit"];
      }});

      const cats = Object.keys(catMap).sort((a, b) => catMap[b].profit - catMap[a].profit);
      if (cats.length === 0) return;

      const padding = {{ top: 20, right: 20, bottom: 45, left: 65 }};
      const chartW = width - padding.left - padding.right;
      const chartH = height - padding.top - padding.bottom;

      const maxVal = Math.max(...cats.map(c => catMap[c].sales), 1000);

      // Y Grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.05)';
      ctx.fillStyle = '#94a3b8';
      ctx.font = '10px sans-serif';
      ctx.textAlign = 'right';

      for (let i = 0; i <= 4; i++) {{
        const yPos = padding.top + chartH - (i / 4) * chartH;
        ctx.beginPath();
        ctx.moveTo(padding.left, yPos);
        ctx.lineTo(width - padding.right, yPos);
        ctx.stroke();
        ctx.fillText(formatCompactINR((i / 4) * maxVal), padding.left - 8, yPos + 3);
      }}

      const slotW = chartW / cats.length;
      const barW = Math.max(8, slotW * 0.32);
      const hitBoxes = [];

      cats.forEach((cat, i) => {{
        const cx = padding.left + i * slotW + slotW / 2;
        const hSales = (catMap[cat].sales / maxVal) * chartH;
        const hProfit = (catMap[cat].profit / maxVal) * chartH;

        const xSales = cx - barW - 1.5;
        const xProfit = cx + 1.5;

        // Sales bar
        ctx.fillStyle = '#334155';
        ctx.fillRect(xSales, padding.top + chartH - hSales, barW, hSales);

        // Profit bar
        ctx.fillStyle = '#22c55e';
        ctx.fillRect(xProfit, padding.top + chartH - hProfit, barW, hProfit);

        // Label
        ctx.fillStyle = '#cbd5e1';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(cat, cx, padding.top + chartH + 16);

        const marginPct = catMap[cat].sales > 0 ? (catMap[cat].profit / catMap[cat].sales) * 100 : 0;
        hitBoxes.push({{
          cx, cat,
          sales: catMap[cat].sales,
          profit: catMap[cat].profit,
          margin: marginPct.toFixed(1)
        }});
      }});

      canvas.onmousemove = (e) => {{
        const b = canvas.getBoundingClientRect();
        const mx = e.clientX - b.left;
        const hit = hitBoxes.find(h => Math.abs(h.cx - mx) < slotW / 2);
        if (hit) {{
          showTooltip(e, `
            <div class="font-bold text-white">${{hit.cat}}</div>
            <div class="text-slate-300 text-xs mt-1">Revenue: ${{formatINR(hit.sales)}}</div>
            <div class="text-green-400 font-bold">Net Profit: ${{formatINR(hit.profit)}}</div>
            <div class="text-amber-400 font-semibold text-[10px]">Margin: ${{hit.margin}}%</div>
          `);
        }} else {{
          hideTooltip();
        }}
      }};
      canvas.onmouseleave = hideTooltip;
    }}

    // ==========================================
    // RENDER ALL 8 VISUALS
    // ==========================================
    function renderAllVisuals() {{
      renderDailySalesChart();
      renderRegionDonut();
      renderProductRankings();
      renderMainRateVsSalesChart();
      renderMarketingSpendVsSales();
      renderCampaignDistribution();
      renderDiscountAnalysis();
      renderProfitAnalysis();
    }}

    // ==========================================
    // GRANULAR DATA LEDGER (TABLE & EXPORT)
    // ==========================================
    function sortTable(col) {{
      if (sortColumn === col) {{
        sortAsc = !sortAsc;
      }} else {{
        sortColumn = col;
        sortAsc = true;
      }}
      filteredData.sort((a, b) => {{
        let vA = a[col];
        let vB = b[col];
        if (typeof vA === 'string') {{
          return sortAsc ? vA.localeCompare(vB) : vB.localeCompare(vA);
        }}
        return sortAsc ? vA - vB : vB - vA;
      }});
      renderLedgerTable();
    }}

    function changePageSize() {{
      pageSize = parseInt(document.getElementById('pageSizeSelect').value, 10);
      currentPage = 1;
      renderLedgerTable();
    }}

    function prevPage() {{
      if (currentPage > 1) {{
        currentPage--;
        renderLedgerTable();
      }}
    }}

    function nextPage() {{
      const maxPages = Math.ceil(filteredData.length / pageSize) || 1;
      if (currentPage < maxPages) {{
        currentPage++;
        renderLedgerTable();
      }}
    }}

    function renderLedgerTable() {{
      const tbody = document.getElementById('ledgerTableBody');
      tbody.innerHTML = '';

      const totalRecs = filteredData.length;
      const maxPages = Math.ceil(totalRecs / pageSize) || 1;
      if (currentPage > maxPages) currentPage = maxPages;

      const startIdx = (currentPage - 1) * pageSize;
      const endIdx = Math.min(startIdx + pageSize, totalRecs);

      document.getElementById('ledgerRecordCount').innerText = `Showing ${{totalRecs > 0 ? startIdx + 1 : 0}}-${{endIdx}} of ${{totalRecs}} records`;
      document.getElementById('pageIndicator').innerText = `Page ${{currentPage}} of ${{maxPages}}`;

      document.getElementById('btnPrevPage').disabled = currentPage <= 1;
      document.getElementById('btnNextPage').disabled = currentPage >= maxPages;

      const pageRows = filteredData.slice(startIdx, endIdx);

      pageRows.forEach(row => {{
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-slate-900/60 transition-colors';
        tr.innerHTML = `
          <td class="p-3 text-slate-300 font-mono">${{row["Date"]}}</td>
          <td class="p-3 text-indigo-400 font-mono font-medium">${{row["Order ID"]}}</td>
          <td class="p-3"><span class="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px]">${{row["Region"]}}</span></td>
          <td class="p-3 font-semibold text-white">${{row["Product"]}}</td>
          <td class="p-3 text-slate-400">${{row["Category"]}}</td>
          <td class="p-3 text-slate-300">
            <span class="inline-flex items-center gap-1 ${{row["Customer Type"] === 'New' ? 'text-cyan-400' : 'text-slate-400'}}">
              ● ${{row["Customer Type"]}}
            </span>
          </td>
          <td class="p-3 text-slate-300">${{row["Campaign"]}}</td>
          <td class="p-3 text-center text-slate-200 font-semibold">${{row["Quantity"]}}</td>
          <td class="p-3 text-right text-slate-300 font-mono">${{formatINR(row["Main Rate"])}}</td>
          <td class="p-3 text-right text-rose-400 font-mono font-semibold">${{formatPercent(row["Discount Rate"])}}</td>
          <td class="p-3 text-right text-emerald-400 font-bold font-mono">${{formatINR(row["Sales"])}}</td>
          <td class="p-3 text-right text-blue-400 font-bold font-mono">${{formatINR(row["Profit"])}}</td>
          <td class="p-3 text-right text-purple-400 font-mono">${{formatINR(row["Marketing Spend"])}}</td>
        `;
        tbody.appendChild(tr);
      }});
    }}

    // Export Filtered Dataset to CSV
    function exportToCSV() {{
      const headers = ["Date", "Region", "Product", "Category", "Order ID", "Customer Type", "Campaign", "Quantity", "Main Rate", "Discount Rate", "Sales", "Profit", "Marketing Spend"];
      const csvRows = [headers.join(",")];

      filteredData.forEach(row => {{
        const values = headers.map(header => {{
          const escaped = ('' + row[header]).replace(/"/g, '\\"');
          return `"${{escaped}}"`;
        }});
        csvRows.push(values.join(","));
      }});

      const blob = new Blob([csvRows.join("\\n")], {{ type: "text/csv;charset=utf-8;" }});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.setAttribute("href", url);
      link.setAttribute("download", `sales_marketing_filtered_${{new Date().toISOString().slice(0, 10)}}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }}

    // Initialize on window load and handle resize
    window.addEventListener('load', () => {{
      updateKPICards();
      renderAllVisuals();
      renderLedgerTable();
    }});

    window.addEventListener('resize', () => {{
      renderAllVisuals();
    }});
  </script>
</body>
</html>
"""

# Save to workspace root
with open("sales_marketing_dashboard.html", "w", encoding="utf-8") as f:
    f.write(html_content)

# Save to artifact directory
artifact_path = r"C:\Users\soura\.gemini\antigravity\brain\2e1bb029-3ae3-457f-9b7e-73a95b811321\sales_marketing_dashboard.html"
with open(artifact_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print("Generated sales_marketing_dashboard.html in workspace and artifact directory successfully.")
