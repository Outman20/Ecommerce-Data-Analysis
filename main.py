"""
E-Commerce Data Analysis
========================
Analyzes sales data to extract business insights:
- Revenue trends over time
- Top-performing products
- Sales by country
- Conversion rate & KPIs
- Customer purchase behavior

Dataset: Online Retail (UCI Machine Learning Repository)
        https://archive.ics.uci.edu/dataset/352/online+retail
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path

# ── Configuration ────────────────────────────────────────────────────────────
PLOTS_DIR = Path("plots")
PLOTS_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    "figure.dpi": 150,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "font.family": "DejaVu Sans",
})

COLORS = ["#2563EB", "#16A34A", "#DC2626", "#D97706", "#7C3AED", "#0891B2"]


# ── Data Loading ─────────────────────────────────────────────────────────────
def load_data(filepath: str = "online_retail.csv") -> pd.DataFrame:
    """Load and validate the dataset."""
    path = Path(filepath)

    if not path.exists():
        print(f"⚠️  '{filepath}' not found. Generating sample dataset...")
        df = _generate_sample_data()
        df.to_csv(filepath, index=False)
        print(f"✅  Sample dataset saved as '{filepath}'\n")
    else:
        df = pd.read_csv(filepath, encoding="ISO-8859-1")

    return df


def _generate_sample_data(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """Generate a realistic sample dataset mirroring the Online Retail schema."""
    rng = np.random.default_rng(seed)

    products = {
        "WHITE HANGING HEART T-LIGHT HOLDER": 2.95,
        "REGENCY CAKESTAND 3 TIER": 12.75,
        "JUMBO BAG RED RETROSPOT": 1.65,
        "ASSORTED COLOUR BIRD ORNAMENT": 1.69,
        "PACK OF 72 RETROSPOT CAKE CASES": 0.55,
        "LUNCH BAG RED RETROSPOT": 1.65,
        "SET OF 3 CAKE TINS PANTRY DESIGN": 4.95,
        "ALARM CLOCK BAKELIKE GREEN": 3.75,
        "VINTAGE UNION JACK MEMOBOARD": 5.06,
        "NATURAL SLATE HEART CHALKBOARD": 2.10,
        "HAND WARMER UNION JACK": 1.85,
        "MINI PAINT SET VINTAGE": 0.65,
        "STRAWBERRY CERAMIC TRINKET BOX": 3.75,
        "PAPER CHAIN KIT VINTAGE CHRISTMAS": 2.95,
        "GLASS STAR FROSTED T-LIGHT HOLDER": 1.25,
    }
    countries = {
        "United Kingdom": 0.82, "Germany": 0.04, "France": 0.04,
        "Netherlands": 0.02, "Australia": 0.02, "Spain": 0.01,
        "Belgium": 0.01, "Switzerland": 0.01, "Sweden": 0.01, "Other": 0.02,
    }

    product_names = list(products.keys())
    product_prices = list(products.values())
    country_names = list(countries.keys())
    country_weights = list(countries.values())

    n_invoices = n // 4
    invoice_nos = [f"{500000 + i}" for i in range(n_invoices)]
    invoice_dates = pd.date_range("2023-01-01", "2023-12-31", periods=n_invoices)
    invoice_countries = rng.choice(country_names, size=n_invoices, p=country_weights)
    customer_ids = rng.integers(12000, 18000, size=n_invoices)

    rows = []
    for idx in range(n_invoices):
        n_items = rng.integers(1, 8)
        chosen = rng.choice(len(product_names), size=n_items, replace=False)
        for c in chosen:
            qty = rng.integers(1, 20)
            # occasional cancellations
            if rng.random() < 0.02:
                invoice_no = "C" + invoice_nos[idx]
                qty = -qty
            else:
                invoice_no = invoice_nos[idx]
            rows.append({
                "InvoiceNo": invoice_no,
                "StockCode": f"8{c:04d}",
                "Description": product_names[c],
                "Quantity": qty,
                "InvoiceDate": invoice_dates[idx],
                "UnitPrice": product_prices[c],
                "CustomerID": customer_ids[idx],
                "Country": invoice_countries[idx],
            })

    return pd.DataFrame(rows)


# ── Data Cleaning ─────────────────────────────────────────────────────────────
def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Remove cancellations, nulls, and invalid prices/quantities."""
    initial = len(df)

    df = df.dropna(subset=["CustomerID"])
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C")]   # cancellations
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]
    df["Month"] = df["InvoiceDate"].dt.to_period("M")
    df["YearMonth"] = df["InvoiceDate"].dt.strftime("%b %Y")

    removed = initial - len(df)
    print(f"🧹  Removed {removed:,} invalid rows ({removed/initial:.1%} of data)")
    return df


