<!-- The separate reviewer's report (Brief 20, M7), written by an agent that had not seen the drafting, on the manuscript as committed in e400a1a; kept as it was written. Line numbers refer to main.tex at that commit. The changes it led to, and the points not changed with their reasons, are recorded in DECISIONS.md D121. -->

# Review report

**Manuscript:** "Neither conduction nor a fixed delivered energy fraction reproduces sixteen two-cell propagation tests: a pre-registered kinetic study" (S. Satte), Journal of Power Sources. Line numbers are main.tex lines.

## Summary of the submission

A published Bayesian CRNN decomposition model (Koenig et al. 2025) is integrated in a lumped and a resolved LG M50 neighbour heated by a one-temperature trigger, and both are set, in eleven pre-registered stages, against the sixteen two-cell tests of Fransson et al. (2024). The manuscript reports that the resolved hot spot starts reacting before the lumped cell and that the kinetics set both onsets; that a Databank body energy ignites neither neighbour by conduction and radiation; that seven ignition criteria differ in outcome and timing; that the delivered fraction of ejected energy each test needs varies 42- to 208-fold and overlaps between outcomes; that with no delivery the far face overshoots four measured maxima; that one digitised history favours a short delivery; that held out no predictor beats a constant; Stage 11 sensitivity bands; and that 36 of 70 registered predictions failed.

## Recommendation

**Major revision.** The study is transparent and reproducible, with careful energy and convergence checks, and its core negative result (a conduction model with one fixed delivered fraction cannot reproduce these tests) is useful. But the abstract, highlights and Conclusions overstate the Results and the study's own corrected records, and the abstract contradicts itself; the central 42- to 208-fold number is ill-conditioned and rests on trigger energies that exceed the calorimetry; several numbers are attributed to the wrong node, quantity or condition; and some comparator statements go beyond their sources. Most fixes are textual; one requested analysis (Major 2) may need runs.

## Major points

1. **Headline claims exceed the evidence (B1 to B8, B11, B13).** The scope words are the problem: "under any kinetic draw", "never", "nothing", "each test's", "rarely".
   - The abstract says conduction ignites neither neighbour. It then credits a local criterion that conduction alone meets in eight tests.
   - The study's own check (DECISIONS.md D109 (6)) corrected "nothing beats the constant" to "by that margin or significantly". The manuscript brings the old wording back in five places.
2. **The between-test spread is fragile and largely restates the inferred trigger.**
   - (a) **How the spread is defined (D105 (4)).** It is the largest non-zero fraction over the smallest, across 11 to 13 of the 16 tests, with the four zeros left out.
     - It mixes two different readings: far-face peaks (fmax) and lumped-clock times (ft(C2)).
     - Its denominator is always SP_Exp3 (0.0013 to 0.0031). That test's lumped neighbour already crosses with no delivery, only 11.5 s late. A ratio to a value near zero is ill-conditioned.
     - Report delivered energies (22- to 64-fold), the share of zeros and absolute ranges alongside it.
   - (b) **Which tests set the ends.**
     - At 21.39 s and 120 s, the spread runs between PT_Exp1 (trigger maximum 164 °C) and SP_Exp3. These are two of the four tests Fransson et al. mark "cell movement" (inputs/fransson2024/m50_tests.csv; D33 (3)). Their paper notes outlier values from moved thermocouples (D89 (5)).
     - At 240 s and 360 s, the spread runs between ST_Exp3 (trigger maximum 282 °C) and SP_Exp3.
     - The author's own ρ(f*, E_b) of −0.92 and −0.97 shows that the thresholds track the trigger.
   - (c) **The trigger energy exceeds the calorimetry.** E_b is fitted to one surface thermocouple maximum.
     - In 13 of 16 tests it exceeds the largest body energy the Databank measured for this cell (33.2 kJ).
     - In 14 of 16 tests, E_e = 3.105 E_b exceeds the largest measured ejecta energy (89.3 kJ; inputs/databank/databank_m50_used.csv).
     - All eight tests in which conduction alone ignites the hot spot have E_b of 46.5 to 54.3 kJ.
     - So f is a share of an ejected energy that the calorimetry does not support. Discuss this, and add a sensitivity case with E_b capped (or E_e fixed at the Databank median).
