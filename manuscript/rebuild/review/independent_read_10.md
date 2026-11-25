# The independent read of Brief 32's changed text, read 10 (25 November 2026)

Brief 32, test 2, first round. The reader was a separate agent, new to the work, that had seen none of reads 1 to 9 or the editor's reads. It read the changed text only:

- every changed passage of the manuscript, quoted with its page (`review/jes/changed_text_10.md`);
- the new letter for the Journal of Energy Storage.

It checked them against the manuscript built for that journal (35 pages) and the supplement (50 pages), both as PDFs at commit 029e28f. It had no other file, command or web access. Its instructions were those of reads 8 and 9 (`independent_prompt.md`), narrowed to the changed text (`review/jes/independent_prompt_10.md`). Its report follows verbatim.

---

Coverage: I read changed_text.md and cover_letter.txt in full, all of manuscript.pdf (pages 1–35) and all of supplementary_material.pdf (pages 1–50). I could not open any cited outside work, so claims that rest only on a citation went unchecked. That includes the reassigned citations in the Introduction's second paragraph ([1] for "one temperature", [3] and [4] for "resolve it"), and someone should check them against the papers themselves.

List 1. Numbers that cannot be traced
none

List 2. Overclaims
2.1 Section 4.1, first paragraph, third sentence (manuscript p. 24): "Under every delivery shape the needed energies are at most about a quarter of the Databank's median ejected energy for this cell, 76.74 kJ".
- What it claims beyond the evidence: The bound is stated for every delivery shape. The sentence includes the weak-trigger test ST-Exp3, because its lumped maximum of 12.3 kJ is ST-Exp3's (12.26 kJ over 240 s, Table S7). For ST-Exp3 under the 360 s delivery, though, no resolved need was found:
  - With 25.6 kJ (33 % of 76.74 kJ), the earliest runaway on the search's grid still came at 196.4 s, against the measured 177 s (Table S7 caption, supplement p. 23; Section 3.2, p. 13).
  - The three-dimensional run at 25.19 kJ over 360 s ran away at 205.5 s (Table S14, supplement p. 37).
  - The sentence measures the resolved neighbour's deliveries "in all over their shapes". On that measure the need in this case is above 25.6 kJ, about a third of 76.74 kJ, not a quarter.
  - The 5.3 to 25.4 % range is itself traceable: it is Table S7's "Resolved, in all" column (4.06 to 19.52 kJ) divided by 76.74 kJ, and Section 3.6 gives 4.1 to 19.5 kJ. It leaves out this case without saying so.
  - Counted only to its runaway, that 25.6 kJ delivery is about 14 kJ (18 %), so the bound might hold on that measure. No need was found to show it.
- What evidence it would need: either the ST-Exp3 360 s search carried past 25.6 kJ until a need is bracketed, or the claim limited to the test-and-shape pairs where a need was found, with this exception stated.

List 3. Borderline items

3.1 Abstract (p. 1) and letter, paragraph 4 (line 9): "With the trigger's [failing cell's] energy fitted or held to 33.2 kJ, conduction and radiation run no resolved neighbour away." Why it is borderline: Section 3.1 and Table S15 show the fitted-trigger half only under the posterior-mean kinetics and nominal properties; at the high contact ten of the sixteen outcomes rest on the reactive cross-section alone; and the resolved runaway is read by the mean, although the hottest point crosses 255.7 °C in eight fitted-trigger tests. The sentence states none of these limits, while the abstract does add "At nominal inputs" to its next result.

3.2 Abstract (p. 1), "calorimetry's largest, 33.2 kJ", and letter, paragraph 4 (line 9), "33.2 kJ, the most that calorimetry gives for this cell". Why it is borderline: the documents trace 33.2 kJ only to the largest body energy in the Battery Failure Databank's ten nail tests of this cell (p. 4; Table 2), so "calorimetry" as a whole stands in for one ten-test set.

3.3 Abstract (p. 1), "in a direction that goes with the trigger's energy", and letter, paragraph 5 (line 11), "For readers who model propagation in modules, ... in a direction that goes with the failing cell's energy". Why it is borderline: the documents show a split between two groups rather than a relation to energy. In three dimensions the ratio is above 1 after four strong triggers and below 1 after two weak ones (Table 3), and the reactive cross-section shows the same split in all sixteen tests (Section 3.3). That evidence holds only at the posterior mean and nominal properties, uses fitted trigger energies the paper itself suspects are inflated, carries a one-way-coupling bias toward the difference that the paper says was not computed (Section 4.4), and comes from no module or pack model. The changed sentence in Section 4.1 limits the same finding to "the six tests whose threshold was bracketed in three dimensions". The "may" hedges the correction but not the direction.

