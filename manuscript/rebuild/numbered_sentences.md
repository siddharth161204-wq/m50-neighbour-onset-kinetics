# Every numbered sentence of the rebuilt manuscript, with its sources (20 November 2026)

Written by `src/make_rebuild_sentences.py` from the numbers check's trace (`numbers_trace.json`). Each sentence is followed by its numbers, the file and value each is read from, and "new" where the manuscript as submitted on 17 November 2026 does not state that number. Sentences are as the check reads them, with LaTeX spacing marks (~ is a space).
170 numbered sentences; 106 of them carry a number the submitted manuscript does not state (294 numbers in all).



## main.tex: abstract

1. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29~K short.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
2. Fitted instead to each test's trigger peak, that energy gives resolved thresholds 1.5 and 1.7 times the lumped ones in two strong-trigger tests and 0.85 times after a weak trigger.
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
3. In one test the resolved neighbour needs every reaction run as if over 17.5~K hotter to run away with the lumped one's energy; kinetic uncertainty spans 6.1~K of ignition temperature.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
4. At the central contact a two-dimensional reactive cross-section afterwards reproduced all 151 archived three-dimensional outcomes, most far from a threshold.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
5. The one published record of a propagating neighbour fits neither: its final rise starts 37~K cooler than on the resolved model's far side.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008

## main.tex: Introduction to Discussion, with figure captions

6. Calorimetry shows why the vent matters: fractional thermal runaway calorimetry of 18650 cells finds that typically 20 to 30\,\% of the total energy leaves through the casing and the rest with the ejecta~ , the Battery Failure Databank holds such measurements for many cells, the LG M50 among them~ , and burning vent gas can add to them in open air~ .
   - 20: manuscript/data/comparators.csv: value where {'key': 'walker2019decoupling', 'quantity': 'share of the total energy released through the casing, low'} = 20
   - 30: manuscript/data/comparators.csv: value where {'key': 'walker2019decoupling', 'quantity': 'share of the total energy released through the casing, high'} = 30
7. Nine propagated, 147 to 342~s after the trigger's runaway.
   - 147: smallest and largest of inputs/fransson2024/m50_tests.csv: time_to_propagation_s = 147
   - 342: smallest and largest of inputs/fransson2024/m50_tests.csv: time_to_propagation_s = 342
8. The neighbours of five of the seven tests that did not propagate peaked at 71 to 133\degC; the other two report 626 and 808\degC, which the paper's note on thermocouples that moved during failure may explain, and are treated as exploratory.
   - 71: smallest and largest of inputs/fransson2024/m50_tests.csv: neighbour_max_C of the tests that did not propagate, without the two exploratory maxima = 71
   - 133: smallest and largest of inputs/fransson2024/m50_tests.csv: neighbour_max_C of the tests that did not propagate, without the two exploratory maxima = 133
   - 626: inputs/fransson2024/m50_tests.csv: neighbour_max_C where {'propagated': 'No'} = 626
   - 808: inputs/fransson2024/m50_tests.csv: neighbour_max_C where {'propagated': 'No'} = 808
9. The failing cell, the trigger, is one temperature that releases its body energy $E_\mathrm{b}$ inside itself as a triangular pulse over 21.39~s, the mean of the trigger's rise times in the two records of Fransson et al.'s supplementary Figure~10 (17.53 and 25.24~s; Supplementary Section~S7).
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 17.53: results/stage7_paper_numbers.json: triggers.levels.tau_s[0] = 17.5332
   - 25.24: results/stage7_paper_numbers.json: triggers.levels.tau_s[2] = 25.2399
10. Each test has its own trigger: the $E_\mathrm{b}$ that puts the model's trigger at the test's measured trigger peak at the central contact (below), 9.0 to 54.3~kJ (Table~ ).
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
11. In thirteen of the sixteen tests it exceeds 33.2~kJ, the largest body energy the Battery Failure Databank measured in the ten nail tests of this cell~ , perhaps because the trigger's flame heats the thermocouple the energy is matched to; the same tests are therefore also run with the body energy held to 33.2~kJ.
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
12. A trigger whose fitted body energy is 31.6 to 54.3~kJ is called strong here, and the two of 9.0 and 16.6~kJ weak.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
13. The Databank's median energy carried by this cell's ejecta is 76.74~kJ and its largest 89.34~kJ; each test's ejected energy is taken as 3.105 times its fitted body energy, the Databank's median ratio for this cell.
   - 76.74: results/stage14_inputs.csv: value where {'key': 'db_Eej_median'} = 76.7412
   - 89.34 (new): results/stage14_inputs.csv: value where {'key': 'db_Eej_max'} = 89.3378
   - 3.105: results/stage8_ejected.csv: ratio_central where {'id': 'M50_PT_Exp1'} = 3.10529
14. The lumped neighbour is one temperature $T$: [display] where $T_1$ is the trigger's temperature, $C=61.75$~J\,K$^{-1}$ the cell's heat capacity and $m$ its mass, $G_c$ the conductance of the contact and its air wedge integrated over the can, $G_t$ that of the welded tabs, $F$ the view factor between the cans and $A_\ell$ the lateral area, $h_a$, $A_a$ and $A_r$ the room's convection coefficient and the areas that convect and radiate to the room at $T_a=25$\degC{} (both cells start at it), $\dot q_r$ the reaction heat per unit mass (Section~ ) and $P(t)$ the delivered heat (Section~ ).
   - 61.75: results/manuscript_numbers.json: constants.C_cell_J_K = 61.75
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
15. The resolved neighbour is a three-dimensional half model, symmetric about the plane through both axes, of linear tetrahedral finite elements on 19,355 nodes: an anisotropic roll inside a 0.25~mm steel can, [display] with the conductivity $\mathbf{k}$ 1.3~W\,m$^{-1}$\,K$^{-1}$ across the layers and 25~W\,m$^{-1}$\,K$^{-1}$ along them and the same total heat capacity.
   - 19,355: results/stage8_paper_numbers.json: v3.base.n_nodes = 19355
   - 0.25: results/manuscript_numbers.json: constants.can_thickness_mm = 0.25
   - 1.3: results/manuscript_numbers.json: constants.k_radial_W_mK = 1.3
   - 25: results/manuscript_numbers.json: constants.k_axial_W_mK = 25
16. On the can, within 45\textdegree{} of the line of contact the heat flux to the trigger is $h(\theta)(T-T_1)$ with [display] a steel-on-steel contact conductance $h_c$ in series with the air in the wedge of width $\delta$ at angle $\theta$ from the line of contact, $a=10.55$~mm being the cell's radius; $h_c$ is 2,000 or 3,700~W\,m$^{-2}$\,K$^{-1}$ for the central and high contact, the two ends of a textbook's range for stainless steel on stainless steel in air, and 200~W\,m$^{-2}$\,K$^{-1}$ for the low contact, its lowest value with the gap evacuated~ , since no conductance between cylindrical cells in contact was found.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
   - 10.55 (new): results/manuscript_numbers.json: constants.cell_radius_mm = 10.55
   - 2,000: results/manuscript_numbers.json: constants.h_contact_W_m2K.central = 2000
   - 3,700: results/manuscript_numbers.json: constants.h_contact_W_m2K.high = 3700
   - 200: results/manuscript_numbers.json: constants.h_contact_W_m2K.low = 200
17. The sector, 45\textdegree{} either side, is that of the earlier two-cell study~ ; the wedge's conductance $k_\mathrm{air}/\delta$ falls below the room's convection coefficient short of its edge, and beyond it the can loses heat to the room by convection; everywhere it radiates to the room and receives the trigger's radiation shared over $\theta$ by the local view factor.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
18. Three criteria read the neighbour's runaway, each at 255.7\degC, the lower edge of the internal-short band of the kinetic source~ , within 900~s of the trigger's release, a window chosen here (Fig.~ b); the level lies above the ignition temperature of Section~ , past which a lumped neighbour's reaction heat outruns its losses, while a hottest point that reaches it need not run the cell away.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
19. (a) The pair at mid-length: the trigger is one temperature; the neighbour is solved as one temperature and as a resolved half model, symmetric about the dash-dotted plane; heat is delivered through the half of its can that faces the trigger; within 45\textdegree{} of the line of contact the cans exchange heat through the contact and its air wedge.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
20. The model's five surface probes lie at mid-length, at 0, 0.33, 88.3, 94.4 and 180\textdegree{} from the line of contact; three are drawn (on the line of contact, on the side and on the far face), and they span the possible angles of the measured thermocouple, which the tests do not report.
   - 0: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 0.325853
   - 0.33: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 0.325853
   - 88.3: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 88.2771
   - 94.4 (new): src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 94.392
   - 180: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 180
21. (b) One run, PT-Exp4 with 7.4~kJ delivered over 21.4~s: the resolved neighbour's hottest point reaches 255.7\degC{} at 8~s, the lumped neighbour at 107~s and the resolved neighbour's mean at 182~s.}
   - 7.4 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: E_J = 7.41562
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 8: results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: C1_t_s = 8.27672
   - 107: results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: lumped_C2_t_s = 106.51
   - 182 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
