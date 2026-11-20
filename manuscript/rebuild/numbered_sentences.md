# Every numbered sentence of the rebuilt manuscript, with its sources (20 November 2026)

Written by `src/make_rebuild_sentences.py` from the numbers check's trace (`numbers_trace.json`). Each sentence is followed by its numbers, the file and value each is read from, and "new" where the manuscript as submitted on 17 November 2026 does not state that number. Sentences are as the check reads them, with LaTeX spacing marks (~ is a space).
163 numbered sentences; 100 of them carry a number the submitted manuscript does not state (237 numbers in all).



## main.tex: abstract

1. Two touching LG M50 cells were modelled with published kinetics, the neighbour as one temperature and as a resolved field, against sixteen tests; 42 of 98 pre-registered predictions failed.
   - 42: manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed = 42
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98
2. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29~K below 255.7\degC.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
3. About 7~kJ delivered over 21.4~s makes the resolved neighbour run away, 1.49 and 1.72 times the lumped neighbour's need in two tests.
   - 7: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.mid_J = 7.0625
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
4. The local threshold is skin conduction, within 3\,\% of a conduction model.
   - 3: src/stage13_inputs.py: /FIRST_STEP = (0\.03)/ = 3
5. The lumped threshold is an energy balance to an ignition temperature of 218.5\degC.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
6. Matching the whole-cell thresholds needs the rate laws shifted over 17.5~K, against a 6.1~K posterior span.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
7. At the measured times the resolved neighbour needs 4.1 to 8.1~kJ, the lumped one 0.2 to 6.0~kJ.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 5.9624
8. In the one published history, the resolved neighbour's far face exceeds the measured surface by 37~K as runaway begins.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
9. Published inputs bound every delivery path at 27.9~kJ or more, above every need.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564

## main.tex: Introduction to Discussion, with figure captions

10. Calorimetry shows why the vent matters: fractional thermal runaway calorimetry of 18650 cells finds that typically 20 to 30\,\% of the total energy leaves through the casing and the rest with the ejecta~ , the Battery Failure Databank holds such measurements for many cells, the LG M50 among them~ , and burning vent gas can add to them in open air~ .
   - 20: manuscript/data/comparators.csv: value where {'key': 'walker2019decoupling', 'quantity': 'share of the total energy released through the casing, low'} = 20
   - 30: manuscript/data/comparators.csv: value where {'key': 'walker2019decoupling', 'quantity': 'share of the total energy released through the casing, high'} = 30
11. Nine propagated, 147 to 342~s after the trigger's runaway.
   - 147: smallest and largest of inputs/fransson2024/m50_tests.csv: time_to_propagation_s = 147
   - 342: smallest and largest of inputs/fransson2024/m50_tests.csv: time_to_propagation_s = 342
12. The neighbours of five of the seven tests that did not propagate peaked at 71 to 133\degC; the other two report 626 and 808\degC, which may not be the neighbour's surface, and are treated as exploratory.
   - 71: smallest and largest of inputs/fransson2024/m50_tests.csv: neighbour_max_C of the tests that did not propagate, without the two exploratory maxima = 71
   - 133: smallest and largest of inputs/fransson2024/m50_tests.csv: neighbour_max_C of the tests that did not propagate, without the two exploratory maxima = 133
   - 626: inputs/fransson2024/m50_tests.csv: neighbour_max_C where {'propagated': 'No'} = 626
   - 808: inputs/fransson2024/m50_tests.csv: neighbour_max_C where {'propagated': 'No'} = 808
13. One history of a neighbour before propagation is published, PT-Exp4's, in the paper's supplementary Figure~10; it was read out of the figure's vector paths twice, by separate code, to 2.47~K and 0.45~s.
   - 2.47: results/stage10_paper_numbers.json: measured.uncertainty_K = 2.47241
   - 0.45: results/stage10_paper_numbers.json: measured.uncertainty_s = 0.454675
14. The failing cell, the trigger, is one temperature that releases its body energy $E_\mathrm{b}$ inside itself as a triangular pulse over 21.39~s, the mean rise time of the two trigger records that the supplement draws.
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
15. Each test has its own trigger: the $E_\mathrm{b}$ that puts the model's trigger at the test's measured trigger peak at the central contact (below), 9.0 to 54.3~kJ (Table~ ).
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
16. In thirteen of the sixteen tests it exceeds 33.2~kJ, the largest body energy the Battery Failure Databank measured in the ten nail tests of this cell~ , probably because the trigger's flame heats the thermocouple the energy is matched to; the same tests are therefore also run with the body energy held to 33.2~kJ.
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
17. The Databank's median energy carried by this cell's ejecta is 76.74~kJ and its largest 89.34~kJ.
   - 76.74: results/stage14_inputs.csv: value where {'key': 'db_Eej_median'} = 76.7412
   - 89.34 (new): results/stage14_inputs.csv: value where {'key': 'db_Eej_max'} = 89.3378
18. The lumped neighbour is one temperature $T$: [display] where $T_1$ is the trigger's temperature, $C=61.75$~J\,K$^{-1}$ the cell's heat capacity and $m$ its mass, $G_c$ the conductance of the contact and its air wedge integrated over the can, $G_t$ that of the welded tabs, $F$ the view factor between the cans and $A_\ell$ the lateral area, $h_a$, $A_a$ and $A_r$ the room's convection coefficient and the areas that convect and radiate to the room at $T_a=25$\degC, $\dot q_r$ the reaction heat per unit mass (Section~ ) and $P(t)$ the delivered heat (Section~ ).
   - 61.75: results/manuscript_numbers.json: constants.C_cell_J_K = 61.75
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
19. The resolved neighbour is a three-dimensional half model, symmetric about the plane through both axes, of linear tetrahedral finite elements on 19,355 nodes: an anisotropic roll inside a 0.25~mm steel can, [display] with the conductivity $\mathbf{k}$ 1.3~W\,m$^{-1}$\,K$^{-1}$ across the layers and 25~W\,m$^{-1}$\,K$^{-1}$ along them and the same total heat capacity.
   - 19,355: results/stage8_paper_numbers.json: v3.base.n_nodes = 19355
   - 0.25: results/manuscript_numbers.json: constants.can_thickness_mm = 0.25
   - 1.3: results/manuscript_numbers.json: constants.k_radial_W_mK = 1.3
   - 25: results/manuscript_numbers.json: constants.k_axial_W_mK = 25
20. On the can, within 45\textdegree{} of the line of contact the heat flux to the trigger is $h(\theta)(T-T_1)$ with [display] a steel-on-steel contact conductance $h_c$ in series with the air in the wedge of width $\delta$ at angle $\theta$ from the line of contact; $h_c$ is 200, 2,000 or 3,700~W\,m$^{-2}$\,K$^{-1}$ for the low, central and high contact, the range of a textbook's table~ , since no conductance between cylindrical cells in contact was found.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
   - 200: results/manuscript_numbers.json: constants.h_contact_W_m2K.low = 200
   - 2,000: results/manuscript_numbers.json: constants.h_contact_W_m2K.central = 2000
   - 3,700: results/manuscript_numbers.json: constants.h_contact_W_m2K.high = 3700
