# Stage 15: the independent read (check V5)

A separate agent that had not seen the work being produced read Stage 15 at commit 9f69150. It recomputed everything from the records with its own read-only scripts and edited nothing. Its report follows as it gave it, with only its ranges written with "to". Line numbers refer to the files at 9f69150. What was done about each finding is in DECISIONS.md D181. None of the findings moves a verdict.

---

The scorecard, the Part B chains and the C1 table all reproduce. The read found 31 discrepancies: most are small, but six statements in the texts are not supported by the records. The main ones are the following.
- The B3 (a) history score's window ended at the end of the stop step (182.0 s), not at C8 (181.923 s) as the registered rule says.
- D178 (1) gives the largest reaction heat wrongly.
- Several README and note statements are wrong or overstated (items 6 to 19).

## Discrepancies

**Numbers that differ from the records**

1. **DECISIONS.md:1014, D178 (1).** The text says "the most is 6,307 J, at that C8".
   - The records give 6,410.2 J, in `s15_B4_PT_Exp4_shift17.5K`, which has no C8 and runs to 900 s.
   - 6,307 J is the most only among the runs that reach C8.
   - "Passes 11.3 kJ in no run" is correct: `t_rxn_mark_s` is null in all 27 records.
2. **DECISIONS.md:1015, D178 (2), and README.md:837.** These quote the B3 (a) history score over "0 to 181.9 s (the window ends at C8)".
   - The text gives:
     - root mean square 51.5 K;
     - 41.7 K above the record on average;
     - 77.3 K above it at the end (244.7 against 167.4 C);
     - a rise over the last 60 s of 34.9 K against 10.7 K.
   - Over the registered window, which ends at C8 (181.923 s), the values are 51.44, 41.56 and 77.21 K (244.56 against 167.35 C), and the rises 34.85 against 10.65 K.
   - The quoted values come from the window 0 to 182.0 s, the end of the step in which C8 falls. `history_score` uses t1 = probe_t[-1], and `stage15_scorecard.json` records `window_s` = [0, 182.0].
   - Our own trapezoid code and `stage10_score.metrics` agree for both windows.
   - D182 does not disclose this departure from the registered rule.
3. **DECISIONS.md:1016, D178 (3).** The text gives the 12.5 W run "at 255.9 s (244.5 against 182.8 C)".
   - At C8 (255.856 s) the values are 244.40 against 182.74 C.
   - The root mean square (33.1 K), the mean (20.4 K) and the 61.7 K difference are the same in either window.
4. **DECISIONS.md:1016, D178 (3).** The text says "3,480 J at 10 W" by C8.
   - At C8 the energy is 10 W × (369.329 − 21.387 s) = 3,479.4 J.
   - 3,480.1 J is the energy to the stop at 369.4 s.
   - The 2,931 J at 12.5 W is correct.
5. **E\*(C2) of M50_ST_Exp3.** DECISIONS.md:1014 gives "12,031 J"; predictions_stage15.md:36 and :73 give "12,030". The value registered is 12,030.5 J.

**Claims the records do not support**

6. **DECISIONS.md:1023, D180 (1).** The text says "Over 240 and 360 s C8 comes before the delivery ends." Over 240 s this is false in two of the eight matched cases:
   - M50_PT_Exp4: C8 at 271.37 s, with all 6,774.8 J delivered.
   - M50_PP_Exp4: C8 at 272.77 s, with all 5,025.1 J delivered.
   - The 4,179 to 8,116 J range is unaffected.
7. **README.md:834, "and with no delivery neither runs away".**
   - With no delivery the lumped twin does run away in M50_PP_Exp1 (277.3 s) and M50_SP_Exp3 (221.5 s), as the `s10_none` records, Stage 7's runs and `stage15_nodelivery.csv` show.
   - README:840 itself gives "the lumped neighbour in 0, 2 and 9".
   - It is only the resolved mean that reaches C8 in none.
8. **README.md:843, "and above the record throughout".** This is false on the record's 0.5 s samples.
   - In the 7,416 J run the far face is below the record from 0 to 17.5 s, by up to 76.7 K at 3.0 s.
   - In the 12.5 W run it is below from 0 to 52.5 s. After Section I it is below by up to 11.9 K at 24.5 s, and it reads 135.7 against 141.0 C at 45 s, as D178 (3) itself states.
