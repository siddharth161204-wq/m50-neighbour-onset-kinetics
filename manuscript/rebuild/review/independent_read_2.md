# The independent read of the rebuilt manuscript, read 2 (20 to 21 November 2026)

A separate agent, new and with no sight of the work, of read 1 or of the editor's reads, read only the built manuscript (30 pages) and supplement (30 pages) as PDFs, as revised after read 1, with no other file, command or web access, and listed untraceable numbers (A), archive-dependent sentences (B), overclaims (C) and other first-reading objections (D), under the same instructions as read 1. The read stopped once on a usage limit and was resumed with the same two files. Its report, verbatim, follows; the changes made after it are in DECISIONS.md D186.

---

I read both PDFs in full as page images (manuscript pp. 1–30, supplement pp. 1–30) and re-checked supplement pp. 11–13 and 23. I opened nothing else. "ms" means the manuscript and "SM" the supplement; page numbers are the printed ones, which match the PDF pages.

Verdict: Not ready. The worst problems are:
- Table S7 shows ST-Exp3 reproduced at 177.0 s by a 240 s delivery (13.84 kJ). That contradicts "bar one test" and the 4.1–8.1 kJ band (C5).
- The paper's own skin model contradicts "surface conduction sets the hot-spot threshold" (C2).
- Table 3 contradicts the text on the holder and on the discharge bound (D2, D3).
- Six numbers have no traceable origin: 5.04 kJ, 6.2 kJ, 220.5 °C, 110.8 kJ, 2,667 J and the two Spearman ρ values.

A. Untraceable numbers

A1. ms p.13 (also p.25): "with enough of that reaction's heat (2,667 J in all) left to carry it to 255.7 °C". Neither document derives it: which enthalpy, which reactant mass, or how it is scaled from the 720 g reference cell. It is in no table.

A2. ms p.13: "At that point the low-temperature cathode reaction gives 73.3 % of the reaction heat under the posterior mean." The share depends on the species state at Tign, which is not described, and it is in no table. Borderline.

A3. ms p.14: "With 5.04 kJ over 21.4 s, the upper end of an earlier, wider bracket on the lumped threshold". That bracket appears in neither document; Table S3 gives (4.66, 4.85]. The value recurs as 5,045 J (SM p.14, step 15 P7) and on SM p.4. It equals 0.040625 × PT-Exp4's ejected energy, so it looks like a bisection point, but neither document says so.

A4. ms p.14: "the thresholds mostly restate the trigger's energy (Spearman's ρ = −0.92 for the local and −0.97 for the lumped)". The text does not say what was ranked. Recomputing from Table S3 bracket midpoints against Table 1 E_b gives about −0.91 and −0.95; using fractions of E_e gives about −0.93 and −0.98. Neither stated value can be reproduced.

A5. ms p.16 (also Fig. 5 caption p.18 and §3.6 p.21): "With 6.2 kJ at constant power over 240 s, a run of an earlier step". The paper never says why 6.2 kJ (6,209 J in SM p.14, step 15 P8). It matches nothing in Table S7: PT-Exp4 at 240 s needs 3.49 kJ (lumped) and 6.77 kJ (resolved). It equals 5 % of PT-Exp4's E_e, but that is not stated.

A6. ms p.16: "while the reactive cross-section's registered value, no runaway with the mean at 220.5 °C, held". No such prediction is in Table S2: step 15 lists only P1–P8, and P8 is the 3D run. 220.5 °C appears nowhere else.

A7. ms p.19 (Table 3, holder row): "bounded as the jet and melt are, 247.3 kJ, the most measured for this cell in all (110.8 kJ)". 110.8 kJ has no citation. It is also missing from Table S5, which SM p.17 says holds every input of the bounds.

A8. SM p.8 (Table S2, step 5 P4): "lies between 0.2 and 0.8 C/s (measured about 0.4)". This measured value has no source. The only published neighbour history was read in step 10, after step 5 was registered. Borderline, since it sits inside a prediction.

