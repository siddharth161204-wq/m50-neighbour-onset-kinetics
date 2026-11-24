# The independent read of the rebuilt manuscript, read 8 (24 November 2026)

Brief 31, test 2, first round. A separate agent, new and with no sight of the work, of reads 1 to 7 or of the editor's reads, read only the built manuscript (35 pages) and supplement (49 pages) as PDFs, as built at commit 123d60d (identical to the PDFs of the submission set at c151ff0), with no other file, command or web access. Under the brief's changed test it sorted every item into three lists: numbers that cannot be traced to a table, a figure or a described computation (List 1); sentences that state more than the evidence shown, with the evidence each would need (List 2); and borderline items of either kind (List 3). The test passes if Lists 1 and 2 are empty. Its instructions are in `independent_prompt.md` beside this file. Its report, verbatim, follows.

---

Coverage: I read every page of manuscript.pdf (pages 1–35) and supplementary_material.pdf (pages 1–49), including all figures and tables.

List 1. Numbers that cannot be traced

1.1 Supplement p.1, opening paragraph and the first bullet of S1: "its fifteen steps" and "one of the study's fifteen stages, each with its own predictions file (Table S1)". What is missing: Table S1 (supp. p.6), S2 (p.5) and main text p.11 all give sixteen steps, each with its own predictions file. Nothing in either document supports fifteen.

1.2 Main text p.18: "and there, with every reactant at its initial amount, the low-temperature cathode reaction gives 73.3% of the reaction heat under the posterior mean". Here "there" means T_ign = 218.5 °C, with the trigger at the neighbour's own temperature. What is missing: the only source given is Table S17 (supp. p.44), and it pairs 73.3% with an ignition temperature of 230.4 °C computed with the trigger at 25 °C. The main text never uses that temperature or that condition, and no table or figure gives the share at 218.5 °C.

List 2. Overclaims

2.1 Abstract, p.1: "Over 21.4 s, … 4.45 to 7.54 kJ through the facing side runs the resolved neighbour away when the eight propagating strong-trigger tests did, and 0.26 to 5.96 kJ the lumped one". The same claim appears in Conclusion 2, p.28 ("At the tests' measured times … needs 4.45 to 7.54 kJ … and the lumped neighbour 0.26 to 5.96 kJ") and on p.24 ("each test's outcome and time fix how much…").
- What it claims beyond the evidence: in PT-Exp4 and ST-Exp4, no three-dimensional run reproduced the measured time. The lower ends of the brackets (7.062 and 5.319 kJ) never run away within 900 s. The upper ends run away at 250.8 s against a measured 272 s, and at 254.6 s against 342 s (Table S16, supp. p.42).
- The lumped neighbour in PT-Exp4 also stops at its threshold (4.85 kJ, marked t; supp. p.5).
- The body (p.13) says these times are "reproduced only within the bracket's width of the threshold". That pins down the threshold, not the time. Nothing shows that any energy inside those brackets gives 272 s or 342 s.
- Evidence needed: runs inside those brackets that run away within 10 s of the measured times. Otherwise the abstract and Conclusion 2 should be limited to six tests, with the other two stated as thresholds.

2.2 Supplement p.43 (S18) and the Table S17 caption (p.44): "Table S17 gathers the results that the main text and this supplement quote from runs or computations that no other table or figure shows".
- What it claims beyond the evidence: several results of exactly that kind are missing from Table S17:
  - Main p.9: the posterior-mean emulation's 179.3 °C and 199.8 °C, and the 164 draws with their 146.3–191.4 °C. These appear only in the text of S2 (supp. p.7).
  - Main p.12: the central-contact peaks of 191.9 and 192.2 °C at 33.2 kJ. These appear only in the text of S3 (supp. p.9).
  - Main p.16: the lumped neighbour's 204.2 °C at 11.32 kJ in PT-Exp1. This appears only in the text of S17 (supp. p.41).
  - In the supplement's own text: step 5's 191.5–192.3 °C and 159.4–162.1 °C (pp.7–8), and the step-9 and step-6 values (13.8–21.1 s; 226.14–226.75 °C). S3 itself says these "rest on runs that no table gives" (pp.8–9).
- Evidence needed: add those values and their runs to Table S17, or limit the sentence to what the table actually holds.

List 3. Borderline items

3.1 Abstract p.1 and Introduction p.2: "the heat a failing cell's neighbour receives, unmeasured in published tests" and "None of these sources measures what part of the ejected energy reaches a neighbour". Borderline because this sweeping negative rests only on the cited sources and a survey (S8 and Table S6, supp. pp.21–22) whose search method and coverage are not described.

3.2 Abstract p.1, p.3 and Table 2 (p.8): 21.39 s, described as "the mean of the two rise times read from the two published records (17.53 and 25.24 s)". Borderline because S7 (supp. p.21) shows the two times were not read off the records. They were computed as (tabulated maximum − an assumed 25 °C start) ÷ the mean heating rate printed for the figure's Section I: 661/37.70 and 605/23.97. The number is traceable only through S7, which describes the derivation differently from the main text.

3.3 Abstract p.1: "conduction and radiation run no resolved neighbour away at either energy". Borderline because, with the fitted triggers at the high contact, ten of the sixteen outcomes rest on the reactive cross-section alone, which was checked against the three-dimensional model only at the central contact (Table S15, supp. p.39; S16, p.38). Section 3.1 says so and the abstract does not, although those cross-section peaks (at most 199.2 °C) sit far below 255.7 °C.