21. Beyond 45\textdegree{} the can loses heat to the room by convection; everywhere it radiates to the room and receives the trigger's radiation shared over $\theta$ by the local view factor.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
22. Time is stepped by backward Euler with a lumped capacity, the reaction integrated node by node in sub-steps that keep any node's reaction heating within 1~K a step. gives the remaining approximations.
   - 1: src/reactive.py: /DT_TARGET = (1\.0)/ = 1
23. Three criteria read the neighbour's runaway, each at 255.7\degC, the lower edge of the internal-short band of the kinetic source~ , within 900~s of the trigger's release (Fig.~ b).
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
24. (a) The pair at mid-length: the trigger is one temperature; the neighbour is solved as one temperature and as a resolved half model, symmetric about the dash-dotted plane; heat is delivered through the half of its can that faces the trigger; within 45\textdegree{} of the line of contact the cans exchange heat through the contact and its air wedge.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
25. (b) One run, PT-Exp4 with 7.4~kJ delivered over 21.4~s: the resolved neighbour's hottest point reaches 255.7\degC{} at 8~s, the lumped neighbour at 107~s and the resolved neighbour's mean at 182~s.}
   - 7.4 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: E_J = 7.41562
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 8: results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: C1_t_s = 8.27672
   - 107: results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: lumped_C2_t_s = 106.51
   - 182 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
26. Reaction $j$ runs at $r_j=\exp\!\big(\sum_s n_{sj}\ln c_s+\ln A_j+b_j\ln T-E_{a,j}/(RT)\big)$, its species change as $\mathrm{d}c_s/\mathrm{d}t=\sum_j\nu_{sj}r_j$, and its heat enters per unit cell mass as $\dot q_r=\sum_j\Delta H_j r_j m_j/M_\mathrm{ref}$, with $m_j$ the reactant masses of the source's 720~g reference cell.
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
27. The posterior enters as 200 joint draws, each one particle of each submodel's file, which treats the three submodels as independent.
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
28. Its shape in time is a triangular pulse over 21.39~s from the start of the trigger's release, a constant power over 120, 240 or 360~s, or, in one test, a pulse followed by a constant power.
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 120: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 120
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 360
29. For a test that propagated, its need is the delivered energy at which a criterion is met at the measured time (within 10~s, or at the threshold where the measured time lies within the search's resolution of it); for a test that did not, the energy at which the far face peaks at the measured maximum (within 5~K).
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
   - 5: predictions_stage9.md: /within (5) K of it/ = 5
30. The two-body model runs the trigger and the lumped neighbour without reaction and asks when the neighbour reaches $T_\mathrm{ign}$ with enough heat of the low-temperature cathode reaction left to reach 255.7\degC.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
31. For each path by which the trigger's ejecta or its circuit can heat the facing half, a lower and an upper bound were set on the energy delivered within the pulse's 21.4~s and in total, from published inputs alone, each read at its source and labelled as measured on this cell or on another (Table~ ; the inputs in Supplementary Table~S5).
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
32. Of 98 predictions, 56 held and 42 failed; every one, its expectation and its verdict are in Supplementary Table~S2.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98
   - 56 (new): manuscript/rebuild/data/predictions_registry.csv: rows with verdict held = 56
   - 42: manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed = 42
33. The energy account of every run closes to within $2\times10^{-11}$ of the heat taken in.
   - 2\times10^{-11}: results/stage8_paper_numbers.json: checks.V4.largest_relative.resolved = 1.9747e-11
34. Halving the mesh spacing and every step limit moved the hottest point's peak rise by at most 0.52\,\% and the resolved neighbour's runaway time near its threshold by 1.5\,\%.
   - 0.52: results/stage8_paper_numbers.json: checks.V3.v3mesh.relative_change = 0.515385
   - 1.5: results/stage15_checks.json: V4/s15_B1_PT_Exp4_s+1_r1.5/rel_change = 1.48397
35. With body energies up to 33.2~kJ and the cans in contact, conduction and radiation take neither neighbour to 255.7\degC{} within 900~s in any of 5,248 runs across the contact, tab, release and connection brackets and the 200 kinetic draws: the hottest point peaks at most at 226.7\degC{} and the lumped neighbour at 180.6\degC.
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 5,248: results/v12_numbers.json: runs.all = 5248
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 226.7: results/v12_numbers.json: all_runs.res_peak_hottest_C.max = 226.67
   - 180.6: results/v12_numbers.json: all_runs.lum_peak_C.max = 180.633
36. With each test's own fitted trigger, conduction carries the hottest point over 255.7\degC{} in the eight tests with the largest fitted triggers (46.5 to 54.3~kJ), within 21.7~s, and the lumped neighbour in two.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 46.5: smallest and largest of results/stage12_capped.csv: E_b_fitted_J = 46.4567
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 21.7: results/stage12_paper_numbers.json: part_a.central.fitted_C1_at_f0_s[1] = 21.7
37. Held to 33.2~kJ, those eight tests ignite neither neighbour: the hottest point peaks at 191.9 to 192.2\degC{} at the central contact and at 226.4 to 226.7\degC{} at the high contact, 63.5 to 63.8~K and 29.0 to 29.3~K short of 255.7\degC, and the lumped neighbour at 159.8 to 161.8 and 175.9 to 177.4\degC.
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
   - 159.8: results/stage12_paper_numbers.json: part_a.central.lumped_peak_C[0] = 159.76
   - 161.8: results/stage12_paper_numbers.json: part_a.central.lumped_peak_C[1] = 161.75
   - 175.9: results/stage12_paper_numbers.json: part_a.high.lumped_peak_C[0] = 175.92
   - 177.4: results/stage12_paper_numbers.json: part_a.high.lumped_peak_C[1] = 177.4
38. With the 21.4~s pulse the three criteria need different energies in every test (Fig.~ ).
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
39. The local threshold is zero in the eight tests whose fitted trigger alone carries the hottest point over 255.7\degC, and at most 4.53~kJ (PT-Exp1).
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 4.53 (new): results/stage14_needs.csv: threshold_C1_hi_J where {'test': 'M50_PT_Exp1'} = 4.5298
40. The lumped threshold is zero in two tests and at most 12.89~kJ (PT-Exp1).
   - 12.89 (new): results/stage14_needs.csv: threshold_C2_hi_J where {'test': 'M50_PT_Exp1'} = 12.8924
41. By the reactive cross-section, the resolved neighbour needs 3.5 to 10.8~kJ in all sixteen: more than the lumped threshold in the fourteen tests whose trigger is strong (body energy 31.6 to 54.3~kJ), including 4.5 and 3.5~kJ in the two where the lumped neighbour needs none, and less in the two with weak triggers.
   - 3.5: smallest and largest of results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J = 3.52778
   - 10.8 (new): smallest and largest of results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J = 10.7812
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 4.5 (new): results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J of the two tests whose lumped neighbour needs no delivery = 4.54167
   - 3.5: results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J of the two tests whose lumped neighbour needs no delivery = 3.52778
42. The resolved neighbour runs away above 7.06~kJ in PT-Exp4 (bracket 6.71 to 7.42~kJ) and 6.85~kJ in PP-Exp2 (6.51 to 7.20~kJ), 1.49 and 1.72 times the lumped thresholds of 4.75 and 3.97~kJ, and above 3.88~kJ in SP-Exp3 (3.70 to 4.06~kJ), whose lumped neighbour runs away with no delivery.
   - 7.06 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.mid_J = 7.0625
   - 6.71 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.lo_J = 6.70937
   - 7.42 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 6.85 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.mid_J = 6.85417
   - 6.51 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.lo_J = 6.51146
   - 7.20 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.hi_J = 7.19687
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 4.75 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.E_C2_J = 4.754
   - 3.97 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.E_C2_J = 3.97496
   - 3.88 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.mid_J = 3.88056
   - 3.70 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.lo_J = 3.70417
   - 4.06 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.hi_J = 4.05694
43. With PT-Exp4's, PP-Exp2's and SP-Exp3's strong triggers the lumped neighbour runs away in every run of these searches, at 106 to 128~s, releasing 22.4 to 22.6~kJ of reaction heat, where the resolved neighbour has released 4.1 to 4.8~kJ by its own runaway.
   - 106 (new): smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_C2_t_s = 106.141
   - 128: smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_C2_t_s = 127.543
   - 22.4 (new): smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_rxn_J = 22.3795
   - 22.6: smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3: lumped_rxn_J = 22.5889
   - 4.1 (new): smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3 with the mean's runaway: rxn_J = 4.07541
   - 4.8: smallest and largest of results/stage15_paper_numbers.json: B1 runs of PT_Exp4, PP_Exp2, SP_Exp3 with the mean's runaway: rxn_J = 4.79567
44. Only ST-Exp3's weak trigger (16.6~kJ) reverses the order: the resolved neighbour needs 10.28~kJ (9.77 to 10.80~kJ), 0.85 times the lumped neighbour's 12.03~kJ, and at 10.80~kJ it runs away at 61.5~s while the lumped neighbour does not run away.
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
   - 10.28 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.mid_J = 10.2812
   - 9.77 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.lo_J = 9.76719
   - 10.80 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.hi_J = 10.7953
   - 0.85 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.ratio_to_C2 = 0.854599
   - 12.03 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.E_C2_J = 12.0305
   - 10.80 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.hi_J = 10.7953
   - 61.5 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3, the run at the bracket's upper end: t_C8_s = 61.5222
45. \caption{The thresholds of the sixteen tests with the 21.4~s pulse, in order of the trigger's fitted body energy (top axis): the least energy delivered to the facing half at which the resolved neighbour's hottest point (triangles), the lumped neighbour (squares) and the resolved neighbour's mean (circles, reactive cross-section; diamonds, three-dimensional model) reach 255.7\degC.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
46. For PT-Exp1 with deliveries of 5 to 120~s, and for ST-Exp3 and PT-Exp3 at 10 and 60~s, the resolved threshold lies within 3\,\% of the cross-section conduction model, whose value is one end of every final bracket; the delivery's Fourier number $\alpha\tau/a^2$ there runs from 0.025 to 0.60, with $\alpha=5.565\times10^{-7}$~m$^2$\,s$^{-1}$ the roll's diffusivity across its layers, $\tau$ the delivery's duration and $a=10.55$~mm the cell's radius.
   - 5: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 5
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 10: results/stage13_skin.csv: tau_d_s where {'test': 'M50_ST_Exp3', 'region': 'half'} = 10
   - 60: results/stage13_skin.csv: tau_d_s where {'test': 'M50_ST_Exp3', 'region': 'half'} = 60
   - 3: src/stage13_inputs.py: /FIRST_STEP = (0\.03)/ = 3
   - 0.025: results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '5.0'} = 0.0250038
   - 0.60 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '120.0'} = 0.600091
   - 5.565\times10^{-7}: results/stage13_sentences.md: /\(([\d.]+e-7) m2/s\)/ = 5.565e-07
   - 10.55 (new): results/manuscript_numbers.json: constants.cell_radius_mm = 10.55
