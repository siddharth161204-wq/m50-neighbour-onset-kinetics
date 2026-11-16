# Stage 13 predictions (version 1.9.0, branch stage13)

Registered before any Stage 13 run of the resolved or the lumped neighbour (DECISIONS.md D130 to D137). Each prediction is the brief's, with its expectation and the rule by which it is scored; the reduced models' own numbers that a prediction states were computed before this file was pushed and are committed with it in `results/stage13_reduced.json`. Comparisons with archived values are explanatory and are not scored; only the new runs are. No tolerance moves after a run.

Symbols: f is the delivered fraction of a test's ejected energy E_e = r E_b (r = 3.105); E = f E_e is the delivered energy; f*(C1) is the least f for which the resolved neighbour's hottest node reaches T_L = 255.68 C within 900 s, f*(C2) the least f for which the lumped neighbour does; a search's bracket (lo, hi] has lo not crossing and hi crossing, and its midpoint is (lo + hi)/2. A1 is the closed form of the local threshold, A2 the cross-section conduction model, B1 the ignition temperature T_ign and B2 the two-body model of the whole-cell threshold.

## The predictions

**P1.** For PT_Exp1 with a 5 s triangular delivery over the facing half, the resolved f*(C1) lies within 10 % of A1's closed form. A1 gives f* = 0.07701, its peak at 3.72 s, with the hot spot's angle (35.0 degrees) and its temperature with no delivery (25.2 C) taken from A2; the pure skin (25 C, no loss) gives 0.07601. Expectation: likely. Scored: |midpoint - A1| <= 0.10 A1.

**P2.** At 40 s (PT_Exp1, facing half), the cross-section model lies within 5 % of the resolved bracket's midpoint. A2 gives f* = 0.21775 (hot spot at 22.0 degrees, 25.1 s). Expectation: uncertain. Scored: |A2 - midpoint| <= 0.05 midpoint.

**P3.** At 120 s (PT_Exp1, facing half), the resolved threshold lies more than 5 % below the cross-section conduction model's (local ignition). A2 gives f* = 0.41450 (hot spot at 30.7 degrees, 73.5 s). Expectation: uncertain. Scored: midpoint < 0.95 A2; A5's run without the reaction at the bracket's upper end is reported beside it.

**P4.** For ST_Exp3 and PT_Exp3, the cross-section model with the trigger's conduction superposed lies within 10 % of the resolved midpoints at 10 and at 60 s, and gives the direction of change from 21.39 s in all four cases. A2 gives ST_Exp3: 0.05740 at 10 s, 0.08023 at 21.39 s, 0.12825 at 60 s; PT_Exp3: 0.02995 at 10 s, 0.02641 at 21.39 s, 0.03292 at 60 s. Expectation: uncertain. Scored: |A2 - midpoint| <= 0.10 midpoint in each of the four cases, and in each the sign of A2(tau) - A2(21.39 s) equals the sign of midpoint(tau) - midpoint(21.39 s), the latter the archived reference refined by A4 (D134); a case whose two resolved brackets overlap is reported as such.

**P5.** For PT_Exp1 at 21.39 s, over the whole lateral surface the threshold in delivered energy is 1.8 to 2.2 times the facing half's. Expectation: likely. A2's own ratio, for the record, is 1.683. Scored: midpoint(whole) / midpoint(half, the refined reference) within [1.8, 2.2].

**P6.** For PT_Exp1 at 21.39 s, over the eighth of the facing half nearest the cap (theta <= 90 degrees, z >= 0.875 L) the threshold in energy per unit area exceeds the facing half's by at least 25 %. Expectation: likely (the archived cap-end quarter exceeds it by about 12 %). A2 cannot hold an axial region and states no number. Scored: (midpoint(eighth) / A_eighth) / (midpoint(half) / A_half) >= 1.25, with A_eighth = A_half / 8.

