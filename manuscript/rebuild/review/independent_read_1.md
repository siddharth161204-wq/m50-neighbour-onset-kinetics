# The independent read of the rebuilt manuscript, read 1 (20 November 2026)

A separate agent read only the built manuscript (26 pages) and supplement (20 pages) as PDFs, with no other file, command or web access, and listed untraceable numbers (A), archive-dependent sentences (B), overclaims (C) and other first-reading objections (D). Its report, verbatim, follows; the changes made after it are in DECISIONS.md D186.

---

Independent read of manuscript.pdf (26 pp.) and supplementary_material.pdf (20 pp.)

I read every page as an image, figures included. I opened no other file and used no web. "MS" means the manuscript and "SM" the supplement. Page numbers are the printed ones.

**Verdict: Not ready.** The most serious problems:
- Several numbers have no visible origin: 25.4 %, 247.3 kJ, 15.6 kJ, 2,667 J, "22- to 64-fold", the held-out scores, and the 6.2 kJ/240 s run.
- Table S2 in the supplement cannot be read without the archive. It uses "Brief", "Stage N", A4, A0.2 and "the file's analysis" without defining them.
- The abstract and conclusions overstate the findings.
- There are internal contradictions:
  - The supplement shows two published neighbour histories; the paper says there is one.
  - The t-values in Table S3 do not match the thresholds beside them.
  - "Only ST-Exp3 reverses" contradicts "the two with weak triggers".
  - The registry's own counts conflict in places.
- The generative-AI declaration is empty.

## A. Untraceable numbers

A1. MS p16, p19: "is 5.3 to 25.4 % of the Databank's median ejected energy". 25.4 % of 76.74 kJ is about 19.5 kJ, and no resolved need of that size appears anywhere. The text says 4.1–8.1 kJ and Table S3's maximum is 10.31 kJ, which give 5.3–10.6 % (13.4 % if ST-Exp3 is included).

A2. MS p17, Table 3, holder row: "(247.3 kJ if bounded as the jet and melt are)". The jet and melt are bounded at 225.8 kJ, and nothing derives 247.3 kJ.

A3. MS p17, Table 3, and SM p15: "15.6 kJ within 21.4 s if the resistance stayed at its 25°C value". The voltage, circuit and resistance used are not given. For example, 4.2 V across 30 mΩ gives about 12.6 kJ.

A4. MS p12: "with enough of that reaction's 2,667 J left to reach 255.7 °C". There is no derivation. C × (255.7 − 218.5) = 2,297 J.

A5. MS p12: "falls from 2.90 at a Fourier number of 0.11 to 1.16 at 0.60 and 0.94 at 1.80".
- PT-Exp1's lumped thresholds for the 120 s and 360 s deliveries appear in no figure or table.
- Table S3's midpoints give 12.715/4.355 = 2.92, not 2.90.

A6. MS p12–14 and p18: "these needs span 22- to 64-fold, the largest non-zero over the smallest".
- The needs for the constant-power shapes are not tabulated.
- Table S3's pulse needs give about 23-fold (5.96/0.26), or about 47-fold (12.11/0.26) if ST-Exp3 is included.
- 64 cannot be found.

A7. MS p14: "the largest gain is 0.062, with permutation p-values of 0.23 to 0.75". There is no table. Methods do not describe what was fitted, to which quantities, or how many permutations were run.

A8. MS p14: "in all twenty-five reproduced cases outside ST-Exp3, whatever the delivery's shape". Eight tests times four shapes is 32. Which seven cases were not reproduced, and why, is not stated, and Table S3 covers only the pulse.

A9. MS p12: "By 250 s the lumped neighbour has taken in 2.1 to 2.3 kJ more than the resolved one". The runs (tests and energies) are not identified, and the quantity is not plotted.

A10. MS p15, Fig. 5 legend: "6.2 kJ over 240 s" (the same run is SM p12, step 15 P8, "6,209 J over 240 s"). The text never mentions this run, and its origin and purpose are not stated.

A11. MS p12 and p14: "At 5.04 kJ over 21.4 s in PT-Exp4" (SM p12: "PT_Exp4's 5,045 J"). The lumped bracket is (4.66, 4.85], and nothing says why 5.04 kJ was chosen.

