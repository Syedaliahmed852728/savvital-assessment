import os
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from config import DATASET_DIR, SCREENSHOTS_DIR, OUTPUT_FILE

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

# loading the dataset
pipeline = pd.read_csv(os.path.join(DATASET_DIR, "sales_pipeline.csv"))
teams = pd.read_csv(os.path.join(DATASET_DIR, "sales_teams.csv"))

pipeline["engage_date"] = pd.to_datetime(pipeline["engage_date"])
pipeline["close_date"] = pd.to_datetime(pipeline["close_date"])

# merge in regional office
pipeline = pipeline.merge(
    teams[["sales_agent", "regional_office"]], on="sales_agent", how="left"
)

# days to close (only for closed deals)
closed = pipeline[pipeline["close_date"].notna()].copy()
closed["days_to_close"] = (closed["close_date"] - closed["engage_date"]).dt.days.abs()

won = pipeline[pipeline["deal_stage"] == "Won"].copy()

# ── colour palette – simple, professional ─────────────────────────────────
BLUE = "#2563EB"
GREEN = "#16A34A"
ORANGE = "#EA580C"
RED = "#DC2626"
GRAY = "#6B7280"
LIGHT = "#F1F5F9"
BG = "#FFFFFF"
TEXT = "#1E293B"

STAGE_COLORS = {
    "Prospecting": GRAY,
    "Engaging": ORANGE,
    "Won": GREEN,
    "Lost": RED,
}

# first metric -> Volume by pipeline stage
stage_order = ["Prospecting", "Engaging", "Won", "Lost"]
stage_counts = pipeline["deal_stage"].value_counts().reindex(stage_order).reset_index()
stage_counts.columns = ["Stage", "Count"]

fig_pipeline = go.Figure(
    go.Bar(
        x=stage_counts["Stage"],
        y=stage_counts["Count"],
        marker_color=[STAGE_COLORS[s] for s in stage_counts["Stage"]],
        text=stage_counts["Count"],
        textposition="outside",
        width=0.5,
    )
)
fig_pipeline.update_layout(
    title=dict(text="Deal Volume by Pipeline Stage", font=dict(size=16, color=TEXT)),
    xaxis_title="Stage",
    yaxis_title="Number of Deals",
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(color=TEXT, size=12),
    yaxis=dict(gridcolor="#E2E8F0"),
    showlegend=False,
    height=380,
    margin=dict(t=50, b=40, l=50, r=20),
)
fig_pipeline.write_image(
    os.path.join(SCREENSHOTS_DIR, "screenshot_1_pipeline_volume.png"), scale=2
)
print("pipeline volume chart saved.")


# our second metrics – Monthly Win Rate (conversion rate)
closed_decisions = pipeline[
    pipeline["deal_stage"].isin(["Won", "Lost"]) & pipeline["close_date"].notna()
].copy()
closed_decisions["month"] = closed_decisions["close_date"].dt.to_period("M")

monthly = closed_decisions.groupby(["month", "deal_stage"]).size().unstack(fill_value=0)
monthly["total"] = monthly.sum(axis=1)
monthly["win_rate"] = (monthly.get("Won", 0) / monthly["total"] * 100).round(1)
monthly = monthly.reset_index()
monthly["month_str"] = monthly["month"].astype(str)

fig_winrate = go.Figure(
    go.Scatter(
        x=monthly["month_str"],
        y=monthly["win_rate"],
        mode="lines+markers",
        line=dict(color=BLUE, width=2.5),
        marker=dict(size=7, color=BLUE),
        fill="tozeroy",
        fillcolor="rgba(37,99,235,0.08)",
        hovertemplate="%{x}<br>Win Rate: %{y:.1f}%<extra></extra>",
    )
)
fig_winrate.update_layout(
    title=dict(
        text="Monthly Win Rate  (Won / Won+Lost)", font=dict(size=16, color=TEXT)
    ),
    xaxis_title="Month",
    yaxis_title="Win Rate (%)",
    yaxis=dict(range=[0, 100], gridcolor="#E2E8F0", ticksuffix="%"),
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(color=TEXT, size=12),
    height=380,
    margin=dict(t=50, b=40, l=60, r=20),
)
fig_winrate.write_image(
    os.path.join(SCREENSHOTS_DIR, "screenshot_2_win_rate.png"), scale=2
)
print("win rate chart saved.")

