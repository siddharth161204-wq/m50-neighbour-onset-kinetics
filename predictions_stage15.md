# Stage 15 predictions: the resolved neighbour's own runaway

Written on branch `stage15` and committed and pushed before any new Stage 15 run of the three-dimensional model. The reduced model's numbers stated here were computed before this file and are committed with it in `results/stage15_cross_section.json` (SHA-256 6d70911a680fc6dae7cba935c5d950565805c0c2bfc91c2dea4c962a22d9c6af). The registered list of Part B's runs and its rules (`src/stage15_partb.py`, `registered_list`) has the SHA-256 99cbbf7a58c1bfaec6b69cbd633a5ec3c074d8e812ea124be31b5b119333ce11. DECISIONS.md D170 to D176 record the design.

## The quantities

- T_L, the level: 255.68 C, the lower end of the two-cell study's onset band.
- The resolved neighbour: the three-dimensional model of the neighbouring cell (19,355 nodes on the half cell), with the posterior-mean decomposition kinetics and their heat fed back, the trigger cell's archived temperature history (its fitted body energy E_b released over 21.39 s), the central contact (2,000 W/(m2 K)) and tabs, 25 C. The lumped neighbour: the same cell as one temperature with one heat capacity, 61.75 J/K, linked to the trigger through the same conductances.
- Tmean, the resolved neighbour's mean temperature: the sum of C_i T_i over the sum of C_i over its nodes, C_i each node's heat capacity (the roll's volumetric heat capacity times the node's volume, plus its share of the can's). It is the stored heat over the heat capacity, the quantity the lumped neighbour's one temperature stands for.
- C1: the resolved neighbour's hottest node reaches T_L (the local criterion). C2: the lumped neighbour reaches T_L (the whole-cell clock). C8: the first time within 900 s at which Tmean reaches T_L (the neighbour's own runaway).
- A delivery: energy E delivered from t = 0 as a uniform flux over the half of the neighbour's can facing the trigger, as the archive's triangular pulse over 21.39 s (zero at 0 and 21.39 s, its peak at 10.69 s) or as a constant power over 120, 240 or 360 s. E_e = 3.105 E_b is a test's ejected energy and f = E / E_e.
- E*(C8): the least delivered energy for which C8 happens, for a stated delivery; E*(C2) likewise for C2. The whole-cell clock's threshold E*(C2) with the 21.39 s delivery is the midpoint of the narrowest archived bracket of the least energy for C2 (Stage 12's, where its continuation of Stage 9's search for the measured time ended at the threshold; otherwise Stage 9's, where its own search did; otherwise Stage 8's), 0 where the lumped neighbour crosses with no delivery.
- The far face: the resolved neighbour's surface node at mid-length opposite the line of contact. Its jump's start: with its rate of rise r(t) = [T(t + 1 s) - T(t - 1 s)] / 2 s on a 0.5 s grid, the first time r reaches 1 K/s after r has first reached 0.5 K/s and then fallen below it, before C8; where there is no such time before C8 (r never falling below 0.5 K/s, the brief's case, or not reaching 1 K/s again, or never reaching 0.5 K/s), the reading 20 s before C8.
- M50_PT_Exp4's measured history: the neighbour's thermocouple in the supplement's Figure 10 of Fransson et al. (2024), read every 0.5 s; it reads 197.3 C at 271.5 s, the onset the figure marks, and then jumps. The jump rule above, applied to the record itself (which starts at 24.16 s), finds its jump starting at 267.5 s at 186.5 C (DECISIONS.md D171 (2)); P5's reference is the brief's, 197.3 C. Stage 10's rule scores a run against the record at the far face over 0 to 271.5 s (the root mean square of the difference, the difference at 271.5 s, the rise over the last 60 s).

## The reduced model (Part A)

The reactive cross-section is Stage 13's conduction model of the mid-height cross-section (conduction in r and theta, the can, the contact and air wedge, convection, radiation, the delivery over the facing half) with the archive's kinetics in every cell of the roll and their heat fed back, the reaction step the three-dimensional model's own (base steps of 0.01 s to 30 s and 0.1 s after, halved as often as needed to keep the reaction's heating of any cell within 1 K a step). It has neither the ends nor the tabs: it is a cell infinitely long under mid-height's conditions. With the reaction off it equals Stage 13's model to 7.4e-13 K (V3).

