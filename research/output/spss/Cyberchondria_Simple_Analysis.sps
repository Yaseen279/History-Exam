* Encoding: UTF-8.
* =====================================================================================
* Health Anxiety, AI Chatbot Use and Cyberchondria Among Adults in Baghdad (n = 300)
* SPSS syntax for EVERY analysis reported in the short thesis (Tables 1-11, Figures 4-8).
*
* HOW TO USE
*   1. Open Cyberchondria_Baghdad.sav in SPSS (File > Open > Data).
*   2. Open this file (File > Open > Syntax), then Run > All.
*   3. Compare the output with the thesis tables (each section says which table it feeds).
*      Small differences in the last decimal are normal; tell the team if anything differs more.
*   4. The thesis states IBM SPSS Statistics version 26 (Section 2.5): run this file in version 26.
* =====================================================================================.

* ------------------------------------------------ 0. Helper variables.
* Language: 1 = English, 0 = Arabic.
COMPUTE lang_en = (language = 2).
* Age dummies, reference = 20-29 (age4: 1 = 18-19, 2 = 20-29, 3 = 30-39, 4 = 40+).
COMPUTE age_1819 = (age4 = 1).
COMPUTE age_3039 = (age4 = 3).
COMPUTE age_40plus = (age4 = 4).
* Occupation dummies, reference = non-health employed/other (occupation = 5).
COMPUTE occ_medstud = (occupation = 1).
COMPUTE occ_othhealth = (occupation = 2).
COMPUTE occ_hcw = (occupation = 3).
COMPUTE occ_nonhstud = (occupation = 4).
VARIABLE LABELS lang_en 'Answered mainly in English' age_1819 'Age 18-19' age_3039 'Age 30-39' age_40plus 'Age 40+'
  occ_medstud 'Medical student' occ_othhealth 'Other health-science student' occ_hcw 'Healthcare worker' occ_nonhstud 'Non-health student'.
* Prevalence at the other SHAI cut-offs (Table 4).
COMPUTE shai_ge15 = (SHAI >= 15).
COMPUTE shai_ge22 = (SHAI >= 22).
COMPUTE shai_ge29 = (SHAI >= 29).
EXECUTE.
* z-scores: creates ZSHAI, ZCSS, ZCSS_excess, ZCSS_compul, ZCSS_distress, ZCSS_reassur.
DESCRIPTIVES VARIABLES=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur /SAVE.

* ------------------------------------------------ 1. Descriptive statistics (Tables 1, 2, 4; Figures 2, 3).
FREQUENCIES VARIABLES=age4 gender education occupation health_background chronic language
  tool_search tool_ai ai_user tool_medplat tool_social tool_profile ai_model
  mot_convenience mot_triage mot_reassurance mot_selfdx mot_cost trust
  beh_delay_reassured beh_ignore beh_multidoc beh_urgent beh_selfmed beh_delay_terrified share relationship
  HA_elevated shai_ge15 shai_ge22 shai_ge29 CSS_high
  /ORDER=ANALYSIS.
* 95% CI of a prevalence (Table 4): Wilson interval, calculated by hand or with an online calculator from n and %.
* AI use by age group (Section 3.1).
CROSSTABS /TABLES=age4 BY ai_user /CELLS=COUNT ROW.

* ------------------------------------------------ 2. Scale scores, normality and reliability (Table 3).
EXAMINE VARIABLES=SHAI CSS CSS_excess CSS_compul CSS_distress CSS_reassur
  /PLOT NPPLOT /STATISTICS DESCRIPTIVES /PERCENTILES(25,50,75).
* Shapiro-Wilk p < 0.05 for SHAI and CSS -> non-parametric group tests.
RELIABILITY /VARIABLES=shai1 TO shai14 /SCALE('SHAI-14') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css1 TO css12 /SCALE('CSS-12') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css1 css2 css3 /SCALE('Excessiveness') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css4 css5 css6 /SCALE('Compulsion') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css7 css8 css9 /SCALE('Distress') ALL /MODEL=ALPHA.
RELIABILITY /VARIABLES=css10 css11 css12 /SCALE('Reassurance') ALL /MODEL=ALPHA.

