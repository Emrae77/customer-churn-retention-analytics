"""Original static dashboard figures, rendered from computed metrics.

These are reproducible PNG report pages, not Power BI Desktop screenshots.
There are no decorative slicers or controls pretending to be interactive.
"""

from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.colors import LinearSegmentedColormap
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NAVY = "#142C46"
TEAL = "#07877E"
ORANGE = "#D87642"
MUTED = "#617284"
BG = "#F2F5F8"
LINE = "#DFE6EC"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12,
                     "text.color": NAVY, "axes.labelcolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": NAVY,
                     "savefig.facecolor": BG, "figure.facecolor": BG})


def box(fig, rect, color="white", edge=LINE):
    patch = FancyBboxPatch((rect[0], rect[1]), rect[2], rect[3],
                          boxstyle="round,pad=0.008,rounding_size=0.012",
                          transform=fig.transFigure, facecolor=color, edgecolor=edge,
                          linewidth=0.7, zorder=0)
    fig.add_artist(patch)


def page(title, subtitle, number):
    fig = plt.figure(figsize=(16, 9), dpi=160)
    fig.text(.04, .949, "TELCO / CUSTOMER ANALYTICS", fontsize=10.5, color=TEAL, weight="bold")
    fig.text(.04, .900, title, fontsize=27, weight="bold")
    fig.text(.04, .861, subtitle, fontsize=11, color=MUTED)
    fig.text(.96, .945, "{:02d} / 03".format(number), ha="right", fontsize=11, color=MUTED)
    fig.text(.04, .031, "IBM Telco sample · Static customer snapshot · Original Python-rendered dashboard preview",
             fontsize=9, color=MUTED)
    fig.text(.96, .031, "Jeffrey Okoduwa", ha="right", fontsize=9, color=MUTED)
    return fig


def card(fig, x, label, value, detail, accent=NAVY):
    box(fig, [x, .701, .213, .124])
    fig.text(x + .015, .793, label, fontsize=10.5, color=MUTED)
    fig.text(x + .015, .742, value, fontsize=26, color=accent, weight="bold")
    fig.text(x + .015, .716, detail, fontsize=9, color=MUTED)


def panel_title(fig, rect, title, subtitle):
    box(fig, rect)
    fig.text(rect[0] + .016, rect[1] + rect[3] - .040, title, fontsize=15, weight="bold")
    fig.text(rect[0] + .016, rect[1] + rect[3] - .073, subtitle, fontsize=9.4, color=MUTED)


def bars(fig, rect, rows, baseline=None, short_labels=None, color=TEAL):
    ax = fig.add_axes(rect)
    ax.set_facecolor("white")
    labels = short_labels or [r["segment"] for r in rows]
    rates = [r["churn_rate_pct"] or 0 for r in rows]
    colors = [ORANGE if value == max(rates) else color for value in rates]
    y = np.arange(len(rows))
    ax.barh(y, rates, height=.48, color=colors, zorder=2)
    ax.set_yticks(y, labels, fontsize=10.5)
    ax.invert_yaxis()
    xmax = max(max(rates) + 13, 60)
    ax.set_xlim(0, xmax)
    ax.set_xticks([0, 20, 40, 60], ["0%", "20%", "40%", "60%"], fontsize=9)
    for i, (r, rate) in enumerate(zip(rows, rates)):
        ax.text(rate + 1.1, i - .07, "{:.1f}%".format(rate), va="center", fontsize=11, weight="bold")
        ax.text(rate + 1.1, i + .19, "{:,} / {:,}".format(r["churned"], r["customers"]),
                va="center", fontsize=8.7, color=MUTED)
    if baseline is not None:
        ax.axvline(baseline, color=MUTED, linestyle=(0, (3, 4)), linewidth=1, zorder=1)
    ax.xaxis.grid(True, color=LINE, linewidth=.7)
    ax.set_axisbelow(True)
    ax.tick_params(axis="both", length=0, pad=6)
    for spine in ax.spines.values():
        spine.set_visible(False)
    return ax


def note(fig, title, text):
    box(fig, [.04, .078, .92, .089], color="#E8F2F1", edge="#D4E7E4")
    fig.text(.056, .135, title, color=TEAL, weight="bold", fontsize=11)
    fig.text(.056, .102, text, fontsize=10.8)


def health(report):
    overall = report["overall"]
    fig = page("Customer retention health", "7,043 customer records. Churn is the share labelled Yes in the supplied sample.", 1)
    card(fig, .04, "CUSTOMERS IN SAMPLE", "{:,}".format(overall["customers"]), "One record per customer")
    card(fig, .275, "CHURNED CUSTOMERS", "{:,}".format(overall["churned"]), "Source label: Churn = Yes", ORANGE)
    card(fig, .51, "OBSERVED CHURN RATE", "{:.2f}%".format(overall["churn_rate_pct"]), "1,869 ÷ 7,043 customers", ORANGE)
    card(fig, .745, "NOT LABELLED CHURNED", "{:,}".format(overall["not_churned"]), "{:.2f}% of the sample".format(overall["not_churned_share_pct"]), TEAL)
    panel_title(fig, [.04, .220, .44, .430], "Churn by contract", "Labels show churned / customers. Dashed line = overall 26.54%.")
    bars(fig, [.154, .285, .283, .245], report["segments"]["contract"], overall["churn_rate_pct"])
    panel_title(fig, [.51, .220, .45, .430], "Churn by customer tenure", "Tenure groups compare customers; they are not a calendar trend.")
    bars(fig, [.622, .278, .292, .275], report["segments"]["tenure"], overall["churn_rate_pct"])
    fig.text(.527, .239, "The 0-month group contains only 11 customers.", fontsize=9, color=MUTED)
    share = 100 * report["segments"]["contract"][0]["churned"] / overall["churned"]
    note(fig, "START WITH MONTH-TO-MONTH CUSTOMERS", "They account for {:.1f}% of recorded churn. Review tenure and customer experience before choosing an intervention.".format(share))
    return fig