A12. MS p16 and p17: "sends at most about 0.37 % of its radiation onto the facing half, about 0.85 kJ". The energy that 0.37 % is taken of is not stated (0.0037 × 225.8 kJ = 0.84 kJ).

A13. MS p17, Table 3: "at most twice its whole-cylinder mean on one half"; "from a sixth of the circumference"; "from half of the circumference". None of these factors has a source or a derivation.

A14. MS p10: "in any of 5,248 runs across the contact, tab, release and connection brackets". Table S4 gives the count, but the design is not given anywhere: the release brackets and body energies are never listed. SM p6 separately mentions "4,800 factorial runs".

A15. MS p3 and p7 (21.39 s): "the mean rise time of the two trigger records that the supplement draws". The two rise times, and how a rise time was read, are not given; S7 reports only the neighbour's record. This one is borderline because [16] is named as the source.

A16. SM p1–2: "C3: the lumped neighbour reaches 150 °C. C4 and C5: the separator's melting temperature, 138.5 °C". Neither value has a source.

A17. SM p6, step 5 P5 and P7 expectations: "the tabs carry 4 to 8 % of the contact path" and "the contact range changes the path 4.6-fold". Neither has an origin.

A18. SM p9, step 9 P7: "rescales every time- and peak-matching fraction by 0.75 to 1.40". The bracket on the ratio is never given.

A19. SM p4–12, expectation column. Examples:
- p4: "4.2 s against 29 s for the 10 s release (86 % earlier)"
- p5: "18.5 % at 100 mW/K, and 10.5 % at 500 mW/K" and "36.5 %"
- p9: "11.9 to 18.5 s" and "ST_Exp3's lies at 61.4 s"

Nothing describes how these "Brief's" or "Study's" central estimates were made.

**Borderline A-items.** These are traced by your definition but can only be recovered by working backwards, or appear in prose alone.
- **Derived constants.**
  - MS p11: "α = 5.565 × 10⁻⁷ m² s⁻¹". MS p21: "e = 1,743 J m⁻² K⁻¹ s⁻¹ᐟ²", "841.7 J m⁻² K⁻¹" and "Φ = 1.2284".
  - The roll's volumetric heat capacity is never stated. α and e only work out if (61.75 − 4.5) J/K is spread over the whole cell volume.
  - 841.7 is the can's 4.5 J/K divided by its full area.
  - Φ has no derivation.
- **Run results given only in prose**, shown in no figure or table:
  - p10: 226.7 and 180.6 °C; 21.7 s; 191.9–192.2 and 226.4–226.7 °C; 159.8–161.8 and 175.9–177.4 °C; 106–128 s; 22.4–22.6 and 4.1–4.8 kJ.
  - p11: 61.5 s; 1.1 K; 18.9 K; 316.5 s; 240.1 °C. The 3 % agreement for ST-Exp3 and PT-Exp3 is also prose-only, since only PT-Exp1 is plotted.
  - p12: 230.4 °C; 73.3 %; 191.2–192.4 °C; 188.3 °C; 221.1 °C; 270.3 s; 13.8–56.3 K.
  - p14: 114.0 s; 16.3 and 16.8 K; 51.4 K; 369.3 s; 233.6 °C; 33.1 K; 235.5 and 235.8 °C.
  - p18: 17–71 s and 240–2,762 s.
- **Log-axis-only values.** The 32.7 and 75.8 kJ needs (p16) appear only as markers on Fig. 4b's log axis.

## B. Archive-dependent sentences

**Main text**

B1. MS p7, Table 2 caption: "The two-cell geometry and its solver are those of an earlier, archived study by the author [22]." Several inputs are sourced only to the author's own Zenodo software deposit:
- the cell's size and the can's properties
- the 61.75 J/K heat capacity and the air conductivity
- the 6.8 mW/K tab conductance (brackets 5 and 10)
- the 10 W m⁻² K⁻¹ room convection

B2. MS p8: "each one particle of each submodel's file, which treats the three submodels as independent". The files and the three submodels are never named.