**P7.** T_ign of the posterior-mean kinetics, with the trigger at the neighbour's own temperature, lies between 215 and 240 C, and the central 95 % of the 200 draws spans less than 40 K. Expectation: likely for the mean, uncertain for the span. The first clause is known at registration, because B2 needs B1's mean: T_ign = 218.48 C (D132); it is reported and not counted. The second clause is computed after this file is pushed. Scored: the 97.5th less the 2.5th percentile of the 200 draws' T_ign (the trigger at the neighbour's own temperature) is below 40 K.

**P8.** B2's delivered energy at the whole-cell threshold lies within the larger of 10 % and 300 J of the full lumped model's midpoint in at least 28 of the 32 low and high contact searches. Expectation: uncertain. B2's 32 values (J): PT_Exp1 low 12251; PT_Exp2 low 9306; PT_Exp3 low 11075; PT_Exp4 low 9881; PP_Exp1 low 7934; PP_Exp2 low 9721; PP_Exp3 low 9220; PP_Exp4 low 8697; ST_Exp1 low 8324; ST_Exp2 low 9106; ST_Exp3 low 11779; ST_Exp4 low 8714; SP_Exp1 low 9047; SP_Exp2 low 8726; SP_Exp3 low 7777; SP_Exp4 low 10188; PT_Exp1 high 12635; PT_Exp2 high 294; PT_Exp3 high 6966; PT_Exp4 high 2338; PP_Exp1 high 0; PP_Exp2 high 1762; PP_Exp3 high 0; PP_Exp4 high 0; ST_Exp1 high 0; ST_Exp2 high 0; ST_Exp3 high 11558; ST_Exp4 high 0; SP_Exp1 high 0; SP_Exp2 high 0; SP_Exp3 high 0; SP_Exp4 high 2841. Scored: the number of searches with |B2 - midpoint| <= max(0.10 midpoint, 300 J) is at least 28.

**P9.** For PT_Exp1, the ratio f*(C2)/f*(C1) falls from 21.39 to 120 to 360 s and is below 1.5 at 360 s. Expectation: likely for the fall, uncertain for the level. The reduced models' ratio B2/A2, for the record: 2.861 at 21.39 s, 1.134 at 120 s, 0.872 at 360 s. Scored: with midpoints, f*(C1) from A4 (the refined reference at 21.39 s, the searches at 120 and 360 s) and f*(C2) from the archive's refined bracket at 21.39 s, (0.4609375, 0.4625], and B4's central searches at 120 and 360 s: ratio(21.39) > ratio(120) > ratio(360), and ratio(360) < 1.5.

**P10.** For PP_Exp3, ST_Exp2 and PT_Exp3, the full lumped model's needed delivered energy falls by 150 to 300 J per kJ of body energy, across the 4 kJ between the shifted runs. Expectation: likely for the first two, uncertain for PT_Exp3. B2's own slopes, for the record: PP_Exp3 435 J per kJ (4139 J at E_b - 2 kJ, 2399 J at E_b + 2 kJ); ST_Exp2 418 J per kJ (3383 J at E_b - 2 kJ, 1710 J at E_b + 2 kJ); PT_Exp3 367 J per kJ (9065 J at E_b - 2 kJ, 7596 J at E_b + 2 kJ). Scored: for each test, (midpoint(E_b - 2 kJ) - midpoint(E_b + 2 kJ)) / 4 kJ within [150, 300] J per kJ; P10 holds if all three do, and each is reported.

## Where the searches start

Each resolved search starts at A2's f* (the eighth at the facing half's flux per area plus 25 %), each lumped search at B2's E* (D134, D135). The starting values, with every other reduced number, are in `results/stage13_reduced.json`.

## Provenance

- Run lists (`stage13_inputs.run_lists()`, 13 resolved and 70 lumped searches): SHA-256 `e018365ea849f80ef690e3cb67928ff584a6d6833aae55a54e0be384c58e08ea`.
- `results/stage13_reduced.json`: SHA-256 `7b1157037140ce30322024d2ce08492f999b8cf0801778f90b734623d53889df`.
- The commit that registers this file and the time it was pushed are recorded in DECISIONS.md and in the state document after the push.
