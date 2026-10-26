* Encoding: UTF-8.
* =============================================================================.
* Artificial Intelligence, Search Engines, and Cyberchondria: Baghdad (n = 300).
* SPSS syntax reproducing the study methodology (thesis Section 2.6).
* -----------------------------------------------------------------------------.
* HOW TO USE.
*   1. Put this file and Cyberchondria_Baghdad.sav in the same folder.
*   2. Edit the CD line below to point to that folder.
*   3. Run section by section (select a block, then Run > Selection).
* NOTES.
*   - Scores (SHAI, CSS, subscales) are already computed in the data file;.
*     Section 1 recomputes them so you can show how scoring works.
*   - FDR (Benjamini-Hochberg) correction and bootstrapped mediation are not.
*     built into base SPSS: see Sections 9 and 11.
*   - Confirmatory factor analysis needs AMOS (or R/lavaan); see Section 3.
* =============================================================================.

CD 'C:\Users\YOU\Documents\Cyberchondria'.
GET FILE='Cyberchondria_Baghdad.sav'.
DATASET NAME study WINDOW=FRONT.

* =============================================================================.
* SECTION 1. Scoring (check that it matches the stored scores).
* SHAI-14: 14 items scored 0-3 by meaning of the chosen statement (total 0-42).
* CSS-12: 12 items Never(1) - Always(5) (total 12-60), four 3-item subscales.
* =============================================================================.
COMPUTE SHAI_chk = SUM(shai1 TO shai14).
COMPUTE CSS_chk = SUM(css1 TO css12).
COMPUTE Excess_chk = SUM(css1, css2, css3).
COMPUTE Compul_chk = SUM(css4, css5, css6).
COMPUTE Distress_chk = SUM(css7, css8, css9).
COMPUTE Reassur_chk = SUM(css10, css11, css12).
COMPUTE HA_elev_chk = (SHAI_chk >= 18).
EXECUTE.
* Every difference below should be 0.
COMPUTE diff_SHAI = SHAI - SHAI_chk.
COMPUTE diff_CSS = CSS - CSS_chk.
DESCRIPTIVES VARIABLES=diff_SHAI diff_CSS /STATISTICS=MIN MAX.
DELETE VARIABLES SHAI_chk TO diff_CSS.

* =============================================================================.
* SECTION 2. Descriptive statistics (Tables 1-3).
* =============================================================================.
FREQUENCIES VARIABLES=age_group gender education occupation health_background chronic language
    tool_ai ai_user tool_search tool_medplat tool_social ai_model tool_profile
    mot_convenience mot_triage mot_reassurance mot_selfdx mot_cost trust
    beh_delay_reassured beh_ignore beh_multidoc beh_urgent beh_selfmed beh_delay_terrified
    share relationship HA_elevated CSS_high
  /ORDER=ANALYSIS.

DESCRIPTIVES VARIABLES=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur trust n_tools n_motives
  /STATISTICS=MEAN STDDEV MIN MAX SKEWNESS KURTOSIS.

* Medians/IQR and normality (Shapiro-Wilk), with histograms and Q-Q plots.
EXAMINE VARIABLES=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur
  /PLOT HISTOGRAM NPPLOT
  /STATISTICS DESCRIPTIVES
  /PERCENTILES(25,50,75)
  /MISSING LISTWISE.

* Prevalence of elevated health anxiety at alternative cut-offs (15, 18, 22, 29).
COMPUTE SHAI_ge15 = (SHAI >= 15).
COMPUTE SHAI_ge22 = (SHAI >= 22).
COMPUTE SHAI_ge29 = (SHAI >= 29).
EXECUTE.
FREQUENCIES VARIABLES=SHAI_ge15 HA_elevated SHAI_ge22 SHAI_ge29.

* =============================================================================.
* SECTION 3. Reliability and factor structure (Table 3).
* =============================================================================.
RELIABILITY /VARIABLES=shai1 TO shai14 /SCALE('SHAI-14') ALL
  /MODEL=ALPHA /STATISTICS=DESCRIPTIVE SCALE CORR /SUMMARY=TOTAL MEANS CORR.