22. Reaction $j$ runs at $r_j=\exp\!\big(\sum_s n_{sj}\ln c_s+\ln A_j+b_j\ln T-E_{a,j}/(RT)\big)$, its species change as $\mathrm{d}c_s/\mathrm{d}t=\sum_j\nu_{sj}r_j$, and its heat enters per unit cell mass as $\dot q_r=\sum_j\Delta H_j r_j m_j/M_\mathrm{ref}$, with $M_\mathrm{ref}$ the mass of the source's 720~g reference cell and $m_j$ its reactant masses.
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
23. The model is the mean of each parameter over the source's posterior particles; in an emulation of the accelerating-rate calorimetry that the source simulated for its 720~g reference cell (Supplementary Section~S2) it gives an exotherm onset of 179.3\degC, inside the source's band of two standard deviations about its main cluster's mean, 169.0 to 198.0\degC, but reaches the source's internal-short rate, 1~K\,min$^{-1}$ of self-heating, at 199.8\degC, below that event's band of 255.7 to 302.1\degC, a difference not resolved here.
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
   - 179.3: results/note_numbers.json: V1.T_in_C = 179.252
   - 169.0: DECISIONS.md: /main-cluster mean, (169\.0) to 198\.0/ = 169
   - 198.0: DECISIONS.md: /main-cluster mean, 169\.0 to (198\.0)/ = 198
   - 1: DECISIONS.md: /T_on at the paper's stated trigger \((1) C/min\)/ = 1
   - 199.8: results/note_numbers.json: V1.T_on_1_C_per_min_C = 199.794
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 302.1: DECISIONS.md: /below the paper's band of 255\.7 to (302\.1)/ = 302.1
24. Over the 164 of the 200 draws below in the source's main cluster the exotherm onset runs from 146.3 to 191.4\degC{} (central 95\,\%), and the check recorded for the draws against the source's band failed; it passed only as amended after the failure (Supplementary Section~S2).
   - 164: results/stage3_v4.json: main_cluster_T_in_C.n = 164
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 146.3 (new): results/stage3_numbers.json: V4_registered/T_in_p2.5_C = 146.3
   - 191.4 (new): results/stage3_numbers.json: V4_registered/T_in_p97.5_C = 191.4
   - 95: predictions_stage13.md: /the central (95) % of the 200 draws/ = 95
25. The posterior enters as 200 joint draws, each taking one posterior particle of each of the three submodels (anode and electrolyte, cathode, separator), which treats them as independent.
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
26. Its shape in time is a triangular pulse over 21.39~s from the start of the trigger's release, rising to its peak at half its length, a constant power over 120, 240 or 360~s, spanning the measured times, or, in one test, a pulse followed by a constant power; the reduced models are tested in Section~ with triangular pulses of 5 to 360~s.
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 120: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 120
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 360
   - 5: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 5
   - 360: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 360
27. For a test that propagated, its need is the least energy with which a criterion is met within 10~s of the measured time, counted as delivered by the time it is met.
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
28. Where the least energy run that meets the criterion meets it before the measured time and the next lower run, 0.5\,\% of the test's ejected energy below, does not meet it, the measured time is reproduced only between the two, within that resolution of the threshold, and the need is the higher, counted to the time it is met (marked t in Supplementary Tables S3 and S7).
   - 0.5: results/stage15_cross_section.json: settings.width_ft = 0.5
29. For a test that did not propagate, the need is the energy at which the far face peaks at the measured maximum (within 5~K).
   - 5: predictions_stage9.md: /within (5) K of it/ = 5
30. The far face's jump is taken to begin when its rate of rise over 2~s first reaches 1~K\,s$^{-1}$ after having reached 0.5~K\,s$^{-1}$ and fallen below it (Supplementary Section~S7).
   - 2: src/stage15_inputs.py: /DIFF_S = (2\.0)/ = 2
   - 1: src/stage15_inputs.py: /RISE_JUMP = (1\.0)/ = 1
   - 0.5: src/stage15_inputs.py: /RISE_SLOW = (0\.5)/ = 0.5
31. The two-body model runs the trigger and the lumped neighbour without reaction and asks when the neighbour reaches $T_\mathrm{ign}$ with enough heat of the low-temperature cathode reaction left to reach 255.7\degC.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
32. For each path by which the trigger's ejecta or its circuit can heat the facing half, a lower and an upper bound were set on the energy delivered within the pulse's 21.4~s and in total, from published inputs alone, each read at its source and labelled as measured on this cell or on another (Table~ ; the inputs in Supplementary Table~S5).
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
33. The neighbour's own discharge in the parallel tests heats it from inside rather than through the facing half, and is bounded for comparison by its stored energy in every window; beside that bound, a short across its least resistance at 25\degC{} would dissipate 15.6~kJ within 21.4~s.
   - 25: results/stage14_inputs.csv: /0\.5 C for 30 s, (25) C/ = 25
   - 15.6 (new): results/stage14_bounds.json: A6/conditional_25C_J/21.39 = 15.6394
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
34. Of 98 predictions (eighteen in four steps on the earlier two-cell study's geometry~ , not reported here), 56 held and 42 failed, 24 of the failures foreseen in the files' own analyses and four of the holds known there from earlier records; every one, its expectation and its verdict are in Supplementary Table~S2, and two departures from this order in Supplementary Section~S2.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98
   - 56 (new): manuscript/rebuild/data/predictions_registry.csv: rows with verdict held = 56
   - 42: manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed = 42
   - 24 (new): manuscript/rebuild/data/predictions_registry.csv: rows foreseen = 24
35. Halving the mesh spacing and every step limit moved the hottest point's peak rise by at most 0.52\,\%; at both ends of PT-Exp4's resolved bracket, refining the mesh by a factor of 1.5 and halving every step limit left the outcome unchanged and moved the runaway time by at most 1.5\,\%.
   - 0.52: results/stage8_paper_numbers.json: checks.V3.v3mesh.relative_change = 0.515385
   - 1.5: predictions_stage15.md: /the mesh refined by (1\.5)/ = 1.5
   - 1.5: results/stage15_checks.json: V4/s15_B1_PT_Exp4_s+1_r1.5/rel_change = 1.48397
36. With body energies up to 33.2~kJ and the cans in contact, conduction and radiation take neither neighbour to 255.7\degC{} within 900~s in any of 5,248 runs over the brackets of contact, tab conductance, the trigger's release (over 10 or 30~s) and connection and under the 200 kinetic draws (Supplementary Section~S2): the hottest point peaks at most at 226.7\degC, 29.0~K short, and the lumped neighbour at 180.6\degC.
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 5,248: results/v12_numbers.json: runs.all = 5248
   - 10: manuscript/data/parameters.csv: /Release durations, Stage 5",tau,(10) and 30/ = 10
   - 30: manuscript/data/parameters.csv: /Release durations, Stage 5",tau,10 and (30)/ = 30
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 226.7: results/v12_numbers.json: all_runs.res_peak_hottest_C.max = 226.67
   - 29.0: 255.7 C less results/v12_numbers.json: all_runs.res_peak_hottest_C.max = 29.0299
   - 180.6: results/v12_numbers.json: all_runs.lum_peak_C.max = 180.633
37. With each test's own fitted trigger, conduction carries the hottest point over 255.7\degC{} in the eight tests with the largest fitted triggers (46.5 to 54.3~kJ), within 21.7~s, and the lumped neighbour in two.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 46.5: smallest and largest of results/stage12_capped.csv: E_b_fitted_J = 46.4567
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 21.7: results/stage12_paper_numbers.json: part_a.central.fitted_C1_at_f0_s[1] = 21.7
38. Held to 33.2~kJ, those eight tests, whose inputs then differ only in their connection, ignite neither neighbour: the hottest point peaks at 191.9 and 192.2\degC{} at the central contact and at 226.4 and 226.7\degC{} at the high contact, 63.5 to 63.8~K and 29.0 to 29.3~K short of 255.7\degC, and the lumped neighbour at most at 177.4\degC.
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 191.9: results/stage12_paper_numbers.json: part_a.central.hot_spot_peak_C[0] = 191.9
   - 192.2: results/stage12_paper_numbers.json: part_a.central.hot_spot_peak_C[1] = 192.16
   - 226.4: results/stage12_paper_numbers.json: part_a.high.hot_spot_peak_C[0] = 226.39
   - 226.7: results/stage12_paper_numbers.json: part_a.high.hot_spot_peak_C[1] = 226.69
   - 63.5: results/stage12_paper_numbers.json: part_a.central.shortfall_hot_spot_K[0] = 63.5
   - 63.8: results/stage12_paper_numbers.json: part_a.central.shortfall_hot_spot_K[1] = 63.8
   - 29.0: results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 29.3: results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[1] = 29.3
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 177.4: results/stage12_paper_numbers.json: part_a.high.lumped_peak_C[1] = 177.4
39. Even with the fitted triggers and no delivery, the resolved neighbour as a whole runs away in no test at any contact (at the low contact its hottest point peaks at most at 162.6\degC; at the high contact this rests in ten tests, PT-Exp2, PT-Exp4, PP-Exp1, PP-Exp2, PP-Exp4, ST-Exp4 and the four SP tests, on the reactive cross-section of Section~ alone, whose mean peaks there at most at 199.2\degC{} and which was checked only at the central contact; Section~ ), while nine tests propagated in the rig.
   - 162.6 (new): results/stage7_crossings.csv: hot_peak_C, the largest of the per-test runs at the low contact = 162.614
   - 199.2 (new): smallest and largest of results/stage15_nodelivery.csv: mean_peak_xs_C, high contact, outcome from the cross-section = 199.206
40. With the 21.4~s pulse the three criteria have different thresholds (Fig.~ ; Supplementary Table~S3), except that in PP-Exp1 and SP-Exp3 the local and lumped are both zero.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
41. The local threshold is zero in the eight tests whose fitted trigger alone carries the hottest point over 255.7\degC, and at most 4.53~kJ (PT-Exp1).
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 4.53 (new): results/stage14_needs.csv: threshold_C1_hi_J where {'test': 'M50_PT_Exp1'} = 4.5298
42. The lumped threshold is zero in two tests and at most 12.89~kJ (PT-Exp1).
   - 12.89 (new): results/stage14_needs.csv: threshold_C2_hi_J where {'test': 'M50_PT_Exp1'} = 12.8924
43. By the reactive cross-section, the resolved threshold is 3.5 to 10.8~kJ in all sixteen tests: above the lumped threshold's bracket in thirteen of the fourteen with strong triggers, including 4.5 and 3.5~kJ in the two where the lumped threshold is zero, above its midpoint in the fourteenth, PT-Exp3, whose two brackets overlap, and below it in the two with weak triggers.
   - 3.5: smallest and largest of results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J = 3.52778
   - 10.8 (new): smallest and largest of results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J = 10.7812
   - 4.5 (new): results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J of the two tests whose lumped neighbour needs no delivery = 4.54167
   - 3.5: results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J of the two tests whose lumped neighbour needs no delivery = 3.52778
44. The three-dimensional model confirms this in the four tests it searched, each search starting 5\,\% either side of the cross-section's value, so that a bracket closed by its first two runs, as in three of the four, has that value as its midpoint.
   - 5: predictions_stage15.md: /less (5) % and plus 5 %/ = 5
45. Its resolved threshold lies between 6.71 and 7.42~kJ in PT-Exp4 and between 6.51 and 7.20~kJ in PP-Exp2, 1.38 to 1.59 and 1.36 to 2.26 times the lumped thresholds across the brackets (4.66 to 4.85 and 3.18 to 4.77~kJ), so the order holds at either end, and the ratios of the midpoints are 1.49 and 1.72.
   - 6.71 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.lo_J = 6.70937
   - 7.42 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 6.51 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.lo_J = 6.51146
   - 7.20 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.hi_J = 7.19687
   - 1.38: results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PT_Exp4 = 1.38309
   - 1.59 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PT_Exp4 = 1.5924
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 2.26 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2 = 2.26317
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 4.85: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_PT_Exp4'} = 4.851
   - 3.18 (new): results/stage14_needs.csv: threshold_C2_lo_J where {'test': 'M50_PP_Exp2'} = 3.18
   - 4.77 (new): results/stage14_needs.csv: threshold_C2_hi_J where {'test': 'M50_PP_Exp2'} = 4.77
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
46. In SP-Exp3 it lies between 3.70 and 4.06~kJ (3.88~kJ), while the lumped neighbour runs away with no delivery.
   - 3.70 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.lo_J = 3.70417
   - 4.06 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.hi_J = 4.05694
   - 3.88 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.mid_J = 3.88056
47. With PT-Exp4's, PP-Exp2's and SP-Exp3's strong triggers the lumped neighbour runs away in every run of these searches, at 106 to 128~s, releasing 22.4 to 22.6~kJ of reaction heat, where the resolved neighbour has released 4.1 to 4.8~kJ by its own runaway.
   - 106 (new): smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_C2_t_s = 106.141
   - 128: smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_C2_t_s = 127.543
   - 22.4 (new): smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_rxn_J = 22.3795
   - 22.6: smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_rxn_J = 22.5889
   - 4.1 (new): smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3 with the mean's runaway: rxn_J = 4.07541
   - 4.8: smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3 with the mean's runaway: rxn_J = 4.79567
48. Of these four tests, only ST-Exp3's weak trigger (16.6~kJ) reverses the order: the resolved threshold lies between 9.77 and 10.80~kJ (10.28~kJ), 0.85 times the lumped threshold of 12.03~kJ (0.81 to 0.90 across the brackets), and at 10.80~kJ the resolved neighbour runs away at 61.5~s while the lumped neighbour does not run away.
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
   - 9.77 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.lo_J = 9.76719
   - 10.80 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.hi_J = 10.7953
   - 10.28 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.mid_J = 10.2812
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
   - 12.03 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.E_C2_J = 12.0305
   - 0.81 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3 = 0.806439
   - 0.90 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3 = 0.903373
   - 10.80 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.hi_J = 10.7953
   - 61.5 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3, the run at the bracket's upper end: t_C8_s = 61.5222
49. \caption{The thresholds of the sixteen tests with the 21.4~s pulse, in order of the trigger's fitted body energy (top axis): the least energy delivered to the facing half at which the resolved neighbour's hottest point (triangles), the lumped neighbour (squares) and the resolved neighbour's mean (circles, reactive cross-section; diamonds, three-dimensional model) reach 255.7\degC.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
50. Up to pulses of 120~s, in the three tests searched, the local threshold is set by conduction (Fig.~ a; Supplementary Table~S8).
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
51. In the searches made to test this, PT-Exp1 at 5, 40 and 120~s and ST-Exp3 and PT-Exp3 at 10 and 60~s, which started at the cross-section conduction model's value with a step of 3\,\%, the resolved model's local threshold lies within one step of that value, which is one end of each final bracket; the table's other brackets up to 120~s contain it, bar one just above it.
   - 5: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 5
   - 40: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 40
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 10: results/stage13_skin.csv: tau_d_s where {'test': 'M50_ST_Exp3', 'region': 'half'} = 10
   - 60: results/stage13_skin.csv: tau_d_s where {'test': 'M50_ST_Exp3', 'region': 'half'} = 60
   - 3: src/stage13_inputs.py: /FIRST_STEP = (0\.03)/ = 3
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
52. The pulse's Fourier number $\alpha\tau/a^2$ there runs from 0.025 to 0.60, with $\alpha=5.565\times10^{-7}$~m$^2$\,s$^{-1}$ the roll's diffusivity across its layers ( ), $\tau$ the pulse's duration and $a$ the cell's radius.
   - 0.025: results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '5.0'} = 0.0250038
   - 0.60 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '120.0'} = 0.600091
   - 5.565\times10^{-7}: results/stage13_sentences.md: /\(([\d.]+e-7) m2/s\)/ = 5.565e-07
