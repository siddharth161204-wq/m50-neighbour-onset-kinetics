# The independent read of Brief 32's changed text, read 11 (25 November 2026)

Brief 32, test 2, second round. A separate agent, new to the work and with no sight of reads 1 to 10 or of the editor's reads, read the changed text only: every changed passage of the manuscript, quoted with its page (`review/jes/changed_text_11.md`), and the letter for the Journal of Energy Storage. It checked them against that journal's manuscript (35 pages) and the supplement (50 pages) as PDFs, as built after read 10's mends (the texts of commit cbee8ff), with no other file, command or web access, under read 10's instructions with the paths changed (`review/jes/independent_prompt_11.md`). The container that ran the session was restarted while it read; it was resumed from its own saved transcript, with its files unchanged, and finished. Its report, verbatim, follows.

---

Coverage: I read changed_text.md and cover_letter.txt in full, then re-read both after the restart and found them unchanged. Before the restart I read every page of both PDFs: manuscript.pdf pages 1–35 and supplementary_material.pdf pages 1–50. The cited papers were not available to me, so I could check the Introduction's changed citations only for whether they resolve to references [1]–[5] (they do), not for what those papers contain.

List 1. Numbers that cannot be traced
none

List 2. Overclaims
none

List 3. Borderline items

3.1 Abstract, fourth sentence ("Most exceed calorimetry's largest, 33.2 kJ"), and the letter paragraph beginning "With the failing cell's energy" ("33.2 kJ, the most that the Battery Failure Databank's calorimetry gives for this cell"). Why borderline: 33.2 kJ traces only as the largest body energy in the Databank's ten nail tests (Section 2.1, Table 2), and neither text says "body", while the manuscript gives 110.8 kJ as the most calorimetry measured for this cell in all and 89.34 kJ for its ejecta (Table 4, Supplementary Table S5), so as worded the number can be read as the wrong quantity.

3.2 Abstract, fifth sentence, and the same letter sentence: "With the trigger's energy fitted or held to 33.2 kJ, conduction and radiation run no resolved neighbour away." Why borderline: it holds under the paper's resolved criterion, the mean reaching 255.7 °C (Section 2.2), which neither text defines, even though with the fitted triggers the hottest point does pass 255.7 °C in eight tests (Section 3.1); for the fitted triggers it is also shown only under the posterior-mean kinetics, and ten of the sixteen high-contact outcomes rest on the reduced cross-section alone (Section 3.1, Supplementary Table S15).

3.3 Abstract, eighth sentence, and the same letter paragraph: "at least 1.36 times the lumped one after [the] four strong triggers searched in three dimensions". Why borderline: of the four, SP-Exp3's lumped threshold is zero, so it has no ratio (Section 4.2 counts three tests), and ST-Exp4's bracket was read from its need's two runs after they were made, not from a threshold search (Section 3.3, Supplementary Section S17); the 1.36 itself is PP-Exp2's 6.51/4.77 in Table 3.

3.4 Abstract, ninth sentence; Section 4.1, the new second half of the sentence that names the class of models; and the letter paragraph beginning "For readers who model propagation in modules": a share calibrated with lumped cells "may (therefore) need correcting ... in a direction that goes with the trigger's [failing cell's] energy". Why borderline: the direction rests on four strong and two weak triggers bracketed in three dimensions (sixteen through the reduced cross-section), all at nominal inputs and on fitted trigger energies that Sections 2.1 and 4.4 say may be too high, and no pack or module model was calibrated or run; Section 4.1 limits the direction to those six tests, but the abstract and letter state it as a general dependence, and the letter offers it to module modellers.

3.5 Section 4.1, third sentence: "the needed energies are at most about a quarter of the Databank's median ejected energy". Why borderline: this holds for the nine propagated tests' needs under the four delivery shapes, but the sentence sets aside only ST-Exp3's 360 s case, while the needs of the two non-propagating tests with exploratory maxima (PT-Exp2, SP-Exp4), which Section 2.4 also defines as needs, are 32.67 to 115.30 kJ or not reached at all (Supplementary Table S7).