Against the archive's 151 central continued runs (explanatory; DECISIONS.md D174) it gives the same outcome, C8 or none within the archived run's span, in 151 and misses 0. That is no more than one run in ten, so it stands for the three-dimensional cell (A3) and P1 is kept.

E*(C8) with the 21.39 s delivery (the bracket's midpoint, J; the bracket no wider than 1 % of it):

| Test | E*(C8) | f*(C8) | E*(C2), archived | ratio |
|---|---|---|---|---|
| M50_PT_Exp1 | 10,781 | 0.38677 | 12,718 (Stage 8) | 0.85 |
| M50_PT_Exp2 | 6,354 | 0.04714 | 2,527 (Stage 8) | 2.51 |
| M50_PT_Exp3 | 8,594 | 0.08761 | 7,970 (Stage 8) | 1.08 |
| M50_PT_Exp4 | 7,062 | 0.05687 | 4,754 (Stage 12) | 1.49 |
| M50_PP_Exp1 | 4,542 | 0.02863 | 0 (Stage 8) | - |
| M50_PP_Exp2 | 6,854 | 0.05389 | 3,975 (Stage 8) | 1.72 |
| M50_PP_Exp3 | 6,229 | 0.04570 | 2,556 (Stage 8) | 2.44 |
| M50_PP_Exp4 | 5,604 | 0.03851 | 909 (Stage 8) | 6.16 |
| M50_ST_Exp1 | 4,431 | 0.02792 | 992 (Stage 8) | 4.47 |
| M50_ST_Exp2 | 5,604 | 0.03885 | 2,705 (Stage 8) | 2.07 |
| M50_ST_Exp3 | 10,281 | 0.19896 | 12,030 (Stage 12) | 0.85 |
| M50_ST_Exp4 | 5,042 | 0.03327 | 1,184 (Stage 9) | 4.26 |
| M50_SP_Exp1 | 5,521 | 0.03798 | 2,726 (Stage 8) | 2.03 |
| M50_SP_Exp2 | 5,069 | 0.03350 | 946 (Stage 8) | 5.36 |
| M50_SP_Exp3 | 3,528 | 0.02092 | 0 (Stage 8) | - |
| M50_SP_Exp4 | 7,104 | 0.05777 | 5,380 (Stage 8) | 1.32 |

E*(C8) with constant power, the nine propagated tests (J):

| Test | 120 s | 240 s | 360 s |
|---|---|---|---|
| M50_PT_Exp4 | 6,820 | 6,398 | 7,055 |
| M50_PP_Exp1 | 3,927 | 3,531 | 3,927 |
| M50_PP_Exp2 | 6,539 | 6,117 | 6,773 |
| M50_PP_Exp4 | 5,016 | 4,578 | 5,078 |
| M50_ST_Exp3 | 12,410 | 13,553 | 15,240 |
| M50_ST_Exp4 | 4,453 | 4,016 | 4,453 |
| M50_SP_Exp1 | 4,953 | 4,516 | 5,016 |
| M50_SP_Exp2 | 4,453 | 4,016 | 4,484 |
| M50_SP_Exp3 | 3,010 | 2,677 | 2,990 |

The delivered energy at which the cross-section's C8 falls at the measured time t_m, by Stage 9's rule for f_t read on C8 (J). The rule reads the grid f8_hi + 0, 0.0125, 0.025, 0.05, 0.1 and 0.2 (fractions of E_e; f8_lo and f8_hi the ends of the E*(C8) bracket) in order up to its first point whose C8 comes before t_m, then bisects between f8_lo and that point until the bracket is at most 0.005 E_e wide or a run's C8 lies within 10 s of t_m. "Matched": a run whose C8 lies within 10 s of t_m (its C8 time in brackets). "Threshold": the bisection ended at its width with its lower end, f8_lo, giving no C8, so t_m lies within 0.005 E_e of the threshold; the cell gives the bracket and the C8 times at f8_hi and at the bracket's upper end (where C8 at f8_hi already comes before t_m, no delivered energy reproduces t_m). "Above grid": C8 does not come before t_m up to f8_hi + 0.2.

| Test | t_m (s) | 21.39 s | 120 s | 240 s | 360 s |
|---|---|---|---|---|---|
| M50_PT_Exp4 | 272 | threshold (7,042, 7,440]: C8 at 310.6 s with 7,083, 188.5 s with 7,440 | threshold (6,797, 7,197]: C8 at 298.2 s with 6,844, 200.6 s with 7,197 | 6,775 (matched, 271.4 s) | 9,395 (matched, 278.9 s) |
| M50_PP_Exp1 | 152 | 6,036 (matched, 156.3 s) | 5,419 (matched, 161.5 s) | 9,485 (matched, 151.7 s) | 13,844 (matched, 154.4 s) |
| M50_PP_Exp2 | 147 | 7,649 (matched, 148.4 s) | 7,743 (matched, 143.7 s) | 12,501 (matched, 154.4 s) | 19,517 (matched, 149.7 s) |
| M50_PP_Exp4 | 275 | threshold (5,583, 6,048]: C8 at 333.0 s with 5,625, 216.9 s with 6,048 | threshold (5,000, 5,463]: C8 at 411.8 s with 5,031, 228.4 s with 5,463 | 5,025 (matched, 272.8 s) | 6,913 (matched, 281.3 s) |
| M50_ST_Exp3 | 177 | threshold (10,250, 10,312]: C8 at 114.0 s with 10,312, before t_m | threshold (12,375, 12,554]: C8 at 190.2 s with 12,445, 160.1 s with 12,554 | 18,773 (matched, 177.0 s) | above grid |
| M50_ST_Exp4 | 342 | threshold (5,028, 5,508]: C8 at 384.8 s with 5,056, 231.8 s with 5,508 | threshold (4,438, 4,919]: C8 at 364.9 s with 4,469, 233.7 s with 4,919 | threshold (4,000, 4,481]: C8 at 388.7 s with 4,031, 272.6 s with 4,481 | 4,919 (matched, 347.1 s) |
| M50_SP_Exp1 | 223 | 5,965 (matched, 223.2 s) | 5,400 (matched, 230.1 s) | 6,348 (matched, 218.7 s) | 9,562 (matched, 218.1 s) |
| M50_SP_Exp2 | 149 | 6,495 (matched, 148.6 s) | 5,880 (matched, 158.7 s) | 9,699 (matched, 156.4 s) | 15,842 (matched, 147.7 s) |
| M50_SP_Exp3 | 210 | 4,582 (matched, 209.9 s) | 4,064 (matched, 201.9 s) | 4,795 (matched, 209.2 s) | 7,216 (matched, 208.8 s) |

The reduced model's values for the predictions:

- E*(C8) with the 21.39 s delivery for B1's four tests: M50_PT_Exp4 7,062 J (bracket 7,042 to 7,083 J), 1.49 times E*(C2) = 4,754 J; M50_PP_Exp2 6,854 J (bracket 6,833 to 6,875 J), 1.72 times E*(C2) = 3,975 J; M50_SP_Exp3 3,528 J (bracket 3,519 to 3,537 J), E*(C2) = 0; M50_ST_Exp3 10,281 J (bracket 10,250 to 10,312 J), 0.85 times E*(C2) = 12,030 J. B1's first runs lie 5 % below and above these.
- M50_PT_Exp4, 21.39 s: at the upper end of the bracket (7,083 J) C8 at 310.6 s, the far face reading 240.1 C twenty seconds before it (no jump before C8); at 1.05 E*(C8) C8 at 192.3 s, the far face's jump starting at 233.8 C; at 1.15 E*(C8) C8 at 121.5 s, the far face's jump starting at 230.2 C.
- The hold (B3 (b)'s rule on the 2.5 W grid from 10 W): matched, 12.5 W; C8 times by power: 10 W 344.2 s, 12.5 W 265.9 s. B3 (b)'s first run is at 12.5 W.
- M50_PT_Exp4 at 5,045 J under the draws of rank 5, 50, 151, 196 and the aged SEI: no C8 (mean peak 189.0 C), no C8 (mean peak 188.5 C), no C8 (mean peak 190.5 C), no C8 (mean peak 189.0 C), no C8 (mean peak 185.5 C); the least shift: 20.0 K (C8 at 316.2 s).
- M50_PT_Exp4 with 240 s of constant power: 6,209 J no C8 (mean peak 220.5 C), 5,821 J no C8 (mean peak 211.4 C).

## Part B, the registered list

- B1 For M50_PT_Exp4, PP_Exp2, SP_Exp3 and ST_Exp3, the 21.39 s triangular delivery: runs at A2's E*(C8) (the reactive cross-section's, results/stage15_cross_section.json, registered with the predictions) less 5 % and plus 5 %; then, while both have C8 or neither has, one further step of 10 % of A2's value on the side needed (down from the lowest with C8, or up from the highest without), until a run with C8 lies above one without. The bracket is (highest without C8, lowest with C8]; its midpoint is the run's E*(C8).
- B2 M50_PT_Exp4 with constant power over 240 s at f = 0.05 (6,209 J, the archived run that ended at 332 s) and at f = 0.046875 (5,821 J), each to C8 or 900 s.
- B3 (a) B1's M50_PT_Exp4 run at the upper end of its bracket, scored against the measured history by Stage 10's rule (the far-face node, 0 to 271.5 s, or to C8 where C8 comes first). (b) The pulse and the hold: f = 0.040625 (5,045 J) over 21.39 s, then a constant power P from 21.39 s until the run ends; P from the cross-section's value on the 2.5 W grid (results/stage15_cross_section.json), then steps of 2.5 W (down while C8 comes more than 10 s before 271.5 s, up while it comes more than 10 s after it or not at all) until C8 lies within 10 s of 271.5 s, or the two neighbouring powers bracket 271.5 s (C8 earlier than 261.5 s at one, later than 281.5 s or absent at the other), or 16 runs are made.
- B4 M50_PT_Exp4 at f = 0.040625 over 21.39 s under Stage 11's kinetic draws by rank 5, 50, 151 and 196 (Stage 3's draws 188, 83, 40 and 184) and with the aged SEI; then, at the posterior mean, the rate laws evaluated at T + s: s = 5, 10, 15, ... K until C8 happens (at most 60 K), then the shift 2.5 K below the first with C8.
- V4 B1's M50_PT_Exp4 runs at the two ends of its bracket, each again with the mesh refined by 1.5 and with every step limit halved (`dt_scale` 0.5).
- A run that fails is made again at once; a run that fails twice is recorded as failed and stops its chain, which is then reported as stopped.

