# KPI Dashboard – Write-up

Data Source:- Kaggle
Link:- https://mavenanalytics.io/data-playground/crm-sales-opportunities

## Why these metrics?

The CRM Sales Opportunities dataset captures the full deal lifecycle — from first contact through to a closed outcome — so the natural story is about pipeline health and revenue.

**Deal Volume by Stage** is the most immediate sanity check: if deals are piling up in Engaging without converting, something is wrong upstream. The four stages (Prospecting → Engaging → Won → Lost) map directly to the funnel steps the business controls.

**Monthly Win Rate** turns the volume picture into a quality picture. A high volume of closed deals means nothing if most are losses. Tracking win rate month-over-month also surfaces seasonality or process changes faster than any other single number.

**Average Days to Close** reveals operational efficiency. Won deals averaging ~130 days versus Lost deals ~120 days (from the data) is a small but telling gap — lost deals close slightly faster, suggesting sales teams may cut their losses earlier rather than prolonging bad-fit deals.

**Monthly Revenue Trend** and **Revenue by Product** answer the "so what" for leadership — which months peaked, and which products drive the most value.

## Data story

Win rate held fairly stable between 55–65% across the tracked period. Revenue spiked in mid-2017 and tapered toward year-end. GTX Basic and MG Special are the volume leaders, while GTX Plus Pro punches above its deal count on revenue per deal.

## Dataset limitation

The dataset has ~1,400 rows with a null account field and ~2,000 rows with no close date (all Prospecting-stage deals). Time-to-close analysis is therefore limited to already-closed deals and cannot estimate how long active deals have been sitting in the pipeline.