B3. MS p9 (also SM p14): "read again by a check that had not drafted the texts". What or who "a check" is is not said.

B4. MS p10: "across the contact, tab, release and connection brackets". "Release brackets" is undefined; Methods describe a single 21.39 s release.

B5. MS p12: "four kinetic draws chosen by the rank of their onset". The ranks are not given.

B6. MS p14: "the far face is the coolest of the model's five probes at mid-length". The five probes are never defined, and Fig. 1 shows three points.

B7. MS p14: "Fitted on one connection and scored on the other ... by the registered margin of 0.1". The method exists only as a registry entry (SM step 10 P6), not in Methods.

B8. MS p16: "runs that the study had carried past the hottest point's crossing". This implies a rule for stopping runs that Methods never describe.

B9. MS p19: "its clock's agreement with the measured times belongs to that construction". "Clock" is the registry label for C2 (SM p1) and is not defined in the main text.

B10. MS p19: "gave the three-dimensional outcome in every archived run it was set against". "Archived run" points to the archive.

B11. MS p3 and p6 (minor): the test names "PT-Exp4" and "SP-Exp3". The second letter of PT, PP, ST and SP is never explained.

**Supplement**

B12. SM p4–12: "Brief's central estimate" and "Brief's expectation". The "Brief" is never defined.

B13. SM p7, step 7 P5: "Likely, conditional on A4." A4 is undefined.

B14. SM p9, step 10 P2: "A0.2 is recorded before this prediction is scored, not before it is written." A0.2 is undefined.

B15. SM p6–11: "Stage 3's onset finding", "In Stage 5 runs", "the six Stage 7 hits", "the Stage 9 (far-face) node", "Stage 6's records". "Stage" is undefined; S1 and S2 say "step".

B16. SM p11–12: "the file records it as fixed by Stage 6's records" and "the bullet says likely; the file's analysis, written before any bound". These refer to content of the predictions files that is not shown.

B17. SM p3, p5 and p10: "30 thermal draws", "thermophysical standard deviation", "four thermal draws", "each of the eight draws". Thermal draws are never defined.

B18. SM p6, step 5 P6: "The share of the 4,800 factorial runs". The factorial design is not given.

B19. SM p5–6, step 5 P1 and P6: "by the estimates above the hot spot stays below 255.7 °C". The "estimates above" are not shown.

B20. SM p8: "In the internal-short event runs at the central contact" and "in every sensitivity test where f* is above 0". Both run sets are undefined.

B21. SM p10, step 11: "For each of the four tests" and "In at least two of six tests". The tests are not identified.

B22. SM p9: "The bracket on the ejected-to-body energy ratio". Undefined.

B23. SM p8–12: file-style names such as "M50_PT_Exp1", "M50_PP_Exp4" and "PT_Exp4". The main text names the tests without the M50 prefix.

B24. SM p5, step 3 P6: "the source paper's early solid electrolyte interphase outlier behaviour". Not explained.

B25. SM p11, step 12 P1: "with the two-cell study's trigger". This refers to the archived study [22].

B26. SM p13: "four tests' brackets were narrowed further with one ejected energy for every test". Which four is not said.

B27. SM p2: "its result is stated in them". The statement is in the predictions file, not in Table S2.

## C. Overclaims

C1. MS p10, including the section heading: "Heat beyond what the trigger's body conducts and radiates must therefore reach the neighbour." Also MS p18: "A conduction model of these tests lacks the heat their triggers deliver". This holds only within the model:
- The kinetics come from another chemistry, the contact conductance is a textbook range, and there is no gas phase.
- §3.3 shows that shifting the rate laws by more than 17.5 K would also produce runaway.
- With the fitted triggers, conduction alone already ignites the hottest point in eight tests.

C2. MS p1: "The local threshold is skin conduction, within 3 % of a conduction model." Also MS p11: "The local threshold is conduction into a skin".
- This is shown for three tests with deliveries up to 120 s, and it fails at 360 s.
- The 3 % is measured against the cross-section model. The semi-infinite skin model falls below that model as the delivery lengthens (Fig. 3a).
- Step 13 P1 tests the skin model only at 5 s, to within 10 %.