3. **The far-face overshoot rests on unmeasured inputs.**
   - At the low contact it holds in one test of four (stage11_paper_numbers.json far_face.four_low_maxima_low_K).
   - The contact values come from a textbook section that the reference check did not read (references_verified.json lienhard2024heat).
   - The source does not give the thermocouple's angle.
   - The abstract and heading 3.5 should say all of this.
4. **The Stage 11 "bands" are sensitivity cases.**
   - The kinetic draws were ranked by the onset in a different geometry.
   - Three of the four (draws 188, 40 and 184) come from the 10.5 % of draws with no short (D111 (1)). The manuscript does not say so.
   - Near zero, the 0.0125 search step makes the factors step-sized: ST_Exp2's "third" is one step (D118 (3)).
   - Report the registered log share (0.30 to 0.43; E2.C2.share_range).
5. **Pre-registration framing.**
   - 22 of the 36 failures were foreseen before the runs.
   - Several predictions came from briefs whose recorded expectation was "May fail" or "uncertain", yet §3.9 says they were "expected" (B17).
   - Quote the 14 unforeseen failures alongside the 36, and disclose B18.
   - The "independent read" was made by another instance of the same model. Call it an internal check.
6. **Recommendations without a test.**
   - No pack model that carries a distribution of delivered fraction is tested.
   - "The local criterion for whether" is contradicted by the held-out f*(C1).
   - The Discussion cites the gas-layer bracket, but in that run the can reaches 1,886 to 1,924 °C (stage8_paper_numbers.json part_d_summary.layer_can_peak_C). That is not physical.
7. **Clarity.** The Results follow the stage chronology, coin many terms (whole-cell clock, far face, readings, brackets) and call Fransson et al. "the paper" (l.57, l.110, l.125). Organise them by question, add a nomenclature table and move the chronology to the supplement. Say that the "published two-cell study" (l.59, l.84) is the author's own Zenodo record, not peer reviewed.

## Minor points

1. §2.2, l.98: the level is set at 255.7 °C, the source's band edge, but the model's own ARC trigger is 199.8 °C. Justify the choice and show C1's sensitivity to it.
2. §2.2 and Limits: the 200 draws treat the three submodels as independent (D22). State this in the Limits.
3. Limits, l.272: the posterior-mean SEI decomposes at 25 °C, losing 80 % in a week (results/explore_sei_storage.json). The 108.4 °C onset and the lead both assume a fresh SEI.
4. §3.1 and Table 2: "published" thermal ranges. The O'Regan ends are the two-cell study's own combinations (README, Stage 3 design), and references_verified.json could not confirm the M50 or the values.
5. §3.2, l.160: "the largest body energy ... 33.2 kJ ... across the ... energy ... brackets" contradicts itself.
6. §2.8, l.130: Stage 9's fraction includes the two exploratory fmax values (D105 (1)). Say so.
7. §4.3, l.262: "Four reports", but three are listed.
8. §3.6, l.210: the short reading at f = 0.0375 never crosses, and at 0.040625 it crosses 56 s early (D111 (5)).
9. Figs. 3b and 5b are overplotted. In 5b every point sits between 0 and 20 s on a 0 to 400 s axis.
10. Table 1: add Fransson's failure category.

## B. Claims against files

1. **l.37, l.73, heading 3.2, l.278, title.**
   - Claim: "With the trigger's body energy ... conduction and radiation ignite neither neighbour under any kinetic draw."
   - Files: this holds at 33.2 kJ (v12_numbers.json all_runs.res_peak_hottest_C.max 226.7; stage6_numbers.json part_b_sets.draws.hot_reaches 0). With each test's own body energy, C1 is met at f = 0 in 8 tests (stage7_paper_numbers.json part_b.C1.central.predicted), and titles.md concedes this. Highlight 2 is affected too: C1 gets 11 of 16 right at f = 0.
   - Verdict: **Error (scope; the abstract is inconsistent).**
