# Assignment 1 - Principles of Data Science

## Repository Layout
- `data/raw/` sources: `frailty_data.csv` for Q1 and `students_performance.csv` for Q2.
- `data/processed/` pipeline outputs such as `frailty_processed.csv`, ingested/cleaned student tables.
- `outputs/analysis/` generated visuals and aggregates for the student performance study.
- `reports/findings.md`: Frailty workflow summary stats and correlation findings.
- `reports/analysis_report.md`: Narrative walkthrough of the five required student performance visuals.
- `src/frailty_workflow.py`, `src/students_viz.py`: Reproducible scripts for both assignment questions.

## Workflows
### Frailty Workflow (Q1)
- Ingests `data/raw/frailty_data.csv`, converts units, engineers BMI and age-group features, and encodes the dataset.
- Persists the processed table to `data/processed/frailty_processed.csv` and refreshes `reports/findings.md` with summary statistics plus the grip-strength correlation.

### Student Performance Workflow (Q2)
- Cleans the Kaggle Students Performance dataset, adds the `overall_avg` feature, and creates five visualizations (V1–V5) saved to `outputs/analysis/`.
- Updates `reports/analysis_report.md` with 5–8 sentence interpretations for each visual.

## How to Run
```
python src/frailty_workflow.py
python src/students_viz.py
```

Running the scripts recreates processed data, figures, and reports from scratch.

## Outputs
- `data/processed/frailty_processed.csv`, `reports/findings.md` — frailty ingest -> process -> analyze deliverables.
- `outputs/analysis/v1_gender_boxplots.png` … `v5_scatter_trend_testprep.png`, plus supporting CSV summaries.
- `reports/analysis_report.md` — student performance narrative tied to the generated visuals.
