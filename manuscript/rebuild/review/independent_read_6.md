# The independent read of the rebuilt manuscript, read 6 (23 November 2026)

Brief 30, item 10. A separate agent, new and with no sight of the work, of reads 1 to 5 or of the editor's reads, read only the built manuscript (33 pages) and supplement (35 pages) as PDFs, as built at commit 5a0cd44 (Brief 30's first round), with no other file, command or web access, and listed untraceable numbers (A), archive-dependent sentences (B), overclaims (C) and other first-reading objections (D), under the instructions of reads 2 to 5, changed only in the page counts. Its report, verbatim, follows; what changed after it is at the end of this file and in DECISIONS.md D189.

---

Verdict: **Not ready.** Lists A, B and C all have items.

The most serious problems:
- **C1:** a general "trigger-dependent correction" claim rests on three three-dimensional tests, and the reversal rests on one of them.
- **C2:** the abstract says an untested heat-flux measurement "would remove" the dependence.
- **A1 and A3:** the 56/42 split of all 98 predictions and the "ten tests" count cannot be traced.
- **B2 and B4:** the supplement uses prediction labels P1–P10 and a "150 °C criterion" without defining them, although it says every label is defined in S1.

No sentence says which neighbour model is right.

MS = manuscript, SM = supplement.

**A. Untraceable numbers**

- **A1.** MS p.11, repeated at SM p.7: "The study registered 98 predictions in all, of which 56 held and 42 failed".
  - Table S1 gives held and failed counts only for the 52 listed predictions (34 and 18).
  - The 22 held and 24 failed among the other 46 appear nowhere. SM p.5 says only that "The verdicts of the others are in the public archive".
- **A2.** SM p.5 (Table S1, step 6) and SM p.6: "the tests' 150 °C criterion and the trigger's measured durations".
  - 150 °C has no source or definition. MS p.3 defines propagation as a second thermocouple spike.
  - The "measured durations" are never given.
  - 150 °C also appears unexplained in Table S2, step 5 P3 (SM p.8).
- **A3.** MS p.12: "at the high contact this rests in ten tests on the reactive cross-section alone".
  - This implies six tests had three-dimensional no-delivery runs at the high contact.
  - Table S13 (SM p.28) and Section S14 (SM p.26) identify only five: PT-Exp1, PT-Exp3, PP-Exp3, ST-Exp1 and ST-Exp2.
- **A4 (borderline).** SM p.9, Table S2: step 7 P1 "Study's expectation: Holds, with eight." and step 8 P2 "Holds, with all seven below 0.3."
  - SM pp.7–8 list where registered numbers came from: hand estimates (step 5), reduced models (steps 13 and 15), and earlier results the tables give.
  - None of these covers these counts made before the runs.
- **A5 (borderline).** SM pp.23–24, echoed at MS p.16: "the 32 searches made there over 120 and 360 s: it lies within the same tolerance in 29".
  - These 32 central-contact lumped thresholds are in no table.
  - So "29 of 32" and "7 to 46 J beyond it" cannot be checked.

**B. Archive-dependent sentences**

- **B1.** Three sentences send the reader to the archive:
  - MS p.11: "every prediction, with its file and its verdict, is in the public archive".
  - SM p.5: "The verdicts of the others are in the public archive".
  - SM p.7: "a listed prediction's expectation is given without the reasons in it that rest on such runs".
- **B2.** SM p.1 says "Every label it uses is defined in Section S1". But P1–P10 are not defined in S1, and are used before Table S2 lists them:
  - SM p.6: "In step 13, P7's first clause … P7's verdict is that of its second clause".
  - SM p.7: "Step 5's P5 gives the measured mean times of the two connections as 8 s apart".
  - SM p.8: "Step 11's P4 was recorded as failing … step 12's P3 and P4 as fixed by step 9's needs".
- **B3.** SM p.5 (Table S1, step 7): "Seven ignition criteria scored test by test".
  - Only C1, C2 and C8 are defined (SM p.2).
  - The label C8 implies criteria C3–C7 that are never described.