# the third matric -> Average days to close by stage
avg_days = (
    closed[closed["deal_stage"].isin(["Won", "Lost"])]
    .groupby("deal_stage")["days_to_close"]
    .mean()
    .round(1)
    .reset_index()
)
avg_days.columns = ["Stage", "Avg Days"]

fig_avgdays = go.Figure(
    go.Bar(
        x=avg_days["Stage"],
        y=avg_days["Avg Days"],
        marker_color=[GREEN if s == "Won" else RED for s in avg_days["Stage"]],
        text=avg_days["Avg Days"].astype(str) + " d",
        textposition="outside",
        width=0.35,
    )
)
fig_avgdays.update_layout(
    title=dict(
        text="Average Days to Close  (Won vs Lost)", font=dict(size=16, color=TEXT)
    ),
    xaxis_title="Outcome",
    yaxis_title="Avg Days",
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(color=TEXT, size=12),
    yaxis=dict(gridcolor="#E2E8F0"),
    showlegend=False,
    height=380,
    margin=dict(t=50, b=40, l=60, r=20),
)
fig_avgdays.write_image(
    os.path.join(SCREENSHOTS_DIR, "screenshot_3_avg_days.png"), scale=2
)
print("avg days chart saved.")

# Metric 4 -> Monthly Revenue Trend (Won deals)
won_monthly = (
    won.dropna(subset=["close_date", "close_value"])
    .assign(month=lambda d: d["close_date"].dt.to_period("M"))
    .groupby("month")["close_value"]
    .sum()
    .reset_index()
)
won_monthly["month_str"] = won_monthly["month"].astype(str)
won_monthly["close_value_k"] = (won_monthly["close_value"] / 1000).round(1)

fig_revenue = go.Figure(
    go.Scatter(
        x=won_monthly["month_str"],
        y=won_monthly["close_value_k"],
        mode="lines+markers",
        line=dict(color=GREEN, width=2.5),
        marker=dict(size=7, color=GREEN),
        fill="tozeroy",
        fillcolor="rgba(22,163,74,0.08)",
        hovertemplate="%{x}<br>Revenue: $%{y:.1f}K<extra></extra>",
    )
)
fig_revenue.update_layout(
    title=dict(
        text="Monthly Closed Revenue  (Won Deals)", font=dict(size=16, color=TEXT)
    ),
    xaxis_title="Month",
    yaxis_title="Revenue ($K)",
    yaxis=dict(gridcolor="#E2E8F0", tickprefix="$", ticksuffix="K"),
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(color=TEXT, size=12),
    height=380,
    margin=dict(t=50, b=40, l=70, r=20),
)
fig_revenue.write_image(
    os.path.join(SCREENSHOTS_DIR, "screenshot_4_revenue_trend.png"), scale=2
)
print("  [4/5] Revenue trend chart saved.")

# the last matric() Top product by won revenue
product_rev = (
    won.dropna(subset=["close_value"])
    .groupby("product")["close_value"]
    .sum()
    .sort_values(ascending=True)
    .reset_index()
)
product_rev["close_value_k"] = (product_rev["close_value"] / 1000).round(1)

fig_product = go.Figure(
    go.Bar(
        y=product_rev["product"],
        x=product_rev["close_value_k"],
        orientation="h",
        marker_color=BLUE,
        text=["$" + str(v) + "K" for v in product_rev["close_value_k"]],
        textposition="outside",
    )
)
fig_product.update_layout(
    title=dict(text="Revenue by Product  (Won Deals)", font=dict(size=16, color=TEXT)),
    xaxis_title="Total Revenue ($K)",
    xaxis=dict(gridcolor="#E2E8F0", tickprefix="$", ticksuffix="K"),
    plot_bgcolor=BG,
    paper_bgcolor=BG,
    font=dict(color=TEXT, size=12),
    showlegend=False,
    height=380,
    margin=dict(t=50, b=40, l=120, r=80),
)
fig_product.write_image(
    os.path.join(SCREENSHOTS_DIR, "screenshot_5_product_revenue.png"), scale=2
)
print("  [5/5] Product revenue chart saved.")