* ------------------------------------------------ 3. Correlation (Table 5, Figure 4).
CORRELATIONS /VARIABLES=SHAI WITH CSS CSS_excess CSS_compul CSS_distress CSS_reassur /PRINT=TWOTAIL.
NONPAR CORR /VARIABLES=SHAI WITH CSS CSS_excess CSS_compul CSS_distress CSS_reassur /PRINT=SPEARMAN TWOTAIL.
* Partial correlation controlling for age, gender, health background, chronic disease, trust and AI use.
PARTIAL CORR /VARIABLES=SHAI CSS BY age_ord female health_background chronic trust ai_user /SIGNIFICANCE=TWOTAIL.
* Scatter plot with fit line (Figure 4).
GRAPH /SCATTERPLOT(BIVAR)=SHAI WITH CSS.
* 95% CI of r (Table 5): Fisher z, by hand: z = atanh(r) +/- 1.96/sqrt(n-3), then back-transform with tanh.
* "Adjusted beta" column of Table 5: Beta of SHAI from the Section 6 model, repeated with each subscale as the dependent variable.

* ------------------------------------------------ 4. Group comparisons (Table 6, Figure 5).
NPAR TESTS /M-W= SHAI CSS BY gender(1 2)
  /M-W= SHAI CSS BY chronic(0 1)
  /M-W= SHAI CSS BY health_background(0 1)
  /M-W= SHAI CSS BY ai_user(0 1)
  /M-W= SHAI CSS BY tool_search(0 1)
  /M-W= SHAI CSS BY tool_social(0 1)
  /M-W= SHAI CSS BY mot_reassurance(0 1)
  /M-W= SHAI CSS BY mot_selfdx(0 1)
  /M-W= SHAI CSS BY language(1 2).
NPAR TESTS /K-W= SHAI CSS BY age4(1 4)
  /K-W= SHAI CSS BY education(1 5)
  /K-W= SHAI CSS BY occupation(1 5)
  /K-W= SHAI CSS BY tool_profile(1 3)
  /K-W= SHAI CSS BY trust(1 5).
MEANS TABLES=SHAI CSS BY age4 gender education occupation chronic ai_user tool_search tool_social tool_profile mot_reassurance mot_selfdx trust language
  /CELLS=COUNT MEAN STDDEV.
EXAMINE VARIABLES=CSS BY tool_profile /PLOT=BOXPLOT /STATISTICS=NONE.

* ------------------------------------------------ 5. Chi-square tests (Table 7).
* Fisher's exact test is printed automatically for 2x2 tables. If you have the Exact Tests module,
* add /METHOD=MC CIN(99) SAMPLES(10000) for larger tables with expected counts < 5.
CROSSTABS /TABLES=HA_elevated CSS_high BY age4 gender occupation chronic ai_user tool_search tool_medplat tool_social tool_profile ai_model
    mot_convenience mot_triage mot_reassurance mot_selfdx mot_cost trust
    beh_delay_reassured beh_ignore beh_multidoc beh_urgent beh_selfmed beh_delay_terrified share relationship language
  /STATISTICS=CHISQ PHI /CELLS=COUNT ROW.
* Odds ratio of high cyberchondria for elevated health anxiety.
CROSSTABS /TABLES=HA_elevated BY CSS_high /STATISTICS=CHISQ RISK /CELLS=COUNT ROW.

* ------------------------------------------------ 6. Hierarchical multiple linear regression of CSS (Table 8).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA CHANGE COLLIN TOL
  /DEPENDENT CSS
  /METHOD=ENTER age_1819 age_3039 age_40plus female occ_hcw occ_medstud occ_nonhstud occ_othhealth chronic lang_en
  /METHOD=ENTER ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage
  /METHOD=ENTER SHAI
  /RESIDUALS HISTOGRAM(ZRESID) NORMPROB(ZRESID).
* Strict AI definition (ticked only): same model with tool_ai instead of ai_user (Section 3.5).
REGRESSION /STATISTICS COEFF OUTS CI(95) R ANOVA /DEPENDENT CSS
  /METHOD=ENTER age_1819 age_3039 age_40plus female occ_hcw occ_medstud occ_nonhstud occ_othhealth chronic lang_en
     tool_ai tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.
