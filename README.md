# Assignment 1 - Principles of Data Science

## Dataset: StudentsPerformance
- Source: Local copy of the public Kaggle `StudentsPerformance` dataset.
- Records: 1000 students, 8 columns capturing demographics and test scores.

### Columns
- `gender`: Student gender (`female` or `male`).
- `race/ethnicity`: Racial or ethnic group label.
- `parental level of education`: Highest education level attained by a parent.
- `lunch`: Lunch type (`standard` or `free/reduced`).
- `test preparation course`: Whether a test preparation course was completed.
- `math score`: Math exam score (0-100).
- `reading score`: Reading exam score (0-100).
- `writing score`: Writing exam score (0-100).

## Pipeline (ingest -> process -> analyze)
1. `python src/pipeline.py`
2. Generated artifacts land in `data/processed/` and `outputs/analysis/`.

## Repository Structure
- `data/raw/students_performance.csv`: Source dataset for the assignment.
- `data/processed/`: Ingested and cleaned tables written by the pipeline.
- `outputs/analysis/`: Aggregated metrics and narrative report from the analysis stage.
- `src/pipeline.py`: End-to-end pipeline that orchestrates ingest -> process -> analyze.

Update or extend the pipeline with notebooks, scripts, or reports to document additional analysis steps and findings.
