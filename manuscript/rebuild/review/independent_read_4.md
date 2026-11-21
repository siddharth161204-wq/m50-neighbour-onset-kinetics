# The independent read of the rebuilt manuscript, read 4 (21 November 2026)

A separate agent, new and with no sight of the work, of reads 1 to 3 or of the editor's reads, read only the built manuscript (32 pages) and supplement (35 pages) as PDFs, as built at commit 5f19074, after read 3's fixes and before those of commits 8d93cfb (the kinetic draws' failed calorimetry check stated) and 32de188 (the sixth editor's read), with no other file, command or web access, and listed untraceable numbers (A), archive-dependent sentences (B), overclaims (C) and other first-reading objections (D), under the instructions of reads 2 and 3, changed only in the page counts. Its report, verbatim, follows; the changes made after it are in DECISIONS.md D186 (5).

---

I read both documents in full, figures included, and nothing else: manuscript.pdf (32 pp.) and supplementary_material.pdf (35 pp.). Below, MS p. is a manuscript page and SM p. a supplement page. Items marked (borderline) are listed because you asked me to err toward listing.

**A. Untraceable numbers**

A1. MS p.6, Fig. 1 caption: "five surface probes lie at mid-length, at 0, 0.33, 88.3, 94.4 and 180°"
- Nothing says where 0.33°, 88.3° and 94.4° come from (mesh nodes?).
- SM S1 (p.2) names a "facing node" and a "90 degree node" but gives no angles.
- The "two side probes" readings on MS p.17 (235.5 and 235.8 °C) depend on them.

A2. MS p.14: "the upper end of an earlier bracket on the lumped threshold, 4.66 to 5.04 kJ"
- No step, search or table gives this bracket. Table S3 (SM p.18) gives PT-Exp4's lumped bracket as (4.66, 4.85].
- The 5.04 kJ value carries a lot: the kinetic-draw test, the 17.5 K shift, Fig. 3d, Fig. 5, the 16.8 K RMS on MS p.17, Conclusion 3, and Table S2 step 15 P7 ("5,045 J").

A3. MS p.15: "at the low contact three of the four stay below their maxima (Supplementary Table S2, step 11)"
- The cited row (SM p.14, step 11 P4) holds only the verdict "failed, foreseen".
- The count of three appears nowhere.

A4. MS p.25: "was at most 1.80 kJ under two kinetic draws and zero with the smallest specific heat"
- The same applies to "PP-Exp3's ran from 0.85 to 4.26 kJ over the eight draws".
- Both are cited to Table S2 step 11, which holds verdicts only, and no table or figure shows the values.
- (Borderline: the text does state them as step 11 results.)

A5. MS p.14, also SM p.3: "those of rank 5, 50, 151 and 196 of 200 by their onset at the hot spot". The rule that picked these four ranks is not stated. (borderline)

A6. SM p.2: "138.5 °C, the peak of the separator's melting at 5 K min−1 under the posterior-mean kinetics". The simulated 5 K/min scan that gives this value is described nowhere. (borderline)

A7. MS p.9: "Over the 200 draws below, the exotherm onset runs from 146.3 to 191.4 °C (central 95 %)". SM S2 (p.7) describes the calorimetry emulation for the posterior mean only. (borderline)

A8. MS p.21, Table 3, gas row: "at most twice the whole-cylinder mean on one half". The factor of 2, which scales the 195.5 kJ bound, has no source or derivation. (borderline)

A9. MS p.5: "The sector, 45° either side, is that of the earlier two-cell study [22]". Its only source is the author's own archived dataset, and unlike the other [22] values in Table 2 it is not flagged as an assumption. (borderline)

**B. Archive-dependent sentences**

B1. MS p.11: "eighteen in four steps on the earlier two-cell study's geometry [22], not reported here"
- These 18 verdicts count toward the 98/56/42/24 tallies and appear in Table S2.
- Neither document reports the runs behind them (SM p.5: "summarised here only through their predictions").

B2. MS p.11, also SM p.19: "read again by an independent check made apart from the drafting"
- The separate code, the run records and the check exist only in the archive.
- Who or what did the check is never said.

B3. MS p.14: "the upper end of an earlier bracket on the lumped threshold". The step that produced this bracket is not named.

B4. MS p.17: "a run made in an earlier step and stopped at 332 s". The step is not named.

B5. MS p.25: "In an earlier step's coarser searches under four kinetic draws and under four thermal draws". The values exist only in the archive.