2. **Abstract, l.73, heading 3.3, Conclusions.**
   - Claim: the local criterion gets "never the time".
   - Files: under the 240 s and 360 s constant powers, C1 reproduces 1 and 2 of the nine measured times (stage9_paper_numbers.json part_b.240/360.summary.C1.n_reproduces). Fig. 7a plots one such reading.
   - Verdict: **Error (scope).**
3. **Abstract, l.73, heading 3.7, l.262, Conclusions.**
   - Claim: "nothing the model yields beats a constant probability".
   - Files: Stage 9's fraction gains 0.062 and 0.025 (stage10_paper_numbers.json part_c.held_out.f9.*.d_log), below the 0.1 margin and not significant. D109 (6) corrected this wording, and l.215 has it right.
   - Verdict: **Error.**
4. **Highlight 3.**
   - Claim: "A local criterion predicts which tests propagate."
   - Files: C1 has 2 false alarms and 3 misses. Held out, f*(C1) scores below the constant (−0.130 and −0.028; part_c.held_out.fC1).
   - Verdict: **Error.**
5. **Highlight 4.**
   - Claim: "The ejected energy ... varies 42- to 208-fold."
   - Files: 42.2 to 208.1 is the spread of the fraction (part_c.spread.C2_*.ratio). The same tests' delivered energies vary 22- to 64-fold (recomputed from stage9_fractions.csv and part_b).
   - Verdict: **Error (wrong quantity).**
6. **l.184.**
   - Claim: "the fraction the lumped neighbour's criterion needs varies 47.6-fold".
   - Files: 47.6 is PT_Exp1's far-face fmax divided by SP_Exp3's ft(C2). The between-test factor of f*(C2) itself is 73 (fstar_ratio).
   - Verdict: **Error (attribution).**
7. **l.37, l.73, l.257, l.278.**
   - Claim: draws "move each test's fraction at most fivefold".
   - Files: this covers 4 of the 16 tests and non-zero values only. ST_Exp2 moves from 0.01875 to 0 and SP_Exp3 from 0 to 0.00625 (stage11_paper_numbers.json thresholds.C2_*.range_all_nine). It also compares f* against a spread of ft and fmax (D116 (1)).
   - Verdict: **Error (scope).**
8. **Heading 3.3, abstract, Conclusions.**
   - Claim: the clock "rarely predicts whether".
   - Files: C2 is right in 9 of 16 tests at f = 0, the same as C3, C4, C5 and C7.
   - Verdict: **Judgement.** Write "rarely predicts propagation (2 of 9)".
9. **l.148.**
   - Claim: "Every history that self-heats first does so at 108.4 °C, by ... the fresh SEI."
   - Files: this holds at the posterior mean only. Over the draws the onset runs from 45.2 to 216.6 °C, and 37 draws start with the cathode (stage3_numbers.json headline_3a_extra, headline_3a.reactions).
   - Verdict: **Error (scope).**
10. **l.148, l.250.**
    - Claim: the band entry moves "by at most 0.01 s".
    - Files: 19.2443 s without the reaction heat against 19.2260 s with it, a shift of 0.018 s (stage2_checks.json no_source and step_halved.band_entry_s_base).
    - Verdict: **Error (minor).**
11. **l.278.**
    - Claim: the hottest node starts first "under every draw", and the kinetics "set both onsets".
    - Files: at 50 mW/K, 16 to 17 % of draws have no onset at all (nine_cases_3a.*G0.05.share_no_onset). The onset decomposition covers one case only. With the cans in contact, the thermal draws moved f*(C2) more than the kinetic draws (stage11_scorecard.json P5).
    - Verdict: **Error (scope).**
12. **l.160.**
    - Claim: "Only the Databank's total energy ... takes the hot spot to 255.7 °C".
    - Files: the lumped neighbour also crosses, in all 42 runs at 40 to 180 s (stage6_numbers.json part_b_sets.total.lumped_reaches).
    - Verdict: **Error (omission).**
13. **Heading 3.5.**
    - Claim: "four of the five non-propagated tests".
    - Files: seven tests did not propagate (m50_tests.csv). At the low contact only one of four overshoots (Major 3).
    - Verdict: **Error (wording) and Judgement.**
