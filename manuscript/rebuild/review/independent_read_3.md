# The independent read of the rebuilt manuscript, read 3 (21 November 2026)

A separate agent, new and with no sight of the work, of reads 1 and 2 or of the editor's reads, read only the built manuscript (32 pages) and supplement (32 pages) as PDFs, as built at commit 46590c7, after read 2's fixes and before the changes that followed the fifth editor's read (commit fcd3a20, which changed the abstract and the letters on the kinetics, the shift and the published record, dropped the abstract's sentence on the ignition temperature and stated the kinetics' failed calorimetry check), with no other file, command or web access, and listed untraceable numbers (A), archive-dependent sentences (B), overclaims (C) and other first-reading objections (D), under the instructions of read 2, changed only in the page counts. Its report, verbatim, follows; the changes made after it are in DECISIONS.md D186 (4).

---

Independent read of the two PDFs: manuscript pp. 1–32 and supplement pp. 1–32, figures included. I opened no other file. "M" means a manuscript page and "S" a supplement page.

Verdict: Not ready. Lists A, B and C all have entries.

**A. Untraceable numbers**

1. M p.17 (also p.24 and the Fig. 5 legend): "A 5.04 kJ pulse followed by a constant 12.5 W brings the resolved runaway to 255.9 s". No source, rationale or search is given for 12.5 W. Table 2 lists this delivery shape but gives no power.
2. M p.9: "emulating the source's calorimetry of its own cell, it gives an exotherm onset of 179.3 °C". The emulation (which cell, which heating protocol, which onset rule) is not described anywhere.
3. M p.9: "inside the two-standard-deviation band of the source's main cluster, 169.0 to 198.0 °C". There is no locator, and the paper does not say whether this band is quoted from [20] or computed from its posterior.
4. S p.4 (S1, used in Table S2 step 8 P5): "the 12 of the 16 tests that the prediction allows a criterion to score". Why the cap is 12 is never explained.
5. S p.6 (S2): "with the body energy at the smallest and the median of the Databank's ten nail tests of this cell". These two energies appear nowhere; only the largest, 33.2 kJ, is given.
6. S p.3 (S1): "the trigger released 33.2 or 21.5 kJ over 10 or 30 s ... values that study set and archived [5]". The 21.5 kJ, the 2 mm gap and the 100–500 mW/K busbars have no primary source. Neither do the 10 and 30 s releases behind step 5 (M p.11). Their only origin is the author's own archive. Borderline.
7. S p.7 (Table S2, steps 1–2): "Central estimate: 4.2 s against 29 s for the 10 s release (86 % earlier)". The same applies to "Central estimate: 100 mW/K", "about one in three" and "about even odds". None is labelled as the brief's or the study's, and no basis is given.
8. S pp.7–8 (Table S2, steps 3–4): "Brief's central estimate: 99 %". The same applies to "8 s and 40 s", "70 % at 100 mW/K", "3", "2", "below 10 %" and "65 %".
   - S1 (S p.1) says only that a brief's estimate is "the outcome the plan expected". Unlike the study's expectations, it gives no basis.
   - The same gap affects brief notes that quote unreported earlier runs: step 9 P1 "crosses at 11.9 to 18.5 s" and P2 "ST-Exp3's lies at 61.4 s" (S p.11).
9. S p.9 (Table S2, step 6 P6): "reaches 255.7 °C in between 10 and 70 % of them (central 35 %)". The origin of the 35 % is not stated.

**B. Archive-dependent sentences**