C3. MS p11: "so the reaction plays no part in it". With the reaction switched off, the hottest point falls short by up to 1.1 K.

C4. MS p1: "The lumped threshold is an energy balance to an ignition temperature of 218.5 °C." Also MS p12: "Because the threshold is the heat that brings the neighbour to T_ign less what the trigger conducts..." The mechanism is stated as fact. The registered slope (SM p12, step 13 P10, 150–300 J/kJ) failed; 393–456 J/kJ was found. The explanation is given afterwards without saying so.

C5. MS p12, repeated on p19: "The resolved threshold is higher because a resolved cell takes in less ... and does not react as one body." Only the intake part is quantified, and its runs are unidentified (A9). The reaction part is asserted, not separated.

C6. MS p12: "The gap is larger than the kinetic uncertainty (Fig. 3d)." This rests on one test at one energy. The posterior span leaves out the chemistry mismatch that §4.4 concedes.

C7. MS p1 and p20, Conclusion 3: "Matching the whole-cell thresholds needs the rate laws shifted over 17.5 K". The only evidence is PT-Exp4 at a single energy (5.04 kJ).

C8. MS p1 and p20, Conclusion 4: "At the measured times the resolved neighbour needs 4.1 to 8.1 kJ, the lumped one 0.2 to 6.0 kJ." This drops the body text's "outside ST-Exp3" (10.31 and 12.11 kJ). The resolved values are also the reduced model's, not the three-dimensional model's.

C9. MS p1: "Published inputs bound every delivery path at 27.9 kJ or more, above every need."
- Conduction through the holder has no bound (Table 3).
- The 27.9 kJ radiation bound is below the two exploratory needs (32.7 and 75.8 kJ).
- The discharge path misses one need (p16).

C10. MS p1, p3, p19 and p20: "Measuring the heat flux on the facing side would decide." Also MS p19: "would give the delivered heat directly".
- A point gauge measures the local total flux, which includes conduction from the trigger. That is not the heat delivered over the half.
- Deciding between readings also requires the kinetics, contact and triggers to be right, which §4.4 lists as limits.

C11. MS p19: "A lumped cell can therefore not serve as the inexpensive model of a cell's own runaway in a module". This says which neighbour model is right. It rests on model-against-model comparisons (§4.4: "Much of what is compared is model against model") in four tests of one cell type.

C12. MS p19: "its clock's agreement with the measured times belongs to that construction". This dismisses the lumped model's agreement with the measured times as an artefact, without any test.

C13. MS p19: "its mean needs 1.49 to 1.72 times the lumped neighbour's energy". This generalises from two tests. ST-Exp3 is 0.85 times, and SP-Exp3's lumped threshold is zero.

C14. MS p19: "would each reconcile the two; the results here do not choose between them". This is not shown for each alternative:
- The 12.5 W hold ("more heat over a longer time") still puts the far-face jump at 233.6 °C, about 36 K above the record (p14).
- A runaway starting from part of the cell was never run against the history.

C15. MS p14: "no quantity the model yields predicts the outcomes better than one probability for every test". The held-out scoring was registered at step 10 (SM p3), before the resolved whole-cell reading existed (step 15).

C16. MS p19: "Four measurements would decide between the readings." The flame's position, the breach direction and the trigger calorimetry only bound or fix inputs; on their own they do not decide between readings.

C17. MS p1, borderline: "About 7 kJ delivered over 21.4 s makes the resolved neighbour run away". This holds in two of the four tests searched in three dimensions; the other two need 3.88 and 10.28 kJ.

C18. MS p16 and p19, borderline: "The reactive cross-section stands for the resolved neighbour's own runaway".
- It was checked only at the central contact.
- It reads the mean's peak up to 20.7 K low in the parallel tests (p18).
- Yet it alone supplies the high-contact verdicts (p10) and twelve of the sixteen thresholds.
- Calling it the cell's "own runaway" (also SM p2, C8) assumes the mean criterion is the true runaway.

## D. Other first-reading objections

D1. MS p22: the "Declaration of generative AI and AI-assisted technologies" heading has no statement under it.

D2. MS p21: for a sole author, the CRediT statement omits Software, Formal analysis, Data curation, Visualization and Writing – original draft.