* Adjusted beta for each CSS dimension (Table 5, last column): Beta of SHAI in each model.
REGRESSION /STATISTICS COEFF /DEPENDENT CSS_excess CSS_compul CSS_distress CSS_reassur
  /METHOD=ENTER age_1819 age_3039 age_40plus female occ_hcw occ_medstud occ_nonhstud occ_othhealth chronic lang_en
     ai_user tool_search tool_medplat tool_social trust mot_reassurance mot_selfdx mot_cost mot_triage SHAI.

* ------------------------------------------------ 7. Binary logistic regression of elevated health anxiety (Table 9, Figure 6).
LOGISTIC REGRESSION VARIABLES HA_elevated
  /METHOD=ENTER age_ord female health_background chronic lang_en ai_user tool_search trust mot_reassurance mot_selfdx ZCSS
  /SAVE=PRED(pred_HA)
  /PRINT=GOODFIT CI(95)
  /CRITERIA=PIN(.05) POUT(.10) ITERATE(20) CUT(.5).
* Area under the ROC curve.
ROC pred_HA BY HA_elevated (1) /PLOT=CURVE(REFERENCE) /PRINT=SE.

* ------------------------------------------------ 8. Behaviours (Table 10): one logistic model per behaviour.
* Read the Exp(B) and 95% CI of ZSHAI and ZCSS (and trust for multiple doctors).
DEFINE !beh (y = !TOKENS(1))
LOGISTIC REGRESSION VARIABLES !y
  /METHOD=ENTER ZSHAI ZCSS trust ai_user age_ord female health_background chronic lang_en
  /PRINT=CI(95).
!ENDDEFINE.
!beh y=beh_urgent.
!beh y=beh_multidoc.
!beh y=beh_delay_reassured.
!beh y=beh_delay_terrified.
!beh y=beh_selfmed.
!beh y=beh_ignore.
!beh y=share_never.
!beh y=rel_negative.

* ------------------------------------------------ 9. Mediation with the Sobel test (Table 11, Figure 7).
* All variables are z-scores, so the coefficients (B) are standardised.
* For each model run three regressions: path a (M on X), paths b and c' (Y on X and M), path c (Y on X).
* Sobel z = (a*b) / SQRT(b**2 * SEa**2 + a**2 * SEb**2); two-sided p from the normal distribution
* (any online "Sobel test calculator" does the same from a, SEa, b, SEb).
* Model A: X = ZSHAI, M = ZCSS_excess, Y = ZCSS_distress.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZCSS_excess /METHOD=ENTER ZSHAI age_ord female health_background chronic trust ai_user.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZCSS_distress /METHOD=ENTER ZSHAI ZCSS_excess age_ord female health_background chronic trust ai_user.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZCSS_distress /METHOD=ENTER ZSHAI age_ord female health_background chronic trust ai_user.
* Model B (thesis model C): X = ZSHAI, M = ZCSS_distress, Y = ZCSS_reassur.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZCSS_distress /METHOD=ENTER ZSHAI age_ord female health_background chronic trust ai_user.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZCSS_reassur /METHOD=ENTER ZSHAI ZCSS_distress age_ord female health_background chronic trust ai_user.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZCSS_reassur /METHOD=ENTER ZSHAI age_ord female health_background chronic trust ai_user.
* Reverse order: X = ZCSS_excess, M = ZCSS_distress, Y = ZSHAI.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZCSS_distress /METHOD=ENTER ZCSS_excess age_ord female health_background chronic trust ai_user.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZSHAI /METHOD=ENTER ZCSS_excess ZCSS_distress age_ord female health_background chronic trust ai_user.
REGRESSION /STATISTICS COEFF OUTS /DEPENDENT ZSHAI /METHOD=ENTER ZCSS_excess age_ord female health_background chronic trust ai_user.
* Figure 8: mean of each CSS dimension by health-anxiety status.
MEANS TABLES=CSS_excess CSS_compul CSS_distress CSS_reassur BY HA_elevated /CELLS=MEAN STDDEV COUNT.