def performance(report):
    fig = page("Customer group performance", "Compare rates with group sizes, then investigate overlapping customer characteristics.", 2)
    internet = report["segments"]["internet_service"]
    payment = report["segments"]["payment_method"]
    panel_title(fig, [.04, .490, .44, .325], "Internet service", "Within-group churn. Labels show churned / customers.")
    bars(fig, [.140, .539, .295, .172], internet, short_labels=["DSL", "Fiber optic", "No internet"])
    panel_title(fig, [.51, .490, .45, .325], "Payment method", "Billing association; payment failure is not measured here.")
    bars(fig, [.652, .537, .263, .191], payment,
         short_labels=["Electronic check", "Mailed check", "Bank transfer\n(automatic)", "Credit card\n(automatic)"])
    panel_title(fig, [.04, .192, .92, .260], "Contract and tenure together", "Each cell shows churn rate and group size (n). Small groups need careful interpretation.")
    ax = fig.add_axes([.180, .239, .695, .111])
    contracts = ["Month-to-month", "One year", "Two year"]
    bands = ["0 months", "1–12 months", "13–24 months", "25–48 months", "49–72 months"]
    entries = {(r["contract"], r["segment"]): r for r in report["contract_by_tenure"]}
    matrix = np.array([[entries[c, b]["churn_rate_pct"] if entries[c, b]["customers"] else np.nan
                        for b in bands] for c in contracts])
    cmap = LinearSegmentedColormap.from_list("telco", ["#E5F2F0", "#C9D7DB", "#F6CEB7", "#D87642"])
    ax.imshow(matrix, cmap=cmap, vmin=0, vmax=60, aspect="auto")
    ax.set_xticks(range(5), bands, fontsize=9)
    ax.set_yticks(range(3), contracts, fontsize=9)
    ax.tick_params(length=0, pad=7)
    for i, c in enumerate(contracts):
        for j, b in enumerate(bands):
            item = entries[c, b]
            label = "{:.1f}%   n={:,}".format(item["churn_rate_pct"], item["customers"]) if item["customers"] else "No customers"
            ax.text(j, i, label, ha="center", va="center", fontsize=9, color=NAVY)
    ax.set_xticks(np.arange(-.5, 5, 1), minor=True)
    ax.set_yticks(np.arange(-.5, 3, 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=3)
    ax.tick_params(which="minor", length=0)
    for spine in ax.spines.values():
        spine.set_visible(False)
    note(fig, "TURN THE COMPARISON INTO A QUESTION", "Review service experience and billing friction in the highlighted groups. These overlapping views do not establish a cause.")
    return fig


def quality(report):
    q = report["data_quality"]
    fig = page("Data health and definitions", "Clear denominators and documented missing values make the analysis easier to review.", 3)
    card(fig, .04, "RAW CUSTOMER RECORDS", "{:,}".format(q["raw_rows"]), "21 original columns")
    card(fig, .275, "ROWS AFTER CLEANING", "{:,}".format(q["clean_rows"]), "No customer rows removed", TEAL)
    card(fig, .51, "DUPLICATE CUSTOMER IDS", str(q["duplicate_customer_ids"]), "7,043 distinct customer IDs", TEAL)
    card(fig, .745, "MISSING TOTAL CHARGES", str(q["total_charges_missing"]), "Preserved as missing, not zero", ORANGE)
    panel_title(fig, [.04, .220, .47, .430], "Data checks", "Results from the pinned IBM source and the preparation script.")
    checks = [
        ("Customer IDs", "All present and unique"),
        ("Churn labels", "Only Yes and No"),
        ("Numeric fields", "No unexpected conversion failures"),
        ("Blank TotalCharges", "11 customers; all tenure = 0"),
        ("Service categories", "No internet / phone service preserved"),
        ("Source file", "SHA-256 checksum matched"),
    ]
    y = .526
    for label, result in checks:
        fig.text(.060, y, label, fontsize=10.5, weight="bold")
        fig.text(.230, y, result, fontsize=10, color=MUTED)
        y -= .048
    panel_title(fig, [.54, .220, .42, .430], "What the metrics mean", "Scope matters as much as the percentage.")
    entries = [
        ("Churn rate", "Churned customers ÷ all customers in the selected group."),
        ("Not-churned share", "Customers labelled No ÷ the same customer population."),
        ("Tenure groups", "Months with the company; not monthly performance history."),
        ("Charges", "Missing totals remain NULL. Charge totals do not prove lost revenue."),
    ]
    y = .530
    for label, value in entries:
        fig.text(.558, y, label, fontsize=11, weight="bold")
        fig.text(.558, y - .028, textwrap.fill(value, 62), fontsize=9.7, color=MUTED, va="top", linespacing=1.35)
        y -= .084
    note(fig, "THE REPORTING POPULATION STAYS AT 7,043", "A missing charge value does not remove an otherwise valid customer from the churn calculation.")
    return fig


def render_all(report):
    out = ROOT / "images"
    out.mkdir(exist_ok=True)
    for filename, renderer in [("customer-health.png", health), ("segment-performance.png", performance), ("data-quality.png", quality)]:
        fig = renderer(report)
        fig.savefig(out / filename, dpi=160)
        plt.close(fig)