A9. SM p.2 (S1): "Onset: the time a node's reaction self-heating first reaches 0.15 K min−1." No source or reason is given, and this onset also ranks the step 11 draws. Borderline.

A10. SM p.3 (S1): "its electrical bracket, 5 to 20 % of the neighbour's stored electrical energy released inside it". No source or reason. Borderline.

A11. SM p.3 (S1): "the trigger released 33.2 or 21.5 kJ over 10 or 30 s: the earlier two-cell study's trigger [4]". The 21.5 kJ, the 2 mm gap and the 100–500 mW/K busbar trace only to the author's archived dataset. Borderline.

A12. SM p.11 (step 9 P7): "rescales every time- and peak-matching fraction by 0.75 to 1.40". S1 names the smallest and largest ejected-to-body ratios but gives neither value, so this range cannot be checked. Borderline, since it sits inside a prediction.

A13. SM p.20 (S7): "over its mean heating rate in the figure (37.70 and 23.97 K s−1), which gives 17.53 and 25.24 s". The interval over which the mean rate was read is not stated. The 21.39 s release used in every run rests on it. Borderline.

A14. SM p.8 (step 6 P3): "the lumped neighbour's peak rises above its step 5 central value (159 to 162 °C)". Step 5's results are tabulated nowhere. Borderline.

B. Archive-dependent sentences

B1. ms p.14: "the upper end of an earlier, wider bracket on the lumped threshold". That search exists only in the archive (see A3).

B2. ms p.16: "a run of an earlier step carried here to 900 s". The Fig. 5 caption (p.18) repeats it: "a run of an earlier step, was carried to 900 s". Which step, and why that delivery, is only in the archive.

B3. ms p.16: "the reactive cross-section's registered value, no runaway with the mean at 220.5 °C, held". This registration is only in the archive's predictions files.

B4. ms p.18: "against the 151 three-dimensional runs of the sixteen tests that had been carried past the hottest point's crossing". Neither document lists this run set: its steps, tests, energies, shapes, or which twelve stop at 332 s. Fig. 7's points cannot be matched to runs.

B5. ms p.25: "Every reduced number scored against a three-dimensional run was registered before that run." Most of these registrations, for example those for the 151 runs, are not in Table S2. Only the archive can confirm the claim.

B6. ms p.10: "Registered numbers and verdicts were recomputed twice, by separate code and from the run records (Supplementary Table S4)." Table S4 shows energy residuals and mesh checks, not this recomputation. SM p.17 adds "by a check that had not drafted them" without saying what the check is.

B7. ms p.10: "eighteen of them in four steps on an earlier geometry, not reported here". The step 1–4 rows of Table S2 (busbar conductances, onsets, "onset lead") can only be judged against the archived study. The same holds for Table S1's step 1 (SM p.5): "along the archived histories of the earlier two-cell study".

B8. SM p.6 (step 1 P2): "reaches 0.15 K/min in exactly 10 of 42 cases". The 42 cases are defined nowhere.

B9. SM p.7 (step 4 P5, expectation): "Held, if the anode-electrolyte file leads at 500 mW/K." The word "file" is undefined.

B10. SM p.7 (step 5 P1, expectation): "May fail: by the estimates above the hot spot stays below 255.7 °C". Step 5 P6 (SM p.8) also says "the estimates above fall short". Those estimates are in the predictions file, not the supplement.

B11. SM p.8 (step 6 P5, and P6 on SM p.9): "In the case matched to the tests in duration and energy". The durations and energies of this case are never given.

B12. SM p.9 (step 7 P1, expectation): "at the median peak, only at the high contact". "Median peak" is undefined.

B13. SM p.10 (step 8 P5): "delivered heat moves the predicted count but not past the cap the outcomes set". "The cap" is undefined.

B14. SM p.12 (step 10 P5, expectation): "If the facing node reads within 4.9 K of the line node". "Line node" is not defined in S1.

B15. SM p.12 (step 11 P3): "Under each of the eight draws, the range of the C2 threshold energy". "Eight draws" is undefined. S1 names four kinetic draws but never says which four thermal draws were used.

