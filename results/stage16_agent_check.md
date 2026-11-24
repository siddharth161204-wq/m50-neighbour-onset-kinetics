# Step 16: the independent agent check (V4, second part), 24 November 2026

An agent with no part in the runs read `predictions_stage16.md` and the run records, worked out every bracket and verdict itself (scripts in its own scratch folder, nothing written to the repository), froze them, and only then compared them with `results/stage16_scorecard.json` and `results/stage16_recheck.json`. Its report, verbatim:

---

I've finished the independent check: my brackets and verdicts match the scorecard and the recheck everywhere. The one real difference is which archived runs count in a single search, and it moves no number.

**How I worked.** I read `predictions_stage16.md` in full, then the 116 Stage 16 records, the 13 Stage 15 B1 records, and the cross-section's `A1_rows` (151 archived runs; I skipped the no-delivery rows). I also used `m50_tests.csv`, `stage15_table.csv` and `stage14_needs.csv`. All the named files existed. The two registered SHA-256 hashes (cross-section and table) match. I replayed every search's rule step by step against the records: each of the 114 base-configuration runs sits at the energy the rule calls for, within the rounding of `f` to nine decimals. I opened the scorecard, the recheck and three targeted snippets of `src/stage16_run.py` only after freezing my results.

**N, with the pulse.** All eight closed and monotone. Brackets are in J; m is the bracket midpoint, d = (E_x − m)/m. Mine equal the scorecard's to better than 1e-9.

| Test | Bracket (J) | m | E_x | d | Lumped need | lo − lumped / hi − lumped |
|---|---|---|---|---|---|---|
| PT-Exp4 | (7,062.5, 7,150.8] | 7,106.6 | 7,440.2 | +4.69 % | 4,851.0 | 2,211.5 / 2,299.8 |
| PP-Exp1 | (5,461.8, 5,653.1] | 5,557.5 | 6,035.8 | +8.61 % | 2,974.4 | 2,487.4 / 2,678.7 |
| PP-Exp2 | (7,423.0, 7,536.1] | 7,479.6 | 7,649.2 | +2.27 % | 5,962.4 | 1,460.6 / 1,573.7 |
| PP-Exp4 | (5,519.8, 5,652.0] | 5,585.9 | 6,048.5 | +8.28 % | 1,819.0 | 3,700.8 / 3,833.0 |
| ST-Exp4 | (5,318.9, 5,508.3] | 5,413.6 | 5,508.3 | +1.75 % | 1,184.0 | 4,134.9 / 4,324.3 |
| SP-Exp1 | (5,964.7, 6,146.4] | 6,055.5 | 5,964.7 | −1.50 % | 2,725.6 | 3,239.1 / 3,420.8 |
| SP-Exp2 | (6,325.7, 6,495.2] | 6,410.4 | 6,495.2 | +1.32 % | 3,783.4 | 2,542.3 / 2,711.8 |
| SP-Exp3 | (4,450.5, 4,581.7] | 4,516.1 | 4,581.7 | +1.45 % | 263.5 | 4,187.0 / 4,318.2 |

**T.** The bracket is (10,242.2, 11,320.3], closed by its first two runs. Its midpoint is 10,781.25 J, so R = 0.8377. Same as the scorecard.

**V.** It refined PP-Exp4: among the six needs whose lower end runs away, it has the latest measured time (275 s). Both ends kept their class, so the refined bracket equals the base bracket and the need moved 0 J (0 %). Lower end (5,519.8 J): the time the mean reached 255.7 C went from 298.80 to 306.84 s (+8.04 s, +2.69 %); late on both meshes. Upper end (5,652.0 J): 249.31 to 252.09 s (+2.78 s, +1.12 %); early on both. No extra refined runs were made. Same as the scorecard.

**X.** Brackets are counted as delivered by t_m + 10 s. Fourteen searches closed; all agree with the scorecard.

| Search | Bracket (J) | d | Lumped need |
|---|---|---|---|
| PT-Exp4, 240 s | (6,403.3, 6,500.3] | +5.01 % | 3,492.7 |
| PP-Exp1, 240 s | (5,121.9, 5,238.3] | +15.75 % | 2,423.7 |
| PP-Exp2, 240 s | (7,570.5, 7,671.7] | +5.55 % | 4,847.7 |
| PP-Exp4, 240 s | (4,479.4, 4,661.3] | +9.95 % | 1,364.2 |
| ST-Exp4, 240 s | (4,102.5, 4,292.0] | +6.77 % | 947.2 |
| SP-Exp1, 240 s | (5,544.7, 5,668.4] | +3.18 % | 2,115.0 |
| SP-Exp2, 240 s | (6,092.1, 6,175.4] | +3.03 % | 3,400.4 |
| SP-Exp3, 240 s | (3,876.2, 4,006.1] | +6.04 % | 228.2 |
| PT-Exp4, 120 s | (6,574.9, 6,678.6] | +8.60 % | 3,880.8 |
| PP-Exp1, 120 s | (4,882.5, 4,989.9] | +9.79 % | 1,982.9 |
| PP-Exp2, 120 s | (7,092.9, 7,185.8] | +8.46 % | 4,770.0 |
| PP-Exp4, 120 s | (4,712.8, 4,837.8] | +14.39 % | 1,464.0 |
| ST-Exp4, 120 s | (4,546.6, 4,670.7] | +6.73 % | 947.2 |
| SP-Exp1, 120 s | (5,298.6, 5,399.6] | +0.94 % | 2,169.4 |