47. With the reaction switched off at the upper end of each such search, the hottest point still reaches 255.7\degC{} or falls short by at most 1.1~K, so the reaction plays no part in it.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 1.1 (new): results/stage13_skin.csv: the largest shortfall of inert_peak_minus_level_K up to a Fourier number of 0.6 = 1.13572
48. Over 360~s (Fourier number 1.80) the cell heats through: the threshold falls below the conduction model, the hottest point without the reaction peaks 18.9~K short, and with it the crossing comes at 316.5~s on the cell's axis with the mean at 240.1\degC, a runaway inside the cell.
   - 360: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 360
   - 1.80 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 1.80027
   - 18.9 (new): results/stage13_skin.csv: inert_peak_minus_level_K where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 18.9319
   - 316.5 (new): results/stage13_skin.csv: res_t_cross_hi_s where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 316.544
   - 240.1 (new): results/stage13_skin.csv: res_mean_at_cross_hi_C where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 240.119
49. The ratio of PT-Exp1's lumped to local threshold accordingly falls from 2.90 at a Fourier number of 0.11 to 1.16 at 0.60 and 0.94 at 1.80.
   - 2.90 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/21.39 = 2.89706
   - 0.11: results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '21.38651984299561'} = 0.106949
   - 1.16 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/120 = 1.15999
   - 0.60 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '120.0'} = 0.600091
   - 0.94 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/360 = 0.938279
   - 1.80 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 1.80027
50. The lumped neighbour's reaction heat, with the separator molten, equals its losses at $T_\mathrm{ign}=218.5$\degC{} with the trigger at the neighbour's own temperature (230.4\degC{} with the trigger at 25\degC), and over the 200 kinetic draws $T_\mathrm{ign}$ runs from 215.3 to 221.4\degC{} (central 95\,\%), a span of 6.1~K.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
   - 230.4 (new): results/stage13_tign.csv: T_ign_C where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'ambient'} = 230.379
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 215.3 (new): results/stage13_paper_numbers.json: scorecard/P7/p2.5_C = 215.257
   - 221.4 (new): results/stage13_paper_numbers.json: scorecard/P7/p97.5_C = 221.395
   - 95: predictions_stage13.md: /the central (95) % of the 200 draws/ = 95
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
51. At that point the low-temperature cathode reaction gives 73.3\,\% of the reaction heat under the posterior mean.
   - 73.3 (new): results/stage13_tign.csv: carrying_share where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 73.3174