53. With the reaction switched off at the upper end of each such search, the hottest point still reaches 255.7\degC{} or falls short by at most 1.1~K, so the reaction plays almost no part in it.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 1.1 (new): results/stage13_skin.csv: the largest shortfall of inert_peak_minus_level_K up to a Fourier number of 0.6 = 1.13572
54. Over 360~s (Fourier number 1.80) the cell heats through: the threshold falls below the conduction model, the hottest point without the reaction peaks 18.9~K short, and with it the crossing comes at 316.5~s on the cell's axis with the mean at 240.1\degC, a runaway inside the cell.
   - 360: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 360
   - 1.80 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 1.80027
   - 18.9 (new): results/stage13_skin.csv: inert_peak_minus_level_K where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 18.9319
   - 316.5 (new): results/stage13_skin.csv: res_t_cross_hi_s where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 316.544
   - 240.1 (new): results/stage13_skin.csv: res_mean_at_cross_hi_C where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 240.119
55. The ratio of PT-Exp1's lumped to local threshold, from the same searches, accordingly falls from 2.90 at a Fourier number of 0.11 to 1.16 at 0.60 and 0.94 at 1.80.
   - 2.90 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/21.39 = 2.89706
   - 0.11: results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '21.38651984299561'} = 0.106949
   - 1.16 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/120 = 1.15999
   - 0.60 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '120.0'} = 0.600091
   - 0.94 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/360 = 0.938279
   - 1.80 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 1.80027
56. The lumped neighbour's reaction heat, with the separator molten, equals its losses at $T_\mathrm{ign}=218.5$\degC{} with the trigger at the neighbour's own temperature (230.4\degC{} with the trigger at 25\degC), and over the 200 kinetic draws $T_\mathrm{ign}$ runs from 215.3 to 221.4\degC{} (central 95\,\%), a span of 6.1~K.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
   - 230.4 (new): results/stage13_tign.csv: T_ign_C where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'ambient'} = 230.379
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 215.3 (new): results/stage13_paper_numbers.json: scorecard/P7/p2.5_C = 215.257
   - 221.4 (new): results/stage13_paper_numbers.json: scorecard/P7/p97.5_C = 221.395
   - 95: predictions_stage13.md: /the central (95) % of the 200 draws/ = 95
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
57. At that point, with every reactant at its initial amount, the low-temperature cathode reaction gives 73.3\,\% of the reaction heat under the posterior mean.
   - 73.3 (new): results/stage13_tign.csv: carrying_share where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 73.3174
58. The two-body model, which asks only whether the neighbour reaches $T_\mathrm{ign}$ with enough of that reaction's heat (2,667~J in all) left to carry it to 255.7\degC{} ( ), lies within the larger of 10\,\% and 300~J of the lumped threshold in all 32 searches at the low and high contacts registered for it, nine of them with both zero (Supplementary Table~S10); at the central contact it lies within that margin, unscored, in 29 of the 32 searches over 120 and 360~s.
   - 2,667 (new): results/stage13_tign.csv: cat1_heat_total_J where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 2667.2
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 10: predictions_stage13.md: /within the larger of (10) % and 300 J/ = 10
   - 300 (new): predictions_stage13.md: /within the larger of 10 % and (300) J/ = 300
   - 32: results/stage13_paper_numbers.json: scorecard.P8.n_within = 32
   - 29 (new): results/stage13_twobody.csv: central-contact searches over 120 and 360 s within the larger of 10 % and 300 J = 29
   - 32: results/stage13_twobody.csv: central-contact searches over 120 and 360 s = 32
   - 120: results/stage13_twobody.csv: tau_d_s of those searches = 120
   - 360: results/stage13_twobody.csv: tau_d_s of those searches = 360
59. If the threshold is the heat that brings the neighbour to $T_\mathrm{ign}$ less what the trigger conducts, it should fall as the trigger's body energy rises, and it does, by 393 to 456~J per kJ (PT-Exp3, ST-Exp2, PP-Exp3); the range registered beforehand, 150 to 300~J per kJ, failed, and the steeper fall is not explained here.
   - 393 (new): smallest and largest of results/stage13_paper_numbers.json: scorecard.P10.cases: slope_J_per_kJ = 393.034
   - 456 (new): smallest and largest of results/stage13_paper_numbers.json: scorecard.P10.cases: slope_J_per_kJ = 456.135
   - 150: predictions_stage13.md: /falls by (150) to 300 J per kJ/ = 150
   - 300 (new): predictions_stage13.md: /falls by 150 to (300) J per kJ/ = 300
60. With no delivery, in PT-Exp4, PP-Exp3 and ST-Exp2 at the central contact, by 250~s the lumped neighbour has taken in 2.1 to 2.3~kJ more than the resolved one through the same conductance, since the resolved cell's contact patch heats toward the trigger's temperature while its mean lags.
   - 250 (new): results/stage15_accounts.json: the accounts' rows at t_s 250 = 250
   - 2.1: smallest and largest of results/stage15_accounts.json: lumped_less_resolved.contact_and_wedge at 250 s = 2.05166
   - 2.3 (new): smallest and largest of results/stage15_accounts.json: lumped_less_resolved.contact_and_wedge at 250 s = 2.30888