- **B4.** SM pp.5–6: "the tests' 150 °C criterion and the trigger's measured durations" are undefined (see A2).
- **B5.** SM p.8 (Table S2, step 5 P1, and P6 on SM p.9): "May fail: by the estimates above the hot spot stays below 255.7 °C".
  - The estimates are described only by kind (SM p.4: "an adiabatic rise, the contact's time scale and a two-node energy balance").
  - Their values exist only in the archive's predictions file.
- **B6.** SM pp.10 and 12 (step 11 P4; step 14 P1, P2, P6): "the predictions file's analysis, written before any bound, says P1 is expected to fail".
  - The analyses that make 6 of the 18 failures "foreseen" exist only in the archive.
  - Step 11 P4 says "at both contacts" without saying which two.
  - "Radial conductivity" is not a label S1 defines.
- **B7.** These choices are inherited from the author's earlier study [22], a Zenodo software record; the reasons for them are only there:
  - MS p.8 (Table 2 caption): "The two-cell geometry and its solver are those of an earlier, archived study by the author [22]".
  - MS p.11: "(over 10 or 30 s, the earlier study's two)".
  - MS p.27: "reflections neglected, as in the earlier study."
- **B8.** MS p.17: "by the time at which the hot spot's self-heating starts in an earlier case".
  - "An earlier case" is not defined in the manuscript.
  - It is step 3's case with a 2 mm gap and busbars, described only at SM pp.3 and 6.
- **B9.** MS p.17: "an earlier search set (Supplementary Table S1, step 9)".
  - The coarser 4.66–5.04 kJ bracket appears in no table.
  - Borderline: step numbers at MS p.11 ("steps 7, 8 and 15"), p.19 ("step 10") and p.26 ("step 11") can be followed only through Table S1.
- **B10.** SM p.26: "each search starting from step 8's bracket". Step 8's brackets are not given anywhere.
- **B11.** SM p.15: "from emitters placed on a grid beyond the trigger's end … from a finer scan than the grid's". The grid's extent and spacing exist only in the code.
- **B12 (borderline).**
  - MS p.11 ("Each step's registered numbers were recomputed from the run records by separate code") and SM p.4 ("the repository records each file's commit, the time of its push and the hash") can be checked only in the repository.
  - SM p.4: "A check on the mapping (step 8)" never says what "the mapping" is.
  - SM p.7 mentions step 8's runs "with Joule heat", which are never described.

**C. Overclaims**

- **C1.** A general rule drawn from too few tests:
  - MS p.1: "so a share calibrated with one needs a trigger-dependent correction for the other".
  - MS p.24 (§4.2): "cannot be carried to the other without a correction whose sign depends on the trigger".
  - MS p.24 (§4.1): "in a direction set by the trigger".
  - Why this overreaches:
    - It rests on three three-dimensional tests.
    - The reversal rests on one weak-trigger test, ST-Exp3, or on two in the cross-section model (adding PT-Exp1, whose trigger peaked at only 164 °C, with "cell movement").
    - Everything is at posterior-mean kinetics and central properties.
    - Table S12 shows the lumped threshold alone ranging 0.85 to 4.26 kJ (PP-Exp3) across draws. That is about as large as the 1.7–4.3 kJ difference between the readings.
    - The resolved threshold was never searched under draws.
- **C2.** An untested measurement presented as decisive:
  - MS p.1: "A heat flux measured there, to well within the readings' difference, would remove the dependence".
  - MS p.25: "One measurement could decide between the readings".
  - MS p.27: "could decide … and so remove the estimate's dependence on the reading".
  - Why this overreaches:
    - It holds only "if the model is otherwise right", and §4.4 gives many reasons to doubt that.
    - The resolved needs it would be compared against come from a reduced model whose runaway time differs from the 3D model's by up to 34.5 s.
    - The abstract's "would" is stronger than the body's "could".
- **C3.** MS p.1: "leaves the neighbour at least 29 K short of runaway by conduction and radiation".
  - This is said of the neighbour, not "in the model" as Conclusion 1 (p.26) says.
  - It treats the chosen 255.7 °C level as runaway, although the same kinetics reach the internal-short rate at 199.8 °C (p.9).