RELIABILITY /VARIABLES=css1 TO css12 /SCALE('CSS-12') ALL
  /MODEL=ALPHA /STATISTICS=DESCRIPTIVE SCALE CORR /SUMMARY=TOTAL MEANS CORR.
RELIABILITY /VARIABLES=css1 css2 css3 /SCALE('Excessiveness') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css4 css5 css6 /SCALE('Compulsion') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css7 css8 css9 /SCALE('Distress') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css10 css11 css12 /SCALE('Reassurance') ALL /MODEL=ALPHA.
* McDonald's omega: SPSS 27+ has /MODEL=OMEGA (older versions: use the OMEGA macro or R).
* RELIABILITY /VARIABLES=shai1 TO shai14 /SCALE('SHAI-14') ALL /MODEL=OMEGA.

* Reliability separately in Arabic and English responders (language equivalence).
SORT CASES BY language.
SPLIT FILE SEPARATE BY language.
RELIABILITY /VARIABLES=shai1 TO shai14 /SCALE('SHAI-14 by language') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css1 TO css12 /SCALE('CSS-12 by language') ALL /MODEL=ALPHA.
SPLIT FILE OFF.

* Sampling adequacy (KMO, Bartlett) and exploratory factor structure.
FACTOR /VARIABLES css1 TO css12
  /PRINT INITIAL KMO EXTRACTION ROTATION
  /CRITERIA FACTORS(4) ITERATE(100)
  /EXTRACTION PAF /ROTATION OBLIMIN.
FACTOR /VARIABLES shai1 TO shai14
  /PRINT INITIAL KMO EXTRACTION
  /CRITERIA FACTORS(1)
  /EXTRACTION PAF.
* The confirmatory factor analysis in the thesis (DWLS and ML; CFI, TLI, RMSEA).
* needs AMOS or R/lavaan; the model is: four correlated factors for CSS-12.
* (items 1-3, 4-6, 7-9, 10-12) and one factor for SHAI-14.

* =============================================================================.
* SECTION 4. Correlations (Table 4, Figure 4).
* =============================================================================.
CORRELATIONS /VARIABLES=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur
  /PRINT=TWOTAIL NOSIG /STATISTICS DESCRIPTIVES.
NONPAR CORR /VARIABLES=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur trust n_tools n_motives age_ord
  /PRINT=SPEARMAN TWOTAIL NOSIG.
* Bootstrap 95% CI for the main correlation.
BOOTSTRAP /SAMPLING METHOD=SIMPLE /VARIABLES INPUT=SHAI CSS
  /CRITERIA CILEVEL=95 CITYPE=PERCENTILE NSAMPLES=5000.
CORRELATIONS /VARIABLES=SHAI CSS /PRINT=TWOTAIL.
* Partial correlation adjusted for covariates.
PARTIAL CORR /VARIABLES=SHAI CSS BY age_ord female health_background chronic trust ai_user
  /SIGNIFICANCE=TWOTAIL.

