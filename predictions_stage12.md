# Stage 12 predictions: the trigger held to the calorimetry

Committed and pushed before any Stage 12 run (brief of 3 November 2026; DECISIONS.md D122 and D123). Stage 12 asks two questions of the conduction model with the trigger's energies held to what calorimetry measured for this cell. Part A: with the trigger's body energy capped at the Battery Failure Databank's largest for the LG M50, 33,222.9 J (row 15, RUN195), do conduction and radiation alone still meet the local criterion C1 in the eight tests where the fitted trigger meets it at f = 0, at the central and the high contact? Part B: with the ejected energy fixed at the Databank's median measured value, 76,741.25 J (rows 9 to 18), instead of 3.105 times each test's fitted body energy, what are the thresholds of the four Stage 11 tests (B1), the fractions that reproduce the nine measured times (B2), and the spread of the fractions between tests (Part C)?

## The predictions (the brief's, word for word)

- **P1.** With E_b capped at 33.2 kJ, conduction and radiation alone meet C1 in none of the eight tests at the central contact. Expectation: likely (Stage 5 found no ignition at 33.2 kJ with the two-cell study's trigger).
- **P2.** At the high contact the same holds. Expectation: uncertain.
- **P3.** With E_e fixed at the Databank's median, the delivered energies E* across the nine propagated tests still span at least tenfold. Expectation: likely.
- **P4.** With E_e fixed, the propagated and non-propagated tests' fractions still overlap (the largest f_max above the smallest f_t(C2)). Expectation: likely.

## What the earlier records already fix

Every outcome below is stated before any Stage 12 run, from records committed with Stages 6 and 9 (D122 (6) and (7)).

- **P1.** With the trigger capped and no delivery, a run depends on the test only through its connection, so the eight tests fall on two points at each contact (six in series, two in parallel). Stage 6 already holds both central-contact points, at the posterior mean, the central tabs, 33,222.9 J and 21.39 s (`results/stage6_runs/body_mean_series_hcentral_gcentral_tau21.39_E33.22.json` and `..._parallel_...`): neither neighbour reaches 255.7 C, the hot spot peaking at 192.16 C (series) and 191.90 C (parallel). P1 therefore holds unless Stage 12's runs, made with the Stage 9 to 11 loops, differ from Stage 6's by more than 63 K at the hot spot; they are expected to agree to round-off (check X).
- **P2.** At the high contact Stage 6 holds both connections with the low and the high tabs, not the central ones: the hot spot peaks at 226.14 to 226.75 C and nothing crosses. The central tabs lie between, so the hot spot is expected near 226.5 C, about 29 K short of 255.7 C. P2 is close to fixed, but these two points are new runs.
- **P3.** A run depends on the fraction and the ejected energy only through the delivered energy, so the energies at f_t(C2) are those Stage 9 found: 1,819.0 to 5,962.4 J in the five matched tests and 265.7 J (interpolated, within (0, 527.0 J]) in M50_SP_Exp3, a span of about 22. The new searches can move M50_SP_Exp3's energy only within its bracket, and can add a threshold test only within its own bracket, 4,657 to 5,045 J (M50_PT_Exp4) or 947 to 1,421 J (ST_Exp4), both inside the span; the span stays above 10 unless M50_SP_Exp3's energy rose above 596.2 J, outside its bracket. P3 is fixed by Stage 9's records.
- **P4.** For the same reason the registered f_max keep their energies: M50_PT_Exp1's 2,090.7 J, a fraction 0.0272 of the fixed energy, the others 0. The smallest f_t(C2) is M50_SP_Exp3's, at most 527.0 J, a fraction at most 0.0069. P4 is fixed by Stage 9's records.

So Stage 12's outcomes are, but for the two high-contact runs, already decided by records made before it; its runs confirm them with the Stage 9 to 11 loops and add the central tabs at the high contact. The predictions are scored as the brief states them all the same.

## Scoring

- **P1** holds if, in both central-contact runs of Part A (series and parallel), the resolved neighbour's hottest node does not reach 255.7 C within 900 s: then C1 is met in none of the eight tests.
- **P2** holds if the same is true of both high-contact runs.
- **P3** holds if, among the propagated tests whose B2 search ends matched or bracketed (Stage 10 C3's rule), the largest delivered energy at f_t(C2), f_t times 76,741.25 J, is at least ten times the smallest. "E*" in the brief's wording is read as that energy, the one B2 computes.
- **P4** holds if the largest registered f_max (the two exploratory maxima apart) exceeds the smallest f_t(C2) of B2 (matched or bracketed), both as fractions of 76,741.25 J.

A failure counts as foreseen if this file records it as already fixed by earlier records (the rule of the supplement's S2). Part C and the bands of Part B are reported, not scored.

## The run list before any Stage 12 record

Ten runs (Part A's four; B1's three and B2's three first steps), SHA-256 d18bed85c5c0c3fbdebcfeb06f1e760c8a5b64644cb8e6d387699bf606e4bfac (`python3 src/stage12_run.py list`). Later runs follow from the records by the searches of D123 (2) and (3).