9. **README.md:843, "The far face is the coolest surface the model offers ... so that difference is a lower bound".**
   - Only five surface probes, all at mid-length, are recorded.
   - The far face is the coolest of them at the jump's start: 234.10 C at 173.0 s, against side 235.79 C and side_out 235.50 C.
   - It is not the coolest throughout:
     - M50_PT_Exp4: the side probes are cooler from 179.0 s to the stop (243.88 against 244.66 C).
     - M50_PP_Exp2: the same from 185.5 s.
     - M50_ST_Exp3: the same from 36.8 s.
     - The 10 W run: the facing probe is cooler from 331.9 s.
   - The "lower bound" is therefore not established.
10. **note:149, "a hold of 10 to 12.5 W brings the runaway to the measured 271.5 s".** C8 comes at 369.3 s with 10 W and 255.9 s with 12.5 W. The two powers only bracket 271.5 s; no run lies within 10 s of it.
11. **note:150, "no kinetic draw".** Only four of the 200 draws were run.
12. **note:147 and README.md:844, "all 151 archived continued runs" and "all 151 archived runs".** These are the 151 central runs of the 199 continued runs.
13. **note:151 and README.md:844, "the fourth within 10 %"; README.md:836, "lies 10 % above".**
    - M50_SP_Exp3's bracket is (3,704, 4,057] J, which is 1.05 to 1.15 times 3,528 J, so the threshold lies 5 to 15 % above the cross-section's value.
    - Only the midpoint is 10.0 % above it (9.1 % by P1's measure).
14. **README.md:842, "in every test with a strong trigger".** The three-dimensional runs cover three tests; the other eleven rest on the cross-section only, which is not said.
15. **README.md:842, "0.26 to 6 kJ".**
    - That is the range for the 21.39 s pulse only (263.5 to 5,962.4 J).
    - Across all four deliveries the clock needs 218.7 to 13,912 J, or 218.7 to 5,962 J delivered by its crossing time.
16. **README.md:840, "no test's cell runs away by C8 at any contact".** At the high contact 10 of the 16 rest on the cross-section only. D180 (2) discloses this; the README does not.
17. **Precision of the midpoints.** README.md:849 (P1 row "0, 0, 9.1 and 0 %") and note:148 (7.06, 6.85, 3.88, 10.28 against 12.03 kJ) state more precision than the 10 %-wide three-dimensional brackets carry.
    - The 0 % values hold by construction, since the first two runs bracket the threshold and the midpoint is then the cross-section's value.
    - README:826 defines E\*(C8) as the least energy, while README:836 reports the bracket's midpoint as E\*(C8).
18. **README.md:838 and sentences:13, "must be shifted by 20 K".** At the registered 2.5 K resolution the least shift lies in (17.5, 20] K.
19. **sentences:3, "Every number is in" the four named files.** Three numbers are not:
    - 215.6 s (line 17) is only in `stage15_readings.json`.
    - 215.3 to 221.4 C and 6.1 K (line 13) are Stage 13's (D140 (1), `stage13_tign.csv`).

**The run log, wording and labels**

20. **D177 (DECISIONS.md:1011), "B4's shift five (5, 10, 15, 20 and 17.5 K)".**
    - The 5 K run was one of the 17 registered first runs, so B4 needed only four more.
    - The correct count is 1 + 1 + 4 + 4 (V4) = 10 = 27 − 17; as written, the count adds up to 11.
21. **D177, "started again at once (06:06:50 and 06:15:00)".** Worker 2's last run of its first session ended at 06:09:00 (`partb_w2.log`), so it was restarted 6 minutes later.
22. **D177, "GitHub's record of every push".** The provenance file lists 11 pushes, the last being 1d09052 at 07:00:38Z. The pushes of 71f4e3d and 9f69150 are not in it.
23. **D181 (DECISIONS.md:1027).** The literal text "V5: V5PLACEHOLDER" is still in place.
24. **D180 (1), "crossing times read from the archived run records".**
    - For the seven matched C2 entries with the pulse, `stage15_table.csv` carries Stage 12's rounded values, not the records' own (for example M50_PP_Exp4: 1,819.0 J and 268.9 s, against 1,818.95 J and 268.94 s in the record).
    - All the differences are within 0.05 s.
25. **Label clashes.**
    - C1 and C2 name both the criteria and Part C's two tables (README:840; D180 (1) and (2) at DECISIONS.md:1023 to 1024), and D180 (1) uses both meanings in one paragraph.
    - "A1's 27.9 kJ" (DECISIONS.md:1023) is Stage 14's path A1, not Stage 15's A1, and is undefined there.
    - The README section uses B1 to B4, A0 and A0.4 without defining them (for example README:849 and README:862).
26. **README.md:862, the caption "under four deliveries".** The figure plots five runs.

**Outside D177 to D182, found while checking the readings, the accounts and the sizing**

27. **D172 (2) (DECISIONS.md:980).**
    - "540 J" should be 541 J (540.6 J).
    - "28.1 K" should be 28.2 K (1,738.35 / 61.75 = 28.15).
    - At 29 s the mean is 58.7 C, not 60 C; it reaches 60 C at 29.8 s.
28. **D172 (3) (DECISIONS.md:981).**
    - "2.2 to 3.7 times faster": the ratios are 2.27 to 3.73.
    - The "107 laptop runs" include 4 runs on the cloud machine; the laptop's 103 have a median of 646 s.
29. **D174 (1) (DECISIONS.md:988).** "15 to 118 kJ" should be 15.4 to 134.8 kJ: M50_PT_Exp2's 240 s and 360 s runs at fractions up to 1.0 cross within 30 s.
30. **D174 (5) (DECISIONS.md:992), "17.2 times (266 J)".** 4,581.7 / 265.59 = 17.25; the 17.2 comes from the rounded 266 J.
31. **V3's 7.4e-13 K (README.md:858, D173).** No stored record of it exists in `results/`. It was not checked, since checking would mean running model code.

## Checked and found correct

- **Registration.**
  - `predictions_stage15.md` and `stage15_cross_section.json` were committed at 3f5e3b6 and pushed at 05:12:45Z, before the first run began at 05:13:22Z, and neither has changed since.
  - The list's hash 99cbbf7a... reproduces, and the cross-section file's SHA-256 6d70911a... matches.
  - After the registration, `stage15_score.py` changed only in V2, Part C1 and the paper numbers, and the figure only in its labels. The `scorecard()` function is unchanged.
  - The earlier texts were only appended to.
  - The snapshot of Stage 14's bounds is identical to 026b9c0's file.
- **The Part B chains.**
  - All 27 runs the rules call for exist and there are no extras; every configuration matches its rule.
  - B1's brackets and midpoints reproduce, B3 ends bracketed, and B4's least shift is 20 K.
  - C8 recomputed from each record's stored mean at every step equals `t_C8_s` to within 5.7e-14 s, at the code's level of 528.831575 K. At exactly 528.83 K the times are 0.0007 to 0.0043 s earlier, and no outcome changes.
- **The scorecard and the counts.** By each registered rule, P1 to P7 held and P8 failed. The running totals of 98, 56 and 42 check against Stage 13's 84 and 39 and Stage 14's 6 with 2 failed.
- **V2.** The worst residuals are 1.61e-12 (resolved) and 1.97e-12 (lumped). Every delivery equals its own integral to the run's end, exactly for the triangular and constant deliveries and to 1.6e-16 for the holds.
- **V4.** The outcomes are unchanged. C8 moves by 1.484 % on the refined mesh and by 0.0091 % with the step limits halved. At the lower end the mean's peak moves from 215.30 C to 214.69 and 215.32 C.
- **The far face's jump starts.** Our own code reproduces the value in every record, and the measured record's own jump starts at 267.5 s at 186.54 C.
- **The history metrics.** Our own code matches `stage10_score.metrics`.
- **`stage15_table.csv`.** All 36 rows match an independent recomputation, with zero differences.
- **`stage15_nodelivery.csv`.** All 48 rows match a recomputation from Stage 7's runs, the archive and the cross-section's runs.
- **The archive and Part A.** The counts of 199, 151 and 92 hold, V1 recomputes, A1 matches in 151 of 151, and there are 675 cross-section runs.
- **The readings and the accounts.** Readings 1 to 5 and A0.4's accounts reproduce from the archived records and series, apart from the values listed above.
- **Banned forms.** None of the Stage 15 texts contains a form the brief's rules exclude: no em or en dash, none of the excluded words, and no letter label for a study.