14. **l.198.**
    - Claim: "at 88.3° or facing ... (overshoot 13.8 to 159.9 K)".
    - Files: the side node gives 16.6 to 60.0 K and the facing node 65.2 to 159.9 K (part_b_summary.four_overshoot_K). The 13.8 K is the far face's value.
    - Verdict: **Error (wrong node).**
15. **Heading 3.6.**
    - Claim: "... and no long one".
    - Files: after 100 s, the short and long readings are 8.8 to 12.0 K and 8.9 to 9.1 K from the record. Over the last 60 s the long readings are closer (2.1 and 3.0 K against 4.4 and 4.8 K; part_a_segments_exploratory).
    - Verdict: **Judgement.** The short delivery's advantage lies only in 24 to 100 s.
16. **l.227.**
    - Claim: "not an artefact of the draws".
    - Files: E1's range is PT_Exp1's E*(C2) minus SP_Exp3's zero (thresholds.*.E_star_J).
    - Verdict: **Judgement.** The claim rests on one test.
17. **l.239.**
    - Claim: Stage 4, Stage 5, Stage 10 and Stage 11 P5 results "were expected".
    - Files: the recorded expectations are "May fail" (predictions_v11.md P4; predictions_v12.md P1, P6) and "uncertain" (predictions_stage10.md P2; predictions_stage11.md P5). The "tighter posterior of the SEI submodel" is in fact the anode-electrolyte central half, a parameter-space proxy (README, Stage 4).
    - Verdict: **Error.**
18. **l.79, l.140.**
    - Claim: "pushed before any of its runs".
    - Files: a full Stage 11 run preceded the predictions (D116 (3)), and the partial scoring at 178 of 216 records was seen (D118 (1)).
    - Verdict: **Error (scope).**
19. **l.140.**
    - Claim: every stage "halved the mesh spacing and the step limits".
    - Files: supplement Table S2 has no row for Stages 4, 10 or 11.
    - Verdict: **Error (scope).**
20. **l.250.**
    - Claim: the clock can "reproduce delays of 147 to 342 s" with 21.39 s.
    - Files: the reproduced delays run from 147 to 275 s. ST_Exp4, PT_Exp4 and ST_Exp3 stop at threshold, 73, 56 and 82 s early (stage9_fractions.csv).
    - Verdict: **Error.**
21. **l.267, l.278.**
    - Claim: the reproduced times "move by up to 56.3 s".
    - Files: under two draws, PP_Exp4 never crosses (clock.per_test.M50_PP_Exp4.no_crossing).
    - Verdict: **Error (omission).**

Every other number checked agrees with its file, including the counts 70, 36 and 22 (manuscript_numbers.json) and all of Table 3(b).

## C. Comparators

1. **Walker et al.** (abstract only): 20 to 30 % through the casing. ✓
2. **Finegan et al.** (full text): 2.6 against 0.21 kJ g⁻¹. ✓ The 19 to 31 % body share is computed from the ten Databank rows, and the paper does not print it (comparators.md §9). Say so.
3. **Coman et al.** (abstract only): 28 % of the electrical energy leaves with the effluent. ✓
4. **Feng et al. 2015** (abstract only), l.255: the "75 % or less" is one of four design targets for the short-circuit electrical energy, not a share of energy that leaves the cell (comparators.md §1). The manuscript places it under "Models have carried the energy that leaves as a fixed share". **Error.**
5. **Said et al.** (abstract only): the abstract says the 56.6 kJ "was computed", not measured. It also comes from the nitrogen tests, while the flaming heat comes from the air tests. **Minor error.**
6. **Torres-Castro et al.**: the numbers match references_verified.json, but the paper is missing from comparators.md. Saying the model "brackets" its 2.0 kJ compares a model delivery in a 21700 pair with energy absorbed in an LCO pouch stack. **Judgement.**
7. **Read, Jones and Marco**: M50, 100 % SOC, not connected, 2 to 5 s. These match comparators.md (full text, Table 4). But references_verified.json records only the abstract and flags exactly these details as unchecked. Reconcile the two records.
8. **Mishra and Jain** (full text): 40/90 s and 95/310 s. ✓ But l.53 cites them for "tabs and holders", which their model does not have.
9. **Hoelle et al.**: l.257 matches their abstract. ✓ The Methods use their Eq. 28 and 29 and Tables V and VI, which D82 records as read in full on 26 October from the author's copy, while both comparator records say "abstract only". Reconcile. Their layer forms by electrolyte vaporisation, so it is not something "the failing cell vents" (l.53).
10. **l.255, "The accepted literature agrees that most of a failing cell's energy leaves it"**: overstated. Coman's share points the other way on its own basis, the sources share no common basis (comparators.md point 2), and Read et al. report that nail tests release more through the casing (§10). **Judgement.**