- **C4.** Model quantities attributed to the tests:
  - MS p.1: "strong-trigger tests need 4.1 to 8.1 kJ by the measured propagation time".
  - MS p.24: "they fix how much of it must reach the neighbour by each test's measured time".
  - Why this overreaches:
    - p.10 itself calls a need "a model quantity … which the tests do not measure".
    - The resolved needs come from the reactive cross-section, whose runaway lands 5.5 s earlier to 34.5 s later than the 3D model's (p.23). That exceeds the 10 s match that defines a need.
    - Its grid was never refined (p.28).
    - The triggers are fitted beyond calorimetry in 13 of 16 tests.
- **C5.** Headings that promise an explanation the section does not give:
  - MS p.16, heading "Why the three thresholds differ"; MS p.18, Fig. 4 caption "Why the thresholds differ."; SM p.5, Table S1 step 13 "The mechanism of each threshold".
  - The section shows only consistency: the lumped threshold is "broadly consistent", and "the steeper fall is not explained here".
  - p.24 says "these runs do not say how much each difference contributes".
- **C6 (borderline).** MS p.16: "Over 360 s (Fourier number 1.80), in PT-Exp1, the cell heats through", then "a runaway inside the cell" and "accordingly falls from 2.90". A mechanism, and a causal "accordingly", drawn from one test at one duration.
- **C7 (borderline).** SM p.15: "so each upper bound is what the published inputs cannot be made to exceed".
  - The gas bound uses an empirical cross-flow correlation (Churchill–Bernstein) applied to vent gas with hydrogen properties at 1000 K.
  - The 1500 °C flame temperature is cited second-hand from a battery module (Table S5, "cited in [9]").
  - A correlation is an estimate, not a strict bound. The conclusions do not change, since every bound exceeds the needs.
- **C8 (borderline).** The title says "resolved and lumped neighbour models against sixteen tests".
  - p.26 admits "Much of what is compared is model against model".
  - Only one measured history is compared, and the held-out test (p.12) finds no quantity that beats a single probability.
- **C9 (borderline).** MS p.24: "the reactive cross-section reproduced the outcomes it was set against afterwards at a small part of the cost".
  - The comparison was made after the runs.
  - 82 of the 92 runaway cases are far above any threshold.
  - Near-threshold agreement holds "by construction" in three of four searches (Fig. 7 caption).
  - Yet this model supplies 12 of the 16 resolved thresholds and every resolved need. §4.2 drops the "far from a threshold" caveat that Conclusion 5 keeps.

**D. Other first-reading objections**

- **D1. Kinetics and the runaway level disagree (MS p.9).**
  - The kinetics reach the internal-short rate "at 199.8 °C, below that event's band of 255.7 to 302.1 °C, a difference not resolved here", yet 255.7 °C is used as the runaway level.
  - The check on the draws "failed; it passed only as amended after the failure".
- **D2. Fitted triggers (MS pp.4, 7, 25).**
  - Every result rests on triggers fitted to one thermocouple peak, above calorimetry in 13 of 16 tests (up to 54.3 kJ against 33.2 kJ).
  - The modelled trigger history is never compared with the measured trigger record.
  - Both weak triggers look anomalous: PT-Exp1 peaked at 164 °C with "cell movement", ST-Exp3 at 282 °C.
- **D3. Table S7 contradicts Table S14 (SM pp.19–21 against pp.29–31).**
  - Table S7 says "a dash, no energy on the search's grid gave a runaway".
  - But Table S14 shows ST-Exp3 running away at 25.19 kJ over 360 s.
  - PT-Exp2's 240 s and 360 s rows are dashed although every such run in Table S14 runs away.
  - The grid's range is never stated.
- **D4. Units typo (SM p.12, step 15 P2).** "the reduced model's value, registered with it: 7.062 J" should be kJ.
- **D5. Geometry inconsistency.** The MS p.8 Table 2 caption says the geometry is the earlier study's. SM p.3 says that study's cells were "2 mm apart and joined by busbars", but here the cans touch.
- **D6. Circular held-out predictor (MS p.11, SM p.23).**
  - The third predictor is "a need whose definition depends on the outcome".
  - It includes two needs (32.7 and 75.8 kJ) that are runaway energies for tests that did not propagate.
- **D7. Abstract against Conclusion 3.**
  - The abstract's "in two strong-trigger tests" drops the qualifier "whose lumped threshold is not zero" that Conclusion 3 (p.26) has.
  - The abstract says "central kinetics" where the body says "posterior mean".