61. With 5.04~kJ over 21.4~s, the upper end of an earlier bracket on the lumped threshold, 4.66 to 5.04~kJ (3.75 to 4.06\,\% of the test's ejected energy), with which the lumped neighbour runs away at 215.6~s under the posterior mean, the resolved neighbour runs away under none of four kinetic draws, those of rank 5, 50, 151 and 196 of 200 by their onset at the hot spot (its mean peaks at 191.2 to 192.4\degC), nor with an aged SEI (188.3\degC); the lumped neighbour runs away under the first two draws and not under the last two or the aged SEI, so under those its threshold too lies above 5.04~kJ.
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 3.75 (new): results/stage10_heldout.json: table, M50_PT_Exp4, f9_lo = 3.75
   - 4.06 (new): results/stage10_heldout.json: table, M50_PT_Exp4, f9_hi = 4.0625
   - 215.6 (new): results/stage15_readings.json: 1.PT_Exp4.lumped_cross_s = 215.6
   - 50: results/manuscript_numbers.json: constants.kin_ranks = 50
   - 151: results/manuscript_numbers.json: constants.kin_ranks = 151
   - 196: results/manuscript_numbers.json: constants.kin_ranks = 196
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 191.2 (new): smallest and largest of results/stage15_paper_numbers.json: B4.draws: peak_mean_C = 191.164
   - 192.4: smallest and largest of results/stage15_paper_numbers.json: B4.draws: peak_mean_C = 192.397
   - 188.3 (new): results/stage15_paper_numbers.json: B4.aged.peak_mean_C = 188.294
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
62. With every rate law evaluated at the local temperature plus a shift, so that each reaction runs as at a temperature that much higher, it needs a shift of more than 17.5~K to run away there: at 17.5~K its mean peaks at 221.1\degC, and at 20~K it runs away at 270.3~s, its far face's jump beginning at 240.4\degC.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 221.1 (new): results/stage15_paper_numbers.json: B4.shift_runs, the run shifted by 17.5 K: peak_mean_C = 221.105
   - 20: results/stage15_paper_numbers.json: B4.shift.least_shift_K = 20
   - 270.3 (new): results/stage15_paper_numbers.json: B4.shift.t_C8_s = 270.338
   - 240.4 (new): results/stage15_paper_numbers.json: B4.shift_runs, the run shifted by 20 K: far_jump.T_C = 240.351
63. Fig.~ d sets beside it the 6.1~K span of the posterior's ignition temperatures, a different measure, which a shift of the rate laws would move by about as much only to first order, an expectation not computed here; the span also leaves out the difference between the kinetic source's materials and this cell's (Section~ ).
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
64. (b) The lumped threshold of three tests with the trigger's fitted body energy (hollow) and shifted by 2~kJ either way (filled), with the fall per kJ.
   - 2: src/stage13_inputs.py: /for d in \(-2000\.0, (2000\.0)\)/ = 2
65. (c) The lumped neighbour's ignition temperature over the 200 kinetic draws.
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
66. (d) On one axis in kelvin, the span of those ignition temperatures (the posterior's kinetic uncertainty) beside the shift added to the temperature in every rate law of PT-Exp4's resolved neighbour, under 5.04~kJ over 21.4~s, the upper end of an earlier bracket on the lumped threshold, with which the lumped neighbour runs away: crosses, shifts with no resolved runaway (up to 17.5~K); circle, the first with one (20~K).}
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 20: results/stage15_paper_numbers.json: B4.shift.least_shift_K = 20
67. With the 21.4~s pulse the lumped neighbour runs away at the measured time with 0.26 to 5.96~kJ in seven propagated tests, and at its threshold in two (PT-Exp4, 4.66 to 4.85~kJ; ST-Exp3, 11.95 to 12.11~kJ); leaving out ST-Exp3's, after its weak trigger, the largest, 5.96~kJ in PP-Exp2, is about 23 times the smallest, 0.26~kJ in SP-Exp3.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 4.85: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_PT_Exp4'} = 4.851
   - 11.95: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_ST_Exp3'} = 11.95
   - 12.11: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_ST_Exp3'} = 12.1115
   - 5.96: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PP_Exp2'} = 5.9624
   - 23 (new): results/stage12_paper_numbers.json: part_c.ratio = 22.6
   - 0.26: results/stage15_table.csv: C2_E_by_t_J where {'test': 'M50_SP_Exp3', 'delivery': '21.39 s pulse'} = 0.2635
68. Of the five tests that did not propagate and report low maxima, four need none, since with no delivery the far face already peaks 13.8 to 56.3~K above their maxima at the central contact, and PT-Exp1 needs 2.09~kJ.
   - 13.8: smallest and largest of results/stage9_paper_numbers.json: part_a.A3: overshoot_K = 13.7556
   - 56.3: smallest and largest of results/stage9_paper_numbers.json: part_a.A3: overshoot_K = 56.3217
   - 2.09: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp1'} = 2.0907
69. With no delivery the model thus overheats those far faces against the record while it runs no neighbour away; at the low contact three of the four stay below their maxima (Supplementary Table~S2, step~11).
   - 11: manuscript/rebuild/data/predictions_registry.csv: the step of P4 on the far face with no delivery = 11
70. In the held-out test (Section~ ) none of the three quantities predicts the outcomes better than one probability for every test by the registered margin of 0.1 in the mean log score: the largest gain is 0.062, with permutation $p$-values of 0.23 to 0.75 (Supplementary Table~S9), and both thresholds fall as the trigger's fitted energy rises (Table~ and Supplementary Table~S3), so that much of what they carry may be the trigger's energy.
   - 0.1: predictions_stage10.md: /by more than (0\.1) in the mean log score/ = 0.1
   - 0.062: results/stage10_paper_numbers.json: part_c.largest_d_log = 0.0624263
   - 0.23: smallest and largest of results/stage10_paper_numbers.json: part_c.held_out: p_log = 0.226477
   - 0.75: smallest and largest of results/stage10_paper_numbers.json: part_c.held_out: p_log = 0.751725
71. After the eight strong triggers among the tests that propagated, the reactive cross-section needs 4.1 to 8.1~kJ, delivered by its runaway, for the resolved neighbour to run away within 10~s of the measured time under each of the four delivery shapes, where the lumped neighbour needs 0.2 to 6.0~kJ in the same thirty-two cases.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 8.11583
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 5.9624
72. In twenty-five of them a run reproduces the time within 10~s; in the other seven, shorter deliveries in PT-Exp4, PP-Exp4 and ST-Exp4, the time is reproduced only within the search's resolution of the threshold.
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
73. With the pulse the resolved need exceeds the lumped one in each of these eight tests, by 1.7 to 4.3~kJ, most in proportion in SP-Exp3, 4.58 against 0.26~kJ.
   - 1.7 (new): smallest and largest of results/stage15_table.csv: the pulse, C8_xs_E_by_t_J less C2_E_by_t_J outside ST_Exp3 = 1.68676
   - 4.3 (new): smallest and largest of results/stage15_table.csv: the pulse, C8_xs_E_by_t_J less C2_E_by_t_J outside ST_Exp3 = 4.32433
   - 4.58 (new): results/stage15_table.csv: C8_xs_E_by_t_J where {'test': 'M50_SP_Exp3', 'delivery': '21.39 s pulse'} = 4.58171
   - 0.26: results/stage15_table.csv: C2_E_by_t_J where {'test': 'M50_SP_Exp3', 'delivery': '21.39 s pulse'} = 0.2635
74. After ST-Exp3's weak trigger the resolved neighbour needs 10.3 to 13.8~kJ under three of the shapes, a run reproducing the measured 177~s only with the 240~s delivery, and no energy on the search's grid bringing its runaway with the 360~s delivery; the lumped neighbour needs 11.5 to 12.3~kJ under all four.
   - 10.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 10.3125
   - 13.8: smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 13.8435
   - 177: results/stage15_table.csv: t_measured_s where {'test': 'M50_ST_Exp3', 'delivery': '21.39 s pulse'} = 177
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_ST_Exp3'} = 240
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_ST_Exp3'} = 360
   - 11.5: smallest and largest of results/stage15_table.csv: ST_Exp3, C2_E_by_t_J = 11.4655
   - 12.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C2_E_by_t_J = 12.2592
75. PT-Exp4's thermocouple starts at 32.2\degC, against the model's 25\degC, reaches 141.0\degC{} by 45~s and 197.3\degC{} at 271.5~s, when the neighbour's jump begins.
   - 32.2 (new): inputs/fransson2024/pt_exp4_history.csv: T_neighbour_C where {'t_s': '0.0'} = 32.1676
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
   - 141.0: results/stage10_paper_numbers.json: measured.at_45_s_C = 140.997
   - 45: results/stage10_paper_numbers.json: /"at_(45)_s_C"/ = 45
   - 197.3: results/stage10_paper_numbers.json: measured.at_onset_C = 197.254
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
76. With 4.66 and 5.04~kJ over 21.4~s, the ends of the earlier bracket on the lumped threshold, the model's far face lies 16.3 and 16.8~K from the record, the root mean square over 0 to 271.5~s, the offset and the opening spike included, but the resolved neighbour does not run away: with 5.04~kJ its mean peaks at 190.6\degC{} and cools.
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 16.3: results/stage10_paper_numbers.json: part_a.tri21_C2_lo_hcentral.nodes.away.window.rms_K = 16.2554
   - 16.8: results/stage10_paper_numbers.json: part_a.tri21_C2_hi_hcentral.nodes.away.window.rms_K = 16.8348
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 190.6 (new): results/stage15_readings.json: 1.PT_Exp4.mean_peak_C = 190.6
77. At 7.42~kJ, the upper end of its own bracket, the resolved neighbour runs away at 181.9~s, and its far face's jump begins at 173~s and 234.1\degC, against the measured 271.5~s and 197.3\degC, 36.8~K higher, and 47.6~K above the record's own jump read by the same rule (Supplementary Section~S7); over 0 to 181.9~s its far face lies 51.4~K from the record.
   - 7.42 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 181.9 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
   - 173 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: far_jump.t_s = 173
   - 234.1 (new): results/stage15_paper_numbers.json: B3a.run.far_jump.T_C = 234.101
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
   - 197.3: results/stage10_paper_numbers.json: measured.at_onset_C = 197.254
   - 36.8 (new): results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
   - 47.6: results/stage15_paper_numbers.json: B1 PT_Exp4's upper run, far_jump.T_C, less the record's jump by the same rule (stage15_archive.far_face_jump on inputs/fransson2024/pt_exp4_history.csv from 24.16 s) = 47.563
   - 181.9 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
   - 51.4 (new): results/stage15_paper_numbers.json: B3a.history.rms_K = 51.4421
