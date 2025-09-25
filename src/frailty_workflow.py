"""Frailty workflow: ingest -> process -> analyze."""
from pathlib import Path
import re
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "frailty_data.csv"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "frailty_processed.csv"
REPORTS_DIR = PROJECT_ROOT / "reports"
FINDINGS_PATH = REPORTS_DIR / "findings.md"

AGE_GROUP_LABELS = ["<30", "30\u201345", "46\u201360", ">60"]


def categorize_age(age: float) -> str:
    if age < 30:
        return AGE_GROUP_LABELS[0]
    if age <= 45:
        return AGE_GROUP_LABELS[1]
    if age <= 60:
        return AGE_GROUP_LABELS[2]
    return AGE_GROUP_LABELS[3]


def load_data() -> pd.DataFrame:
    return pd.read_csv(RAW_PATH)


def enrich_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["Height_m"] = df["Height_in"] * 0.0254
    df["Weight_kg"] = df["Weight_lb"] * 0.45359237
    df["BMI"] = (df["Weight_kg"] / (df["Height_m"] ** 2)).round(2)
    df["AgeGroup"] = df["Age_yr"].apply(categorize_age)
    df["Frailty_binary"] = (df["Frailty"].str.upper() == "Y").astype("int8")

    age_group_cat = pd.Categorical(df["AgeGroup"], categories=AGE_GROUP_LABELS, ordered=True)
    age_dummies = pd.get_dummies(age_group_cat, prefix="AgeGroup")
    for label in AGE_GROUP_LABELS:
        col_name = f"AgeGroup_{label}"
        df[col_name] = age_dummies.get(col_name, 0).astype("int8")

    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = df.select_dtypes(include=["number"]).columns
    summary = df[numeric_cols].agg(["mean", "median", "std"]).T
    return summary.round(2)


def update_findings(summary: pd.DataFrame, correlation: float) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    table_lines = ["| Column | Mean | Median | Std |", "| --- | ---: | ---: | ---: |"]
    for column, stats in summary.iterrows():
        table_lines.append(
            f"| {column} | {stats['mean']:.2f} | {stats['median']:.2f} | {stats['std']:.2f} |"
        )
    table_markdown = "\n".join(table_lines)

    paragraph = (
        "The frailty workflow ingests raw measurements, converts units to the metric system, "
        "and engineers BMI alongside a categorical age group representation. "
        "These features are encoded, including a binary frailty flag and one-hot vectors for each age bracket, "
        "before the processed dataset is persisted. "
        "Finally, summary statistics and the relationship between grip strength and frailty are documented for reporting."
    )

    section_lines = [
        "## Frailty Workflow",
        paragraph,
        "",
        table_markdown,
        "",
        f"Correlation(Grip_kg, Frailty_binary) = {correlation:.3f}"
    ]
    section = "\n".join(section_lines).strip()

    existing = ""
    if FINDINGS_PATH.exists():
        existing = FINDINGS_PATH.read_text(encoding="utf-8")
        pattern = re.compile(r"## Frailty Workflow[\s\S]*?(?=\n## |\Z)")
        existing = pattern.sub("", existing).strip()

    if existing:
        existing = existing.rstrip() + "\n\n"

    FINDINGS_PATH.write_text(existing + section + "\n", encoding="utf-8")


def main() -> None:
    raw_df = load_data()
    enriched_df = enrich_features(raw_df)
    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    enriched_df.to_csv(PROCESSED_PATH, index=False, encoding="utf-8")
    summary = summarize(enriched_df)
    correlation = enriched_df["Grip_kg"].corr(enriched_df["Frailty_binary"])
    update_findings(summary, correlation)
    print("Frailty workflow completed successfully.")


if __name__ == "__main__":
    main()