3.4 Table 4, radiation row (p. 23): "a flame held on the vent's axis, about 0.85 kJ by ray tracing (Supplementary Section S6)". Why it is borderline: S6 gives only the ray-traced share (about 0.0038). The 0.85 kJ appears only in Sections 3.6 and 4.3, as that share of the 225.8 kJ total, which assumes the whole release radiates from that flame. The row says neither, nor whether the value is a total or falls within 21.4 s.

3.5 Fig. 5 caption, first sentence (p. 21): "the circles mark where the measured jump and the model's jumps begin". Why it is borderline: the black circle sits at 271.5 s and 197.3 °C, where Fransson et al.'s figure marks the jump. The caption's own jump rule (its last sentence), applied to the record, puts the start at 267.5 s and 186.5 °C (S7), which moves the comparison from 36.8 K to 47.6 K. These words are in the quoted sentence but outside the phrase that changed.

3.6 Letter, paragraphs 6 and 7 (lines 13 and 15): the manuscript number "EST-D-26-19130", the statement that it "shares no results or text with this one", and "B.Tech 2026". Why it is borderline: no table, figure or computation in the documents can trace or confirm an identifier, a degree year or a declaration. I put them here rather than in List 1 because they are not results, but the manuscript number should be checked against the journal's system.

Verdict: Lists 1 and 2 are not both empty. List 1 is empty, but List 2 has one item (2.1).

---

## What changed after read 10

List 2 was not empty, so the test was not passed. Under the brief, the one overclaim was mended, and a second fresh agent read the changed text once more (read 11, `independent_read_11.md`).

Mended (commit after 857c1ef). The mends kept main text and appendices within 8,000 words (7,995), and both numbers checks stay at 0 failures.
- 2.1. Section 4.1's sentence no longer says "Under every delivery shape". It now limits the bound to the cases where a need was found and names the one where none was: "Except ST-Exp3's resolved neighbour with the 360 s delivery, for which no need was found (Section 3.2), the needed energies are at most about a quarter of the Databank's median ejected energy for this cell, 76.74 kJ". The resolved figure is now that of "the deliveries at the resolved neighbour's needs". The sentence before Brief 32, "Either way ...", had the same reach without saying so. Brief 32's opening made it explicit, and so made it visible.
- 3.4, in a table, at no cost in words. Table 4's radiation row now gives the ray-traced share and what the 0.85 kJ is: "a flame held on the vent's axis would send the facing half about 0.38 % of its radiation, by ray tracing (Supplementary Section S6), about 0.85 kJ of the 225.8 kJ in all".
- 3.5, in a caption, at no cost in words. Fig. 5's caption now says what the circles mark: "the measured jump where the published figure marks it and the model's jumps where they begin by the rule below". The black circle is drawn at 271.5 s and 197.3 °C, where Fransson et al.'s figure marks the jump (`src/make_rebuild_figures.py`), not where the caption's rule puts its start.
- 3.2, in the letter only. The letter now says "the most that the Battery Failure Databank's calorimetry gives for this cell". The abstract keeps "calorimetry's largest", for want of words.

Not mended, with the reason each stays.
- 3.1 (the abstract's "fitted or held to 33.2 kJ" without read 9's 3.1). This is item 1(d) of the brief, to go in only if words remained, and the abstract is at 250 of 250. Section 3.1 states the limit.
- 3.3 ("in a direction that goes with the trigger's energy"). These are the brief's own words for item 1(a). The abstract's preceding sentence gives the split they summarise, after four strong triggers searched in three dimensions and after both weak ones, at nominal inputs.
- 3.6 (the manuscript number EST-D-26-19130, the statement that it shares nothing with this manuscript, and the degree year). These are facts about the author, not results, and no document can trace them. The number is the one the journal's system gave on 26 October 2026, as the project's record of that day and the brief both give it.
- The reader's coverage note. The reassigned citations could not be checked from the two PDFs. They were checked against the references themselves before the read, as the state document of 25 November records: Feng et al. 2015, Mishra and Jain 2021, Hoelle et al. 2023, Coman et al. 2017 and Kim et al. 2021.