52. The two-body model, which asks only whether the neighbour reaches $T_\mathrm{ign}$ with enough of that reaction's 2,667~J left to reach 255.7\degC, lies within the larger of 10\,\% and 300~J of the lumped threshold in all 32 searches at the low and high contacts.
   - 2,667 (new): results/stage13_tign.csv: cat1_heat_total_J where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 2667.2
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 10: predictions_stage13.md: /within the larger of (10) % and 300 J/ = 10
   - 300 (new): predictions_stage13.md: /within the larger of 10 % and (300) J/ = 300
   - 32: results/stage13_paper_numbers.json: scorecard.P8.n_within = 32
53. Because the threshold is the heat that brings the neighbour to $T_\mathrm{ign}$ less what the trigger conducts, it falls by 393 to 456~J per kJ of the trigger's body energy (PT-Exp3, ST-Exp2, PP-Exp3).
   - 393 (new): smallest and largest of results/stage13_paper_numbers.json: scorecard.P10.cases: slope_J_per_kJ = 393.034
   - 456 (new): smallest and largest of results/stage13_paper_numbers.json: scorecard.P10.cases: slope_J_per_kJ = 456.135
54. By 250~s the lumped neighbour has taken in 2.1 to 2.3~kJ more than the resolved one through the same conductance, since the resolved cell's contact patch heats toward the trigger's temperature while its mean lags; and the resolved neighbour's reaction heat stays local.
   - 250 (new): results/stage15_accounts.json: accounts rows: t_s = 250
   - 2.1: smallest and largest of results/stage15_accounts.json: lumped_less_resolved.contact_and_wedge at 250 s = 2.05166
   - 2.3 (new): smallest and largest of results/stage15_accounts.json: lumped_less_resolved.contact_and_wedge at 250 s = 2.30888
55. At 5.04~kJ over 21.4~s in PT-Exp4, where the lumped neighbour runs away at 215.6~s, the resolved neighbour runs away under none of four kinetic draws chosen by the rank of their onset (its mean peaks at 191.2 to 192.4\degC) nor with an aged SEI (188.3\degC).
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 215.6 (new): results/stage15_readings.json: 1.PT_Exp4.lumped_cross_s = 215.6
   - 191.2 (new): smallest and largest of results/stage15_paper_numbers.json: B4.draws: peak_mean_C = 191.164
   - 192.4: smallest and largest of results/stage15_paper_numbers.json: B4.draws: peak_mean_C = 192.397
   - 188.3 (new): results/stage15_paper_numbers.json: B4.aged.peak_mean_C = 188.294
56. Every rate law must be shifted by more than 17.5~K for it to run away there: at 17.5~K its mean peaks at 221.1\degC, and at 20~K it runs away at 270.3~s.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 221.1 (new): results/stage15_paper_numbers.json: B4.shift_runs, the run shifted by 17.5 K: peak_mean_C = 221.105
   - 20: results/stage15_paper_numbers.json: B4.shift.least_shift_K = 20
   - 270.3 (new): results/stage15_paper_numbers.json: B4.shift.t_C8_s = 270.338
57. That shift is about three times the 6.1~K span of the posterior's ignition temperatures.
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
58. (b) The lumped threshold of three tests with the trigger's fitted body energy (hollow) and shifted by 2~kJ either way (filled), with the fall per kJ.
   - 2: src/stage13_inputs.py: /for d in \(-2000\.0, (2000\.0)\)/ = 2
59. (c) The lumped neighbour's ignition temperature over the 200 kinetic draws.
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
60. (d) That spread beside the shift of every rate law that the resolved neighbour of PT-Exp4 needs to run away at 5.04~kJ: crosses, no runaway; circle, runaway.}
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
61. With the 21.4~s pulse the lumped neighbour runs away at the measured time with 0.26 to 5.96~kJ in seven propagated tests, and at its threshold in two (PT-Exp4, 4.66 to 4.85~kJ; ST-Exp3, 11.95 to 12.11~kJ).
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 4.85: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_PT_Exp4'} = 4.851
   - 11.95: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_ST_Exp3'} = 11.95
   - 12.11: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_ST_Exp3'} = 12.1115
62. Of the five tests that did not propagate and report low maxima, four need none, since with no delivery the far face already peaks 13.8 to 56.3~K above their maxima, and PT-Exp1 needs 2.09~kJ, 7.9 times what SP-Exp3 needed to propagate.
   - 13.8: smallest and largest of results/stage9_paper_numbers.json: part_a.A3: overshoot_K = 13.7556
   - 56.3: smallest and largest of results/stage9_paper_numbers.json: part_a.A3: overshoot_K = 56.3217
   - 2.09: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp1'} = 2.0907
   - 7.9: results/stage12_paper_numbers.json: P4.ratio = 7.9
63. Over the four delivery shapes these needs span 22- to 64-fold, the largest non-zero over the smallest.
   - 22: results/stage12_paper_numbers.json: part_c.stage10_energy_ratio_range[0] = 21.8
   - 64: results/stage12_paper_numbers.json: part_c.stage10_energy_ratio_range[1] = 63.8
64. Fitted on one connection and scored on the other, no quantity the model yields predicts the outcomes better than one probability for every test by the registered margin of 0.1 in the mean log score: the largest gain is 0.062, with permutation $p$-values of 0.23 to 0.75, and the thresholds mostly restate the trigger's energy (Spearman's $\rho=-0.92$ for the local and $-0.97$ for the lumped).
   - 0.1: predictions_stage10.md: /by more than (0\.1) in the mean log score/ = 0.1
   - 0.062: results/stage10_paper_numbers.json: part_c.largest_d_log = 0.0624263
   - 0.23: smallest and largest of results/stage10_paper_numbers.json: part_c.held_out: p_log = 0.226477
   - 0.75: smallest and largest of results/stage10_paper_numbers.json: part_c.held_out: p_log = 0.751725
   - -0.92 (new): results/stage10_paper_numbers.json: part_c.rho_E_b.fC1 = -0.920358
   - $-0.97 (new): results/stage10_paper_numbers.json: part_c.rho_E_b.fC2 = -0.974721
65. For the resolved neighbour to run away at a test's measured time, the reactive cross-section needs 4.1 to 8.1~kJ delivered by then in all twenty-five reproduced cases outside ST-Exp3, whatever the delivery's shape, where the lumped neighbour needs 0.2 to 6.0~kJ in the same cases.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 5.9624
66. With the pulse the resolved need exceeds the lumped one in every test it reproduces, most in SP-Exp3, 4.58 against 0.26~kJ.
   - 4.58 (new): results/stage15_table.csv: C8_xs_E_by_t_J where {'test': 'M50_SP_Exp3', 'delivery': '21.39 s pulse'} = 4.58171
   - 0.26: results/stage15_table.csv: C2_E_by_t_J where {'test': 'M50_SP_Exp3', 'delivery': '21.39 s pulse'} = 0.2635
67. In ST-Exp3 the resolved neighbour runs away at 114.0~s already at its threshold, before the measured 177~s, so no delivered energy reproduces that test's time.
   - 114.0 (new): results/stage15_table.csv: C8_xs_t_at_E_star_hi_s where {'test': 'M50_ST_Exp3', 'delivery': '21.39 s pulse'} = 113.987
   - 177: results/stage15_table.csv: t_measured_s where {'test': 'M50_ST_Exp3', 'delivery': '21.39 s pulse'} = 177