* =============================================================================.
* SECTION 5. Group comparisons for every variable (Table 5).
* Two groups: Mann-Whitney U.  Three or more: Kruskal-Wallis H with pairwise tests.
* =============================================================================.
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY female(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY chronic(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY health_background(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY ai_user(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY tool_search(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY tool_medplat(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY tool_social(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY mot_reassurance(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY mot_selfdx(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY mot_triage(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY mot_convenience(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY mot_cost(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY language(1 2).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY beh_delay_reassured(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY beh_delay_terrified(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY beh_selfmed(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY beh_urgent(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY beh_multidoc(0 1).
NPAR TESTS /M-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY beh_ignore(0 1).

NPAR TESTS /K-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY age4(1 4).
NPAR TESTS /K-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY education(1 5).
NPAR TESTS /K-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY occupation(1 5).
NPAR TESTS /K-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY tool_profile(1 3).
NPAR TESTS /K-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY trust(1 5).
NPAR TESTS /K-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY share(1 3).
NPAR TESTS /K-W=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur BY relationship(1 3).

* Pairwise post-hoc comparisons with adjusted p (Dunn-Bonferroni), e.g. SHAI by occupation.
NPTESTS /INDEPENDENT TEST (SHAI CSS) GROUP (occupation) KRUSKAL_WALLIS(COMPARE=PAIRWISE).
NPTESTS /INDEPENDENT TEST (SHAI CSS) GROUP (tool_profile) KRUSKAL_WALLIS(COMPARE=PAIRWISE).
NPTESTS /INDEPENDENT TEST (SHAI) GROUP (age4) KRUSKAL_WALLIS(COMPARE=PAIRWISE).

* Parametric confirmation (Welch ANOVA), e.g. by occupation.
ONEWAY SHAI CSS BY occupation /STATISTICS DESCRIPTIVES WELCH.

* Group means for Table 5.
MEANS TABLES=SHAI CSS BY age4 gender occupation chronic ai_user tool_search tool_social tool_profile
    mot_reassurance mot_selfdx trust language
  /CELLS=MEAN STDDEV COUNT MEDIAN.

* =============================================================================.
* SECTION 6. Chi-square tests (Table 6).
* =============================================================================.
CROSSTABS /TABLES=age4 gender education occupation health_background chronic ai_user tool_search
    tool_medplat tool_social tool_profile ai_model mot_convenience mot_cost mot_reassurance mot_selfdx
    mot_triage trust beh_delay_reassured beh_delay_terrified beh_selfmed beh_urgent beh_multidoc
    beh_ignore share relationship language BY HA_elevated CSS_high
  /STATISTICS=CHISQ PHI
  /CELLS=COUNT ROW EXPECTED
  /METHOD=MC CIN(99) SAMPLES(10000).
* /METHOD=MC gives Monte-Carlo exact p (needs the Exact Tests module); Fisher's exact.
* test is printed automatically for 2 x 2 tables.  Odds ratio for HA x high cyberchondria:.
CROSSTABS /TABLES=HA_elevated BY CSS_high /STATISTICS=CHISQ RISK /CELLS=COUNT ROW.

* =============================================================================.
* SECTION 7. Hierarchical linear regression of cyberchondria (Table 7).
* HC3 robust standard errors: use GENLIN or the RLM syntax below (SPSS 28+:.
* REGRESSION has no HC3; UNIANOVA /ROBUST=HC3 does).
* =============================================================================.
* Dummy variables (reference: age 20-29; occupation: non-health employee/other).
RECODE age4 (1=1)(ELSE=0) INTO age_18_19.
RECODE age4 (3=1)(ELSE=0) INTO age_30_39.
RECODE age4 (4=1)(ELSE=0) INTO age_40plus.
RECODE occupation (1=1)(ELSE=0) INTO occ_medstud.
RECODE occupation (2=1)(ELSE=0) INTO occ_othhealth.
RECODE occupation (3=1)(ELSE=0) INTO occ_hcw.
RECODE occupation (4=1)(ELSE=0) INTO occ_nhstud.
COMPUTE lang_en = (language = 2).
EXECUTE.

REGRESSION
  /STATISTICS COEFF OUTS CI(95) R ANOVA CHANGE COLLIN TOL
  /DEPENDENT CSS
  /METHOD=ENTER age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en
  /METHOD=ENTER ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage
  /METHOD=ENTER SHAI
  /RESIDUALS HISTOGRAM(ZRESID) NORMPROB(ZRESID)
  /SCATTERPLOT=(*ZRESID ,*ZPRED).

* Same final model with HC3 robust standard errors (SPSS 26+).
UNIANOVA CSS WITH age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en
    ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI
  /PRINT=PARAMETER /ROBUST=HC3
  /DESIGN=age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en
    ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.

* Sensitivity: AI use defined as ticked only (thesis Section 3.7).
REGRESSION /STATISTICS COEFF CI(95) R
  /DEPENDENT CSS
  /METHOD=ENTER age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en
    tool_ai tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.

* Reverse model: health anxiety on cyberchondria.
REGRESSION /STATISTICS COEFF CI(95) R ANOVA CHANGE
  /DEPENDENT SHAI
  /METHOD=ENTER age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en
    ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage
  /METHOD=ENTER CSS.

* Each CSS subscale on SHAI (same covariates).
REGRESSION /STATISTICS COEFF CI(95) R /DEPENDENT CSS_excess
  /METHOD=ENTER age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.
REGRESSION /STATISTICS COEFF CI(95) R /DEPENDENT CSS_compul
  /METHOD=ENTER age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.
REGRESSION /STATISTICS COEFF CI(95) R /DEPENDENT CSS_distress
  /METHOD=ENTER age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.
REGRESSION /STATISTICS COEFF CI(95) R /DEPENDENT CSS_reassur
  /METHOD=ENTER age_18_19 age_30_39 age_40plus female occ_medstud occ_othhealth occ_hcw occ_nhstud chronic lang_en ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.

* =============================================================================.
* SECTION 8. Logistic and ordinal regression (Tables 8-9).
* Scores are entered per 1 SD (z-scores), as in the thesis.
* =============================================================================.
DESCRIPTIVES VARIABLES=SHAI CSS /SAVE.
* Creates ZSHAI and ZCSS.

LOGISTIC REGRESSION VARIABLES HA_elevated
  /METHOD=ENTER age_ord female health_background chronic lang_en ai_user tool_search trust mot_reassurance mot_selfdx ZCSS
  /PRINT=CI(95) GOODFIT
  /SAVE=PRED(p_HA).
* AUC for the model.
ROC p_HA BY HA_elevated (1) /PRINT=SE /PLOT=CURVE(REFERENCE).

* Each behaviour on health anxiety and cyberchondria (repeat with each outcome).
LOGISTIC REGRESSION VARIABLES beh_urgent
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).
LOGISTIC REGRESSION VARIABLES beh_multidoc
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).
LOGISTIC REGRESSION VARIABLES beh_delay_reassured
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).
LOGISTIC REGRESSION VARIABLES beh_delay_terrified
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).
LOGISTIC REGRESSION VARIABLES beh_selfmed
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).
LOGISTIC REGRESSION VARIABLES beh_ignore
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).
LOGISTIC REGRESSION VARIABLES share_never
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).
LOGISTIC REGRESSION VARIABLES rel_negative
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en /PRINT=CI(95).

* Ordinal logistic regression (relationship strain; non-disclosure).
PLUM relationship WITH ZSHAI ZCSS trust ai_user age_ord female health_background chronic
  /LINK=LOGIT /PRINT=FIT PARAMETER SUMMARY TPARALLEL.
PLUM share WITH ZSHAI ZCSS trust ai_user age_ord female health_background chronic
  /LINK=LOGIT /PRINT=FIT PARAMETER SUMMARY TPARALLEL.

* =============================================================================.
* SECTION 9. Mediation (Table 10, Figure 7) - Hayes PROCESS macro, model 4.
* Install PROCESS first (processmacro.org), then run its .sps file once.
* Variables are standardised to match the thesis (standardised coefficients).
* =============================================================================.
DESCRIPTIVES VARIABLES=CSS_excess CSS_distress CSS_compul CSS_reassur /SAVE.
* Model A: health anxiety -> excessive searching -> post-search distress.
PROCESS y=ZCSS_distress /x=ZSHAI /m=ZCSS_excess /cov=age_ord female health_background chronic trust ai_user
  /model=4 /boot=5000 /seed=2026.
* Model B: health anxiety -> excessive searching -> compulsion.
PROCESS y=ZCSS_compul /x=ZSHAI /m=ZCSS_excess /cov=age_ord female health_background chronic trust ai_user
  /model=4 /boot=5000 /seed=2026.
* Model C: health anxiety -> post-search distress -> reassurance seeking.
PROCESS y=ZCSS_reassur /x=ZSHAI /m=ZCSS_distress /cov=age_ord female health_background chronic trust ai_user
  /model=4 /boot=5000 /seed=2026.
* Model D (reverse): excessive searching -> distress -> health anxiety.
PROCESS y=ZSHAI /x=ZCSS_excess /m=ZCSS_distress /cov=age_ord female health_background chronic trust ai_user
  /model=4 /boot=5000 /seed=2026.
* Serial model: health anxiety -> excessive searching -> distress -> reassurance (model 6).
PROCESS y=ZCSS_reassur /x=ZSHAI /m=ZCSS_excess ZCSS_distress /cov=age_ord female health_background chronic trust ai_user
  /model=6 /boot=5000 /seed=2026.

* =============================================================================.
* SECTION 10. Moderation (does the SHAI-CSS link differ by group?).
* =============================================================================.
COMPUTE SHAI_c = SHAI - 12.35.
COMPUTE trust_c = trust - 2.687.
COMPUTE SHAIxTrust = SHAI_c * trust_c.
COMPUTE SHAIxAI = SHAI_c * ai_user.
COMPUTE SHAIxHB = SHAI_c * health_background.
COMPUTE SHAIxFem = SHAI_c * female.
COMPUTE SHAIxChron = SHAI_c * chronic.
COMPUTE SHAIxLang = SHAI_c * lang_en.
COMPUTE SHAIxAge = SHAI_c * age_ord.
EXECUTE.
REGRESSION /STATISTICS COEFF CI(95) R CHANGE /DEPENDENT CSS
  /METHOD=ENTER SHAI_c trust_c age_ord female health_background chronic ai_user
  /METHOD=ENTER SHAIxTrust.
REGRESSION /STATISTICS COEFF CI(95) R CHANGE /DEPENDENT CSS
  /METHOD=ENTER SHAI_c age_ord female health_background chronic trust ai_user
  /METHOD=ENTER SHAIxAI SHAIxHB SHAIxFem SHAIxChron SHAIxLang SHAIxAge.
* (The thesis tests each interaction in a separate model; enter them one at a time to match.).
* Alternative: PROCESS model 1, e.g. PROCESS y=CSS /x=SHAI /w=trust /model=1 /center=1.

* Subgroup correlations.
SORT CASES BY occupation.
SPLIT FILE LAYERED BY occupation.
CORRELATIONS /VARIABLES=SHAI CSS.
SPLIT FILE OFF.

* =============================================================================.
* SECTION 11. Multiple-testing correction (Benjamini-Hochberg FDR).
* SPSS has no built-in FDR.  Copy the p-values of a family of tests into a new.
* dataset (one column named p), then run the block below; q < 0.05 survives.
* =============================================================================.
* DATASET ACTIVATE pvalues.
* SORT CASES BY p (A).
* COMPUTE rank = $CASENUM.
* AGGREGATE /OUTFILE=* MODE=ADDVARIABLES /m = N.
* COMPUTE q_raw = p * m / rank.
* SORT CASES BY rank (D).
* COMPUTE q = q_raw.
* IF ($CASENUM > 1) q = MIN(q_raw, LAG(q)).
* COMPUTE q = MIN(q, 1).
* SORT CASES BY rank (A).
* EXECUTE.

* =============================================================================.
* SECTION 12. Sensitivity analyses.
* =============================================================================.
* Straight-line responders (identical answers on all items of a scale).
COMPUTE sd_shai = SD(shai1 TO shai14).
COMPUTE sd_css = SD(css1 TO css12).
COMPUTE straightline = (sd_shai = 0 OR sd_css = 0).
EXECUTE.
FREQUENCIES VARIABLES=straightline.
TEMPORARY.
SELECT IF (straightline = 0).
CORRELATIONS /VARIABLES=SHAI CSS.
* Early vs late responders (median split of submission date).
RANK VARIABLES=date (A) /NTILES(2) INTO half.
NPAR TESTS /M-W=SHAI CSS BY half(1 2).
