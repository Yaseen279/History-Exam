# Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad

Graduation research project: full analysis pipeline and manuscript.

## Outputs (`output/`)
- `Cyberchondria_Research_Baghdad.docx` — the manuscript, formatted to the college instructions
  (Times New Roman 14; roman numerals for preliminary pages, arabic from the Introduction; Vancouver references).
  Word will ask to update fields on opening — click **Yes** to refresh page numbers in the lists of tables/figures.
- `Cyberchondria_Research_Baghdad_preview.pdf` — PDF rendering of the manuscript for quick viewing.
- `tables/all_results.xlsx` — supplementary workbook with every statistical test (27 sheets).
- `figures/` — all figures at 300 dpi.
- `study/summary.pdf` — one-page summary of findings.
- `study/guide.pdf` — study & defence guide (concepts, statistics, results walkthrough, slide plan, committee Q&A).
- `study/Defence_Presentation.pptx` — 18-slide defence presentation with speaker notes.
- `study/Defence_Presentation_UOBCOM.pptx` — 34-slide defence deck in the UOBCOM student-research style (college logos, CC0 photos, maps), speaker notes split by student; `_preview.pdf` alongside.
- `questionnaire/` — the questionnaire pages reproduced in Appendix B.
- `summary.json` — key numbers used in the text.

## Reproduce
```
python3 analysis/01_clean_score.py <raw responses.xlsx> clean.pkl
python3 analysis/02_analysis.py clean.pkl output
python3 analysis/02b_extra.py output                 # optimism-corrected AUC, SRMR, f2, item-2 sensitivity
python3 analysis/02c_invariance.py output/analysed.pkl output/tables   # Arabic vs English multi-group CFA + item DIF
python3 analysis/03_figures.py output
python3 analysis/03b_framework_figures.py output    # conceptual framework (Fig. 1) and study flowchart (Fig. 2)
python3 analysis/04_build_docx.py output output/Cyberchondria_Research_Baghdad.docx [pages.json]
python3 analysis/05_page_map.py <rendered.pdf> pages.json output/toc_entries.json   # page numbers for TOC and lists
python3 analysis/06_study_materials.py output        # summary + guide HTML (print to PDF) and numbers.json
python3 analysis/11_team_guide.py output/study/numbers.json output/study/team_guide.html   # team guide (print to PDF)
NODE_PATH=<node_modules with pptxgenjs> node analysis/07_build_deck.js output/study/numbers.json output/study/Defence_Presentation.pptx <apply_theme.js>
NODE_PATH=<node_modules with pptxgenjs, jszip> node analysis/09_build_uobcom_deck.js output/study/numbers.json assets/uobcom output/questionnaire output/study/Defence_Presentation_UOBCOM.pptx
node analysis/maps/10_draw_maps.mjs <node_modules with world-atlas, topojson-client, d3-geo> <out dir>   # SVG maps; rendered to assets/photos/map_*.png
```
Photo sources and licences: `assets/photos/CREDITS.csv` (StockSnap CC0; maps from public-domain Natural Earth data).

Requires pandas, scipy, statsmodels, pingouin, factor_analyzer, semopy, matplotlib, python-docx.
The raw participant-level responses are not stored in this repository.

## Placeholders to complete
Title page (logo, university, college, degree, students, supervisor, year), Acknowledgment, and ethics approval details (Method 2.7).