SP-Exp2 and SP-Exp3 over 120 s are unfinished, still open at (5,119.2, 5,879.7] and (3,102.9, 4,064.3]. None of the eight 360 s searches was started.

**Verdicts.** Mine, the scorecard's and the recheck's are identical: 9 hold, 2 fail.

| Prediction | Verdict | Deciding numbers |
|---|---|---|
| P1 | holds | largest abs(d) is 8.61 % |
| P2 | fails | SP-Exp1: E_x is the bracket's late lower end, below m |
| P3 | holds | brackets span 4,450.5 to 7,536.1 J |
| P4 | holds | every lower end is above its lumped need |
| P5 | holds | margins run from 1,460.6 J to 4,324.3 J |
| P6 | holds | 11,320.3 ≤ 12,848.8 J |
| P7 | holds | R = 0.838 |
| P8 | holds | both refined ends kept their class |
| P9 | holds | 2.69 % and 1.12 %, both under 3 % |
| P10 | fails | PP-Exp1 over 240 s and PP-Exp4 over 120 s exceed 10 % |
| P11 | holds | 14 of 14 closed searches |

**Differences from the scorecard.**
- Which runs count, PT-Exp4 over 240 s (8 in the scorecard, 6 in mine). The scorecard also counts Stage 15's two B2 runs, at 5,821.1 and 6,209.2 J. The registered text names only the cross-section's archived runs and the B1 runs, which is what I counted; the code counts "Stage 15 runs of the same configuration". Both B2 runs are late and sit at or below the archived late run at 6,209.2 J, so the bracket and verdicts are the same either way. The rule's opening sentence ("every three-dimensional run already made in the same configuration counts") supports the code.
- Presentation only. The scorecard gives no bracket for the two unfinished 120 s searches (the recheck lists the same open brackets as mine) and labels the 360 s searches "not started" where the recheck says "open".

**Things in the rules or records that looked wrong or ambiguous.** None changes a verdict.
1. Lumped PT-Exp1 bracket. `stage14_needs.csv` gives (12,543.9, 12,892.4], but the rules use (12,848.8, 12,892.4]. That lower end traces to the archived lumped run `refA_c2_M50_PT_Exp1_f0.460937500` in `results/stage13_archive_runs.csv`. I used the rules' value. With the CSV's value, P6's bound becomes 12,543.9 J and R becomes 0.848; both still hold.
2. Width test for constant power. The rules define the bracket as counted by t_m + 10 s, but the code tests the 0.00125 E_e width on nominal energies. This mattered once: in SP-Exp2 over 240 s, the bracket (9,195.6, 9,447.0] was already 166.6 J wide counted by t_m + 10 s (limit 189.2 J) but 251.5 J nominally, so an extra run was made at 9,321.3 J. Since every run made counts, the final bracket stands. Under the other reading d would be +2.34 % instead of +3.03 %.
3. "Six hours of a worker's time." The code reads it as six worker-hours summed over both workers: 6.158 h at the end, about 3.1 h each. Under that reading the cut was applied correctly: the last X run started at 5.985 h, the total passed 6 h at 13:13:43, and nothing started after. Read per worker, X should have continued.
4. What P10 and P11 are scored on. Only the 14 closed searches count, because those rules say "every X search closed". I agree with that reading.
5. Brackets exactly at the width limit. Four brackets are exactly half a grid step wide by construction. Two of them (SP-Exp1 with the pulse, ST-Exp4 over 240 s) exceed the limit by 1e-13 J in floating point, so a strict comparison would have demanded another run. The code's tolerance of 1e-6 E_e closes them, as the rule intends.
6. Thin margins. Two bracket ends are decided by less than 0.1 s: PP-Exp1 over 240 s at 7,760.5 J (161.951 s against 162 s) and SP-Exp2 over 240 s at 9,321.3 J (158.901 s against 159 s). P10's failure does not depend on these: PP-Exp4 over 120 s fails on its own. Other close calls: PP-Exp4 over 240 s at +9.95 %, PP-Exp1 over 120 s at +9.79 %, and P9's lower end at 2.69 % against 3 %.
7. Record integrity. Energy residuals are at most 2e-12 for both neighbours, deliveries equal their shape's integral to each run's end, and no record is flagged as failed. The PT-Exp4 archived runs that ended at 332 s without C8 are decidably late, since 332 s is past t_m + 10 = 282 s. The refined B1 runs were rightly left out of the count; they would not have changed anything.

Agreement: yes. Every bracket and every verdict agrees with `results/stage16_scorecard.json` and `results/stage16_recheck.json`. The only difference is that the scorecard also counts Stage 15's two B2 runs in PT-Exp4's 240 s search, which changes nothing.