# kpi sumary at the top
total_deals = len(pipeline)
total_won = int((pipeline["deal_stage"] == "Won").sum())
total_revenue = won["close_value"].sum()
overall_win_rate = round(
    total_won / len(pipeline[pipeline["deal_stage"].isin(["Won", "Lost"])]) * 100, 1
)
avg_deal_value = round(won["close_value"].mean(), 0)

kpi_labels = ["Total Deals", "Deals Won", "Total Revenue", "Win Rate", "Avg Deal Value"]
kpi_values = [
    f"{total_deals:,}",
    f"{total_won:,}",
    f"${total_revenue / 1e6:.2f}M",
    f"{overall_win_rate}%",
    f"${avg_deal_value:,.0f}",
]
kpi_colors = [BLUE, GREEN, GREEN, ORANGE, BLUE]

fig_kpis = go.Figure()
for i, (label, value, color) in enumerate(zip(kpi_labels, kpi_values, kpi_colors)):
    fig_kpis.add_trace(
        go.Indicator(
            mode="number",
            value=None,
            number=dict(font=dict(size=28, color=color)),
            title=dict(
                text=f"<b>{value}</b><br><span style='font-size:13px;color:{GRAY}'>{label}</span>"
            ),
            domain=dict(x=[i / 5, (i + 1) / 5], y=[0, 1]),
        )
    )
fig_kpis.update_layout(
    height=120,
    paper_bgcolor=LIGHT,
    margin=dict(t=10, b=10, l=10, r=10),
    font=dict(color=TEXT),
)

# Assemble full HTML dashboard
kpi_html = pio.to_html(
    fig_kpis, full_html=False, include_plotlyjs=False, config={"displayModeBar": False}
)

charts_html = ""
chart_pairs = [
    (fig_pipeline, "Deal Volume by Stage"),
    (fig_winrate, "Monthly Win Rate"),
    (fig_avgdays, "Avg Days to Close"),
    (fig_revenue, "Monthly Revenue Trend"),
    (fig_product, "Revenue by Product"),
]
for fig, _ in chart_pairs:
    charts_html += f"""
    <div class="chart-card">
        {pio.to_html(fig, full_html=False, include_plotlyjs=False, config={"displayModeBar": False})}
    </div>
    """

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>CRM Sales Operations KPI Dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.35.0.min.js"></script>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #F8FAFC;
      color: {TEXT};
    }}
    header {{
      background: {BLUE};
      color: white;
      padding: 18px 32px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    header h1 {{ font-size: 20px; font-weight: 600; }}
    header span {{ font-size: 13px; opacity: 0.85; }}
    .kpi-row {{
      background: {LIGHT};
      padding: 12px 24px;
      border-bottom: 1px solid #E2E8F0;
    }}
    .charts-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      padding: 24px;
    }}
    .chart-card {{
      background: white;
      border-radius: 8px;
      border: 1px solid #E2E8F0;
      padding: 8px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }}
    .chart-card:last-child:nth-child(odd) {{
      grid-column: 1 / -1;
    }}
    footer {{
      text-align: center;
      padding: 16px;
      font-size: 12px;
      color: {GRAY};
      border-top: 1px solid #E2E8F0;
    }}
  </style>
</head>
<body>
  <header>
    <h1>CRM Sales Operations KPI Dashboard</h1>
    <span>Dataset: CRM Sales Opportunities &nbsp;|&nbsp; Period: Oct 2016 – Dec 2017</span>
  </header>
  <div class="kpi-row">{kpi_html}</div>
  <div class="charts-grid">{charts_html}</div>
  <footer>Data source: CRM Sales Opportunities dataset &nbsp;|&nbsp; Built with Python + Plotly</footer>
</body>
</html>
"""

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html)

print("\nDone.")
print(f"  Dashboard : {OUTPUT_FILE}")
print(f"  Screenshots: {SCREENSHOTS_DIR}/")