78. A search in steps of 2.5~W, from the reactive cross-section's 12.5~W, for the constant power that after a 5.04~kJ pulse brings the resolved runaway within 10~s of the measured 271.5~s ended between 10~W, with the runaway at 369.3~s, and 12.5~W, with it at 255.9~s and the far face's jump beginning at 233.6\degC.
   - 2.5: predictions_stage15.md: /then steps of (2\.5) W/ = 2.5
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.start_W = 12.5
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
   - 369.3 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold10.0W: t_C8_s = 369.329
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.result.P_hi_W = 12.5
   - 255.9 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: t_C8_s = 255.856
   - 233.6 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: far_jump.T_C = 233.595
79. Carried on to 900~s, a run made in an earlier step and stopped at 332~s, the measured time plus 60~s, with 6.2~kJ, 5\,\% of the test's ejected energy, at constant power over 240~s, does not run away, its mean peaking at 241.4\degC: the prediction registered for it, that it would run away, failed, and the reactive cross-section's value registered beside it, no runaway with the mean peaking at 220.5\degC, held (Supplementary Table~S2).
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 332 (new): results/stage15_readings.json: 1.PT_Exp4.t_end_s = 332
   - 60: src/stage10_run.py: /Table 3's 272 s plus (60) s/ = 60
   - 6.2 (new): results/stage15_paper_numbers.json: B2/0.05/E_J = 6.20922
   - 5: predictions_stage15.md: /at f = (0\.05) \(6,209 J/ = 5
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 241.4 (new): results/stage15_paper_numbers.json: B2/0.05/peak_mean_C = 241.354
   - 220.5 (new): predictions_stage15.md: /6,209 J no C8 \(mean peak (220\.5) C\)/ = 220.5
80. The thermocouple's angle is not reported; a post hoc reading of the 7.42~kJ run finds the far face the coolest of the model's five probes at mid-length when its jump begins (the two side probes read 235.5 and 235.8\degC), a reading from which nothing here is concluded.
   - 7.42 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 235.5 (new): results/stage15_independent_read.md: the two side probes' readings at the far face's jump = 235.5
   - 235.8 (new): results/stage15_independent_read.md: the two side probes' readings at the far face's jump = 235.79
81. (a) For the nine tests that propagated, in order of the measured time: the energy delivered to the facing half by the time at which the lumped neighbour (filled) or the resolved neighbour's mean (hollow, reactive cross-section) reaches 255.7\degC, within 10~s of the measured time, for the four delivery shapes; where the measured time is reproduced only within the search's resolution of the threshold, the least energy on the search's grid whose runaway comes before it is shown, which can lie above the threshold of Fig.~ by up to that resolution; in ST-Exp3 with the 360~s delivery no energy on the grid brings the resolved runaway.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_ST_Exp3'} = 360
82. (b) For the seven tests that did not propagate: the energy delivered over 21.4~s that puts the far face's peak at the measured maximum; hollow, the two maxima that may not be the neighbour's surface; at the bottom, tests whose far face exceeds the maximum with no delivery.}
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
83. (b) The resolved neighbour's mean temperature under the same deliveries: 5.0~kJ over 21.4~s, the upper end of the earlier bracket on the lumped threshold; 6.7 and 7.4~kJ over 21.4~s, the ends of the resolved bracket; the 5.0~kJ pulse followed by 12.5~W; and 6.2~kJ over 240~s.
   - 5.0: results/stage15_readings.json: 1.PT_Exp4.E_J = 5.045
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 6.7 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.lo_J = 6.70937
   - 7.4 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 5.0: results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.result.P_hi_W = 12.5
   - 6.2 (new): results/stage15_paper_numbers.json: B2/0.05/E_J = 6.20922
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
84. The resolved neighbour runs away where its mean reaches 255.7\degC.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
85. The run of 5.0~kJ over 21.4~s was carried to 332~s; that of 6.2~kJ over 240~s, made earlier and stopped at 332~s, was carried on to 900~s and does not run away.
   - 5.0: results/stage15_readings.json: 1.PT_Exp4.E_J = 5.045
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 332 (new): results/stage15_readings.json: 1.PT_Exp4.t_end_s = 332
   - 6.2 (new): results/stage15_paper_numbers.json: B2/0.05/E_J = 6.20922
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 332 (new): results/stage15_readings.json: 1.PT_Exp4.t_end_s = 332
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
86. A jump begins where the rate of rise over 2~s first reaches 1~K\,s$^{-1}$ after having reached 0.5~K\,s$^{-1}$ and fallen below it.
   - 2: src/stage15_inputs.py: /DIFF_S = (2\.0)/ = 2
   - 1: src/stage15_inputs.py: /RISE_JUMP = (1\.0)/ = 1
   - 0.5: src/stage15_inputs.py: /RISE_SLOW = (0\.5)/ = 0.5
87. The 4.66~kJ run of Section~ is not drawn.}
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
88. From published inputs alone, what the ejecta can release in this rig is at most 225.8~kJ, with the heat of burning their gas taken from another cell, and in total every path of the ejecta is bounded by that alone; the holder's conduction is not determinable, no source giving the inserts' material or contact, energy conservation alone capping it at 247.3~kJ, all that the trigger can release (Table~ , Fig.~ ).
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 247.3 (new): results/stage14_corrections.json: E_global_J = 247.333
89. Within 21.4~s, radiation can deliver at most 27.9~kJ, a black body at 1500\degC{} filling the facing half's view; a flame held on the vent's axis would send at most about 0.38\,\% of its radiation onto the facing half, about 0.85~kJ of the 225.8~kJ, but no source places the flame.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 0.38 (new): results/stage14_independent_read.md: /gives (0\.003759) \+- 0\.000022 at 0\.85 R/ = 0.3759
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
90. Gas beside the neighbour, a breach's jet facing it and solids and melt on it can deliver at most 195.5, 225.8 and 225.8~kJ, and the neighbour's own discharge in the parallel tests, from inside, 65.5~kJ.
   - 195.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A2', 'window_s': '21.39'} = 195.516
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 65.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A6', 'window_s': '21.39'} = 65.52
91. Within 21.4~s gas, a breach's jet and solids and melt each reach all twelve of the needs with the pulse in Section~ that are not zero; radiation reaches ten and misses only the two exploratory maxima (32.7 and 75.8~kJ); the discharge reaches five of the six parallel needs.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 32.7 (new): results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_SP_Exp4'} = 32.667
   - 75.8 (new): results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp2'} = 75.8149
92. Every delivery of Supplementary Table~S7 with which the resolved neighbour runs away carries 4.1 to 19.5~kJ in all over its shape, 5.3 to 25.4\,\% of the Databank's median ejected energy, and so less than 27.9~kJ, the least bound within 21.4~s of a path through the facing half, which the bounds over longer deliveries exceed.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_J, every delivery with which the cross-section runs away = 4.06435
   - 19.5 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_J, every delivery with which the cross-section runs away = 19.5167
   - 5.3 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 5.29617
   - 25.4 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 25.4319
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
93. \caption{What each path can deliver to the neighbour's facing half, from published inputs alone (upper bounds within the pulse's 21.4~s and in total; every lower bound is zero), against what the neighbour models need: the lumped neighbour's needs at the measured times with the pulse and the energy the resolved neighbour needs to run away at the measured times under the four shapes, both after strong triggers (after ST-Exp3's weak trigger they are 12.1 and 10.3 to 13.8~kJ, left out), and the energy calorimetry measured in this cell's ejecta.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 12.1 (new): results/stage15_table.csv: C2_E_by_t_J where {'test': 'M50_ST_Exp3', 'delivery': '21.39 s pulse'} = 12.111
   - 10.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 10.3125
   - 13.8: smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 13.8435
94. At the central contact, against the 151 three-dimensional runs of the sixteen tests made in earlier steps and carried past the hottest point's crossing, six of them repeating another's configuration in a different step, to 900~s or, in twelve, to 332~s (Supplementary Table~S11), the reactive cross-section gave the same outcome, the mean's runaway or none by the run's end, in all 151 (Fig.~ ).
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 332 (new): results/stage15_cross_section.json: A1_rows, the earliest end of a run = 332
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
95. In the 92 runs in which both run away, 82 of them in the two exploratory tests at deliveries of 15 to 135~kJ, far above any threshold, its runaway comes 1.0~s later on average (5.5~s earlier to 34.5~s later); in the 59 in which neither does, its mean peaks 1.9~K lower on average and at most 20.7~K lower, in PT-Exp4's run of 6.2~kJ over 240~s, against the 241.2\degC{} at which the three-dimensional run had been stopped at 332~s.
   - 92 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.n = 92
   - 82 (new): results/stage15_cross_section.json: A1_rows of PT_Exp2 and SP_Exp4 in which both run away = 82
   - 15: smallest and largest of results/stage15_cross_section.json: A1_rows of PT_Exp2 and SP_Exp4 in which both run away, E_J = 15.3727
   - 135 (new): smallest and largest of results/stage15_cross_section.json: A1_rows of PT_Exp2 and SP_Exp4 in which both run away, E_J = 134.782
   - 1.0: results/stage15_cross_section.json: A1_summary.dt_C8_s.mean = 1.03766
   - 5.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.min = 5.48377
   - 34.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.max = 34.5232
   - 59 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.n = 59
   - 1.9 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.mean = 1.87063
   - 20.7 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.min = 20.6721
   - 6.2 (new): results/stage15_paper_numbers.json: B2/0.05/E_J = 6.20922
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 241.2 (new): results/stage15_cross_section.json: A1_rows, the archived 6,209 J run over 240 s: mean_peak_3d_C = 241.179
   - 332 (new): results/stage15_cross_section.json: A1_rows, the archived 6,209 J run: t_end_s = 332