D3. The paper repeatedly says "the one published history" (MS p1, p3, p14, p20; SM p15 heading).
- But SM p15 says Fransson et al.'s Figure 10 "draws the thermocouple records of two tests ... PT-Exp4 ... and PP-Exp3".
- PP-Exp3's record is never used.
- Yet PP-Exp3 is one of the four tests where the model's far face overshoots the measured maximum with no delivery (MS p12, p19).

D4. MS p11 says "Only ST-Exp3's weak trigger (16.6 kJ) reverses the order", but MS p10 says "less in the two with weak triggers". PT-Exp1 also reverses (10.78 against 12.72 kJ).

D5. "Need" is defined on p8 as the energy at the measured time, but it is used for thresholds:
- p1: "the lumped neighbour's need"
- p10: "needs 3.5 to 10.8 kJ" and "needs none"
- p20: Conclusion 2

Read as defined, PP-Exp2 gives 7.65/5.96 = 1.28 (Table S3), not 1.72.

D6. The three-dimensional brackets are, by construction, ±5 % around the cross-section's value. In three tests they are just the two opening runs (SM p13; MS p18).
- So the abstract's "about 7 kJ" and the ratios 1.49 and 1.72 are the reduced model's numbers.
- With both brackets, the ratios run from about 1.38 to 1.59 for PT-Exp4 and about 1.36 to 2.26 for PP-Exp2.

D7. SM p13, Table S3: the t-marked resolved needs sit 0.4–0.5 kJ above those tests' cross-section thresholds, although the caption calls a t-value a threshold. As a result, Fig. 2 and Fig. 4a show different values for PT-Exp4.

| Test | t-marked need (kJ) | Cross-section threshold (kJ) |
|---|---|---|
| PT-Exp4 | 7.44 | (7.04, 7.08] |
| PP-Exp4 | 6.05 | (5.58, 5.62] |
| ST-Exp4 | 5.51 | (5.03, 5.06] |

D8. Arithmetic:
- MS p12, "2.90": Table S3 gives 2.92.
- MS p12, "7.9 times": 2.09/0.26 = 8.0.

D9. MS p19 says "Four measurements" but lists five.

D10. SM p11, step 13 P7, says "(known when registered, not counted)". But Table S1 (SM p3) counts all ten step-13 predictions, with P7 among the seven held.

D11. SM p10: step 10 P3 and P5 are marked "failed, foreseen", but their recorded expectations read "uncertain" and "likely". That contradicts the rule for "foreseen" (SM p2–4), so the total of 24 foreseen failures cannot be checked.

D12. SM p2: "In step 14, A1 to A6 are the paths of Table S5, in its order."
- Table S5 lists 16 inputs, not six paths; the paths are in MS Table 3.
- A1, A2, B1, B2 and A1–A6 are defined but never used in Table S2.
- A4 and A0.2 are used but never defined.

D13. SM p1 says "Everything in it can be read without the archive", and SM p4 says "Labels are defined in Section S1". Items B12–B27 contradict both.

D14. MS p15, Fig. 5: the 6.2 kJ over 240 s run failed its registered outcome (SM p12, step 15 P8: "runs away"). The main text never says so. If 6.2 kJ is the reduced model's 240 s need, the reduced and three-dimensional models disagree in this run. That would contradict "in all 151" (p16) and "every archived run" (p19).

D15. MS p1: the "42 of 98" includes the 18 predictions of steps 1–4. Those steps used an earlier geometry with a gap and busbars (SM p2), and their results are not reported.

D16. MS p9 says the predictions were committed before each step's runs. SM p2 records two departures that the main text does not mention:
- a full run made before step 11's predictions were committed
- verdicts seen on 178 of step 11's 216 records

D17. MS p12: with no delivery, the model's far face exceeds four non-propagated tests' measured maxima by 13.8–56.3 K. The model therefore over-heats those neighbours, which sits uneasily with §3.1's "not enough". Only §4.3 touches on it.

D18. MS p3: the fitted body energies exceed the calorimetric maximum (33.2 kJ) in 13 of 16 tests, reaching 54.3 kJ (+64 %). The only explanation offered is "probably because the trigger's flame heats the thermocouple", yet most results rest on these fitted triggers.