Every run: both neighbours, the resolved one stopped at C8 or run to 900 s, its hot spot's crossing recorded without a stop, the lumped twin to 900 s; Stage 10's five probes of the resolved neighbour at mid-length; the sub-step limit 4,096 from the delivery's start. The first runs of every chain:

- `s15_B1_PT_Exp4_s-1`
- `s15_B1_PT_Exp4_s+1`
- `s15_B1_PP_Exp2_s-1`
- `s15_B1_PP_Exp2_s+1`
- `s15_B1_SP_Exp3_s-1`
- `s15_B1_SP_Exp3_s+1`
- `s15_B1_ST_Exp3_s-1`
- `s15_B1_ST_Exp3_s+1`
- `s15_B2_PT_Exp4_con240_f0.050000`
- `s15_B2_PT_Exp4_con240_f0.046875`
- `s15_B3_PT_Exp4_hold12.5W`
- `s15_B4_PT_Exp4_draw188`
- `s15_B4_PT_Exp4_draw83`
- `s15_B4_PT_Exp4_draw40`
- `s15_B4_PT_Exp4_draw184`
- `s15_B4_PT_Exp4_aged`
- `s15_B4_PT_Exp4_shift5.0K`

## Predictions

**P1.** The reactive cross-section's E*(C8) lies within 15 % of the midpoint of the three-dimensional bracket in at least three of B1's four tests. *Scored:* for each of B1's four tests, |E*(C8) of the cross-section - m| / m <= 0.15, m the midpoint of B1's final bracket (a test whose search does not bracket counts as not within); holds if at least three are within. *Reduced model:* the cross-section's E*(C8) are the centres of B1's searches (above); P1 measures how near the three-dimensional threshold lies to them. *Expectation (unscored):* uncertain.