3.6 Section 4.1, third sentence: "carry 5.3 to 25.4 % of it in all over their shapes". Why borderline: the percentages appear nowhere else and come only from dividing the 4.1 to 19.5 kJ of Section 3.6 by 76.74 kJ; the passage cites neither. That range is Supplementary Table S7's "Resolved, in all" column (4.06 to 19.52 kJ), which holds the reactive cross-section's deliveries, not the three-dimensional model's.

3.7 Table 3 caption, new clause: "a bracket 0.5 % of the test's ejected energy wide". Why borderline: Supplementary Section S17 and Section 3.7 (0.62 to 0.84 kJ) give the width as 0.5 %, but Supplementary Section S9 says each need search stops once its bracket is narrower than 0.5 %, so it is unclear whether 0.5 % is the width or a bound on it. The Difference column itself does recompute from the unrounded runs in Supplementary Table S16.

3.8 Table 4, radiation row, new words: "about 0.85 kJ of the 225.8 kJ in all". Why borderline: it is the 0.38 % share times 225.8 kJ, which with the rounded share gives 0.86 kJ, so 0.85 rests on an unrounded share that is not shown; it also counts all 225.8 kJ as radiated (a radiant fraction of 1, under Supplementary Section S6's rule for fractions no source gives), which the row does not say.

3.9 Letter, the paragraphs beginning "A separate manuscript" and "I am a mechanical engineer": "EST-D-26-19130" and "B.Tech 2026, COEP Technological University, Pune". Why borderline: these are an identifier and biographical facts, not results, and nothing in the documents can confirm them, nor the statements that the other manuscript shares no results or text with this one and that this one is not under consideration elsewhere. They go here rather than in List 1 because they are not results, but they should be checked before sending. The manuscript does confirm the independent affiliation, no funding and no competing interests.

Verdict: Lists 1 and 2 are both empty. Every other number in the changed passages and the letter traced to the tables, figures or computations the documents give; I recomputed the Table 2 rise times (17.53, 25.24 and 21.39 s), the Table 3 differences and the 27.9 kJ bound. List 3 holds nine borderline items.

---

## What changed after read 11

Nothing. Lists 1 and 2 are empty, so the test passed. The brief says that after the second read the work stops and is reported, whatever the result. The nine borderline items therefore stand as they are. Each is set out in the state document of 25 November with what it would take, so that the main chat can decide. Three of them could be mended in the main text at a cost of at most two words, within the 8,000 (7,995 now):

- 3.5: "the needed energies" could become "the propagated tests' needs".
- 3.6: the sentence could point to Section 3.6.
- 3.8: Table 4 could say that the whole release is taken as radiated.

Two would need words that the abstract, at 250 of 250, does not have: 3.1 ("body energy") and 3.2 (read 9's 3.1). Three rest on the brief's own wording or on pre-existing text:

- 3.3: the abstract's four tests include SP-Exp3, whose ratio is unbounded above.
- 3.4: the direction, in the brief's words.
- 3.7: the caption's "0.5 % wide", unchanged since Brief 31.

The last, 3.9, consists of facts about the author that no document can trace. The manuscript number is the one the journal's system gave on 26 October 2026, and the earlier version of this study, submitted on 17 November to the Journal of The Electrochemical Society, was declined without review on 19 November, so the manuscript is under consideration nowhere.

## After Brief 33 (26 November 2026)

Brief 33 mended four of the nine items, and five stand: 3.2, 3.3, 3.4, 3.7 and 3.9.
- 3.5: Section 4.1's "the needed energies" became "the propagated tests' needs".
- 3.6: the same sentence now points its 5.3 to 25.4 % to Section 3.6.
- 3.8: Table 4's radiation row says that the whole 225.8 kJ is taken as radiated.
- 3.1: the abstract says "calorimetry's largest body energy, 33.2 kJ", and the letter says "the largest body energy that the Battery Failure Databank's calorimetry gives for this cell". The abstract's two words were freed in its first sentence, where "or a temperature field (resolved)" became "or many (resolved)", which still defines the term against "one temperature (lumped)". That wording was not mended by any of reads 8 to 11.

No further read was made.