D19. MS p10: the high-contact verdict comes "by the reactive cross-section ... in ten of the sixteen tests". Which ten, and why not the three-dimensional model, is not stated. No low- or high-contact thresholds are shown anywhere, although the 32-search comparison on p12 rests on them.

D20. MS p7, Table 2, lists the shapes as "triangular over 21.39 s; constant power over 120, 240 or 360 s". It omits the pulse-plus-power shape (p8) and the 5–120 s deliveries of §3.3 (p11).

D21. Bounds:
- MS p14, "every path but one is bounded only near that": conduction through the holder, which has no bound, is a second exception.
- MS p16 refers to bounds within 120–360 s, which Table 3 does not give.

D22. MS p17 and SM p16: the hydrogen and air properties are "tabulated to 1000 and 1500 K" but are used for gas at 1500 °C (1773 K). The extrapolation is not mentioned. Also, citation [26] (Churchill–Bernstein) is attached to "hydrogen's properties".

D23. MS p16–17: the neighbour's own discharge is internal Joule heating, yet Table 3 and Fig. 6 present it as energy delivered "to the neighbour's facing half".

D24. SM p15: the source for the 30 ± 6 mΩ resistance ("LG Chem, Product Specification ... read in November 2026") is not in the reference list or in Table S5.

D25. Uncited supplement material:
- The main text never cites Tables S3, S4 or S6, or Section S7.
- SM p13 says Table S3 gives "the brackets that Fig. 2 and Fig. 4a ... draw".
- But Fig. 4a's constant-power needs and Fig. 4b's values are not tabulated.

D26. MS p1, "exceeds the measured surface by 37 K as runaway begins":
- The model's jump is at 173 s (Fig. 5a); the measured jump is at 271.5 s.
- The model run runs away about 90 s early.
- The measured record starts at 32.2 °C (SM p15), but the model's initial temperature is not stated (presumably the 25 °C ambient). That offset is inside the RMS figures (16.3–51.4 K) and is not discussed.

D27. The Fig. 1 caption (MS p5) says "The three points at mid-length", while p14 says "five probes".

D28. MS p18: the cross-section has no tabs and reads the mean's peak up to 20.7 K low in the parallel tests. It nevertheless sets the thresholds for all eight parallel tests.

D29. MS p12–13: "Every rate law must be shifted by more than 17.5 K". The shift is never defined (what is shifted, and in which direction). Fig. 3d puts a spread of T_ign and a rate-law shift on the same axis.

D30. MS p4:
- The central contact conductance of 2,000 W m⁻² K⁻¹ is neither the midpoint (1,950) nor the geometric mean (about 860) of the cited 200–3,700 range.
- The 45° contact sector is not justified.

D31. Undefined or ambiguous terms:
- MS p8: "M_ref" is undefined.
- MS p3: "the two trigger records that the supplement draws" is ambiguous; it could mean Fransson's supplement or this paper's.

D32. MS p2: "None of these sources, as far as they could be read, measures..." reads as an admission of incomplete reading. p19 then cites [12]'s estimate of 2.0 kJ absorbed by the next cell.

D33. Figure issues:
- Fig. 5b (MS p15) lists "measured (Fransson et al.)" in its legend but has no measured curve.
- The bands in Fig. 6 (MS p16) leave out ST-Exp3 without saying so.

D34. MS p1: the abstract does not mention that the kinetics were fitted to NCM811 and graphite while the M50 uses silicon-graphite, although the 17.5 K argument depends on it.

D35. MS p3 against Fig. 1b: test times are counted from "the trigger's runaway", model times from "the start of the trigger's release". The paper never says these are the same.

D36. Layout and grammar:
- SM p3: the page number "3" is printed inside Table S1's step-14 row.
- SM step 2: its labels P5(a)–(c) continue step 1's numbering.
- MS p20, Conclusion 1: "held to the largest calorimetry gives for this cell".

D37. Throughout: the prose is very compressed and idiosyncratic ("reading", "need", "delivery", "far face", "clock"). Many sentences need two passes to parse, which will slow reviewers.

Not ready