3.4 Abstract p.1: "so here a heat share calibrated with one representation needs a trigger-dependent correction for the other". Borderline for three reasons:
- The ratios (at least 1.36, at most 0.91) were computed only at the posterior mean with nominal properties, and the sign reversal rests on the two weak triggers, whose fitted energies lie below the calorimetry range.
- The resolved threshold was never searched under a draw, yet Table S12 (supp. p.33) shows lumped thresholds moving widely under draws: PP-Exp3 ranges 0.85–4.26 kJ, and PT-Exp1's falls to (10.80, 11.15], overlapping its resolved bracket (10.24, 11.32].
- Sections 4.2 and 4.4 and Conclusion 3 carry the posterior-mean qualifier; the abstract does not.

3.5 Main p.11: "Of the 63, 43 held, seven of them known beforehand to be fixed, or nearly". Borderline because the two sources disagree on which seven. Table S2's expectations mark 12 P1–P4, 16 P4, 16 P7 and 16 P11 as fixed or nearly. S3 (supp. p.9) names 12 P1–P4, 15 P1, 16 P4 and 16 P7. That is eight predictions across the two lists, so the count of seven depends on a choice that is not stated.

3.6 Main p.11, supp. pp.5 and 21: "the files were not changed afterwards", "after which no code, rule or run changed" and "The rule was fixed before the runs it reads". Borderline because the documents show only push dates (Table S1, supp. p.6), so these claims rest on an archive the reader does not have.

3.7 Table 3 (p.15), p.13 ("3.88 to 7.67 kJ by the runaway") and p.24: the three-dimensional brackets over 240 s for PP-Exp2, SP-Exp2, PP-Exp1, SP-Exp3 and SP-Exp1. Borderline because the caption says "counted to the runaway", but the values follow from Table S16 only if its energies are read as totals counted to 10 s after the measured time, as the Table S7 caption (supp. p.23) says.
- Example, PP-Exp1: 7.588 kJ with a runaway at 164.1 s gives 5.19 kJ counted to the runaway, but 5.12 kJ counted to 162 s. Table 3 shows 5.12.
- So the "Difference (%)" column mixes two counting conventions. Under a single convention the percentages move by less than a point.

3.8 Main pp.18–20: four run results that appear only as unlabelled points or curves in Figs. 4d and 5, and not in Table S17:
- "191.2 to 192.4 °C" for the four kinetic draws. Fig. 4d's label gives only 188.3–192.4 °C, covering the draws and the aged SEI together.
- "221.1 °C" at a 17.5 K shift (Fig. 4d).
- "255.9 s" and "233.6 °C" for the 12.5 W hold (Fig. 5).
- "241.4 °C" for the 6.2 kJ/240 s run carried to 900 s. Table S14 (supp. p.36) lists that run only to 332 s, at 241.2 °C.
Borderline because the origin is shown only indirectly.

3.9 Main p.20 and Table 4 (p.22): "what the ejecta can release in this rig is at most 225.8 kJ" and "radiation can deliver at most 27.9 kJ". Borderline because:
- S6 (supp. p.18) calls these bounds "estimates of that most rather than strict limits".
- 89.34 kJ is the largest of ten Databank nail tests, not a value from this rig. The rig's fitted triggers imply ejecta of up to 168.6 kJ under the paper's own 3.105 ratio (Table S12).
- On the other side, Section 2.6 frames each bound as the most the published inputs allow, and larger inputs would only raise bounds that are already above every need.

3.10 Main p.24, p.26 and Conclusion 5 (p.29): "the cross-section's need lies 1.5% below to 8.6% above the three-dimensional bracket's midpoint, within the 10% registered". Borderline because each cross-section need is the upper end of a search bracket up to 0.5% of the test's ejected energy wide (Section 2.4, p.9; S9, supp. p.22). That is 0.62–0.84 kJ, or 8–18% of the needs, and Table 3 does not show these widths. The stated agreement is finer than the search resolves; for example, SP-Exp1's 5.96 kJ could lie about 12% lower.

3.11 Main p.27 (Section 4.4): "so triggers held within that range would raise the lumped needs after the thirteen and lower them after the two". Borderline because the trigger energy was shifted only for lumped thresholds, not needs, and only in three tests by ±2 kJ (Fig. 4b, p.18). Holding the triggers within 18.7–33.2 kJ would mean shifts of up to −21.1 kJ and +9.7 kJ. The direction is consistent with Fig. 4b and Section 3.1, but it was not computed for needs.

3.12 Main p.28 (Conclusion 1): "at least 29 K short of 255.7 °C at every contact conductance considered". Borderline because S3 (supp. p.9) reports step-6 runs at 33.2 kJ over 21.39 s at the high contact peaking at up to 226.75 °C, which is 28.95 K short. Section 3.1 and Table S17 round this to 226.7 °C and 29.0 K.

3.13 Main p.31 (Data availability) against reference [28] (p.35) and supplement reference [1] (p.46): "version 1.13.0 holds every result used here" versus "every result used here is in version v1.11.0, doi:10.5281/zenodo.24368356". Borderline because the documents name different archive versions as holding the results, and only v1.11.0 has its own DOI.

Verdict: Lists 1 and 2 are not both empty. List 1 has two items and List 2 has two items.