B16. SM p.14 (step 14 P1, expectation): "the bullet says likely; the predictions file's analysis, written before any bound". "The bullet" is undefined.

B17. ms p.5 and Table 2 (p.8): "The sector is that of the earlier two-cell study [22]". The reasons for the 45° sector and for the inherited "assumed" values exist only in that archived study. Borderline.

B18. ms p.11: "at the high contact this rests in ten tests on the reactive cross-section of Section 2.5 alone". The paper does not say which ten tests these are, or which six had 3D runs at that contact.

C. Overclaims

C1. ms p.1 (title): "a lumped neighbour needs less heat than a resolved one after strong triggers". This is stated generally. The 3D model brackets both readings in only two strong-trigger tests, with one cell type, one rig and kinetics from another chemistry. In PT-Exp3 the two brackets overlap (C4).

C2. ms p.1: "Up to 120 s, surface conduction sets the hot-spot threshold, within 3 % of a conduction model." p.13 says the same: "set by conduction into the cell's surface layer".
- The paper's own surface-layer (skin) model lies about 11–27 % below the resolved brackets from 21.4 to 120 s (Table S8: 3.90 vs 4.36–4.53 kJ; 8.39 vs 11.21–11.55 kJ).
- Appendix B itself says the skin model "falls below" as heat spreads along the layers. Only the full cross-section model matches.
- The claim rests on three tests, and on PT-Exp1 alone at 120 s.

C3. ms p.1 (also p.13): "The lumped threshold follows an energy balance to 218.5 °C, where reaction heat outruns losses."
- The registered slope test failed: 393–456 J/kJ against a predicted 150–300, which the paper says is "not explained here".
- The two-body check was run only at the low and high contacts, never at the central contact where every headline lumped threshold sits.
- Nine of its 32 agreements are zero against zero (Table S10).

C4. ms pp.11–12: "above the lumped threshold in the fourteen with strong triggers". For PT-Exp3 the cross-section bracket (8.56, 8.62] overlaps the lumped bracket (7.36, 8.58] in Table S3, so the order is not established in that test.

C5. ms p.16: "so no delivered energy reproduces that test's time". The same claim appears in the Fig. 6 caption (p.20, "ST-Exp3, whose time it cannot reproduce, left out"), in the abstract ("bar one test") and in Conclusion 5 (p.24, "outside ST-Exp3").
- Table S7 (SM p.23) contradicts it. With the 240 s constant power, the resolved neighbour runs away at 177.0 s, the measured time, with 13.84 kJ delivered by then (lumped: 12.26 kJ), and the entry is not marked t.
- With that case included, the resolved needs span 4.1–13.8 kJ, not 4.1–8.1, and the lumped needs 0.2–12.3 kJ.
- For the t cases, "no energy reproduces" rests on a grid of 0.5 % of E_e. In PP-Exp4, for example, 6.05 kJ runs away at 216.9 s while the threshold is 5.58–5.62 kJ. Energies in between, where runaway can come later, were never sampled.

C6. ms p.14: "whatever the delivery's shape", and the Fig. 6 caption (p.20): "under any shape". Both generalise from four shapes.

C7. ms p.16: "so 36.8 K is the least difference those probes give", and p.22: "its far face's jump begins 37 K hotter than the measured surface's". Both rest on a reading the paper itself calls post hoc (that the far face is the coolest probe), and the §4.2 verdict "fits neither cleanly" leans on it. The far-face comparison itself was registered (step 15 P5).

C8. ms p.22: "a lumped cell cannot stand in for a resolved one in a module model without a correction". This is a rule for all module models, drawn from two strong-trigger tests and one weak-trigger test searched in 3D, on one cell at one contact. It also treats the resolved reading as the reference, while §4.3 says no measurement yet decides between the readings.

C9. ms p.22: "the next pouch cell absorbed 2.0 kJ on average before it failed [12], inside the lumped range found here". Readers will take this as support for the lumped model, though it comes from a different cell, format and stack. Borderline.

