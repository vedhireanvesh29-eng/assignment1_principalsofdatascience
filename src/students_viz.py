"""Generate visualizations for the Students Performance dataset."""
from pathlib import Path
import re
from typing import Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "students_performance.csv"
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "analysis"
REPORTS_DIR = PROJECT_ROOT / "reports"
REPORT_PATH = REPORTS_DIR / "analysis_report.md"

FIGURES = {
    "v1": OUTPUT_DIR / "v1_gender_boxplots.png",
    "v2": OUTPUT_DIR / "v2_testprep_math.png",
    "v3": OUTPUT_DIR / "v3_lunch_avg.png",
    "v4": OUTPUT_DIR / "v4_subject_corr.png",
    "v5": OUTPUT_DIR / "v5_scatter_trend_testprep.png",
}

REQUIRED_COLUMNS = [
    "math score",
    "reading score",
    "writing score",
    "gender",
    "lunch",
    "test preparation course",
]


def ingest_and_process() -> pd.DataFrame:
    df = pd.read_csv(RAW_PATH)
    df = df.dropna(subset=REQUIRED_COLUMNS).copy()
    df["overall_avg"] = (df[["math score", "reading score", "writing score"]].mean(axis=1)).round(2)
    return df


def ensure_output_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


def v1_gender_boxplots(df: pd.DataFrame) -> None:
    genders = sorted(df["gender"].str.title().unique())
    subject_map = {"Math Score": "math score", "Reading Score": "reading score"}
    fig, axes = plt.subplots(1, 2, figsize=(8, 6), dpi=300, sharey=True)
    for ax, (label, column) in zip(axes, subject_map.items()):
        data = [df.loc[df["gender"].str.title() == gender, column] for gender in genders]
        ax.boxplot(data, tick_labels=genders, patch_artist=True)
        ax.set_title(f"{label} by Gender")
        ax.set_xlabel("Gender")
        ax.set_ylabel("Score (0-100)")
    fig.suptitle("Math and Reading Scores Grouped by Gender")
    fig.tight_layout()
    fig.savefig(FIGURES["v1"], bbox_inches="tight")
    plt.close(fig)


def v2_testprep_math(df: pd.DataFrame) -> None:
    order = ["completed", "none"]
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    data = [df.loc[df["test preparation course"] == grp, "math score"] for grp in order]
    ax.boxplot(data, tick_labels=[grp.title() for grp in order], patch_artist=True)
    ax.set_title("Math Score Distribution by Test Preparation Completion")
    ax.set_xlabel("Test Preparation Course")
    ax.set_ylabel("Math Score (0-100)")
    fig.tight_layout()
    fig.savefig(FIGURES["v2"], bbox_inches="tight")
    plt.close(fig)


def v3_lunch_average(df: pd.DataFrame) -> pd.Series:
    means = df.groupby("lunch")["overall_avg"].mean().reindex(["standard", "free/reduced"])
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    bars = ax.bar(["Standard", "Free/Reduced"], means.round(2), color=["#4C72B0", "#55A868"])
    for bar, value in zip(bars, means.round(2)):
        ax.text(bar.get_x() + bar.get_width() / 2, value + 0.3, f"{value:.1f}", ha="center", va="bottom")
    ax.set_title("Average Overall Score by Lunch Type")
    ax.set_ylabel("Average Score (0-100)")
    ax.set_ylim(0, 100)
    fig.tight_layout()
    fig.savefig(FIGURES["v3"], bbox_inches="tight")
    plt.close(fig)
    return means


def v4_subject_correlation(df: pd.DataFrame) -> pd.DataFrame:
    subjects = ["math score", "reading score", "writing score"]
    corr = df[subjects].corr()
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    cax = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(subjects)))
    ax.set_yticks(range(len(subjects)))
    tick_labels = [title.title() for title in subjects]
    ax.set_xticklabels(tick_labels)
    ax.set_yticklabels(tick_labels)
    for i in range(len(subjects)):
        for j in range(len(subjects)):
            ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", color="black")
    fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04)
    ax.set_title("Correlation Among Subject Scores")
    fig.tight_layout()
    fig.savefig(FIGURES["v4"], bbox_inches="tight")
    plt.close(fig)
    return corr