B6. MS p.15 and p.25: "(Supplementary Table S2, step 11)". The main text never says in plain words what step 11 was, and the pointer leads to a verdict, not to the result.

B7. SM p.3: "by the time of their onset at the hot spot in step 3's passive case". "Passive case" is not defined, and step 3's runs are not reported.

B8. SM p.1: "Some expectations cite runs of earlier steps that neither document reports; their records are in the archive."
- Examples: SM p.11 step 7 P1, "step 6 ignited the hot spot only at the Databank's total energy".
- SM p.11 step 7 P4, "the hot spot passed 138.5 °C in every step 5 run".
- SM p.12 step 8 P1, "close to 255.7 °C in several misses"; step 8 P4, "step 7 had one of eight within 60 s".
- SM p.12 step 9 P1, "crosses at 11.9 to 18.5 s"; step 9 P2, "ST-Exp3's lies at 61.4 s".
- SM p.13 step 9 P8, "step 7: the aged SEI changed no verdict".
- SM p.15 step 12 P1–P4, "fixed by step 6's records" and "step 9's records".
- The "foreseen" verdicts also rest on "the predictions file's analysis", a file that is only in the archive.

B9. SM p.7: "their numbers are the estimates the files recorded before the runs, by the means each file sets out". The means are only in the archive files.

B10. SM p.5: "the repository records each file's commit, the time of its push and the hash of each step's run list"
- The evidence for pre-registration, and for "after which no code, rule or run changed", can be checked only in the repository.
- The same holds for "178 of its 216 records to test a figure's script".

B11. SM p.10, Table S2 step 5 P7: "reversing step 3's onset finding". That finding is never stated in plain words.

B12. SM p.12, step 9 P2: "seven upper-end crossings lie inside the window". "Upper-end crossings" and "the window" are not defined in S1.

B13. SM p.14, step 10 P7: "No ranked model quantity correlates with the measured outcome or time". "Ranked model quantity" is not defined.

B14. SM p.16, step 14 P2: "the largest need among the seven matched times". "Matched times" is not defined.

B15. MS p.8, Table 2 caption: "The two-cell geometry and its solver are those of an earlier, archived study by the author [22]". The solver is documented only in an archived dataset, and the time-step limits are given nowhere.

B16. MS p.20: "against the 151 three-dimensional runs of the sixteen tests made in earlier steps". The runs are not listed one by one: Table S11 gives only counts and energy ranges. (borderline)

**C. Overclaims**

C1. MS p.1, title: "a lumped neighbour needs less heat than a resolved one after strong triggers"
- The title states this as a general result.
- It is a model-against-model comparison for one cell pair in one rig.
- It is bracketed in three dimensions in only two tests (in the third, SP-Exp3, the lumped threshold is zero); the rest comes from the reactive cross-section.
- MS p.25 says "every comparison of the two thresholds above is at the posterior mean and the central properties", yet step 11 moved the lumped thresholds by up to 3.4 kJ across draws.

C2. MS p.1: "In this model, heat calibrated with one neighbour needs a trigger-dependent correction for the other."
- MS p.24 adds "a correction whose sign depends on the trigger".
- The sign change rests on two weak-trigger tests, and only ST-Exp3 is bracketed in three dimensions.

C3. MS p.1: "kinetic uncertainty spans 6.1 K of ignition temperature", set beside the 17.5 K shift.
- Conclusion 3 (MS p.26) repeats it: "every rate law would have to be shifted by more than 17.5 K, against a 6.1 K span".
- MS p.15 itself calls the span "a different measure", with "an expectation not computed here".
- The posterior-mean kinetics already miss the source's internal-short band by 56 K (MS p.9).
- The four-draw test is informative for only two draws: under the other two the lumped neighbour does not run away either (MS p.15).

C4. MS p.24: "the reactive cross-section gives the resolved reading at a small part of the cost (Section 3.6)"
- This is a general claim of adequacy drawn from a comparison the paper says was made after the runs (MS p.20).
- That comparison is at the central contact only, and 82 of the 92 runaway runs are far above any threshold.
- One near-threshold run peaks 20.7 K low, and runaway times lag by up to 34.5 s.

C5. MS p.12: "and for the resolved reading under the posterior mean with the fitted triggers". At the high contact this rests, in ten tests, on the cross-section, which the same paragraph says "was checked only at the central contact".

C6. MS p.23: "Read through a resolved neighbour, the needs at the measured times fall within 4.1 to 8.1 kJ"
- MS p.15 makes the same point: "the needs fall in a narrower band".
- These are the cross-section's needs, matched to the measured time within 10 s, although the cross-section's runaway can lag the 3D model by 34.5 s.
- The band is narrower only as a ratio; in kJ the two widths are 4.0 and 5.8.
- The wording implies the resolved reading fits better.