C10. ms p.21: "so a pack model that ignites a neighbour at one delivered share will reproduce some tests and not others". p.22 adds: "A pack model would do better to carry the delivered heat as a distribution". These are prescriptions for pack models drawn from one cell's lumped needs, with no pack model run (the paper acknowledges this). Borderline.

C11. ms p.1: "A facing-side heat flux measurement would decide." p.22: "One measurement would decide between the readings".
- The abstract drops the condition "if the model's other inputs stand".
- With the pulse, the two readings differ by only 1.7–4.3 kJ per test (PP-Exp2: 5.96 vs 7.65 kJ). A measurement decides only if its uncertainty, integrated over half a can during venting, is well below that.

C12. ms p.11: "the resolved neighbour as a whole runs away in no test at any contact". At the high contact this rests, for ten tests, on a reduced model checked only at the central contact; the paper says so in parentheses. Borderline.

C13. ms p.13: "After strong triggers the resolved threshold is higher, and part of the reason is what each neighbour takes in." This is a causal attribution, yet §4.2 says "these runs do not separate" it from the one-temperature construction. Borderline.

C14. ms p.21: "in PT-Exp4's run of 6.2 kJ over 240 s, a parallel test whose tabs it lacks". This attributes the largest miss (20.7 K) to the missing tabs without checking it. Borderline.

C15. ms p.5: "its calorimetry curves reproduce the source's", and SM p.2: "which the posterior-mean kinetics reproduce". Neither document shows a figure or a metric for this.

C16. ms p.23 (Conclusion 1, also the abstract): "conduction and radiation leave the neighbour's hottest point at least 29 K short of 255.7 °C". It is stated as a finding about the cells rather than "in this model". "At least" assumes a textbook flat-contact value (3,700 W m−2 K−1) bounds a line contact, and uses a runaway level taken from another chemistry. Borderline.

C17. ms p.12 (also pp.1, 22, 23): "1.49 and 1.72 times the lumped thresholds of 4.75 and 3.97 kJ". The brackets do not support this precision. PP-Exp2's lumped bracket (3.18, 4.77] allows ratios of 1.36–2.26. PT-Exp4's allows 1.38–1.59, and ST-Exp3's allows 0.81–0.90.

C18. ms p.1: "it needs 4.1 to 8.1 kJ, the lumped neighbour 0.2 to 6.0 kJ, within published bounds". The bounds are upper bounds with every unknown fraction set to 1 and every lower bound zero. "Within" is therefore guaranteed rather than tested; §3.5 itself says the bounds "do not choose". Borderline.

C19. ms p.14 (also the abstract and Conclusion 3): "That shift lies well beyond the 6.1 K span of the posterior's ignition temperatures". This compares a uniform rate-law shift on the resolved neighbour with the spread of the lumped neighbour's ignition temperature, which is a different quantity. The direct check used only four kinetic draws. Borderline.

C20. ms p.1: "At the central contact a reactive cross-section reproduced all 151 three-dimensional outcomes." Most of the 151 runs are far from threshold. Near threshold, its SP-Exp3 value is 9.1 % below the 3D bracket's midpoint, runaway times differ by up to 34.5 s, and twelve runs stop at 332 s. Borderline.

D. Other first-reading objections

D1. The ST-Exp3 contradiction in C5, between Table S7 on one side and §3.4, Fig. 6, the abstract and Conclusion 5 on the other, is the most damaging internal inconsistency.

D2. Holder path. p.16 says it is bounded "not at all" and p.18 says it is "not determinable". Table 3 (p.19) says "bounded as the jet and melt are, 247.3 kJ", yet shows "–" in both columns.

D3. Neighbour's discharge. §2.6 (p.10) bounds it "within 21.4 s by its open-circuit voltage across its resistance", which gives 15.6 kJ. Table 3 and Fig. 6 list 65.5 kJ in the 21.4 s column, and SM p.18 confirms the table uses the whole stored energy.

D4. For the 6.2 kJ run, p.21 says "at most 20.7 K lower". p.16 gives 241.4 °C for the 3D model against 220.5 °C for the registered cross-section value, which is 20.9 K.