1. M p.8 (Table 2 caption): "The two-cell geometry and its solver are those of an earlier, archived study by the author [22]". The solver details, and the reason behind every "assumed" value, exist only in that archive.
2. M p.5: "The sector is that of the earlier two-cell study [22]". The 45° sector is justified only by the archived study. Using the paper's own numbers, the stated wedge argument (k_air/δ below 10 W m⁻² K⁻¹) already holds from about 31°.
3. M p.10: "(eighteen of them in four steps on the earlier two-cell study's geometry [22], not reported here)". These predictions count in the 98/56/42 totals but concern an archived, unreported configuration. Borderline.
4. M p.10: "committed to a public repository and pushed, and the files were not changed afterwards [27]". This can only be checked in the repository; the documents give dates but no commits or hashes. Borderline.
5. M p.11: "recomputed from the run records by separate code and read again by an independent check". The code and the check exist only in the archive.
6. M p.17: "Carried to 900 s, a run of step 10 that the archive held to 332 s". This uses a step label and the archive's state. The main text never says why 332 s; only S13 explains it (measured time plus 60 s).
7. M p.17: "the reactive cross-section's value registered with it, no runaway with the mean peaking at 220.5 °C, held". This registered value is not in Table S2, which lists only P1–P8 for step 15, so it can only be checked in the archive. "P8" is used as a bare pointer.
8. M p.19 (Fig. 5 caption): "that of 6.2 kJ over 240 s, a run of step 10, was carried to 900 s". A step label appears in a caption.
9. M p.20: "against the 151 three-dimensional runs of the sixteen tests in the archive", and "the archive's 241.2 °C at 332 s". The run set is simply whatever the archive held. S p.28 confirms this: "They are every archived run carried past the hottest point's crossing".
10. S p.3: "Its 42 cases are its archived histories with two busbar strips". The 42 cannot be rebuilt from the stated factors (2 energies × 2 releases would need 10.5 conductances), and "two busbar strips" is undefined.
11. S p.3 (used in step 11 P6): "and its six, the tests whose measured time the posterior mean reproduced within 10 s in step 9". The six tests are never named.
12. S p.3: "Step 11's four thermal draws are those with the smallest and largest conductivity across the layers". The draws' values are not given. Borderline.
13. S p.15 (step 14 P1, P2): "The upper bounds of the cap-end paths that are determinable sum to less than 5.96 kJ". "Cap-end vent" and "cap-end paths" are not defined in S1 or Table 3.
14. S p.10 and p.11 (step 7 P6, step 8 P6): "Likely; a check on the mapping, not a result." "The mapping" is undefined.
15. S p.8 (step 4 P2): "The three submodels' main-effect shares of the onset lead's variance". The term is undefined. Borderline.
16. Two registry entries rely on step-6, step-8 and step-9 runs that are reported nowhere in either document:
    - S p.14 (step 12 P1–P4): "the predictions file records it as fixed by step 6's records".
    - S p.10 (step 7 P1): "step 6 ignited the hot spot only at the Databank's total energy".
17. S p.14 (step 12 P3): "the delivered energies E* across the nine propagated tests still span at least tenfold". S1 defines E* as a threshold, but here it appears to mean time-matching energies. Borderline.
18. S p.4: "the scoring was once run on 178 of its 216 records to test a figure's script". The records and the script are archive-only. Borderline.
19. S p.1: "The plan of a step, its brief, was written by the author before the step's code and predictions". The briefs exist only in the archive, so no "Brief's expectation" can be checked. Borderline.

**C. Overclaims**

1. M p.1 (title): "a lumped neighbour needs less heat than a resolved one after strong triggers". This is a general statement. The 3D model searched only three strong-trigger tests (two bracketed), in one cell, one rig, with borrowed kinetics. The rest comes from a reduced model checked post hoc.
2. M p.1: "Heat calibrated with one model thus needs a trigger-dependent correction for the other." This generalises from two strong-trigger tests and one weak-trigger 3D test (ST-Exp3), and drops the body's "in this model". The same applies at p.24: "cannot be carried to the other without a correction whose sign depends on the trigger".
3. M p.1: "Matching the two thresholds in one test needs rates over 17.5 K hotter, beyond the kinetics' 6.1 K span."
   - It compares a shift of the rate laws with a span of ignition temperatures, which p.15 itself calls "a different measure".
   - The link between them is asserted, not computed (p.15: "since a shift of the rate laws moves the ignition temperature by about as much").
4. M p.15: "In PT-Exp4 the kinetic uncertainty does not close the gap between the two thresholds (Fig. 3d)."
   - The test used four of 200 draws, applied to the resolved model only, at one energy.
   - The lumped threshold under the same draws is not shown. Table S2 step 11 P1 failed: under some draw the lumped threshold left a factor of two of its posterior-mean value.
5. M p.1, p.24, p.26 (Conclusion 4): "a two-dimensional reactive cross-section reproduced all 151 three-dimensional outcomes".
   - p.20 says the comparison "was made after those runs".
   - 82 of the 151 are exploratory-test runs at 15–135 kJ, far above any threshold.
   - In the one near-threshold run with no runaway, the cross-section's mean peaked 20.7 K lower than the 3D model's.
   - In SP-Exp3 its threshold lay outside the 3D bracket.
   - Despite this, 12 of the 16 resolved thresholds, every resolved need and ten high-contact outcomes rest on it (p.25).
6. M p.1: "The lumped cell ignites at 218.5 °C, where reaction heat outruns losses." This holds only with the trigger at the neighbour's own temperature. With the trigger at 25 °C it is 230.4 °C (p.14).
7. M p.1: "the final rise starts 37 K cooler than on the resolved model's far side". This rests on one run (7.42 kJ) and one probe. The thermocouple angle is unknown, the model's jump-onset criterion is undefined, and PT-Exp4's trigger ruptured its sidewall. Borderline.
8. M p.24: "The measured history fits neither cleanly." and "its far face's jump begins 37 K hotter than the measured surface's". Comparing with "the measured surface" assumes where the thermocouple was. Only the post hoc probe reading (p.17, "from which nothing here is concluded") would make this independent of the angle.
9. M p.1, p.24, p.26: "a facing-side heat flux measurement would, if the other inputs stand", and "One measurement would decide between the readings, and four would narrow the model's inputs."
   - That the measurement would decide is not shown.
   - It would need accuracy well within 1.7–4.3 kJ and knowledge of the delivery's shape.
   - It also depends on inputs the paper itself calls uncertain: the textbook contact, triggers fitted above calorimetry, and another anode chemistry.
