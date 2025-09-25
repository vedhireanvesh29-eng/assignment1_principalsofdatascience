## Frailty Workflow
The frailty workflow ingests raw measurements, converts units to the metric system, and engineers BMI alongside a categorical age group representation. These features are encoded, including a binary frailty flag and one-hot vectors for each age bracket, before the processed dataset is persisted. Finally, summary statistics and the relationship between grip strength and frailty are documented for reporting.

| Column | Mean | Median | Std |
| --- | ---: | ---: | ---: |
| Height_in | 68.60 | 68.45 | 1.67 |
| Weight_lb | 131.90 | 136.00 | 14.23 |
| Age_yr | 32.50 | 29.50 | 12.86 |
| Grip_kg | 26.00 | 27.00 | 4.52 |
| Height_m | 1.74 | 1.74 | 0.04 |
| Weight_kg | 59.83 | 61.69 | 6.46 |
| BMI | 19.68 | 19.19 | 1.78 |
| Frailty_binary | 0.40 | 0.00 | 0.52 |
| AgeGroup_<30 | 0.50 | 0.50 | 0.53 |
| AgeGroup_30–45 | 0.30 | 0.00 | 0.48 |
| AgeGroup_46–60 | 0.20 | 0.00 | 0.42 |
| AgeGroup_>60 | 0.00 | 0.00 | 0.00 |

Correlation(Grip_kg, Frailty_binary) = -0.476