68. PT-Exp4's thermocouple reaches 141.0\degC{} by 45~s and 197.3\degC{} at 271.5~s, when the neighbour's jump begins.
   - 141.0: results/stage10_paper_numbers.json: measured.at_45_s_C = 140.997
   - 45: results/stage10_paper_numbers.json: /"at_(45)_s_C"/ = 45
   - 197.3: results/stage10_paper_numbers.json: measured.at_onset_C = 197.254
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
69. With 4.66 and 5.04~kJ over 21.4~s, either side of the lumped neighbour's threshold, the model's far face lies 16.3 and 16.8~K from the record, the root mean square over 0 to 271.5~s, but the resolved neighbour does not run away: with 5.04~kJ its mean peaks at 190.6\degC{} and cools.
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 16.3: results/stage10_paper_numbers.json: part_a.tri21_C2_lo_hcentral.nodes.away.window.rms_K = 16.2554
   - 16.8: results/stage10_paper_numbers.json: part_a.tri21_C2_hi_hcentral.nodes.away.window.rms_K = 16.8348
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 190.6 (new): results/stage15_readings.json: 1.PT_Exp4.mean_peak_C = 190.6
70. At 7.42~kJ, the upper end of its own bracket, the resolved neighbour runs away at 181.9~s, before the measured onset at 271.5~s, and its far face's jump begins at 234.1\degC, 36.8~K above the 197.3\degC{} from which the measured neighbour jumped; over 0 to 181.9~s its far face lies 51.4~K from the record.
   - 7.42 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 181.9 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
   - 234.1 (new): results/stage15_paper_numbers.json: B3a.run.far_jump.T_C = 234.101
   - 36.8 (new): results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
   - 197.3: results/stage10_paper_numbers.json: measured.at_onset_C = 197.254
   - 181.9 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
   - 51.4 (new): results/stage15_paper_numbers.json: B3a.history.rms_K = 51.4421
71. A 5.04~kJ pulse followed by a constant 12.5~W brings the resolved runaway to 255.9~s, and one followed by 10~W to 369.3~s, the two holds having added 2.9 and 3.5~kJ; with 12.5~W the far face's jump begins at 233.6\degC, and it lies 33.1~K from the record over 0 to 255.9~s.
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.result.P_hi_W = 12.5
   - 255.9 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: t_C8_s = 255.856
   - 10: results/stage15_paper_numbers.json: B3b.result.P_lo_W = 10
   - 369.3 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold10.0W: t_C8_s = 369.329
   - 2.9 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: delivered_J.delivery2 = 2.93142
   - 3.5: results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold10.0W: delivered_J.delivery2 = 3.48013
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.result.P_hi_W = 12.5
   - 233.6 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: far_jump.T_C = 233.595
   - 33.1 (new): results/stage15_paper_numbers.json: B3b.history.rms_K = 33.1383
   - 255.9 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: t_C8_s = 255.856
72. The thermocouple's angle is not reported, but when the jump begins the far face is the coolest of the model's five probes at mid-length (the two side probes read 235.5 and 235.8\degC), so 36.8~K is the least difference those probes give.
   - 235.5 (new): results/stage15_independent_read.md: the two side probes' readings at the far face's jump = 235.5
   - 235.8 (new): results/stage15_independent_read.md: the two side probes' readings at the far face's jump = 235.79
   - 36.8 (new): results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
73. (a) For the nine tests that propagated, in order of the measured time: the energy delivered to the facing half by that time at which the lumped neighbour (filled) or the resolved neighbour's mean (hollow, reactive cross-section) reaches 255.7\degC{} at the measured time, for the four delivery shapes; in ST-Exp3 the resolved neighbour runs away before the measured time even at its threshold, which is shown.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
74. (b) For the seven tests that did not propagate: the energy delivered over 21.4~s that puts the far face's peak at the measured maximum; hollow, the two maxima that may not be the neighbour's surface; at the bottom, tests whose far face exceeds the maximum with no delivery.}
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
75. (b) The resolved neighbour's mean temperature under the same deliveries; the resolved neighbour runs away where its mean reaches 255.7\degC.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
76. The run of 5.0~kJ over 21.4~s was carried to 332~s.}
   - 5.0: results/stage15_readings.json: 1.PT_Exp4.E_J = 5.045
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 332 (new): results/stage15_readings.json: 1.PT_Exp4.t_end_s = 332
77. From published inputs alone, what the ejecta can release in this rig is at most 225.8~kJ, and every path but one is bounded only near that (Table~ , Fig.~ ).
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
78. Within 21.4~s, radiation can deliver at most 27.9~kJ, a black body at 1500\degC{} filling the facing half's view; a flame held on the vent's axis sends at most about 0.37\,\% of its radiation onto the facing half, about 0.85~kJ, but no source places the flame.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 0.37 (new): results/stage14_corrections.json: scans.axis_max_w = 0.373225
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
79. Gas beside the neighbour can deliver at most 195.5~kJ, a breach's jet facing the neighbour and solids and melt on it 225.8~kJ each, and the neighbour's own discharge in the parallel tests 65.5~kJ.
   - 195.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A2', 'window_s': '21.39'} = 195.516
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 65.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A6', 'window_s': '21.39'} = 65.52
80. Within 21.4~s gas, a breach's jet and solids and melt each reach all twelve needs that are not zero; radiation reaches ten and misses only the two exploratory maxima (32.7 and 75.8~kJ); the discharge reaches five of the six parallel needs.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 32.7 (new): results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_SP_Exp4'} = 32.667
   - 75.8 (new): results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp2'} = 75.8149
81. Every energy the resolved neighbour needs, under any of the four shapes, is 5.3 to 25.4\,\% of the Databank's median ejected energy and below the least of the bounds within the delivery's duration.
   - 5.3 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 5.29617
   - 25.4 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 25.4319
82. \caption{What each path can deliver to the neighbour's facing half, from published inputs alone (upper bounds within the pulse's 21.4~s and in total; every lower bound is zero), against what the neighbour models need: the lumped neighbour's needs at the measured times with the pulse, the energy the resolved neighbour needs delivered by the measured times, and the energy calorimetry measured in this cell's ejecta.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
83. Against the 151 central three-dimensional runs that the study had carried past the hottest point's crossing, it gave the same outcome, runaway of the mean within 900~s or none, in all 151.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
84. In the 92 runs in which both run away, its runaway comes 1.0~s later on average (5.5~s earlier to 34.5~s later); in the 59 in which neither does, its mean peaks 1.9~K lower on average, and up to 20.7~K lower in the parallel tests, whose tabs it lacks.
   - 92 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.n = 92
   - 1.0: results/stage15_cross_section.json: A1_summary.dt_C8_s.mean = 1.03766
   - 5.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.min = 5.48377
   - 34.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.max = 34.5232
   - 59 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.n = 59
   - 1.9 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.mean = 1.87063
   - 20.7 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.min = 20.6721