10. M p.5: "the level lies above the ignition temperature of Section 3.3, past which a whole neighbour runs away". The ignition temperature is computed for the lumped neighbour only. The two-body model itself also needs enough cathode-reaction heat left.
11. M p.24: "reaches its runaway with less delivered heat partly because it takes in more through the same contact". This is a causal claim, yet the same sentence says the runs "do not separate" this cause from the other difference. The evidence is three no-delivery runs.
12. M p.23: "so a pack model that ignites a neighbour at one delivered share would reproduce some tests and not others". It sets lumped needs against far-face (resolved-model) needs. The same test is never applied to the resolved reading, which implicitly favours the resolved model.
13. M p.12: "unless its reactions run far faster than the kinetics' posterior allows (Section 3.3)". Section 3.3's 17.5 K result is for PT-Exp4 with 5.04 kJ delivered, not for this no-delivery case. Borderline.
14. M p.11: "the resolved neighbour as a whole runs away in no test at any contact". No low-contact runs are reported. Borderline.
15. M p.20: "what the ejecta can release in this rig is at most 225.8 kJ". The 136.5 kJ in it was measured on another cell, which S p.18 says "sets no value for this one". Borderline.
16. M p.14: "The lumped threshold is consistent with an energy balance to an ignition temperature (Fig. 3b,c)." The registered slope test of that balance failed (150–300 registered, 393–456 J per kJ observed). Borderline.
17. M p.23: "Either way the needed energies are a small part of what the ejecta carry". The figure is up to 25.4 % of the Databank median, and only resolved-model numbers are cited. Borderline.
18. M p.17: "The one published history of a neighbour that propagated sits between the two (Fig. 5)." The claim is vague. Borderline.
19. M p.1: "conduction and radiation leave the neighbour at least 29 K short". This rests on a textbook range for flat plates and on assumed tab conductances, and the abstract drops "at every contact conductance considered". Borderline.
20. M p.15: "so that much of what they carry is the trigger's energy". This is an interpretation that was not tested. Borderline.

**D. Other first-reading objections**

1. **Cross-reference:** M p.11 cites the checks as "(Supplementary Section S4)", but they are in S5.
2. **Empty declaration:** on M p.28 the generative-AI declaration heading has no text under it.
3. **CRediT:** M p.27 omits Writing – original draft, Software, Formal analysis, Data curation and Visualization for a sole author.
4. **PT-Exp4's sidewall rupture:**
   - PT-Exp4, the only history the paper compares against, is category 4 ("sidewall rupture of the trigger", M p.7).
   - S p.20 excludes the Read, Jones and Marco dataset for exactly that path.
   - Limits says the model has no sidewall rupture, and PT-Exp4's rupture is never mentioned.
5. **"Different thresholds in every test":** M p.12 says this, but PP-Exp1 and SP-Exp3 have local and lumped thresholds both zero (Table S3).
6. **"Resolved threshold" changes meaning:** in Sections 2.2 and 3.2 it is the mean criterion; in Section 3.3 and Fig. 3a (M p.12, p.14) it is the local threshold.
7. **Table S7 "Resolved" column:**
   - The values equal the energy delivered by each run's own runaway time, not by the measured time as the caption and M p.9 define.
   - Example, PT-Exp4 at 360 s: 9.39 × 278.9/360 ≈ 7.28, but by 272 s only 7.09 had been delivered.
   - Example, PP-Exp2 at 360 s: 8.12, against 7.97 by 147 s.
8. **Fig. 5b legend:** it appears to key 5.0 kJ to green and 7.4 kJ to blue. The data fit the reverse: the green curve runs away near 182 s and carries the 234.1 °C/173 s mark, while the blue curve peaks near 190 °C and ends at 332 s. Worth checking.
9. **Undefined onset:** the model far face's "jump begins" (M p.15, p.17) has no stated criterion, yet the abstract's 37 K depends on it.
10. **3D brackets by construction:**
    - The 3D searches start 5 % either side of the cross-section value and in three of four tests stop there (M p.20, S p.16).
    - So the 3D midpoints and the ratios 1.49, 1.72 and 0.85 are the cross-section's values by construction.
    - Likewise, the "within 3 %" agreement in Section 3.3 follows from searches that start at the model value with a 3 % step (S p.25).