- **D8. Sensitivities never run.**
  - The bias from coupling the trigger one way is "toward the difference found here" and "was not computed" (p.25).
  - The flux region, uniform over the facing half, is never varied.
  - The reduced models' grid was not refined (p.28).
  - The mesh checks in Table S4 measure the hottest point's peak, not the thresholds.
- **D9. Parameter choices (MS p.8, SM pp.3 and 27–28).**
  - The mass is assumed at 65 g although "the Databank's cells weighed 68.05 to 68.52 g".
  - The "central" 1.3 W m⁻¹ K⁻¹ and 950 J kg⁻¹ K⁻¹ are not central in the cited ranges.
  - Thermal draws are labelled by one property but change all three. The lumped threshold moves under "conductivity" draws, and the other values are not given.
- **D10. Weak scoring (MS p.16, SM pp.12, 23–24).**
  - The 300 J floor passes small thresholds trivially: "PT-Exp2's 0.29 kJ … counts as within a bracket of 0.09 to 0.11 kJ", and nine cases are zero–zero.
  - The main case (central contact, 21.4 s pulse) is not scored.
  - Step 15 P1 holds by construction yet counts among the 34 held.
- **D11. Adaptive design under a pre-registration frame (MS p.11, SM pp.4–5).**
  - Key elements "entered in steps 7, 8 and 15, after earlier predictions failed".
  - One run was made before step 11's predictions, and verdicts were seen mid-run.
- **D12. Front matter (MS pp.29–30).**
  - The generative-AI declaration heading has no text under it.
  - The sole author's CRediT entry omits Software, Formal analysis and Writing – original draft.
- **D13. Readability and figures.**
  - Very long nested sentences (e.g. p.9, "Where the least energy run that meets the criterion…").
  - Fig. 2a's t and b markers are illegible at print size.
  - Fig. 3 mixes markers drawn at bracket upper ends with markers drawn at midpoints.
  - Fig. 6's legend appears cut off ("four shape").
  - p.13, "In twenty-five of them…", does not say which reading it means.
- **D14. Minor inconsistencies.**
  - SM p.2 attaches "within 900 s" only to C8; MS p.5 applies it to all three criteria.
  - PT-Exp1 at 360 s is 1.23 kJ in Table S7 but 1.22 kJ in Table S14.
  - SP-Exp3's pulse need is 0.26 kJ in Tables S3 and S7 but 0.27 kJ in Table S14.
  - "8.5 s" (MS p.25) against "79.9 °C at 8.4 s" (SM p.17).
  - E* is defined twice (SM pp.3–4).
  - MS Table 2's "about 300 s" relies on a source cited only in the supplement.
  - Table S14 has no central-contact no-delivery 3D run for PT-Exp2, PP-Exp2, ST-Exp3 or SP-Exp4, although p.12 flags only the high contact as resting on the cross-section.

Not ready

---

## What changed after read 6 (Brief 30, second round)

No run was made and no result changed; every number added is traced by `numbers_check.py` (both logs, 0 failures).