Lamb, Kim and Fransson are cited correctly. ✓

## D. Form

- Abstract: 198 words. ✓ This leaves no room for the qualifiers in B.
- Highlights: 5, of 78 to 84 characters each. ✓ The content of highlights 2 to 4 needs fixing (B1, B4, B5).
- Keywords: 7. ✓
- Main text: 6,577 words. ✓ The captions add 1,046.
- Figures: 8. ✓
- References: the 21 cited entries are complete, with DOIs. ✓ Remaining fixes:
  - satte2026repo cites the all-versions DOI, which resolved to v1.4.0. Cite the v1.7.0 DOI.
  - lienhard2024heat needs a section, with its values confirmed in the 6th edition.
  - Feng's formula needs subscripts.
  - Table S4 names four works without citing them.
  - The comment in references.bib about item 24 is stale, and the supplement (l.35) says "D1 to D118" where the log runs to D120.
- Em dashes: none in main.tex, supplement.tex, the tables, highlights.txt, titles.md or either PDF. ✓
- R-squared: none. ✓
- "Pilot": only in the two-cell record's title. ✓
- Timelines: none. "The module study ... is the next question" (l.272) is borderline.
- AI declaration: the section title and the template sentence are correct. ✓ Three changes:
  - The [REASON] lists research tasks (code, runs, reading sources, the decisions log). Elsevier wants these in Methods, where §2.9 already names the model (Claude Opus 5.5) and the developer (Anthropic); add the interface and dates there.
  - "Draft ... figures": state that the figures are deterministic plots of the data, made without generative image tools.
  - CRediT credits the author with Software and Writing – original draft, while §2.9 assigns both to the model. Align them.
- Corresponding e-mail: missing (l.32).

## E. Stage 11 texts outside the manuscript (mismatches only)

1. README item 73, first bullet: "one test's threshold moves at most fivefold" drops the "non-zero" that README item 69, note item 2 and .zenodo.json keep. In the file, ST_Exp2 moves from 0.01875 to 0 and SP_Exp3 from 0 to 0.00625 (thresholds.C2_*.range_all_nine).
2. Note item 1 and .zenodo.json ("in four tests"; limits: "in four of the sixteen tests"): Part C ran five tests and Part D nine (far_face.per_test, clock.per_test).
3. README Stage 11 introduction: "four of the five non-propagated tests". Seven did not propagate.
4. Everything else agrees with stage11_paper_numbers.json and stage11_scorecard.json: README items 68 to 72, the scorecard, the Figure 10 caption (two panels, matching the figure), note items 2 to 5 and the Zenodo Stage 11 sentences.

## Must-fix before submission

1. Scope the claims in the abstract, highlights 2 to 4, the Introduction's answers, headings 3.2, 3.3, 3.5 and 3.7 and the Conclusions (B1 to B8, B11, B13). Restore D109 (6)'s "by the registered margin or significantly".
2. Define the 42- to 208-fold spread: its quantity, its tests, its zeros and the tests at its ends. Give delivered energies beside it, and correct highlight 4.
3. Discuss E_b and E_e against the Databank values (13 and 14 tests exceed them) and the "cell movement" tests at the ends of the spread, with a sensitivity case.
4. Correct B6, B9, B10, B12, B14, B17, B20, B21, C4 and C5.
5. Report the 14 unforeseen failures and disclose B18 and B19. Restructure the AI declaration and CRediT, and cite the v1.7.0 DOI.
