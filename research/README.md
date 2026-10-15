# Artificial Intelligence, Search Engines, and Cyberchondria — Baghdad

Graduation research project: full analysis pipeline and manuscript.

## Outputs (`output/`)
- `Cyberchondria_Research_Baghdad.docx` — the manuscript, formatted to the college instructions
  (Times New Roman 14; roman numerals for preliminary pages, arabic from the Introduction; Vancouver references).
  Word will ask to update fields on opening — click **Yes** to refresh page numbers in the lists of tables/figures.
- `Cyberchondria_Research_Baghdad_preview.pdf` — PDF rendering of the manuscript for quick viewing.
- `tables/all_results.xlsx` — supplementary workbook with every statistical test (27 sheets).
- `figures/` — all figures at 300 dpi.
- `summary.json` — key numbers used in the text.

## Reproduce
```
python3 analysis/01_clean_score.py <raw responses.xlsx> clean.pkl
python3 analysis/02_analysis.py clean.pkl output
python3 analysis/03_figures.py output
python3 analysis/04_build_docx.py output output/Cyberchondria_Research_Baghdad.docx [pages.json]
```
Requires pandas, scipy, statsmodels, pingouin, factor_analyzer, semopy, matplotlib, python-docx.
The raw participant-level responses are not stored in this repository.

## Placeholders to complete
Title page (logo, university, college, degree, students, supervisor, year), Acknowledgment, and ethics approval details (Method 2.7).
