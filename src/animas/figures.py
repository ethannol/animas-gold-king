"""Matplotlib figures in one visual system: thin marks, hairline grid, fixed palette."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SEQ = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
DIVERGING = LinearSegmentedColormap.from_list("bluered", ["#104281", "#2a78d6", "#f0efec", "#e34948", "#7a1a1a"])
SEQ_CMAP = LinearSegmentedColormap.from_list("blues", [SURFACE, *SEQ])
RELEASE = pd.Timestamp("2015-08-05")
PLANT = pd.Timestamp("2015-10-01")
ORG_ORDER = ["CORIVWCH_WQX", "USGS-CO", "USGS-NM", "ARSG", "USEPA_REGION8", "BPMWQX", "21COL001_WQX", "21COL001",
             "SOUTHUTE"]
ORG_LABEL = {"CORIVWCH_WQX": "Colorado River Watch", "USGS-CO": "USGS Colorado", "USGS-NM": "USGS New Mexico",
             "ARSG": "Animas River Stakeholders", "USEPA_REGION8": "EPA Region 8", "BPMWQX": "EPA Bonita Peak",
             "21COL001_WQX": "CDPHE (WQX)", "21COL001": "CDPHE (legacy)", "SOUTHUTE": "Southern Ute Tribe"}
REACH_LABEL = {"cement_creek": "Cement Creek at Silverton (impacted)",
               "animas_above_cement": "Animas above Cement Creek (control)",
               "animas_below_silverton": "Animas below Silverton (impacted)",
               "animas_durango": "Animas at Durango (downstream)",
               "animas_cedar_hill": "Animas near Cedar Hill, NM (downstream)"}


def style() -> None:
    plt.rcParams.update({
        "font.family": ["Helvetica Neue", "Arial", "DejaVu Sans"], "font.size": 9,
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": AXIS, "axes.linewidth": 0.8, "axes.spines.top": False, "axes.spines.right": False,
        "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-",
        "axes.titlecolor": INK, "axes.titlesize": 10, "axes.titleweight": "medium", "axes.titlelocation": "left",
        "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2,
        "ytick.labelcolor": INK2, "text.color": INK, "legend.frameon": False, "legend.fontsize": 8,
        "lines.linewidth": 1.5, "savefig.dpi": 160, "savefig.bbox": "tight",
    })


def _clip_y(ax, values: np.ndarray, lo: float = -2.5, hi: float = 2.0) -> None:
    """Keep the axis on the bulk of the data; say how many points fall outside."""
    n_out = int(((values < lo) | (values > hi)).sum())
    ax.set_ylim(lo, hi)
    if n_out:
        ax.text(0.99, 0.02, f"{n_out} point(s) below {lo:g} not shown", transform=ax.transAxes,
                ha="right", va="bottom", fontsize=7, color=INK2)


def event_lines(ax, labels: bool = True, y: float = 0.98) -> None:
    for x, lab in ((RELEASE, "release 2015-08-05"), (PLANT, "plant Oct 2015")):
        ax.axvline(x, color=MUTED, linewidth=0.8)
        if labels:
            ax.text(x, y, " " + lab, transform=ax.get_xaxis_transform(), color=INK2, fontsize=7,
                    va="top", ha="left" if x == PLANT else "right", rotation=90)


def coverage(samples: pd.DataFrame, path: Path, reaches: list[str]) -> pd.DataFrame:
    """Samples per year by organisation, one panel per reach (metal results only)."""
    style()
    metals = ["zinc", "copper", "lead", "cadmium", "iron", "manganese", "aluminium", "arsenic"]
    d = samples[samples["constituent"].isin(metals)]
    d = d.drop_duplicates(["org", "site_id", "date", "time"])  # sampling events, not results
    tab = d.groupby(["reach", "year", "org"]).size().rename("events").reset_index()
    orgs = [o for o in ORG_ORDER if o in tab["org"].unique()]
    fig, axes = plt.subplots(len(reaches), 1, figsize=(8.5, 1.9 * len(reaches)), sharex=True)
    years = np.arange(2005, int(d["year"].max()) + 1)
    for ax, reach in zip(axes, reaches, strict=True):
        bottom = np.zeros(len(years))
        for i, org in enumerate(orgs):
            sel = tab[(tab["reach"] == reach) & (tab["org"] == org)]
            s = sel.set_index("year")["events"].reindex(years).fillna(0.0)
            ax.bar(years, s.to_numpy(), bottom=bottom, width=0.8, color=SERIES[i % 8], label=ORG_LABEL.get(org, org),
                   edgecolor=SURFACE, linewidth=1.0)
            bottom += s.to_numpy()
        ax.set_title(REACH_LABEL.get(reach, reach))
        ax.axvline(2015.5, color=MUTED, linewidth=0.8)
        ax.set_ylabel("sampling events")
        ax.grid(axis="x", visible=False)
    axes[-1].set_xlabel("year (line: Gold King release, August 2015)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, ncol=3, loc="lower center", bbox_to_anchor=(0.5, -0.02))
    fig.subplots_adjust(hspace=0.45, bottom=0.12)
    fig.savefig(path)
    plt.close(fig)
    return tab


def detection_limits(samples: pd.DataFrame, path: Path, constituents: list[str]) -> pd.DataFrame:
    """Colorado River Watch dissolved-metal reporting limits by year: reported vs bounds."""
    style()
    rw = samples[(samples["org"] == "CORIVWCH_WQX") & (samples["fraction"] == "dissolved")]
    rows = []
    fig, axes = plt.subplots(2, 4, figsize=(10, 4.6), sharex=True)
    for ax, c in zip(axes.ravel(), constituents, strict=True):
        d = rw[rw["constituent"] == c]
        rep = d[d["rl_source"] == "reported"].groupby("year")["rl"].median()
        imp = d[d["rl_source"].isin(["min_detect_same_year", "earliest_recorded_rl"])].groupby("year")["rl"].median()
        share = d.groupby("year")["censored"].mean()
        ax.plot(rep.index, rep.to_numpy(), color=SERIES[0], marker="o", markersize=4, label="reported limit (median)")
        ax.plot(imp.index, imp.to_numpy(), color=SERIES[1], marker="o", markersize=4, markerfacecolor=SURFACE,
                linestyle="none", label="bound assigned (no limit on file)")
        ax.set_yscale("log")
        ax.set_title(c)
        ax.axvline(2015.5, color=MUTED, linewidth=0.8)
        for y, s in share.items():
            rows.append({"constituent": c, "year": int(y), "share_censored": float(s),
                         "rl_reported_median": float(rep.get(y, np.nan)), "rl_bound_median": float(imp.get(y, np.nan))})
    axes[0, 0].legend(loc="upper left", bbox_to_anchor=(0, 1.45), ncol=2)
    for ax in axes[1]:
        ax.set_xlabel("year")
    for ax in axes[:, 0]:
        ax.set_ylabel("limit, ug/L")
    fig.suptitle("Colorado River Watch dissolved-metal reporting limits by year", x=0.01, ha="left", fontsize=10)
    fig.savefig(path)
    plt.close(fig)
    return pd.DataFrame(rows)


def timeseries_with_discharge(adj: pd.DataFrame, daily: pd.DataFrame, path: Path, title: str, unit: str) -> None:
    style()
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(10, 5.2), sharex=True, gridspec_kw={"height_ratios": [3, 2]})
    det = adj[~adj["censored"]]
    cen = adj[adj["censored"]]
    a1.plot(det["date"], det["value"], color=SERIES[0], linewidth=0.8, marker="o", markersize=3, label="detected")
    if len(cen):
        a1.plot(cen["date"], cen["rl"], color=SERIES[0], marker="v", markersize=4, linestyle="none",
                markerfacecolor=SURFACE, label="non-detect (at limit)")
    a1.set_yscale("log")
    a1.set_ylabel(f"concentration, {unit}")
    a1.set_title(title)
    event_lines(a1)
    a1.legend(loc="lower left")
    a2.plot(daily["date"], daily["q_cfs"], color=SERIES[2], linewidth=0.7)
    a2.set_yscale("log")
    a2.set_ylabel("daily mean discharge, ft3/s")
    a2.set_xlabel("date")
    event_lines(a2, labels=False)
    fig.savefig(path)
    plt.close(fig)


def cq_plot(adj: pd.DataFrame, cq_fit, w, path: Path, title: str) -> None:
    style()
    fig, ax = plt.subplots(figsize=(6.5, 4.6))
    pre = adj["date"] < w.release
    post = adj["date"] > w.plume_end
    for m, col, lab in ((pre, SERIES[0], "pre-period (model fitted here)"), (post, SERIES[1], "post-period")):
        d = adj[m]
        ax.scatter(d.loc[~d["censored"], "log_q"], d.loc[~d["censored"], "log_c"], s=14, color=col, alpha=0.8,
                   edgecolor=SURFACE, linewidth=0.5, label=lab)
        ax.scatter(d.loc[d["censored"], "log_q"], d.loc[d["censored"], "log_c"], s=18, marker="v", facecolor=SURFACE,
                   edgecolor=col, linewidth=0.8)
    xs = np.linspace(adj["log_q"].min(), adj["log_q"].max(), 50)
    ax.plot(xs, cq_fit.coef("intercept") + cq_fit.coef("log_q") * xs, color=INK, linewidth=1.2,
            label="pre-period fit, seasonal terms at zero")
    ax.set_xlabel("ln discharge (ft3/s)")
    ax.set_ylabel("ln concentration (ug/L)")
    ax.set_title(title)
    ax.legend(loc="best")
    fig.savefig(path)
    plt.close(fig)


def its_plot(sub: pd.DataFrame, its_fit, w, path: Path, title: str, counterfactual: np.ndarray) -> None:
    style()
    fig, ax = plt.subplots(figsize=(10, 4.2))
    det = sub[~sub["censored"]]
    cen = sub[sub["censored"]]
    ax.scatter(det["date"], det["resid"], s=12, color=SERIES[0], alpha=0.7, edgecolor=SURFACE, linewidth=0.4,
               label="flow-adjusted residual")
    if len(cen):
        ax.scatter(cen["date"], cen["resid"], s=16, marker="v", facecolor=SURFACE, edgecolor=SERIES[0],
                   linewidth=0.8, label="non-detect (bound)")
    pre = sub["date"] < w.release
    ax.plot(sub.loc[pre, "date"], its_fit.fitted[pre.to_numpy()], color=INK, linewidth=1.6, label="fitted")
    ax.plot(sub.loc[~pre, "date"], its_fit.fitted[(~pre).to_numpy()], color=INK, linewidth=1.6)
    ax.plot(sub.loc[~pre, "date"], counterfactual[(~pre).to_numpy()], color=SERIES[1], linewidth=1.4,
            label="pre-period trend continued (counterfactual)")
    ax.axvspan(w.release, w.plume_end, color=GRID, alpha=0.6, lw=0, label="plume window (excluded)")
    ax.axhline(0, color=AXIS, linewidth=0.8)
    event_lines(ax)
    _clip_y(ax, sub["resid"].to_numpy())
    ax.set_ylabel("ln concentration minus C-Q + seasonal fit")
    ax.set_xlabel("date")
    ax.set_title(title)
    ax.legend(loc="lower left", ncol=2)
    fig.savefig(path)
    plt.close(fig)


def sensitivity_grid(grid: pd.DataFrame, path: Path, title: str) -> None:
    """3 panels (post end) x heatmap (pre start x plume end) of percent level change."""
    style()
    posts = list(dict.fromkeys(grid["post_end"]))
    pres = list(dict.fromkeys(grid["pre_start"]))
    plumes = list(dict.fromkeys(grid["plume_end"]))
    vmax = float(np.nanmax(np.abs(grid["level_change_pct"]))) or 1.0
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    fig, axes = plt.subplots(1, len(posts), figsize=(3.3 * len(posts) + 1, 3.4), sharey=True)
    for ax, pe in zip(np.atleast_1d(axes), posts, strict=True):
        g = grid[grid["post_end"] == pe]
        M = np.full((len(pres), len(plumes)), np.nan)
        for _, r in g.iterrows():
            M[pres.index(r["pre_start"]), plumes.index(r["plume_end"])] = r["level_change_pct"]
        ax.imshow(M, cmap=DIVERGING, norm=norm, aspect="auto")
        for _, r in g.iterrows():
            i, j = pres.index(r["pre_start"]), plumes.index(r["plume_end"])
            star = "*" if (r["level_change_lo"] > 0 or r["level_change_hi"] < 0) else ""
            label = (f"{r['level_change_pct']:+.0f}%{star}\n"
                     f"[{r['level_change_pct_lo']:+.0f}, {r['level_change_pct_hi']:+.0f}]")
            ax.text(j, i, label, ha="center", va="center", fontsize=7.5, color=INK)
        ax.set_xticks(range(len(plumes)), [f"to {p[5:]}" for p in plumes], fontsize=8)
        ax.set_yticks(range(len(pres)), [p[:4] for p in pres])
        ax.set_title(f"post-period to {pe[:4]}")
        ax.set_xlabel("plume window (from 2015-08-05)")
        ax.grid(False)
    np.atleast_1d(axes)[0].set_ylabel("pre-period start")
    fig.suptitle(title + "  (* = 95% interval excludes zero)", x=0.01, ha="left", fontsize=10)
    fig.savefig(path)
    plt.close(fig)


def changepoint_plot(monthly: pd.DataFrame, cps_pelt: list[int], cps_bs: list[int], path: Path, title: str) -> None:
    style()
    fig, ax = plt.subplots(figsize=(10, 3.8))
    x = monthly["month"].dt.to_timestamp()
    y = monthly["resid"].to_numpy()
    ax.plot(x, y, color=SERIES[0], linewidth=0.9, label="monthly mean residual")
    bounds = [0, *cps_pelt, len(y)]
    for a, b in zip(bounds[:-1], bounds[1:], strict=True):
        ax.hlines(y[a:b].mean(), x.iloc[a], x.iloc[b - 1], color=INK, linewidth=1.6)
    for k in cps_pelt:
        ax.axvline(x.iloc[k], color=INK, linewidth=1.2)
    for k in cps_bs:
        ax.axvline(x.iloc[k], color=SERIES[1], linewidth=1.0, ymax=0.15)
    ax.plot([], [], color=INK, linewidth=1.2, label="PELT change-point and segment means")
    ax.plot([], [], color=SERIES[1], linewidth=1.0, label="binary segmentation (tick)")
    ax.axhline(0, color=AXIS, linewidth=0.8)
    event_lines(ax)
    _clip_y(ax, y)
    ax.set_title(title)
    ax.set_ylabel("residual, ln units")
    ax.legend(loc="lower left", ncol=3)
    fig.savefig(path)
    plt.close(fig)


def multiplicity_grid(mult: pd.DataFrame, path: Path, title: str, reaches: list[str]) -> None:
    style()
    rows = [(c, f) for c in ["zinc", "copper", "lead", "cadmium", "iron", "manganese", "aluminium", "arsenic"]
            for f in ["dissolved", "total"]]
    M = np.full((len(rows), len(reaches)), np.nan)
    fig, ax = plt.subplots(figsize=(8, 7))
    vmax = float(np.nanmax(np.abs(mult["level_change_pct"]))) if mult["level_change_pct"].notna().any() else 1.0
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    for _, r in mult.iterrows():
        i = rows.index((r["constituent"], r["fraction"]))
        j = reaches.index(r["reach"])
        if r["estimable"]:
            M[i, j] = r["level_change_pct"]
    ax.imshow(M, cmap=DIVERGING, norm=norm, aspect="auto")
    for _, r in mult.iterrows():
        i = rows.index((r["constituent"], r["fraction"]))
        j = reaches.index(r["reach"])
        if not r["estimable"]:
            ax.text(j, i, "not\nestimable", ha="center", va="center", fontsize=6.5, color=MUTED)
            continue
        mark = "**" if r["bh_reject"] else ("*" if r["level_change_p"] < 0.05 else "")
        label = (f"{r['level_change_pct']:+.0f}%{mark}\n"
                 f"[{r['level_change_pct_lo']:+.0f}, {r['level_change_pct_hi']:+.0f}]")
        ax.text(j, i, label, ha="center", va="center", fontsize=7, color=INK)
    ax.set_xticks(range(len(reaches)), [REACH_LABEL[r].replace(" (", "\n(") for r in reaches], fontsize=8)
    ax.set_yticks(range(len(rows)), [f"{c} {f}" for c, f in rows], fontsize=8)
    ax.grid(False)
    ax.set_title(title + "  (* raw p<0.05, ** survives BH 5% FDR)")
    fig.savefig(path)
    plt.close(fig)