# ── KPI Summary ───────────────────────────────────────────────────────────────
def print_kpis(df: pd.DataFrame) -> None:
    total_revenue   = df["Revenue"].sum()
    total_orders    = df["InvoiceNo"].nunique()
    total_customers = df["CustomerID"].nunique()
    aov             = total_revenue / total_orders           # Average Order Value
    arpc            = total_revenue / total_customers        # Avg Revenue per Customer
    top_country     = df.groupby("Country")["Revenue"].sum().idxmax()

    print("\n" + "=" * 45)
    print("  📊  KEY PERFORMANCE INDICATORS")
    print("=" * 45)
    print(f"  Total Revenue      : £{total_revenue:>12,.2f}")
    print(f"  Total Orders       : {total_orders:>12,}")
    print(f"  Unique Customers   : {total_customers:>12,}")
    print(f"  Avg. Order Value   : £{aov:>12,.2f}")
    print(f"  Avg. Rev/Customer  : £{arpc:>12,.2f}")
    print(f"  Top Country        : {top_country:>12}")
    print("=" * 45 + "\n")


# ── Plots ─────────────────────────────────────────────────────────────────────
def plot_monthly_revenue(df: pd.DataFrame) -> None:
    monthly = (
        df.groupby("Month")["Revenue"]
        .sum()
        .reset_index()
        .sort_values("Month")
    )
    monthly["Label"] = monthly["Month"].dt.strftime("%b")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(monthly["Label"], monthly["Revenue"], marker="o",
            color=COLORS[0], linewidth=2.5, markersize=6)
    ax.fill_between(monthly["Label"], monthly["Revenue"],
                    alpha=0.12, color=COLORS[0])
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    ax.set_title("Monthly Revenue")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (£)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "01_monthly_revenue.png")
    plt.close()
    print("  ✅  01_monthly_revenue.png")


def plot_top_products(df: pd.DataFrame, n: int = 10) -> None:
    top = (
        df.groupby("Description")["Revenue"]
        .sum()
        .nlargest(n)
        .sort_values()
    )

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.barh(top.index, top.values, color=COLORS[0])
    ax.bar_label(bars, fmt="£%.0f", padding=4, fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    ax.set_title(f"Top {n} Products by Revenue")
    ax.set_xlabel("Revenue (£)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "02_top_products.png")
    plt.close()
    print("  ✅  02_top_products.png")


def plot_sales_by_country(df: pd.DataFrame) -> None:
    by_country = df.groupby("Country")["Revenue"].sum().nlargest(8)

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(by_country.index, by_country.values,
                  color=COLORS[:len(by_country)])
    ax.bar_label(bars, fmt="£%.0f", padding=3, fontsize=9)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.0f}"))
    ax.set_title("Revenue by Country (Top 8)")
    ax.set_xlabel("Country")
    ax.set_ylabel("Revenue (£)")
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "03_revenue_by_country.png")
    plt.close()
    print("  ✅  03_revenue_by_country.png")


def plot_orders_per_month(df: pd.DataFrame) -> None:
    orders = (
        df.groupby("Month")["InvoiceNo"]
        .nunique()
        .reset_index()
        .sort_values("Month")
    )
    orders["Label"] = orders["Month"].dt.strftime("%b")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.bar(orders["Label"], orders["InvoiceNo"], color=COLORS[1])
    ax.set_title("Number of Orders per Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("Orders")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "04_orders_per_month.png")
    plt.close()
    print("  ✅  04_orders_per_month.png")


def plot_aov_trend(df: pd.DataFrame) -> None:
    aov = (
        df.groupby("Month")
        .apply(lambda g: g["Revenue"].sum() / g["InvoiceNo"].nunique())
        .reset_index(name="AOV")
        .sort_values("Month")
    )
    aov["Label"] = aov["Month"].dt.strftime("%b")

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(aov["Label"], aov["AOV"], marker="s",
            color=COLORS[3], linewidth=2.5, markersize=6)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"£{x:,.2f}"))
    ax.set_title("Average Order Value (AOV) per Month")
    ax.set_xlabel("Month")
    ax.set_ylabel("AOV (£)")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "05_aov_trend.png")
    plt.close()
    print("  ✅  05_aov_trend.png")


def plot_quantity_distribution(df: pd.DataFrame) -> None:
    clipped = df["Quantity"].clip(upper=50)

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.hist(clipped, bins=30, color=COLORS[4], edgecolor="white", linewidth=0.5)
    ax.set_title("Distribution of Quantity per Line Item (capped at 50)")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(PLOTS_DIR / "06_quantity_distribution.png")
    plt.close()
    print("  ✅  06_quantity_distribution.png")


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("\n🚀  E-Commerce Data Analysis — starting...\n")

    df_raw = load_data("online_retail.csv")
    df     = clean_data(df_raw)
    print_kpis(df)

    print("📈  Generating plots...")
    plot_monthly_revenue(df)
    plot_top_products(df)
    plot_sales_by_country(df)
    plot_orders_per_month(df)
    plot_aov_trend(df)
    plot_quantity_distribution(df)

    print(f"\n✅  All plots saved in '{PLOTS_DIR}/' folder.")
    print("    Open them to preview the results.\n")


if __name__ == "__main__":
    main()