C7. MS p.23: "a pack model that ignites a lumped neighbour at one delivered share would reproduce some tests"
- The point is applied to the lumped reading only, though the resolved needs also span 4.1–13.8 kJ.
- The spread rests on fitted triggers, and MS p.15 says "much of what they carry may be the trigger's energy".

C8. MS p.13: "falls below them for the longer ones, as heat spreads along the layers" (and the same claim on MS p.27).
- The mechanism is asserted without being isolated.
- The skin and cross-section models also differ in curvature, can, contact, wedge, trigger conduction and losses.

C9. MS p.14: "it should fall as the trigger's body energy rises, and it does, by 393 to 456 J per kJ"
- The direction would follow from any conduction model, so it is weak support for the energy-balance picture.
- The registered range of 150–300 J/kJ failed.
- The main text omits the two-body model's offset that depends on trigger strength (SM p.28).

C10. MS p.24: "After a strong trigger the lumped neighbour ... takes in more through the same contact". This is generalized from three no-delivery runs (MS p.14). (borderline)

C11. MS p.1: "The one published record of a propagating neighbour fits neither"
- The body says "fits neither reading cleanly" (MS p.17).
- It is one test, and its trigger ruptured its sidewall, which the model does not represent.
- (borderline)

C12. MS p.1: "The tests cannot decide; a facing-side heat flux and the thermocouple's angle could, if the other inputs stand."
- The closing paragraph (MS p.26) repeats this.
- MS p.24 is narrower: only the heat flux could decide, and only if measured to well within 1.7–4.3 kJ.
- By the post hoc reading on MS p.17, every probe reads at least 234.1 °C when the jump begins, so no thermocouple angle closes the 37 K gap.
- (borderline)

C13. MS p.1: "Propagation models treat a lithium-ion cell as one temperature ... calibrating on tests the vented heat reaching a neighbour". This generalizes across the field; the introduction cites only some models that represent vented heat ([2], [5]). (borderline)

C14. MS p.10: "so each upper bound is what the published inputs cannot be made to exceed"
- This holds only for the sources surveyed.
- For example, the 1500 °C flame is "cited in [9], p. 2", and the factor of 2 in A8 has no source.
- (borderline)

**D. Other first-reading objections**

D1. Declarations and authorship
- MS p.29: the "Declaration of generative AI and AI-assisted technologies" heading has no statement under it.
- MS p.28: the CRediT statement omits Writing – original draft, Software, Formal analysis, Data curation and Visualization.
- Together with the unidentified "independent check" (B2), an editor will ask who drafted the text, wrote the code and did the checking.

D2. PT-Exp4's lumped threshold appears as (4.66, 4.85] in SM Table S3 but as 4.66–5.04 kJ on MS p.14, p.17 and in Figs. 3d and 5. Conclusion 3's "energy with which the lumped neighbour does" is 5.04 kJ, not the tabulated threshold.

D3. The abstract's "37 K" (also MS p.24) compares the model's jump, found by the paper's rule, with the onset the figure marks. Read by the same rule on both sides, the gap is 47.6 K (MS p.17; SM p.22).

D4. MS p.9: the posterior-mean kinetics reach the source's internal-short rate at 199.8 °C, 56 K below that event's band, "a difference not resolved here". Yet the band's lower edge, 255.7 °C, is the runaway level of all three criteria.

D5. MS p.10 says "Four reduced models", then describes five: skin, cross-section, ignition temperature, two-body and reactive cross-section.

D6. MS p.11: the 5,248 runs with the body energy held to calorimetry used 10 or 30 s releases, and some used 20 or 30 °C ambients (SM p.7). Every other result uses the 21.39 s release, so "under every kinetic draw" (MS p.12) holds only for those releases.

D7. Inconsistencies around the Battery Failure Databank and the earlier study
- MS p.4 and SM p.7 refer to "ten nail tests" (smallest and median body energy 18.67 and 25.88 kJ).
- SM p.3 refers to "seventeen tests" (8.75, 21.5 and 33.2 kJ).
- SM p.3 also says "a busbar of 100 to 500 mW K−1" and then lists 5–500 mW/K.
- It says "33.2 or 21.5 kJ" and then lists three body energies.