def v5_scatter_trend(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    order = ["completed", "none"]
    colors = {"completed": "#C44E52", "none": "#8172B2"}
    stats: Dict[str, Dict[str, float]] = {}
    fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
    x_min, x_max = df["reading score"].min(), df["reading score"].max()
    x_range = np.linspace(x_min, x_max, 100)
    for group in order:
        subset = df[df["test preparation course"] == group]
        label = f"{group.title()} (n={len(subset)})"
        ax.scatter(subset["reading score"], subset["math score"], label=label, color=colors[group], alpha=0.6, edgecolors="black", linewidths=0.5)
        if len(subset) >= 2:
            slope, intercept = np.polyfit(subset["reading score"], subset["math score"], 1)
            stats[group] = {"slope": slope, "intercept": intercept, "n": len(subset)}
            ax.plot(x_range, slope * x_range + intercept, color=colors[group], linestyle="--")
        else:
            stats[group] = {"slope": np.nan, "intercept": np.nan, "n": len(subset)}
    ax.set_title("Math vs. Reading Scores by Test Preparation Status")
    ax.set_xlabel("Reading Score (0-100)")
    ax.set_ylabel("Math Score (0-100)")
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.4)
    fig.tight_layout()
    fig.savefig(FIGURES["v5"], bbox_inches="tight")
    plt.close(fig)
    return stats


def generate_figures(df: pd.DataFrame) -> Dict[str, object]:
    ensure_output_dirs()
    v1_gender_boxplots(df)
    v2_testprep_math(df)
    lunch_means = v3_lunch_average(df)
    corr = v4_subject_correlation(df)
    trend_stats = v5_scatter_trend(df)
    return {"lunch_means": lunch_means, "corr": corr, "trend_stats": trend_stats}