85. Its thresholds were registered as the centres of the three-dimensional searches: in three of the four tests the searches' opening two runs, 5\,\% either side of its value, bracketed the threshold, and in SP-Exp3 the threshold lay above both, its value 9.1\,\% below the bracket's midpoint.
   - 5: predictions_stage15.md: /less (5) % and plus 5 %/ = 5
   - 9.1 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.rel_diff_xs = 9.09091
86. A run takes 17 to 71~s on one processor core, against 240 to 2,762~s for the three-dimensional runs of the same searches.
   - 17: smallest and largest of results/stage15_xs/*.json: wall_s = 16.9846
   - 71: smallest and largest of results/stage15_xs/*.json: wall_s = 71.3495
   - 240: smallest and largest of results/stage15_paper_numbers.json: runs.wall_s min and max = 239.781
   - 2,762 (new): smallest and largest of results/stage15_paper_numbers.json: runs.wall_s min and max = 2762.3
87. (a) The time the resolved neighbour's mean reaches 255.7\degC, in the runs where both models run away.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
88. (c) The thresholds of the four tests searched in three dimensions with the 21.4~s pulse.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
89. Read through a lumped neighbour, what each test needs varies 22- to 64-fold and overlaps between the tests that propagated and those that did not, so a pack model that ignites a neighbour at one delivered share will reproduce some tests and not others.
   - 22: results/stage12_paper_numbers.json: part_c.stage10_energy_ratio_range[0] = 21.8
   - 64: results/stage12_paper_numbers.json: part_c.stage10_energy_ratio_range[1] = 63.8
90. Read through a resolved neighbour, the needs at the measured times fall within 4.1 to 8.1~kJ outside one test, a narrower band, though one the tests cannot yet confirm.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 8.11583
91. Either way the needed energies are a small part of what the ejecta carry: 5.3 to 25.4\,\% of the Databank's median for this cell for the resolved neighbour~ .
   - 5.3 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 5.29617
   - 25.4 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 25.4319
92. For a different cell and stack, Torres-Castro et al.\ estimated that the next pouch cell absorbed 2.0~kJ on average before it failed~ , inside the lumped range found here.
   - 2.0: manuscript/data/comparators.csv: value where {'key': 'torrescastro2020passive', 'quantity': 'energy the next cell absorbs before it fails, mean'} = 2
93. The resolved neighbour's hottest point crosses within seconds of the delivery, and its mean needs 1.49 to 1.72 times the lumped neighbour's energy.
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
94. Under the lumped neighbour's energy the model's far face lies 16.3 to 16.8~K from PT-Exp4's record but the resolved cell does not run away; at the resolved cell's own runaway its far face is 37~K hotter than the measured surface when the jump begins.
   - 16.3: results/stage10_paper_numbers.json: part_a.tri21_C2_lo_hcentral.nodes.away.window.rms_K = 16.2554
   - 16.8: results/stage10_paper_numbers.json: part_a.tri21_C2_hi_hcentral.nodes.away.window.rms_K = 16.8348
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
95. A runaway that starts from part of the cell, more heat arriving over a longer time, or rate laws shifted by more than 17.5~K would each reconcile the two; the results here do not choose between them.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
96. The thermocouple's angle would say which part of the neighbour's surface the published maxima and history describe, and so whether the far face's overshoot with no delivery and its 37~K excess at the jump are real.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
97. The flame's position and temperature beside the cells would bound radiation by geometry, from 27.9~kJ toward 0.85~kJ.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
98. One cell type, in one laboratory's rig, carries the comparison, and one published history; that history was read from a figure, and its opening 8.5~s, a spike to 102\degC, are taken as the thermocouple's exposure at the trigger's runaway.
   - 8.5: results/stage10_paper_numbers.json: measured.dip_after_spike_t_s = 8.5
   - 102: results/stage10_paper_numbers.json: measured.spike_on_the_samples_C = 101.711

## main.tex: Conclusions

99. \item With the trigger's body energy held to the largest calorimetry gives for this cell, conduction and radiation leave the neighbour's hottest point at least 29~K short of 255.7\degC.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
100. \item With 21.4~s of delivered heat the resolved neighbour runs away as a whole at 1.49 and 1.72 times the energy the lumped neighbour needs in two tests.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
101. \item Bringing the resolved threshold down to the lumped one would need every rate law shifted by more than 17.5~K, against a 6.1~K span of the posterior's ignition temperatures.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
102. \item At the tests' measured times the resolved neighbour needs 4.1 to 8.1~kJ delivered by then, against 0.2 to 6.0~kJ for the lumped neighbour.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 5.9624
103. \item Every need lies within the bounds of at least two delivery paths, which published inputs cannot narrow below 27.9~kJ within 21.4~s.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## main.tex: appendices

104. The resolved neighbour's mesh is graded toward the line of contact, the roll is homogeneous and anisotropic, the can is a shell of steel with its own conductance and heat capacity, and the contact sector spans 45\textdegree{} either side of the line of contact, where room convection is removed.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
105. Every run's energy account, the heat taken in through each boundary against the change in stored heat and the reaction heat released, closes to within $2\times10^{-11}$ of the heat taken in.
   - 2\times10^{-11}: results/stage8_paper_numbers.json: checks.V4.largest_relative.resolved = 1.9747e-11
106. The skin model's peak rise is $\Phi E''/(e\sqrt{\tau})$, with $E''$ the delivered energy per unit area, $\tau$ the pulse's duration, $e=1,743$~J\,m$^{-2}$\,K$^{-1}$\,s$^{-1/2}$ the roll's effusivity across its layers and $\Phi=1.2284$ for the triangular pulse; the can enters as a surface layer of 841.7~J\,m$^{-2}$\,K$^{-1}$ with a linear surface loss.
   - 1,743 (new): results/stage13_readings.json: reading_1.e_roll_as_resolved = 1742.5
   - 1.2284 (new): results/stage13_checks.json: V5.Phi00 = 1.22842
   - 841.7 (new): results/stage13_readings.json: reading_1.C_s_J_m2K = 841.736

## manuscript/rebuild/tables/t1_tests.tex: caption

107. \caption{The sixteen two-cell tests of LG M50 cells of Fransson et al.~ (their Tables 3 and 4), and the body energy $E_\mathrm{b}$ that puts the model's trigger at the measured trigger peak at the central contact when released over 21.39~s.
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
108. Category, Fransson et al.'s failure category: 1, the trigger's nail-penetration failure; 2, failure in the propagating cell; 4, sidewall rupture of the trigger; c.m., ``cell movement'' in the X-ray camera's field of view, given in place of a category; a dash, none given.}
   - 1: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 1
   - 2: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 2
   - 4: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 4

## manuscript/rebuild/tables/t2_parameters.tex

109. } \toprule Quantity & Value & Source \\ \midrule {\textit{Geometry and cells}} \\ Cell diameter and length & 21.1 and 70.1 mm & \\ Can: wall and conductivity; mass and specific heat & 0.25 mm, 15 W\,m$^{-1}$\,K$^{-1}$; 9 g, 500 J\,kg$^{-1}$\,K$^{-1}$ & \\ Roll conductivity across and along the layers & 1.3 and 25 W\,m$^{-1}$\,K$^{-1}$ & \\ Cell heat capacity & 61.75 J\,K$^{-1}$ (65 g at 950 J\,kg$^{-1}$\,K$^{-1}$) & \\ Resolved neighbour & half model, 19,355 nodes & this study \\ {\textit{Heat paths}} \\ Contact conductance between the cans, $h_c$ & 200, 2,000, 3,700 W\,m$^{-2}$\,K$^{-1}$ (low, central, high) & \\ Air in the wedge beside the contact & 0.03 W\,m$^{-1}$\,K$^{-1}$ & \\ Welded tabs: series one, parallel two & 6.8 mW\,K$^{-1}$ per tab (5 and 10 as brackets) & \\ View factor between the cans; emissivity & 0.1817; 0.8 & \\ Room convection; ambient & 10 W\,m$^{-2}$\,K$^{-1}$; 25\textdegree C & \\ {\textit{Trigger}} \\ Model and release & one temperature; triangular over 21.39 s & \\ Body energy $E_\mathrm{b}$ & 9.0 to 54.3 kJ, one per test (Table 1); 33.2 kJ held to calorimetry & \\ {\textit{Kinetics}} \\ Model & Bayesian chemical reaction neural network: posterior mean, and 200 joint draws & \\ Reactant masses; initial SEI amount & per 720 g reference cell; 0.15 (fresh), 0 (aged) & \\ Runaway level & 255.7\textdegree C, within 900 s & \\ {\textit{Delivered heat}} \\ Region & the half of the neighbour's can facing the trigger, a uniform flux & this study \\ Shapes & triangular over 21.39 s; constant power over 120, 240 or 360 s & this study \\ \bottomrule
   - 21.1: results/manuscript_numbers.json: constants.cell_diameter_mm = 21.1
   - 70.1: results/manuscript_numbers.json: constants.cell_length_mm = 70.1
   - 0.25: results/manuscript_numbers.json: constants.can_thickness_mm = 0.25
   - 15: results/manuscript_numbers.json: constants.can_conductivity_W_mK = 15
   - 9: external/m50-two-cell-pilot/src/lumped_two_cell.py: /M_CAN += (0\.009)/ = 9
   - 500: external/m50-two-cell-pilot/src/lumped_two_cell.py: /CP_CAN += (500\.0)/ = 500
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

## manuscript/rebuild/tables/t3_bounds.tex

110. \centering \footnotesize \caption{What each path can deliver to the neighbour's facing half, from published inputs alone: the upper bound within the 21.4~s of the pulse and in total (every lower bound is zero), what sets it, and the measurement that would bound it more tightly.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
111. What the ejecta can release in the rig is 225.8~kJ, the most calorimetry measured for this cell's ejecta (89.34~kJ)~ with the heat of burning the vent gas in open air (at most 136.5~kJ, measured on another 21700 cell)~ ; the gas and flame are taken at up to 1500\textdegree C~ and the vent gas at up to 398.5~m\,s$^{-1}$~ .}
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 89.34 (new): results/stage14_inputs.csv: value where {'key': 'db_Eej_max'} = 89.3378
   - 136.5 (new): results/stage14_inputs.csv: value where {'key': 'vendra_Qt_max'} = 136.5
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 398.5 (new): results/stage14_inputs.csv: value where {'key': 'u_vent_max'} = 398.5
112. rr } \toprule Path & {21.4 s} & {Total} & What sets the bound & Measurement that would bound it \\ & (kJ) & (kJ) & & \\ \midrule Radiation from a vent's jet or flame & 27.9 & 225.8 & a black body at 1500\textdegree C filling the facing half's view, the holder possibly reflecting; held on the vent's axis, about 0.85~kJ & the flame's position and temperature beside the cells \\ Gas beside the neighbour, burning or not & 195.5 & 225.8 & convection at 398.5~m\,s$^{-1}$ with hydrogen's properties~ , at most twice its whole-cylinder mean on one half, and radiation at 1500\textdegree C & the gas's temperature and velocity in the wedges beside the line of contact \\ A breach's jet facing the neighbour & 225.8 & 225.8 & what the ejecta can release; a narrow jet strikes the facing half from a sixth of the circumference & where breaches face and what they carry \\ Solids and melt on or against the facing half & 225.8 & 225.8 & what the ejecta can release; melt falls onto the facing half from half of the circumference & the debris left on the neighbour \\ Conduction through the cell holder & -- & -- & no source gives the inserts' material or contact (247.3~kJ if bounded as the jet and melt are) & the holder's inserts and their contact \\ The neighbour's own discharge (parallel tests) & 65.5 & 65.5 & the rated stored energy (15.6~kJ within 21.4~s if the resistance stayed at its 25\textdegree C value) & the current between parallel cells \\ \bottomrule
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
   - 195.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A2', 'window_s': '21.39'} = 195.516
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 398.5 (new): results/stage14_inputs.csv: value where {'key': 'u_vent_max'} = 398.5
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 247.3 (new): results/stage14_corrections.json: E_global_J = 247.333
   - 65.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A6', 'window_s': '21.39'} = 65.52
   - 65.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A6', 'window_s': '21.39'} = 65.52
   - 15.6 (new): results/stage14_bounds.json: A6/conditional_25C_J/21.39 = 15.6394
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 25: results/stage14_inputs.csv: /0\.5 C for 30 s, (25) C/ = 25

## manuscript/rebuild/highlights.txt

113. Held to calorimetry, conduction and radiation leave a neighbour at least 29 K short In two tests a resolved neighbour needs 1.49 to 1.72 times a lumped neighbour's heat Skin conduction sets the local threshold; an ignition energy balance the lumped one Matching the lumped threshold needs rates shifted over 17.5 K; posterior span 6.1 K The one published history jumps from 37 K below the resolved neighbour's far face
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008

## manuscript/rebuild/ga_text.txt

114. failing cell neighbour heat delivered to the facing half with calorimetry's energy, conduction and radiation alone leave the neighbour at least 29 K short of runaway 4.75 | PT-Exp4, the lumped neighbour's threshold, kJ 7.06 | PT-Exp4, the resolved neighbour's threshold, kJ 1.49 times | PT-Exp4, the resolved threshold over the lumped one 3.97 | PP-Exp2, the lumped neighbour's threshold, kJ 6.85 | PP-Exp2, the resolved neighbour's threshold, kJ 1.72 times | PP-Exp2, the resolved threshold over the lumped one PT-Exp4 PP-Exp2 heat in 21.4 s for runaway (kJ) lumped neighbour resolved neighbour The one published history jumps from 37 K below the resolved far face.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 4.75 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.E_C2_J = 4.754
   - 7.06 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.mid_J = 7.0625
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 3.97 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.E_C2_J = 3.97496
   - 6.85 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.mid_J = 6.85417
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
115. Published inputs bound every delivery path at 27.9 kJ or more.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564

## manuscript/rebuild/letters/Cover_letter_FSJ.txt

116. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short of runaway.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
117. In two tests the resolved neighbour needs 1.49 and 1.72 times the heat the lumped neighbour needs.
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
118. Skin conduction sets the resolved neighbour's local threshold, and an energy balance to an ignition temperature of 218.5 °C sets the lumped one.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
119. Matching the two would need every rate law shifted by more than 17.5 K, against a 6.1 K span from the kinetic posterior.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
120. In the one published temperature history, the resolved neighbour's far face begins its jump 37 K above the reading from which the measured surface jumps.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
121. Published inputs bound every delivery path at 27.9 kJ or more, so they cannot decide between the two readings; the paper names the measurement that would, the heat flux on the neighbour's facing side.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
122. The code, inputs and run records are openly archived, and the study's 98 predictions were committed before the runs they concern.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98

## manuscript/rebuild/letters/Cover_letter_JES.txt

123. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short of runaway.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
124. In two tests the resolved neighbour needs 1.49 and 1.72 times the heat the lumped neighbour needs.
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
125. Skin conduction sets the resolved neighbour's local threshold, and an energy balance to an ignition temperature of 218.5 °C sets the lumped one.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
126. Matching the two would need every rate law shifted by more than 17.5 K, against a 6.1 K span from the kinetic posterior.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
127. In the one published temperature history, the resolved neighbour's far face begins its jump 37 K above the reading from which the measured surface jumps.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
128. Published inputs bound every delivery path at 27.9 kJ or more, so they cannot decide between the two readings; the paper names the measurement that would, the heat flux on the neighbour's facing side.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
129. The code, inputs and run records are openly archived, and the study's 98 predictions were committed before the runs they concern.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98

## manuscript/rebuild/letters/Cover_letter_JPS.txt

130. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K short of runaway.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
131. In two tests the resolved neighbour needs 1.49 and 1.72 times the heat the lumped neighbour needs.
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
132. Skin conduction sets the resolved neighbour's local threshold, and an energy balance to an ignition temperature of 218.5 °C sets the lumped one.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
133. Matching the two would need every rate law shifted by more than 17.5 K, against a 6.1 K span from the kinetic posterior.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
134. In the one published temperature history, the resolved neighbour's far face begins its jump 37 K above the reading from which the measured surface jumps.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
135. Published inputs bound every delivery path at 27.9 kJ or more, so they cannot decide between the two readings; the paper names the measurement that would, the heat flux on the neighbour's facing side.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
136. The code, inputs and run records are openly archived, and the study's 98 predictions were committed before the runs they concern.
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98

## manuscript/rebuild/letters/Enquiry_FSJ.txt

137. Two touching LG M50 cells were modelled with published kinetics, the neighbour as one temperature and as a resolved field, against sixteen tests; 42 of 98 pre-registered predictions failed.
   - 42: manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed = 42
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98
138. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K below 255.7 °C.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
139. About 7 kJ delivered over 21.4 s makes the resolved neighbour run away, 1.49 and 1.72 times the lumped neighbour's need in two tests.
   - 7: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.mid_J = 7.0625
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
140. The local threshold is skin conduction, within 3 % of a conduction model.
   - 3: src/stage13_inputs.py: /FIRST_STEP = (0\.03)/ = 3
141. The lumped threshold is an energy balance to an ignition temperature of 218.5 °C.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
142. Matching the whole-cell thresholds needs the rate laws shifted over 17.5 K, against a 6.1 K posterior span.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
143. At the measured times the resolved neighbour needs 4.1 to 8.1 kJ, the lumped one 0.2 to 6.0 kJ.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 5.9624
144. In the one published history, the resolved neighbour's far face exceeds the measured surface by 37 K as runaway begins.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
145. Published inputs bound every delivery path at 27.9 kJ or more, above every need.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564

## manuscript/rebuild/letters/Enquiry_JES.txt

146. Two touching LG M50 cells were modelled with published kinetics, the neighbour as one temperature and as a resolved field, against sixteen tests; 42 of 98 pre-registered predictions failed.
   - 42: manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed = 42
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98
147. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K below 255.7 °C.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
148. About 7 kJ delivered over 21.4 s makes the resolved neighbour run away, 1.49 and 1.72 times the lumped neighbour's need in two tests.
   - 7: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.mid_J = 7.0625
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
149. The local threshold is skin conduction, within 3 % of a conduction model.
   - 3: src/stage13_inputs.py: /FIRST_STEP = (0\.03)/ = 3
150. The lumped threshold is an energy balance to an ignition temperature of 218.5 °C.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
151. Matching the whole-cell thresholds needs the rate laws shifted over 17.5 K, against a 6.1 K posterior span.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
152. At the measured times the resolved neighbour needs 4.1 to 8.1 kJ, the lumped one 0.2 to 6.0 kJ.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 5.9624
153. In the one published history, the resolved neighbour's far face exceeds the measured surface by 37 K as runaway begins.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
154. Published inputs bound every delivery path at 27.9 kJ or more, above every need.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564

## manuscript/rebuild/letters/Enquiry_JPS.txt

155. Two touching LG M50 cells were modelled with published kinetics, the neighbour as one temperature and as a resolved field, against sixteen tests; 42 of 98 pre-registered predictions failed.
   - 42: manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed = 42
   - 98 (new): manuscript/rebuild/data/predictions_registry.csv: rows = 98
156. With the failing cell's energy held to calorimetry, conduction and radiation leave the neighbour at least 29 K below 255.7 °C.
   - 29 (new): results/stage12_paper_numbers.json: part_a.high.shortfall_hot_spot_K[0] = 29
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
157. About 7 kJ delivered over 21.4 s makes the resolved neighbour run away, 1.49 and 1.72 times the lumped neighbour's need in two tests.
   - 7: results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.mid_J = 7.0625
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 1.49 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.ratio_to_C2 = 1.48559
   - 1.72 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.ratio_to_C2 = 1.72434
158. The local threshold is skin conduction, within 3 % of a conduction model.
   - 3: src/stage13_inputs.py: /FIRST_STEP = (0\.03)/ = 3
159. The lumped threshold is an energy balance to an ignition temperature of 218.5 °C.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
160. Matching the whole-cell thresholds needs the rate laws shifted over 17.5 K, against a 6.1 K posterior span.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 6.1 (new): results/stage13_paper_numbers.json: scorecard.P7.span_K = 6.13765
161. At the measured times the resolved neighbour needs 4.1 to 8.1 kJ, the lumped one 0.2 to 6.0 kJ.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, matched cases outside ST_Exp3 = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same cases = 5.9624
162. In the one published history, the resolved neighbour's far face exceeds the measured surface by 37 K as runaway begins.
   - 37: results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
163. Published inputs bound every delivery path at 27.9 kJ or more, above every need.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