96. Its thresholds were registered as the centres of the three-dimensional searches (Section~ ); in SP-Exp3 the threshold lay above both opening runs, its value 9.1\,\% below the bracket's midpoint.
   - 9.1 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.rel_diff_xs = 9.09091
97. A run takes 17 to 71~s on one processor core, against 240 to 2,762~s for the three-dimensional runs of the same searches.
   - 17: smallest and largest of results/stage15_xs/*.json: wall_s = 16.9846
   - 71: smallest and largest of results/stage15_xs/*.json: wall_s = 71.3495
   - 240: smallest and largest of results/stage15_paper_numbers.json: runs.wall_s min and max = 239.781
   - 2,762 (new): smallest and largest of results/stage15_paper_numbers.json: runs.wall_s min and max = 2762.3
98. (a) The time the resolved neighbour's mean reaches 255.7\degC, in the runs where both models run away.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
99. (c) The thresholds of the four tests searched in three dimensions with the 21.4~s pulse.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
100. Read through a lumped neighbour, what each test that propagated needs varies about 23-fold with the pulse outside ST-Exp3, so a pack model that ignites a lumped neighbour at one delivered share would reproduce some tests and not others.
   - 23 (new): results/stage12_paper_numbers.json: part_c.ratio = 22.6
101. Read through a resolved neighbour, the needs at the measured times fall within 4.1 to 8.1~kJ after strong triggers, a narrower band, though one the tests cannot yet confirm, and lie at 10.3 to 13.8~kJ after the weak one.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 8.11583
   - 10.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 10.3125
   - 13.8: smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 13.8435
102. Either way the needed energies are at most about a quarter of what the ejecta carry: the lumped neighbour needs at most 12.3~kJ by its runaway, and the deliveries with which the resolved neighbour runs away carry 5.3 to 25.4\,\% of the Databank's median for this cell, 76.74~kJ~ .
   - 12.3 (new): results/stage15_table.csv: C2_E_by_t_J, the largest = 12.2592
   - 5.3 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 5.29617
   - 25.4 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 25.4319
   - 76.74: results/stage14_inputs.csv: value where {'key': 'db_Eej_median'} = 76.7412
103. Torres-Castro et al.'s estimate for pouch cells, 2.0~kJ absorbed on average by the next cell before it failed~ , lies inside the lumped range found here, though a different cell cannot choose between the readings of this one.
   - 2.0: manuscript/data/comparators.csv: value where {'key': 'torrescastro2020passive', 'quantity': 'energy the next cell absorbs before it fails, mean'} = 2
104. Since the resolved threshold is 1.49 and 1.72 times the lumped one in the two strong-trigger tests where both are bracketed and 0.85 times after the weak trigger, a heat share calibrated in this model with either neighbour cannot be carried to the other without a correction whose sign depends on the trigger; the reactive cross-section gives the resolved reading at a small part of the cost (Section~ ).
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
105. Under the lumped neighbour's energy the model's far face lies 16.3 to 16.8~K from PT-Exp4's record but the resolved cell does not run away; at the resolved cell's own runaway its far face's jump begins 37~K hotter than the measured thermocouple's, and earlier, at the probe where that comparison was registered.
   - 16.3: results/stage10_paper_numbers.json: part_a.tri21_C2_lo_hcentral.nodes.away.window.rms_K = 16.2554
   - 16.8: results/stage10_paper_numbers.json: part_a.tri21_C2_hi_hcentral.nodes.away.window.rms_K = 16.8348
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
106. Neither alternative run here closes that gap: with the 12.5~W hold or the 20~K shift the jump begins at 233.6 and 240.4\degC.
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.result.P_hi_W = 12.5
   - 20: results/stage15_paper_numbers.json: B4.shift.least_shift_K = 20
   - 233.6 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: far_jump.T_C = 233.595
   - 240.4 (new): results/stage15_paper_numbers.json: B4.shift_runs, the run shifted by 20 K: far_jump.T_C = 240.351
107. A heat flux measured at several points of the neighbour's facing side, away from the line of contact and through the venting, would give the heat delivered to that half, which the readings need in different amounts, in place of a need inferred through a model; it could decide if the model's other inputs stand (Section~ ) and if it gives the heat delivered to that half to well within the 1.7 to 4.3~kJ by which the two readings' needs differ with the pulse after strong triggers.
   - 1.7 (new): smallest and largest of results/stage15_table.csv: the pulse, C8_xs_E_by_t_J less C2_E_by_t_J outside ST_Exp3 = 1.68676
   - 4.3 (new): smallest and largest of results/stage15_table.csv: the pulse, C8_xs_E_by_t_J less C2_E_by_t_J outside ST_Exp3 = 4.32433
108. The flame's position and temperature beside the cells would bound radiation by geometry, from 27.9~kJ toward 0.85~kJ.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
109. One cell type, in one laboratory's rig, carries the comparison, and one published history of a neighbour that propagated, from a test whose trigger ruptured its sidewall; that history was read from a figure, and its opening 8.5~s, a spike to 102\degC, are taken as the thermocouple's exposure at the trigger's runaway.
   - 8.5: results/stage10_paper_numbers.json: measured.dip_after_spike_t_s = 8.5
   - 102: results/stage10_paper_numbers.json: measured.spike_on_the_samples_C = 101.711
110. In an earlier step's coarser searches under four kinetic draws and four thermal draws at the ends of the roll's published ranges (Supplementary Table~S2, step~11), ST-Exp2's lumped threshold, 2.70~kJ on that grid under the posterior mean, was at most 1.80~kJ under two kinetic draws and zero with the smallest specific heat, and PP-Exp3's ran from 0.85 to 4.26~kJ over the eight draws; every comparison of the two thresholds above is at the posterior mean and the central properties.
   - 11: manuscript/rebuild/data/predictions_registry.csv: the step of P4 on the far face with no delivery = 11
   - 2.70 (new): results/stage11_scorecard.json: P1, ST_Exp2's posterior-mean f*, times its ejected energy (results/stage8_ejected.csv) = 2.7049
   - 1.80 (new): results/stage11_thresholds.csv: hi of ST_Exp2's C2 brackets under draws 188 and 83, times its ejected energy = 1.80326
   - 0.85 (new): smallest and largest of results/stage11_thresholds.csv: E_star_J of PP_Exp3's C2 under the eight draws = 0.851923
   - 4.26 (new): smallest and largest of results/stage11_thresholds.csv: E_star_J of PP_Exp3's C2 under the eight draws = 4.25961

## main.tex: Conclusions

111. \item In the model, with the trigger's body energy held to the largest that calorimetry gives for this cell, conduction and radiation leave the neighbour's hottest point at least 29~K short of 255.7\degC{} at every contact conductance considered.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
112. \item With 21.4~s of delivered heat the resolved neighbour runs away as a whole at 1.49 and 1.72 times the lumped neighbour's threshold in the two tests with strong triggers where both are bracketed, at least 1.36 times across the brackets, and at 0.85 times, at most 0.90, in the one with a weak trigger.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
   - 0.90 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3 = 0.903373
113. \item In PT-Exp4, for the resolved neighbour to run away with the energy with which the lumped neighbour does under the posterior mean, every rate law would have to be shifted by more than 17.5~K, against a 6.1~K span of the posterior's ignition temperatures.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
114. \item At the central contact a reactive cross-section gave the outcome of the three-dimensional model in all 151 archived runs it was set against afterwards, most of them far from a threshold, at a small part of its cost.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
115. \item At the tests' measured times the reactive cross-section's resolved neighbour needs 4.1 to 8.1~kJ after strong triggers and the lumped neighbour 0.2 to 6.0~kJ; published inputs cannot bound at least four delivery paths below 27.9~kJ within 21.4~s, so the bounds exclude neither.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 5.9624
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## main.tex: appendices

116. The resolved neighbour's mesh is graded toward the line of contact, the roll is homogeneous and anisotropic, the can is a shell of steel with its own conductance and heat capacity, and the contact sector spans 45\textdegree{} either side of the line of contact, where room convection is removed.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
117. Time is stepped by backward Euler with a lumped capacity, the reaction integrated node by node in sub-steps that keep any node's reaction heating within 1~K a step, and room radiation is lagged one step.
   - 1: src/reactive.py: /DT_TARGET = (1\.0)/ = 1
118. Every run's energy account, the heat taken in through each boundary against the change in stored heat and the reaction heat released, closes to within $2\times10^{-11}$ of the heat taken in.
   - 2\times10^{-11}: results/stage8_paper_numbers.json: checks.V4.largest_relative.resolved = 1.9747e-11
119. For a bare semi-infinite solid under the triangular pulse, the surface's peak rise is $\Phi E''/(e\sqrt{\tau})$, with $E''$ the delivered energy per unit area, $\tau$ the pulse's duration and $e=(k_r\rho c)^{1/2}=1,743$~J\,m$^{-2}$\,K$^{-1}$\,s$^{-1/2}$ the roll's effusivity across its layers, $k_r$ its conductivity there and $\rho c$ the cell's heat capacity less the can's 4.5~J\,K$^{-1}$, over the cell's volume, which also gives $\alpha=k_r/\rho c$; the peak comes at two thirds of the pulse, and $\Phi=1.2284$ is [display] The skin model adds the can as a surface layer, its 4.5~J\,K$^{-1}$ over the cell's outer area, 841.7~J\,m$^{-2}$\,K$^{-1}$, and a linear surface loss, and is solved in closed form.
   - 1,743 (new): results/stage13_readings.json: reading_1.e_roll_as_resolved = 1742.5
   - 4.5 (new): manuscript/data/parameters.csv: /9; 500 \((4\.5) J/K\)/ = 4.5
   - 1.2284 (new): results/stage13_checks.json: V5.Phi00 = 1.22842
   - 4.5 (new): manuscript/data/parameters.csv: /9; 500 \((4\.5) J/K\)/ = 4.5
   - 841.7 (new): results/stage13_readings.json: reading_1.C_s_J_m2K = 841.736
120. The two-body model follows the lumped neighbour without reaction under the trigger's history and the delivery; once past $T_\mathrm{ign}$, with $Q$ its reaction heat there, the neighbour crosses if the heat of that cathode reaction still unreleased along its path covers $C(T_L-T)+CQ/(\mathrm{d}Q/\mathrm{d}T)$, the heat that carries it to $T_L=255.7$\degC{} and its loss over one induction time at the balance point; that reaction's whole heat, 2,667~J, is its posterior-mean enthalpy, 164.9~J per gram of cathode, times the cathode's 179.12~g in the source's 720~g reference cell, scaled to this cell's 65~g.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 2,667 (new): results/stage13_tign.csv: cat1_heat_total_J where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 2667.2
   - 164.9 (new): inputs: the posterior-mean kinetics (src/bcrnn.py): dH of cat1, J/g = 164.942
   - 179.12 (new): src/bcrnn.py: /M_IVV = (179\.12)/ = 179.12
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
   - 65: src/stage13_tign.py: /the reaction heat of the (65) g cell/ = 65
121. Both cross-section models are solved on 3,034 cells over the half section, graded toward the surface and the line of contact; their grid was not refined in a separate check, so the error of their values, quoted to the searches' resolution, is not known beyond their agreement with the three-dimensional model.
   - 3,034 (new): src/stage13_section.py: Section(): nr x nt = 3034
122. Every reduced number scored against a three-dimensional run made for that purpose was registered before the run; the reactive cross-section's agreement with the 151 archived runs was found after them.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151

## manuscript/rebuild/tables/t1_tests.tex: caption

123. \caption{The sixteen two-cell tests of LG M50 cells of Fransson et al.~ (their Tables 3 and 4), and the body energy $E_\mathrm{b}$ that puts the model's trigger at the measured trigger peak at the central contact when released over 21.39~s.
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
124. Category, Fransson et al.'s failure category: 1, the trigger's nail-penetration failure; 2, failure in the propagating cell; 4, sidewall rupture of the trigger (3, sidewall melting, is given for none of these tests); c.m., ``cell movement'' in the X-ray camera's field of view, given in place of a category; a dash, none given.
   - 1: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 1
   - 2: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 2
   - 4: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 4
   - 3: inputs/fransson2024/SOURCE.md: /; (3), \"Representation of sidewall melting/ = 3

## manuscript/rebuild/tables/t2_parameters.tex

125. >{\raggedright\arraybackslash} >{\raggedright\arraybackslash} } \toprule Quantity & Value & Source \\ \midrule {\textit{Geometry and cells}} \\ Cell diameter and length & 21.1 and 70.1 mm & \\ Can wall & 0.25 mm & \\ Can: conductivity; mass and specific heat & 15 W\,m$^{-1}$\,K$^{-1}$, a stainless steel's (no source gives the grade); 9 g, 500 J\,kg$^{-1}$\,K$^{-1}$ & assumed$^{a}$ \\ Roll conductivity across and along the layers & 1.3 and 25 W\,m$^{-1}$\,K$^{-1}$ & \\ Cell heat capacity & 61.75 J\,K$^{-1}$ (65 g at 950 J\,kg$^{-1}$\,K$^{-1}$) & ; mass assumed$^{a}$ \\ Resolved neighbour & half model, 19,355 nodes & this study \\ {\textit{Heat paths}} \\ Contact conductance between the cans, $h_c$ & 200, 2,000, 3,700 W\,m$^{-2}$\,K$^{-1}$ (low, central, high) & \\ Air in the wedge beside the contact & 0.03 W\,m$^{-1}$\,K$^{-1}$ & assumed$^{a}$ \\ Welded tabs: series one, parallel two & 6.8 mW\,K$^{-1}$ per tab (5 and 10 as brackets) & assumed$^{a}$ \\ View factor between the cans; emissivity & 0.1817; 0.8 & ; assumed$^{a}$, as in \\ Room convection; ambient and start & 10 W\,m$^{-2}$\,K$^{-1}$; 25\textdegree C & assumed$^{a}$ \\ {\textit{Trigger}} \\ Model and release & one temperature; triangular over 21.39 s & \\ Body energy $E_\mathrm{b}$ & 9.0 to 54.3 kJ, one per test (Table 1); 33.2 kJ held to calorimetry & \\ {\textit{Kinetics}} \\ Model & Bayesian chemical reaction neural network: posterior mean, and 200 joint draws & \\ Reactant masses; initial SEI amount & per 720 g reference cell; 0.15 of the source's normalised amount (fresh), 0 (aged) & \\ Runaway level; window & 255.7\textdegree C; within 900 s & ; this study \\ {\textit{Delivered heat}} \\ Region & the half of the neighbour's can facing the trigger, a uniform flux & this study \\ Shapes & triangular over 21.39 s; constant power over 120, 240 or 360 s; in PT-Exp4 also the pulse followed by a constant power; for Section~ , triangular over 5 to 360 s & this study \\ \bottomrule
   - 21.1: results/manuscript_numbers.json: constants.cell_diameter_mm = 21.1
   - 70.1: results/manuscript_numbers.json: constants.cell_length_mm = 70.1
   - 0.25: results/manuscript_numbers.json: constants.can_thickness_mm = 0.25
   - 15: results/manuscript_numbers.json: constants.can_conductivity_W_mK = 15
   - 9: manuscript/data/parameters.csv: /m_can; c_can,(9); 500/ = 9
   - 500: manuscript/data/parameters.csv: /m_can; c_can,9; (500)/ = 500
   - 1.3: results/manuscript_numbers.json: constants.k_radial_W_mK = 1.3
   - 25: results/manuscript_numbers.json: constants.k_axial_W_mK = 25
   - 61.75: results/manuscript_numbers.json: constants.C_cell_J_K = 61.75
   - 65: results/manuscript_numbers.json: constants.m_cell_kg = 65
   - 950: results/manuscript_numbers.json: constants.cp_cell_J_kgK = 950
   - 19,355: results/stage8_paper_numbers.json: v3.base.n_nodes = 19355
   - 200: results/manuscript_numbers.json: constants.h_contact_W_m2K.low = 200
   - 2,000: results/manuscript_numbers.json: constants.h_contact_W_m2K.central = 2000
   - 3,700: results/manuscript_numbers.json: constants.h_contact_W_m2K.high = 3700
   - 0.03: results/manuscript_numbers.json: constants.k_air_W_mK = 0.03
   - 6.8: results/manuscript_numbers.json: constants.g_tab_mW_K.central = 6.8
   - 5: results/manuscript_numbers.json: constants.g_tab_mW_K.low = 5
   - 10: results/manuscript_numbers.json: constants.g_tab_mW_K.high = 10
   - 0.1817: results/manuscript_numbers.json: constants.view_factor_cans_in_contact = 0.18169
   - 0.8: results/manuscript_numbers.json: constants.emissivity = 0.8
   - 10: results/manuscript_numbers.json: constants.h_conv_W_m2K = 10
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
   - 0.15: results/manuscript_numbers.json: constants.sei_initial_amount = 0.15
   - 0: src/stage15_inputs.py: /SEI_AGED = (0\.0)/ = 0
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 120: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 120
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 360
   - 5: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 5
   - 360: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 360

## manuscript/rebuild/tables/t3_bounds.tex

126. \centering \footnotesize \caption{What each path can deliver to the neighbour's facing half, from published inputs alone (Supplementary Table~S5): the upper bound within the pulse's 21.4~s and in total (every lower bound is zero), what sets it, and the measurement that would bound it more tightly.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
127. The ejecta can release at most 225.8~kJ in the rig: the most calorimetry measured for this cell's ejecta, 89.34~kJ~ , with the heat of burning the vent gas in open air, at most 136.5~kJ on another 21700 cell~ ; gas and flame are taken at up to 1500\textdegree C~ , the vent gas at up to 398.5~m\,s$^{-1}$~ .
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 89.34 (new): results/stage14_inputs.csv: value where {'key': 'db_Eej_max'} = 89.3378
   - 136.5 (new): results/stage14_inputs.csv: value where {'key': 'vendra_Qt_max'} = 136.5
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 398.5 (new): results/stage14_inputs.csv: value where {'key': 'u_vent_max'} = 398.5
128. rr>{\raggedright\arraybackslash} >{\raggedright\arraybackslash} } \toprule Path & {21.4 s} & {Total} & What sets the bound & Measurement that would bound it \\ & (kJ) & (kJ) & & \\ \midrule Radiation from a vent's jet or flame & 27.9 & 225.8 & a black body at 1500\textdegree C filling the facing half's view (the holder may reflect); a flame held on the vent's axis, about 0.85~kJ & the flame's position and temperature beside the cells \\ Gas beside the neighbour, burning or not & 195.5 & 225.8 & convection by Churchill and Bernstein's relation~ at 398.5~m\,s$^{-1}$~ , at the film temperature of gas at 1500\textdegree C over a can at 25\textdegree C, with hydrogen's properties at 1000~K~ , at most twice the whole-cylinder mean on one half; radiation at 1500\textdegree C & the gas's temperature and velocity in the wedges beside the line of contact \\ A breach's jet facing the neighbour & 225.8 & 225.8 & what the ejecta can release; a narrow jet strikes only from within 30\textdegree{} of the line of centres, a sixth of the circumference & where breaches face and what they carry \\ Solids and melt on or against the facing half & 225.8 & 225.8 & what the ejecta can release; melt falls onto it from a breach on the trigger's lower half, half of the circumference & the debris left on the neighbour \\ Conduction through the cell holder & -- & -- & not determinable: the inserts' material and contact are not given; energy conservation alone caps it at 247.3~kJ, all the trigger can release, the most measured for this cell in all (110.8~kJ~ ) with the vent gas burning & the holder's inserts and their contact \\ The neighbour's own discharge (parallel tests; for comparison) & 65.5 & 65.5 & heats from inside: the stored energy, 18.2~Wh, in every window; beside it, a short across 24~m$\Omega$~ at 4.189~V and 25\textdegree C, 731~W or 15.6~kJ within 21.4~s & the current between parallel cells \\ \bottomrule
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
   - 195.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A2', 'window_s': '21.39'} = 195.516
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 398.5 (new): results/stage14_inputs.csv: value where {'key': 'u_vent_max'} = 398.5
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
   - 1000 (new): results/stage14_inputs.csv: /Table A\.6, 50 to (1000) K/ = 1000
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 30: results/stage14_corrections.json: A3.narrow_jet_strikes_for_phi_below_deg = 30
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 247.3 (new): results/stage14_corrections.json: E_global_J = 247.333
   - 110.8 (new): results/stage14_inputs.csv: value where {'key': 'db_Etotal_max'} = 110.833
   - 65.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A6', 'window_s': '21.39'} = 65.52
   - 65.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A6', 'window_s': '21.39'} = 65.52
   - 18.2 (new): results/stage14_inputs.csv: /Cell-Energy-Wh \((18\.2)\)/ = 18.2
   - 24 (new): results/stage14_bounds.json: inputs.R_dc_min_ohm = 24
   - 4.189 (new): results/stage14_bounds.json: inputs.V_oc_V = 4.189
   - 25: results/stage14_inputs.csv: /0\.5 C for 30 s, (25) C/ = 25
   - 731 (new): results/stage14_bounds.json: A6.rate_25C_W = 731.155
   - 15.6 (new): results/stage14_bounds.json: A6/conditional_25C_J/21.39 = 15.6394
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## manuscript/rebuild/highlights.txt

129. Capped at calorimetry, modelled conduction and radiation fall at least 29 K short In two strong-trigger tests the resolved threshold is 1.5 and 1.7 times the lumped To 120 s, conduction sets the hot spot; a lumped cell ignites at 218.5 to 230.4 °C Afterwards, a reactive cross-section matched all 151 archived central-contact runs The tests cannot decide; a facing-side heat flux could, if the other inputs stand
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
   - 230.4 (new): results/stage13_tign.csv: T_ign_C where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'ambient'} = 230.379
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151

## manuscript/rebuild/ga_text.txt

130. failing cell neighbour heat delivered to the facing half with calorimetry's energy, conduction and radiation alone leave the neighbour at least 29 K short of runaway 4.75 | PT-Exp4, the lumped neighbour's threshold, kJ 7.06 | PT-Exp4, the resolved neighbour's threshold, kJ 1.5 times | PT-Exp4, the resolved threshold over the lumped one 3.97 | PP-Exp2, the lumped neighbour's threshold, kJ 6.85 | PP-Exp2, the resolved neighbour's threshold, kJ 1.7 times | PP-Exp2, the resolved threshold over the lumped one PT-Exp4 PP-Exp2 heat in 21.4 s for runaway (kJ) lumped neighbour resolved neighbour In the one published record of a propagating neighbour, the final rise starts 37 K cooler than on the resolved neighbour's far side.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 4.75 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.E_C2_J = 4.754
   - 7.06 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.mid_J = 7.0625
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 3.97 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.E_C2_J = 3.97496
   - 6.85 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.mid_J = 6.85417
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
131. No path through the facing half is bounded below 27.9 kJ within 21.4 s by published inputs.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## manuscript/rebuild/letters/Cover_letter_Fire_Safety_J.txt

132. With each test's trigger fitted to its measured peak, the resolved neighbour's threshold is 1.5 and 1.7 times the lumped neighbour's in the two tests with strong triggers (fitted body energies of 31.6 to 54.3 kJ) where both are bracketed, and 0.85 times in the one with a weak trigger.
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
133. Reduced models point to the mechanisms: up to 120 s, conduction sets the resolved cell's hot spot, and the lumped cell's runaway is consistent with an energy balance to an ignition temperature of 218.5 to 230.4 °C.
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
   - 230.4 (new): results/stage13_tign.csv: T_ign_C where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'ambient'} = 230.379
134. In one test the resolved neighbour runs away with the lumped neighbour's energy only if every reaction runs as if over 17.5 K hotter; the kinetics' published uncertainty spans 6.1 K of ignition temperature and omits the difference between their materials and the M50's.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
135. At the central contact a two-dimensional reactive cross-section, set afterwards against all 151 archived three-dimensional runs, most far from a threshold, reproduced every outcome at a fraction of their cost.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
136. In the model, with the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short of runaway.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
137. No published input bounds a path through the neighbour's facing half below 27.9 kJ within 21.4 s, more than either treatment needs, so the sixteen tests cannot decide between them.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
138. The one published record of a propagating neighbour fits neither cleanly, its final rise starting 37 K cooler than on the resolved model's far side; a heat flux measured on its facing side, with the thermocouple's angle, could decide, if the model's other inputs stand.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
139. The code, inputs and run records are archived openly, with the study's 98 predictions, each committed before its runs.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98

## manuscript/rebuild/letters/Cover_letter_J_Energy_Storage.txt

140. With each test's trigger fitted to its measured peak, the resolved neighbour's threshold is 1.5 and 1.7 times the lumped neighbour's in the two tests with strong triggers (fitted body energies of 31.6 to 54.3 kJ) where both are bracketed, and 0.85 times in the one with a weak trigger.
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
141. Reduced models point to the mechanisms: up to 120 s, conduction sets the resolved cell's hot spot, and the lumped cell's runaway is consistent with an energy balance to an ignition temperature of 218.5 to 230.4 °C.
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
   - 230.4 (new): results/stage13_tign.csv: T_ign_C where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'ambient'} = 230.379
142. In one test the resolved neighbour runs away with the lumped neighbour's energy only if every reaction runs as if over 17.5 K hotter; the kinetics' published uncertainty spans 6.1 K of ignition temperature and omits the difference between their materials and the M50's.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
143. At the central contact a two-dimensional reactive cross-section, set afterwards against all 151 archived three-dimensional runs, most far from a threshold, reproduced every outcome at a fraction of their cost.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
144. In the model, with the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short of runaway.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
145. No published input bounds a path through the neighbour's facing half below 27.9 kJ within 21.4 s, more than either treatment needs, so the sixteen tests cannot decide between them.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
146. The one published record of a propagating neighbour fits neither cleanly, its final rise starting 37 K cooler than on the resolved model's far side; a heat flux measured on its facing side, with the thermocouple's angle, could decide, if the model's other inputs stand.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
147. The code, inputs and run records are archived openly, with the study's 98 predictions, each committed before its runs.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98

## manuscript/rebuild/letters/Cover_letter_J_Power_Sources.txt

148. With each test's trigger fitted to its measured peak, the resolved neighbour's threshold is 1.5 and 1.7 times the lumped neighbour's in the two tests with strong triggers (fitted body energies of 31.6 to 54.3 kJ) where both are bracketed, and 0.85 times in the one with a weak trigger.
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
149. Reduced models point to the mechanisms: up to 120 s, conduction sets the resolved cell's hot spot, and the lumped cell's runaway is consistent with an energy balance to an ignition temperature of 218.5 to 230.4 °C.
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
   - 230.4 (new): results/stage13_tign.csv: T_ign_C where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'ambient'} = 230.379
150. In one test the resolved neighbour runs away with the lumped neighbour's energy only if every reaction runs as if over 17.5 K hotter; the kinetics' published uncertainty spans 6.1 K of ignition temperature and omits the difference between their materials and the M50's.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
151. At the central contact a two-dimensional reactive cross-section, set afterwards against all 151 archived three-dimensional runs, most far from a threshold, reproduced every outcome at a fraction of their cost.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
152. In the model, with the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short of runaway.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
153. No published input bounds a path through the neighbour's facing half below 27.9 kJ within 21.4 s, more than either treatment needs, so the sixteen tests cannot decide between them.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
154. The one published record of a propagating neighbour fits neither cleanly, its final rise starting 37 K cooler than on the resolved model's far side; a heat flux measured on its facing side, with the thermocouple's angle, could decide, if the model's other inputs stand.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
155. The code, inputs and run records are archived openly, with the study's 98 predictions, each committed before its runs.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98

## manuscript/rebuild/letters/Enquiry_Fire_Safety_J.txt

156. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
157. Fitted instead to each test's trigger peak, that energy gives resolved thresholds 1.5 and 1.7 times the lumped ones in two strong-trigger tests and 0.85 times after a weak trigger.
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
158. In one test the resolved neighbour needs every reaction run as if over 17.5 K hotter to run away with the lumped one's energy; kinetic uncertainty spans 6.1 K of ignition temperature.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
159. At the central contact a two-dimensional reactive cross-section afterwards reproduced all 151 archived three-dimensional outcomes, most far from a threshold.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
160. The one published record of a propagating neighbour fits neither: its final rise starts 37 K cooler than on the resolved model's far side.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008

## manuscript/rebuild/letters/Enquiry_J_Energy_Storage.txt

161. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
162. Fitted instead to each test's trigger peak, that energy gives resolved thresholds 1.5 and 1.7 times the lumped ones in two strong-trigger tests and 0.85 times after a weak trigger.
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
163. In one test the resolved neighbour needs every reaction run as if over 17.5 K hotter to run away with the lumped one's energy; kinetic uncertainty spans 6.1 K of ignition temperature.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
164. At the central contact a two-dimensional reactive cross-section afterwards reproduced all 151 archived three-dimensional outcomes, most far from a threshold.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
165. The one published record of a propagating neighbour fits neither: its final rise starts 37 K cooler than on the resolved model's far side.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008

## manuscript/rebuild/letters/Enquiry_J_Power_Sources.txt

166. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
167. Fitted instead to each test's trigger peak, that energy gives resolved thresholds 1.5 and 1.7 times the lumped ones in two strong-trigger tests and 0.85 times after a weak trigger.
   - 1.5: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.7 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
168. In one test the resolved neighbour needs every reaction run as if over 17.5 K hotter to run away with the lumped one's energy; kinetic uncertainty spans 6.1 K of ignition temperature.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
169. At the central contact a two-dimensional reactive cross-section afterwards reproduced all 151 archived three-dimensional outcomes, most far from a threshold.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
170. The one published record of a propagating neighbour fits neither: its final rise starts 37 K cooler than on the resolved model's far side.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
