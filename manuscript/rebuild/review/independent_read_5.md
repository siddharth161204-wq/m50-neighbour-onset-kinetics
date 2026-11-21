# The independent read of the rebuilt manuscript, read 5 (21 November 2026)

A separate agent, new and with no sight of the work, of reads 1 to 4 or of the editor's reads, read only the built manuscript (33 pages) and supplement (38 pages) as PDFs, as built at commit 241428d, after read 4's fixes and before those of commit 131baef (the seventh editor's read), with no other file, command or web access, and listed untraceable numbers (A), archive-dependent sentences (B), overclaims (C) and other first-reading objections (D), under the instructions of reads 2 to 4, changed only in the page counts. Its report, verbatim, follows; the changes made after it are in DECISIONS.md D186 (6).

---

I read both files in full, figures included, and nothing else: manuscript.pdf (MS, 33 pp.) and supplementary_material.pdf (SM, 38 pp.). Page numbers below are the printed ones, which match the PDF pages. Most numbers trace cleanly: I checked the main tables and figures against each other (Table 1, S3, S7, S8, S10, S11, S12), and the tallies, ratios, ranges and the derived quantities (α, e, Φ, view factor, 27.9 kJ, 15.6 kJ, 21.39 s) are consistent. The problems are below.

**A. Untraceable numbers**

1. **MS p.1 (abstract):** "and below it, at most 0.91 times, after weak ones." **MS p.26 (Conclusion 2):** "and at 0.85 times, at most 0.91, in the one with a weak trigger."
   - 0.91 appears nowhere in the body. §3.2 (p.13) gives "0.81 to 0.90 across the brackets" (10.80/11.95 = 0.904, apparently rounded up). See also D1.
2. **(borderline) MS p.11:** "the trigger's release (over 10 or 30 s)".
   - Neither document gives a source or reason for these two releases. Table 2 lists only the 21.39 s release, and SM p.3 mentions only the earlier study's "two releases", without values.
3. **(borderline) MS p.9:** "Over the 164 of the 200 draws below in the source's main cluster…" (SM p.8 repeats "the 164 such draws").
   - The rule that puts a draw in the source's main cluster is never stated. So 164, and the 146.3–191.4 °C and 178.8 °C that rest on it, cannot be traced.
4. **(borderline) SM p.4:** "5 to 20 % of the neighbour's stored electrical energy … set in that step's plan … with no source".
   - An input with neither a source nor a rationale. It drives step 8 P7 (SM p.13).
5. **(borderline) SM p.5:** "the thermal standard deviation being 0.027 of the kinetic."
   - This is a step-3 result, and neither document reports step 3's runs (SM p.6).

**B. Archive-dependent sentences**

*Manuscript*

1. **MS p.11:** "Of 98 predictions (eighteen in four steps … not reported here), 56 held and 42 failed".
   - The tally includes verdicts on runs that are not reported.
   - "24 of the failures foreseen in the files' own analyses" and "known there to be fixed" point to files that exist only in the archive (see B13).
2. **MS p.11:** "were committed to a public repository and pushed, and the files were not changed afterwards [27]."
   - This can only be checked in the repository.
3. **MS p.11:** "read again by an independent check made apart from the drafting (Supplementary Section S5)."
   - Neither document says what this check was or who made it.
4. **MS p.9:** "the 164 of the 200 draws below in the source's main cluster".
   - "Main cluster" is never defined in plain words.
5. **MS p.15:** "by the time at which the hot spot's self-heating starts in an earlier case".
   - The "earlier case" is step 3's case on the earlier geometry (SM p.3), whose runs neither document reports.
6. **MS p.15:** "that an earlier search set (Supplementary Table S1, step 9) and a later one narrowed".
   - A step number is used as provenance, and the main text never says what that step was.
7. **MS p.17:** "a run made in step 10 (Supplementary Table S1) and stopped at 332 s". Same problem as B6.
8. **MS p.25:** "In coarser searches made in an earlier step (Supplementary Table S1, step 11)". Same problem as B6.
9. **MS p.8, Table 2 caption:** "a value that study set without a primary source, held here as an assumption."
   - The inputs marked "a", the 45° sector (p.5), the solver and the can-to-can radiation form ("as in the earlier study", p.27) all come from the author's Zenodo dataset [22]. Their basis is only there.
10. **MS p.20:** "the 151 three-dimensional runs … made in earlier steps, … six of them repeating another's configuration".
    - The individual runs, and which six repeat, can only be identified in the archive. Table S11 gives counts only.

*Supplement*

11. **SM p.1:** "Some expectations cite runs of earlier steps that neither document reports; their records are in the archive."
    - This contradicts the same paragraph's claim, "It is written to be read without the archive".
12. **Table S2 expectations that cite unreported runs:**
    - SM p.11 (6 P1): "the step 5 central case already shows it"
    - SM p.12 (7 P1): "step 6 ignited the hot spot only at the Databank's total energy and … only at the high contact"
    - SM p.13 (8 P4): "step 7 had one of eight within 60 s for C3 at f = 0"
    - SM p.13 (9 P1): "the hot spot crosses at 11.9 to 18.5 s at the threshold's upper end"
    - SM p.13 (9 P2): "seven upper-end crossings lie inside the window; ST-Exp3's lies at 61.4 s"
    - SM p.14 (9 P8): "step 7: the aged SEI changed no verdict"
    - SM p.16 (12 P1, P2): "fixed by step 6's records" and "close to fixed (step 6, with other tabs)"
13. **Verdicts that cannot be checked from the two documents:**
    - Steps 1–4 entirely (SM p.6: "summarised here only through their predictions").
    - Step 6, P1–P6.
    - Step 7, P2, P3, P5 and P8.
    - Step 8, P4, P7 and P8.
    - Step 9, P6.
    - Step 10, P2 and P7.
    - Step 11, P2 and P6.
    - Step 13, P5 and P6. The whole-lateral-surface and cap-eighth thresholds are reported nowhere.
14. **SM p.8:** "their numbers are the estimates the files recorded before the runs, by the means each file sets out".
    - Those means exist only in the archived files.
15. **SM p.8:** "After the failure was reported to the author, with a diagnosis of how the verdict moves with the statistic".
    - The diagnosis, and who reported it, exist only in the archive.
16. **SM p.20:** "by an independent check made apart from the drafting, which recomputed each number from the records".
    - The check is not described.
17. **SM p.33, Table S12:** "Kinetic draw ranked 5 (draw 188)", and likewise draws 83, 40 and 184.
    - These are archive indices and are never defined.
18. **SM p.5:** "in step 14, A1, A2 and A5, the paths its plan counts as the cap end's."
    - The labels are used before they are defined (at the end of S1), and the "plan" exists only in the archive.
19. **SM p.5:** "Upper-end crossings (step 9): the times at which the lumped neighbour crossed 255.7 °C in step 8's runs".
    - These are unreported runs, and "the plan does not say which window it meant" refers to archived text.
20. **SM p.3:** "the four drawn by rank in step 11 are those ranked 5, 50, 151 and 196 … in step 3's case".
    - The ranking rests on unreported runs.
    - The same applies at SM p.5: "over step 3's draws the kinetic posterior spread the hot spot's onset time far more".
21. **SM p.14 (10 P2):** "A0.2 is recorded before this prediction is scored, not before it is written."
    - The chronology can only be checked in the archive.
22. **SM pp.14–15 (10 P3, 10 P5, 11 P4):** truncated quotations of "the predictions file's analysis".
    - Example: "If the facing node reads within 4.9 K of the line node" … The full reasoning exists only in the archive.
23. **SM p.31:** "Six repeat another's configuration in a different step, two of them carried only to 332 s".
    - The six runs are not identified.
24. **SM p.13 (8 P1):** "the hot spot is close to 255.7 °C in several misses".
    - "Misses" is never defined (S1 defines only hits and false alarms), and the step-7 values are unreported.
25. **(borderline) SM p.6:** "the repository records each file's commit, the time of its push and the hash of each step's run list [1]."

**C. Overclaims**

No sentence says which neighbour model is right.

1. **MS p.1, title:** "a lumped neighbour needs less heat than a resolved one after strong triggers".
   - This is stated as a general finding. The evidence behind it:
     - one cell type in one rig;
     - resolved thresholds at one contact only;
     - posterior-mean kinetics and central properties;
     - three-dimensional support in only two tests with a non-zero lumped threshold;
     - the rest from a reduced model.
2. **MS p.1:** "that energy puts the resolved threshold above the lumped after strong triggers, at least 1.36 times in two three-dimensional searches".
   - The abstract does not say that p.25 admits "every comparison of the two thresholds above is at the posterior mean and the central properties".
   - The lumped threshold alone moves from 0.85 to 4.26 kJ over eight draws in PP-Exp3, and drops to zero in ST-Exp2 with the smallest specific heat.
   - The resolved threshold is never searched under draws (apart from PT-Exp4 at one energy) or at the low or high contact.
3. **MS p.1:** "vented heat calibrated with one neighbour needs a trigger-dependent correction for the other." **MS p.24:** "cannot be carried to the other without a correction whose sign depends on the trigger".
   - The sign change rests on two weak-trigger tests, only one of them searched in three dimensions, at the posterior mean only.
4. **MS p.26 (Conclusion 2):** "runs away as a whole at 1.49 and 1.72 times the lumped neighbour's threshold". Also on pp.12 and 24, and 0.85 for ST-Exp3.
   - These are presented as three-dimensional results, but they are the reduced model's values by construction. Those brackets opened ±5% around the cross-section's value and closed in their first two runs, so the midpoint is that value (p.12).
   - They equal the reduced-model values registered in advance (SM p.17, step 15 P3: "1.49, 1.72, … 0.85").
   - The three-dimensional model itself supports only 1.38–1.59 and 1.36–2.26.
5. **(borderline) MS p.1:** "afterwards reproduced all 151 archived three-dimensional outcomes."
   - The abstract leaves out that:
     - the outcomes are binary and at the central contact only;
     - the comparison was post hoc;
     - 82 of the 92 runaways are in two exploratory tests "far above any threshold";
     - runaway times differ by −5.5 to +34.5 s.
   - The same model then supplies 12 of the 16 resolved thresholds and every resolved need (p.25).
6. **(borderline) MS p.12:** "The three-dimensional model confirms this in the four tests it searched".
   - That is four tests with ±5% brackets, and in SP-Exp3 the reduced value fell outside the bracket (9.1% low).
7. **(borderline) MS p.13, heading:** "Why the three thresholds differ". **MS p.14:** "since the resolved cell's contact patch heats toward the trigger's temperature while its mean lags."
   - A mechanism is asserted from three no-delivery runs, yet p.24 concedes "these runs do not say how much each difference contributes".
   - The long-pulse statements ("the cell heats through", the ratio "accordingly falls") rest on PT-Exp1 alone.
8. **(borderline) MS p.14:** "The lumped threshold is consistent with an energy balance to an ignition temperature (Fig. 3b,c)."
   - Fig. 3b's slope failed the registered 150–300 J per kJ, and "the steeper fall is not explained here".
   - The 32 of 32 agreement uses a tolerance of at least 300 J, includes nine cases where both are zero, and shows a systematic offset with trigger strength at the low contact (SM p.30).
9. **(borderline) MS p.24:** "After a strong trigger the lumped neighbour … takes in more through the same contact".
   - Stated for any strong trigger, but shown in three tests without delivery (p.14).
10. **(borderline) MS p.23:** "a pack model that ignites a neighbour at one delivered share would reproduce some tests and not others".
    - No such model was run, and the same sentence allows that the spread may come from the fitted triggers.
11. **(borderline) MS p.1:** "a facing-side heat flux could, if the model is otherwise right". The same claim appears in the final sentence on MS p.26 and on MS p.24: "One measurement could decide between the readings".
    - The abstract and conclusion drop §4.3's own condition that the heat be resolved "well within the 1.7 to 4.3 kJ".
    - A decision would also depend on the chosen delivery region and shapes and on the fitted triggers.
12. **(borderline) MS p.10:** "so each upper bound is what the published inputs surveyed cannot be made to exceed."
    - The gas bound uses a crossflow correlation (not impingement) with hydrogen properties at 1000 K, below the roughly 1036 K film temperature.
    - The flame temperature is a module value cited second-hand (SM p.22, "cited in [9]").
    - The 225.8 kJ ceiling (p.20) adds another cell's heat of burning to this cell's ejecta.

**D. Other first-reading objections**

1. The abstract and Conclusion 2 say "at most 0.91"; §3.2 (p.13) says "0.81 to 0.90".
2. **MS p.1:** "at least 1.36 times in two three-dimensional searches and in 13 of 14 by a reduced model" can be read as saying the reduced model also gives at least 1.36. By Table S3 it gives about 1.15 in SP-Exp4 (7.08 against 6.15).
3. **MS p.20** cites "(Supplementary Table S11)" for the 32.7 and 75.8 kJ needs. Those values are in Table S7 and Section S11; Table S11 is the list of 151 runs.
4. **MS p.8, Table 2, "Shapes" row:** a stray glyph overprints "21.39 s".
5. **Undisclosed contributors:**
   - MS p.29: the "Declaration of generative AI and AI-assisted technologies…" heading has no text under it.
   - CRediT (p.28) lists no Software, Formal analysis, Data curation, Visualization or Writing – original draft for a sole author.
   - SM p.1 separates the author's "brief" from the study's predictions file, SM p.8 says a failure "was reported to the author, with a diagnosis", and SM p.20 refers to a check "made apart from the drafting".
   - Together these imply a second agent that is not disclosed.
6. **One-way trigger coupling (MS pp.4, 26):** the trigger's history is computed with a lumped neighbour and then imposed on the resolved one.
   - The resolved neighbour takes in 2.1–2.3 kJ less by 250 s (p.14), which is about 35 K of the trigger's 61.75 J/K.
   - A trigger beside a resolved neighbour would therefore run hotter. The bias favours the headline result, and the paper lists it only as a limit.
7. **Energy budget of the fitted triggers:** Ee = 3.105 Eb reaches 168.6 kJ (SM p.33), and Eb + Ee about 223 kJ. The cell's measured maxima are 89.34 kJ ejected and 110.8 kJ in all (Table 3).
8. **MS p.9:** the posterior-mean kinetics reach the internal-short rate at 199.8 °C, 56 K below the 255.7 °C used as the runaway criterion, and the paper says only "a difference not resolved here".
9. **SM p.8:** the failed calorimetry check of the draws was amended after the failure into one almost bound to pass ("So amended it passed").
10. **Pre-registration tally:**
    - 24 of the 42 failures were registered as expected to fail (e.g. SM p.14, "P3 fails whatever the runs give"), and four holds were registered as already fixed.
    - Verdicts were seen partway through step 11 (SM p.6).
    - So the 56 of 98 count (p.11) carries little evidential weight.
11. **Held-out test:** it uses "a need whose definition depends on the outcome" (p.11; SM p.29), which is leakage, and eight tests per split give little power.
12. **Figures 7c and 2:**
    - Fig. 7c (p.23) shows agreement in three of four tests by construction.
    - Fig. 2 places triangles and squares at bracket upper ends but circles and diamonds at midpoints.
13. **Timing of the resolved needs:**
    - The reduced model's runaway-time error (−5.5 to +34.5 s) exceeds the 10 s window that defines every resolved need.
    - Seven of the 32 resolved needs are "t" values, across which the run goes from no runaway to one up to 110 s early. Example: ST-Exp4, 231.8 s against 342 s (Table S7).
    - The measured time is a thermocouple's second spike, while the modelled time is a mean or lumped temperature reaching 255.7 °C.
14. **Convergence:**
    - The reduced models' grid was "not refined" (p.28).
    - The mesh checks cover peak rise or runaway time, not the threshold energies the paper reports (Table S4).
15. **PT-Exp4's history:**
    - The "lumped reading" of this history is judged with the resolved model's far face (pp.17, 24).
    - The model starts at 25 °C against the record's 32.2 °C.
16. **Non-propagated tests:**
    - With no delivery, the far face overshoots four non-propagated maxima by 13.8–56.3 K (p.15).
    - The 32.7 and 75.8 kJ "needs" run the model's neighbour away in tests that did not propagate, yet they count among the needs the bounds must reach (p.20).
17. **Choices a reviewer will question:**
    - The cell mass of 65 g is "assumed", while the Databank's cells weighed 68.05–68.52 g (Table 2).
    - The strong/weak cut (p.4) sits exactly where the ordering flips.
    - Neither Fig. 2 nor Table S3 states the contact conductance.
18. **Small inconsistencies:**
    - SM p.2 says "255.7 °C and above", while MS p.9 and SM p.6 say "255.7 to 302.1 °C".
    - SM p.6 says "The main text reports the results of steps 5 to 15", but step 6's results appear nowhere.
    - SM p.23 says "10.7 K", where 197.3 − 186.5 = 10.8.
    - MS p.18 says "20.9 K lower" and p.20 says "at most 20.7 K lower" for the same run.
    - Fig. 3d is labelled "5.0 kJ", against 5.04 kJ in the text and "5,045 J" on SM p.18.
    - Fig. 2's top axis prints "46" for 46.5 kJ.
    - The Fig. 6 legend reads "four shape".
19. **Figure readability:**
    - Fig. 4 needs the caption and Table S7 to be decoded, and its bar labelled "(b)" reads as panel b.
    - In Fig. 5 the jump of the 12.5 W run is not marked.
    - Fig. 1a calls the probe on the line of contact "facing", while S1 defines the facing node as the 0.33° node.
20. **Overloaded labels in S1:** A1 and A2 name step-13 models and step-14 paths, A4 names step-7 runs, and E* names both a threshold and step 12's time-matched energy.
21. **Prose:**
    - The text is very compressed throughout.
    - ε in Eq. (1) is undefined at first use.
    - "a lower and an upper bound were set" (p.10), though every lower bound is zero.
22. **Sources:**
    - The assumed inputs and the solver rest on an unreviewed Zenodo dataset [22].
    - [29] is a 2017 "tentative specification".
    - The dataset survey (SM S8) states no search method.

Not ready