**P2.** For M50_PT_Exp4 with the 21.39 s delivery, E*(C8) lies between 6 and 10 kJ. *Scored:* holds if the midpoint of B1's final bracket for M50_PT_Exp4 lies between 6,000 and 10,000 J. *Reduced model:* 7,062 J. *Expectation (unscored):* likely (the mean peaks at 190.6 C with 5,045 J and gains about 9 K per further kilojoule).

**P3.** In at least three of B1's four tests E*(C8) exceeds the whole-cell clock's threshold by 25 % or more. *Scored:* for each test, the midpoint of B1's final bracket against E*(C2) (above): it exceeds it by 25 % or more if it is at least 1.25 E*(C2); where E*(C2) is 0 (M50_SP_Exp3) any E*(C8) above 0 does; holds if at least three tests do. *Reduced model:* PT_Exp4 1.49; PP_Exp2 1.72; SP_Exp3 E*(C2) = 0; ST_Exp3 0.85 times E*(C2). *Expectation (unscored):* likely for the three strong triggers, uncertain for M50_ST_Exp3, whose weak trigger leaves the delivery to heat the whole cell in either model.

**P4.** For M50_PT_Exp4, in the crossing run at the upper end of B1's bracket the mean crosses between 150 and 400 s after the trigger's start. *Scored:* holds if that run's C8 time lies between 150 and 400 s. *Reduced model:* C8 at 310.6 s at the upper end of its bracket, 192.3 s at 1.05 E*(C8). *Expectation (unscored):* likely.