11. **Undefined term:** "the test's ejected energy" (M p.9, p.15, p.17) is defined only in S1 (Ee = 3.105 Eb).
12. **Notation and radiation:**
    - The symbol R means the radius in Eq. (3), where it is undefined, and the gas constant in Section 2.3. The radius is also written a.
    - Eq. (1)'s ε²σFAℓ radiation exchange between grey surfaces is not justified.
13. **PT-Exp4 comparison window:** the model starts at 25 °C but the record at 32.2 °C. The paper does not say whether the RMS "over 0 to 271.5 s" excludes that offset or the opening 8.5 s spike.
14. **Thermocouple-angle logic:** the far face is the coolest probe (M p.17), so no other angle could remove the no-delivery overshoot or the 37 K excess. M p.15 and p.24 nevertheless say the angle bears on whether these "are real".
15. **Contradiction on local runaway:** M p.24 says "A runaway that starts from part of the cell, which these models do not represent", but M p.14 reports "a runaway inside the cell".
16. **Registry gaps:**
    - The cross-section value said to be "registered ... held" (M p.17) is absent from Tables S1 and S2.
    - Step 15 P6 (5–25 W) is marked held, but no reported run supports its lower bound.
17. **Step 11 results not reported:** the failures of P1, P4 and P5 (kinetic and thermal draws) are not discussed in the main text, and thermal-property uncertainty is missing from Limits.
18. **Held-out predictor:** the "need" predictor is defined from the outcome it predicts, which is circular, and each fit uses n = 8.
19. **Mixed comparison:** non-propagated "needs" are far-face (resolved-model) quantities under both readings, so the "overlap" in M p.15 and p.23 compares quantities from different models.
20. **Abstract–body inconsistencies:**
    - The abstract's "needs about 7 kJ" refers to the thresholds (7.06 and 6.85); the body's defined needs for those tests are 7.44 and 7.65 kJ.
    - The abstract's deciding measurement omits the conclusions' "with the thermocouple's angle".
21. **Rounding:**
    - The shown brackets give 6.51/4.77 = 1.365, not the stated "1.37" (M p.12, p.25).
    - "Most in SP-Exp3" (M p.17) conflicts with Table S7, where ST-Exp4's difference is 4.33 against SP-Exp3's 4.32.
22. **Numerical checks:**
    - The reduced-model grid was "not refined in a separate check" (M p.27), yet it supplies most resolved values, which are quoted to 0.01 kJ without error.
    - The 3D mesh checks use one run per configuration (S pp.17–18).
23. **Loose two-body tolerance (S p.27):**
    - The tolerance is the larger of 10 % and 300 J, and 9 of the 32 searches are zero in both.
    - For PT-Exp2 at high contact, 0.29 kJ against a (0.09, 0.11] kJ bracket counts as "within".
24. **Weak input basis:**
    - Many inputs in Table 2 are assumptions carried over from the author's earlier study.
    - The contact conductance is a flat stainless-steel textbook range.
    - The fitted triggers exceed calorimetry in 13 of 16 tests (up to 54.3 against 33.2 kJ).
25. **Missing details:**
    - Table 1 has no failure category 3.
    - The angles of most surface probes are not given.
    - The triangular pulse's shape is only implied in Appendix B.
    - The 120, 240 and 360 s durations are not justified.
    - SEI and NCM811 are not expanded, and the M50's cathode is not stated.
    - Fransson et al.'s own 150 °C propagation criterion (S1) is absent from the main text.
26. **Citations and Table S5:**
    - Table 3 (M p.21) places "[26]" after "398.5 m s⁻¹", which reads as the velocity's source; the velocity comes from [28].
    - Table S5 lists inputs whose use is never stated (1.131 s, about 300 s, "2 to 5 s later", the five-fold resistance rise).
    - The supplement numbers its references differently from the main text.
27. **Supplement claims vs. content:**
    - S p.1 claims "every label is defined in Section S1" and that predictions are quoted "as they were committed". B10–B17 show undefined labels, and S3 says the statements are "shortened".
    - S1 and Table S2 step 6 P2 call the far face "the thermocouple node" or "the thermocouple's position", contrary to the main text's unknown angle.
28. **Same peak twice:** 226.7 °C is given both as the maximum over the 5,248 step-5 runs and as the single high-contact case in M p.11. It is unclear which one the abstract's 29 K rests on.
29. **Minor:**
    - The "independent check" in a sole-author study does not say who did it.
    - Table S11 has duplicate no-delivery runs for ST-Exp1 and ST-Exp2.
    - The table header is repeated on S p.24.
    - In Fig. 4b, zero needs sit at the foot of a log axis and look like about 0.2 kJ.
    - "23 times the smallest" (M p.15) silently leaves out the four zero needs.

Not ready