- A1. Supplementary Table S1 gives, step by step, how many predictions held and failed among those Table S2 lists and among the others (22 held and 24 failed of the 46); Section 2.7 points to it.
- A2 and B4. The 150 °C is defined in Supplementary Section S1 (the least onset temperature of propagation in Fransson et al.'s tests, read off their Fig. 3a, an observation and not their test of propagation), in Table S1's step 6 and in Section S2, which also gives the measured durations: the two rise times, 17.53 and 25.24 s (Section S7).
- A3, and D14's last item. New Supplementary Table S15 and Section S16 give every test's no-delivery outcome at each contact and how it is established: at the low contact the hottest point stays below 255.7 °C in all sixteen tests; at the central contact in eight, and three-dimensional runs to 900 s cover the other eight; at the high contact in three, step 11's runs cover three more and the cross-section alone the other ten. Section 3.1 cites the table.
- A4. "With eight" (step 7's P1) and "with all seven below 0.3" (step 8's P2), counts drawn from sizing runs neither document reports, are taken out of the expectations Table S2 quotes.
- A5. Table S10 adds the 32 searches at the central contact with triangular pulses of 120 and 360 s, each with its tolerance and verdict.
- B1. The two archive sentences of Section 2.7 and Section S3 are the brief's and stay; Table S1's caption no longer sends the reader to the archive.
- B2 and B3. Section S1 defines a step's P1, P2 and so on, and describes C3 to C7.
- B5. Section S1 gives step 5's hand estimates with their values.
- B6. Table S2 quotes, in short, the analyses that foresaw step 14's P1 and P2 failing and its P6 holding; Section S1 defines step 11's "both contacts" (the low and the high); "radial conductivity" is written "conductivity across the layers".
- B7. Table 2's caption says how the earlier study's geometry differs (cells apart and joined by busbars; here in contact, with welded tabs); Appendix A no longer cites the earlier study for neglecting reflections.
- B8. Section 3.4 says that the case by which the kinetic draws were ranked is on the earlier study's geometry, with a gap between the cells.
- B9. Section S4 gives PT-Exp4's coarser bracket, step 9's 4.66 to 5.04 kJ, and Section 3.4 cites it there.
- B10. Section S14 says that step 8's bracket is the posterior mean's row of Table S12.
- B11. Section S6 describes the 181 emitter points and the finer scan on the vent's axis, and corrects the ray counts: two million directions per grid point and four million per point of the finer scan, where the text had said four to eight million.
- B12. Section S1 says what the mapping is; Section S3 describes step 8's runs with Joule heat.
- C1. The abstract no longer states the trigger-dependent correction; Sections 4.1 and 4.2 and the letters scope it to the tests searched, and Section 4.2 says that in three dimensions it rests on three tests and its reversal on one (two by the reactive cross-section), at the posterior mean and the nominal properties; Section 4.4 adds that the resolved threshold was searched under no draw.
- C2. "Would" became "could" in the abstract and the highlights; Section 4.3 and the conclusions add that the measured heat must be set against resolved needs computed in three dimensions.
- C3. The abstract says "the modelled neighbour" and names 255.7 °C as the runaway level.
- C4. The abstract, the introduction, Section 3.2 (now "The needs at the measured times"), Section 4.1, the highlights, the graphical abstract and the letters give the needs as the model's.
- C5. Section 3.4 is now "The thresholds against reduced models", and Fig. 4's caption likewise; the local threshold "agrees with" conduction; the introduction asks how far reduced models account for each threshold; Table S1's step 13 reads "Reduced models of each threshold".
- C6. "In PT-Exp1, the one test searched there", "as if the cell had heated through", and no "accordingly".
- C7. Section S6's wording of the bounds matches the main text's, and calls the gas's and the flame's bounds estimates of that most rather than strict limits.
- C8. The title is Brief 30's and stays.
- C9. Section 4.2 adds "most of them far from a threshold".
- D3. Table S7's caption says what a dash means: for the resolved need, that no energy on the search's grid, which ran to 0.2 of the test's ejected energy above the threshold's upper end, brought the runaway within 10 s of the measured time (ST-Exp3 over 360 s: no earlier than 196.4 s, with 25.6 kJ); for the far face, that it stays below the maximum with up to the test's whole ejected energy. Section 3.2, Fig. 2's caption and Section S9 say the same. The earlier caption ("no energy on the search's grid gave a runaway") was wrong.
- D4. "7,062 J" is written 7.06 kJ.
- D5. Table 2's caption (B7).
- D7. Conclusion 3 adds "all at the posterior mean and the nominal properties"; "central kinetics" is gone.
- D9. The "central properties" are now the nominal properties, defined in Section S1 as Table 2's values, inside the published ranges though not at their middle; Tables S12 and S13 give each thermal draw's three properties.
- D10. Section S3 says that step 15's P1 holds partly by construction.
- D13. Fig. 6's legend fits; Fig. 2a's dots are larger; Section 3.2 says "a run of the resolved neighbour".
- D14. Section S1 reads every criterion within 900 s; Table S14's caption says why two of its energies differ in the last digit from the needs; Section S7 gives 80.0 °C at 8.5 s on the 0.5 s samples beside 79.9 °C at 8.4 s; Section S1 says step 12's E* is a different quantity; Table 2 cites the source of "about 300 s".
- D1, D2, D6, D8 and D11 are limits the text already states; D12 (the generative AI section and the CRediT line) is the author's.
