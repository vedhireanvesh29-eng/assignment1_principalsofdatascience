"""Data pipeline for the StudentsPerformance dataset.

Stages: ingest -> process -> analyze
"""

from pathlib import Path
from typing import Tuple

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "students_performance.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
ANALYSIS_DIR = PROJECT_ROOT / "outputs" / "analysis"

def ingest(raw_path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw dataset and persist an ingested copy."""
    df = pd.read_csv(raw_path)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ingested_path = PROCESSED_DIR / "students_performance_ingested.csv"
    df.to_csv(ingested_path, index=False)
    return df

def process(df: pd.DataFrame) -> pd.DataFrame:
    """Clean column names, derive helper columns, and persist the result."""
    renamed = df.rename(
        columns={
            "race/ethnicity": "race_ethnicity",
            "parental level of education": "parental_education",
            "test preparation course": "test_preparation_course",
            "math score": "math_score",
            "reading score": "reading_score",
            "writing score": "writing_score",
        }
    )
    renamed.columns = [col.replace(" ", "_").lower() for col in renamed.columns]

    numeric_cols = ["math_score", "reading_score", "writing_score"]
    renamed["average_score"] = renamed[numeric_cols].mean(axis=1)
    renamed["score_band"] = pd.cut(
        renamed["average_score"],
        bins=[0, 60, 80, 100],
        labels=["needs_support", "proficient", "advanced"],
        include_lowest=True,
    )

    processed_path = PROCESSED_DIR / "students_performance_processed.csv"
    renamed.to_csv(processed_path, index=False)
    return renamed

def analyze(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Generate aggregate views and persist analysis artifacts."""
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

    score_summary = df[["math_score", "reading_score", "writing_score", "average_score"]].agg(
        ["mean", "median", "std"]
    ).round(2)
    summary_path = ANALYSIS_DIR / "score_summary.csv"
    score_summary.to_csv(summary_path)

    prep_course = (
        df.groupby("test_preparation_course")["average_score"].agg(["mean", "median", "count"])
        .sort_values("mean", ascending=False)
        .round(2)
    )
    prep_path = ANALYSIS_DIR / "prep_course_performance.csv"
    prep_course.to_csv(prep_path)

    report_lines = [
        "# StudentsPerformance Analysis",
        "",
        "## Overall score statistics",
        "Saved to `score_summary.csv` with mean/median/std for math, reading, writing, and average scores.",
        "",
        "## Test preparation course impact",
        "Saved to `prep_course_performance.csv` sorted by highest average score.",
        "",
        "### Key observations",
    ]
    top_band_share = (df["score_band"] == "advanced").mean() * 100
    prep_gain = prep_course.loc["completed", "mean"] - prep_course.loc["none", "mean"] if {"completed", "none"}.issubset(prep_course.index) else float("nan")
    report_lines.append(f"- Advanced score band represents {top_band_share:.1f}% of students.")
    if not pd.isna(prep_gain):
        report_lines.append(
            f"- Completing the test preparation course increases average scores by {prep_gain:.1f} points over students without it."
        )

    report_path = ANALYSIS_DIR / "analysis_report.md"
    report_path.write_text("\n".join(report_lines))

    return score_summary, prep_course

def run_pipeline() -> None:
    """Execute pipeline stages end-to-end."""
    raw_df = ingest()
    processed_df = process(raw_df)
    analyze(processed_df)

if __name__ == "__main__":
    run_pipeline()