**P5.** In that run the far face reads more than 15 K above 197.3 C, the reading from which the measured neighbour jumped, when its own jump begins. *Scored:* holds if the far face's reading at its jump's start (the rule above) exceeds 212.3 C. *Reduced model:* 240.1 C at the upper end of its bracket, 233.8 C at 1.05 E*(C8). *Expectation (unscored):* likely.

**P6.** In B3 (b) the hold that brings the cell's own runaway to 271.5 s lies between 5 and 25 W. *Scored:* holds if the power at which C8 falls within 10 s of 271.5 s lies between 5 and 25 W; where the search ends with two neighbouring powers bracketing 271.5 s instead, if both lie between 5 and 25 W; otherwise it fails. *Reduced model:* 12.5 W. *Expectation (unscored):* likely.

**P7.** Under none of the four draws and not with the aged SEI does the resolved cell run away at M50_PT_Exp4's 5,045 J; and the least shift of the rate laws that makes it run away is 10 K or more, against the 6.1 K that the posterior's ignition temperatures span. *Scored:* holds if none of B4's five runs reaches C8 and B4's least shift (on its 5 K, then 2.5 K steps) is at least 10 K. *Reduced model:* none of the five reaches C8; the least shift 20.0 K. *Expectation (unscored):* likely.

**P8.** M50_PT_Exp4's 240 s run at 6,209 J, carried to 900 s, runs away. *Scored:* holds if B2's run at f = 0.05 reaches C8 within 900 s. *Reduced model:* no C8. *Expectation (unscored):* likely.

## Checks

- V1 (made in Part A0): the mean's crossing and peak of every archived continued run read by two separate codes from the stored series agree to 0.1 s and 0.01 K. Result: they agree to 0 s and 0 K in all 199.
- V2: every new run's energy account closes to under 1e-9 of the heat taken in, and a run stopped at C8 reports the energy delivered up to its stop (each delivery equal to its pulse's integral to the stop, to 1e-9 relative).
- V3 (made in Part A): the reactive cross-section with the reaction off equals Stage 13's conduction model to 1e-8 K. Result: 7.4e-13 K.
- V4: B1's two M50_PT_Exp4 runs at the ends of its bracket made again with the mesh refined by 1.5 and with every step limit halved: the outcome (C8 or none) does not change, and the C8 time moves by less than 5 %.
- V5: an independent read by a separate agent that has not seen the work being produced: every number of the note's Stage 15 lines, the table and the sentences recomputed from the records.