D5. Fig. 2 (p.12): squares and triangles sit at the top of their brackets and the 3D diamonds at the midpoint, and the caption doesn't say which. §2.4 (p.9) says "its midpoint is quoted". p.12's "runs away above 7.06 kJ" quotes a midpoint as if a run had been made at it.

D6. Held-out test (p.11, Table S9).
- The "need" predictor is defined by the outcome it predicts ("the lumped neighbour's where a test propagated, the far face's where not"), which is leakage.
- The logistic fit is not described. The baseline score of −0.718 implies p ≈ 0.61, not the 5/8 training frequency (which gives −0.725), so some unreported regularisation was used.

D7. p.11: "Held to 33.2 kJ, those eight tests ignite neither neighbour". With E_b fixed, the tests within a connection have identical inputs, so this is two configurations per contact and each quoted range is just two values (Table S4 lists 10 runs for step 12). Also, the 5,248-run maximum (with 10 or 30 s releases) and the 21.39 s maximum are both exactly 226.7 °C, which is worth a check.

D8. Table S10's two-body check covers only the low and high contacts. Nine of its 32 cases are 0 vs 0. The low-contact differences are systematic: +0.25 to +0.48 kJ after strong triggers, and −0.28 and −0.44 kJ after weak ones.

D9. p.10: "56 held and 42 failed". The tally includes step 12 P1–P4, all "held", which the files had already recorded as fixed by earlier records. It also includes step 10 P3 and step 11 P4, recorded as failing whatever the runs gave. The main text doesn't say this.

D10. Missing method details.
- Convergence (p.10, Table S4) is reported for the peak rise and one runaway time, but not for the thresholds the paper rests on.
- The cross-section model's discretisation is not given.
- The ranges of the 30 thermal draws are not given (SM p.3).
- The ray-tracing set-up behind the 0.0038 share is not given (SM p.17).
- Why some runs stop at 332 s is not explained (pp.18, 21).

D11. The "Declaration of generative AI ..." heading (p.26) has no text under it. The CRediT statement (p.25) omits Software, Formal analysis, Data curation, Visualization and Writing – original draft, although there is a single author.

D12. Unclear references.
- p.16: "a post hoc reading of the same run" follows the 6.2 kJ run, which has no jump; it must mean the 7.42 kJ run.
- p.14: "In PT-Exp4 the gap is larger than the kinetic uncertainty (Fig. 3d)". The preceding gap is in kJ, while Fig. 3d is in K.

D13. Results and figures.
- "with the jump at 240.4 °C" (p.22) appears only in the Discussion, in no result or figure.
- Fig. 5 draws a 6.7 kJ run the text never discusses, but omits the 4.66 kJ run it does discuss.
- Fig. 5a's model curves are keyed only in the legend of 5b.
- Fig. 3d cannot be read without the text: it needs it to explain why 5.04 kJ and what the 17.5–20 K band is.

D14. Inputs.
- Table 2 (p.8) credits "255.7 °C, within 900 s" to [20], but the 900 s window looks like the study's own choice.
- Using another chemistry's internal-short level as the runaway criterion is not argued.
- The SEI amount "0.15" has no unit.
- The 65 g cell mass is "assumed" although the manufacturer's specification [29] is cited.
- The can conductivity and the stainless-steel contact values have no source for the can's material.

D15. p.3: "626 and 808 °C, which may not be the neighbour's surface" gives no reason. The second letter of the test names PT/PP and ST/SP is never explained.

D16. Supplement presentation.
- Table S2 has raw underscores ("E_b", "E_e", "f_max", "f_t" on SM pp.11 and 13), and "255.7 C" and "C/s" on SM p.8.
- SM p.1 claims "every label is defined in Section S1", which B8–B16 contradict.
- Step 5 P5's "measured means differ by 8 s" is 8.7 s by Table 1.
- The abstract's compressed phrasing ("a cell's reaction rates over 17.5 K hotter", "bar one test") is hard to follow without the body.

Not ready