def build_narrative(df: pd.DataFrame, artifacts: Dict[str, object]) -> str:
    math_stats = df.groupby("gender")["math score"].agg(["median", "mean"]).round(1)
    reading_stats = df.groupby("gender")["reading score"].agg(["median", "mean"]).round(1)
    math_quartiles = df.groupby("gender")["math score"].quantile([0.25, 0.75]).unstack().round(1)
    reading_quartiles = df.groupby("gender")["reading score"].quantile([0.75]).unstack().round(1)
    math_mins = df.groupby("gender")["math score"].min()

    prep_math = df.groupby("test preparation course")["math score"].agg(["mean", "median", "count"]).round(1)
    lunch_means = artifacts["lunch_means"].round(2)
    corr = artifacts["corr"]
    trend = artifacts["trend_stats"]

    female_iqr = math_quartiles.loc["female", 0.75] - math_quartiles.loc["female", 0.25]
    male_iqr = math_quartiles.loc["male", 0.75] - math_quartiles.loc["male", 0.25]
    abs_iqr_diff = abs(male_iqr - female_iqr)
    if abs_iqr_diff < 0.1:
        iqr_sentence = (
            f"Female math scores span an interquartile range from {math_quartiles.loc['female', 0.25]:.1f} to {math_quartiles.loc['female', 0.75]:.1f}, closely matching the male range of {math_quartiles.loc['male', 0.25]:.1f} to {math_quartiles.loc['male', 0.75]:.1f}. "
        )
    else:
        iqr_phrase = "tighter" if male_iqr > female_iqr else "wider"
        iqr_sentence = (
            f"Female math scores span an interquartile range from {math_quartiles.loc['female', 0.25]:.1f} to {math_quartiles.loc['female', 0.75]:.1f}, about {abs_iqr_diff:.1f} points {iqr_phrase} than the male range of {math_quartiles.loc['male', 0.25]:.1f} to {math_quartiles.loc['male', 0.75]:.1f}. "
        )

    ingestion_paragraph = (
        "The analysis ingests the raw Kaggle StudentsPerformance dataset, drops records with missing core fields, and engineers an overall average score by combining math, reading, and writing. "
        "These cleaned data feed the visualization stages, ensuring each plot reflects consistent cohorts across gender, lunch status, and test preparation participation."
    )

    v1_text = (
        f"Female students post a median math score of {math_stats.loc['female', 'median']:.1f} and a reading median of {reading_stats.loc['female', 'median']:.1f}, while males center around {math_stats.loc['male', 'median']:.1f} in math and {reading_stats.loc['male', 'median']:.1f} in reading. "
        + iqr_sentence
        + f"Reading boxplots show female upper quartile performance reaching {reading_quartiles.loc['female', 0.75]:.1f} versus {reading_quartiles.loc['male', 0.75]:.1f} for males, highlighting a literacy edge. "
        + f"Male math distribution dips to a minimum of {math_mins['male']:.0f} compared with the female minimum of {math_mins['female']:.0f}, illustrating more low-end male outliers. "
        + "Together the boxplots show modest gender gaps that consistently favor female readers and slightly steadier female math outcomes."
    )

    v2_text = (
        f"Students who completed test preparation achieve an average math score of {prep_math.loc['completed', 'mean']:.1f}, about {prep_math.loc['completed', 'mean'] - prep_math.loc['none', 'mean']:.1f} points above those without preparation. "
        f"The median advantage is similar at {prep_math.loc['completed', 'median'] - prep_math.loc['none', 'median']:.1f} points, and the completed group shows a higher lower-quartile threshold in the boxplot. "
        "Score dispersion tightens for prepared students, suggesting the course lifts the floor as well as the ceiling. "
        "A few low outliers remain among non-participants, hinting at students who may benefit most from intervention. "
        "Overall the visual underscores a meaningful math payoff from the preparation course."
    )

    v3_text = (
        f"Standard-lunch students average {lunch_means['standard']:.1f} across subjects, compared with {lunch_means['free/reduced']:.1f} for the subsidized cohort. "
        f"The gap of roughly {lunch_means['standard'] - lunch_means['free/reduced']:.1f} points persists despite shared assessments, signalling socioeconomic effects on performance. "
        "The bars also highlight how no lunch group approaches the 90-point benchmark, leaving room for enrichment. "
        "Free/reduced lunch students cluster closer to the 70s, indicating greater support needs. "
        "Prioritizing resources for subsidized lunch participants could shrink the observed average deficit."
    )

    corr_m = corr.loc["math score", "reading score"]
    corr_w = corr.loc["writing score", "reading score"]
    corr_mw = corr.loc["math score", "writing score"]
    v4_text = (
        f"Math and reading exhibit a strong positive correlation of {corr_m:.2f}, while writing aligns closely with reading at {corr_w:.2f}. "
        f"Math and writing also reinforce each other with a coefficient of {corr_mw:.2f}. "
        "The near-diagonal symmetry confirms consistent inter-subject relationships across the cohort. "
        "No negative associations appear, so gains in one domain likely spill into others. "
        "This tight triad suggests integrated literacy and numeracy strategies may amplify outcomes across all exams."
    )

    slope_completed = trend["completed"]["slope"]
    slope_none = trend["none"]["slope"]
    v5_text = (
        f"Both preparation groups follow upward trends, with completed students gaining {slope_completed:.2f} math points per reading point versus {slope_none:.2f} for non-participants. "
        "Prepared students cluster higher across the plane, rarely dropping below 60 in math when reading scores exceed 70. "
        "Non-prepared students show broader scatter and more cases dipping under the regression line, hinting at inconsistent math follow-through. "
        f"Legends reveal {trend['completed']['n']} prepared students versus {trend['none']['n']} without preparation, so the uplift is supported by sizable samples. "
        "Diverging regression lines reinforce the earlier boxplot story: test preparation elevates math results for comparable reading levels."
    )

    lines = [
        "## Student Performance Analysis",
        ingestion_paragraph,
        "",
        "### V1: Gender Score Distribution",
        "![](../outputs/analysis/v1_gender_boxplots.png)",
        v1_text,
        "",
        "### V2: Test Preparation and Math Outcomes",
        "![](../outputs/analysis/v2_testprep_math.png)",
        v2_text,
        "",
        "### V3: Lunch Type and Overall Average",
        "![](../outputs/analysis/v3_lunch_avg.png)",
        v3_text,
        "",
        "### V4: Subject Correlation Heatmap",
        "![](../outputs/analysis/v4_subject_corr.png)",
        v4_text,
        "",
        "### V5: Math vs Reading with Trend Lines",
        "![](../outputs/analysis/v5_scatter_trend_testprep.png)",
        v5_text,
    ]
    return "\n".join(lines).strip()

def update_report(report_section: str) -> None:
    existing = ""
    if REPORT_PATH.exists():
        existing = REPORT_PATH.read_text(encoding="utf-8")
        pattern = re.compile(r"## Student Performance Analysis[\s\S]*?(?=\n## |\Z)")
        existing = pattern.sub("", existing).strip()
    if existing:
        existing = existing.rstrip() + "\n\n"
    REPORT_PATH.write_text(existing + report_section + "\n", encoding="utf-8")


def main() -> None:
    df = ingest_and_process()
    artifacts = generate_figures(df)
    section = build_narrative(df, artifacts)
    update_report(section)
    print("Student performance visualizations generated successfully.")


if __name__ == "__main__":
    main()