D8. Fitted trigger energies
- The fitted triggers reach 54.3 kJ.
- The ejected energy, taken as 3.105 × fitted Eb, reaches 168.6 kJ, nearly twice the Databank's largest ejecta (89.34 kJ) and above its largest total (110.8 kJ).
- That ejected energy still sets every search grid and fraction.
- With no delivery at all, the model already overheats four of the five low-maximum non-propagated neighbours by 13.8–56.3 K (MS p.15).

D9. MS p.14 reports the two-body model within tolerance in "all 32 searches". It omits the offset reported on SM p.28 (+0.25 to +0.48 kJ after strong triggers, −0.28 and −0.44 after weak ones). The 300 J floor lets PT-Exp2 pass at 0.29 kJ against a bracket of (0.09, 0.11].

D10. The held-out test (MS p.11, p.15; SM p.28) includes a "need" predictor that is defined from the very outcome it predicts. With eight cases per fit, it has little power to detect the registered gain of 0.1.

D11. For two non-propagated tests flagged as exploratory, the far-face "needs" (75.81 and 32.67 kJ) are energies at which the model's neighbour runs away; Table S11 shows all 82 such runs ran away. Values that imply runaway cannot stand for non-propagation, yet they enter the held-out test and the radiation count on MS p.20.

D12. Fig. 3d (MS p.16) draws the 6.1 K span from zero on the axis of rate-law shift, inviting the comparison that C3 says was never computed.

D13. MS p.12: the 3D searches opened 5 % either side of the cross-section's value, so three of the four 3D midpoints equal that value by construction. The abstract's 1.49 and 1.72 are therefore the cross-section's ratios; the 3D runs only bound them to within ±5 %.

D14. Time matching for the needs
- Needs require the runaway within 10 s of the measured time (MS p.9), but the cross-section lags the 3D model by up to 34.5 s.
- 7 of the 32 strong-trigger needs are marked t, with runaways up to 110 s early (ST-Exp4: 231.8 s against 342 s, SM p.25).
- Fig. 4a does not mark which needs are t values or which are interpolated (b); the b mark is not defined in the Methods.

D15. In the parallel tests the neighbour's own discharge (up to 15.6 kJ within 21.4 s, MS p.10) is as large as the needs, yet it is not modelled. This confounds the parallel tests' needs and the series/parallel comparison.

D16. The 360 s delivery outlasts the "longest combustion, about 300 s" that SM p.20 takes as the window in which a path of the ejecta can act.

D17. MS p.17 says the cross-section's registered value "held", although its peak (220.5 °C) was 20.9 K below the 3D peak (241.4 °C), and Table S2 records no verdict for it.

D18. Reproducibility gaps
- The time-step limits are never given.
- The skin model's linear surface-loss coefficient is not given (MS p.27).
- The processor behind the run times on MS p.23 is not named.
- The cell mass is "assumed" at 65 g although the cited specification [29], itself a "Tentative specification", would give it.

D19. Minor inconsistencies
- MS p.20's "twelve ... needs" leaves out the nine resolved needs without saying so.
- On MS p.12 the time at which the 22.4–22.6 kJ is counted is not stated.
- Six of the 151 archived runs repeat another run's configuration (SM p.30).
- SM p.22 says the inputs cover the M50 "without an invented value", but Table 2 holds several assumed values.
- MS p.25's "ends of the roll's published ranges" are in fact the extremes of 30 Latin-hypercube draws (SM p.3).
- MS p.11 calls four holds "known", but SM p.15 step 12 P2 says "close to fixed".
- In Table S2, the steps 1–2 central estimates are not attributed to either the brief or the predictions file.
- MS p.12 says "either reading" where there are three readings.

D20. The pre-registration is self-hosted, and the model changed after failed steps: steps 5–6 failed 12 of 14 predictions, and the per-test triggers, the delivered heat and the resolved-mean criterion came later. A reviewer will ask which modelling choices were fixed before the data were seen.

D21. Further points of physics and method
- The strong/weak split (MS p.4) has only two weak tests, yet it carries the title.
- Lumped brackets up to 1.7 kJ wide (SM p.18) are comparable to the 1.7–4.3 kJ gap between readings.
- The gas bound uses hydrogen's properties at 1000 K without saying why.
- With the trigger above the neighbour (SM p.20), buoyant gas rises away from the neighbour.

D22. Presentation
- The prose is very dense, and the text inside Figs. 2, 4 and 6 is very small.
- The label in Fig. 1a, "releases its body energy over 21.4", appears to be cut off.
- In Fig. 3c the labels overlap the bars.
- The Discussion compares the results with only one published estimate ([12]).

Not ready
