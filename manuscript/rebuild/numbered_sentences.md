# Every numbered sentence of the rebuilt manuscript, with its sources (20 November 2026)

Written by `src/make_rebuild_sentences.py` from the numbers check's trace (`numbers_trace.json`). Each sentence is followed by its numbers, the file and value each is read from, and "new" where the manuscript as submitted on 17 November 2026 does not state that number. Sentences are as the check reads them, with LaTeX spacing marks (~ is a space).
165 numbered sentences; 104 of them carry a number the submitted manuscript does not state (323 numbers in all).



## main.tex: abstract

1. Fitted to peak temperatures, failing-cell energies are 31.6 to 54.3~kJ in fourteen (strong triggers), mostly above calorimetry's 33.2~kJ maximum, and 9.0 and 16.6~kJ in two (weak); conduction and radiation run no resolved neighbour away at either energy.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
2. Over 21.4~s, the two published records' mean rise time, 4.45 to 7.54~kJ through the facing side runs the resolved neighbour away by the eight propagating strong-trigger tests' measured times (two at its threshold, the least that runs it away at all), and 0.26 to 5.96~kJ the lumped one.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
3. The resolved threshold is at least 1.36 times the lumped one after four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs, so here a heat share calibrated with either may need a trigger-dependent correction for the other.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
4. Published inputs rule out no path delivering 27.9~kJ within 21.4~s; a facing-side heat flux could test the needs.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## main.tex: Introduction to Discussion, with figure captions

5. Calorimetry shows why the vent matters: fractional thermal runaway calorimetry of 18650 cells finds that typically 20 to 30\,\% of the total energy leaves through the casing and the rest with the ejecta~ , the Battery Failure Databank holds such measurements for the LG M50 among many cells~ , and burning vent gas can add to them in open air~ .
   - 20: manuscript/data/comparators.csv: value where {'key': 'walker2019decoupling', 'quantity': 'share of the total energy released through the casing, low'} = 20
   - 30: manuscript/data/comparators.csv: value where {'key': 'walker2019decoupling', 'quantity': 'share of the total energy released through the casing, high'} = 30
6. Nine propagated, 147 to 342~s after the trigger's runaway.
   - 147: smallest and largest of inputs/fransson2024/m50_tests.csv: time_to_propagation_s = 147
   - 342: smallest and largest of inputs/fransson2024/m50_tests.csv: time_to_propagation_s = 342
7. The neighbours of five of the seven tests that did not propagate peaked at 71 to 133\degC; the other two, 626 and 808\degC, which the paper's note on thermocouples that moved during failure may explain, are treated as exploratory.
   - 71: smallest and largest of inputs/fransson2024/m50_tests.csv: neighbour_max_C of the tests that did not propagate, without the two exploratory maxima = 71
   - 133: smallest and largest of inputs/fransson2024/m50_tests.csv: neighbour_max_C of the tests that did not propagate, without the two exploratory maxima = 133
   - 626: inputs/fransson2024/m50_tests.csv: neighbour_max_C where {'propagated': 'No'} = 626
   - 808: inputs/fransson2024/m50_tests.csv: neighbour_max_C where {'propagated': 'No'} = 808
8. The failing cell, the trigger, is one temperature that releases its body energy $E_\mathrm{b}$ inside itself as a triangular pulse over 21.39~s, the mean of the trigger's rise times derived from the two records of Fransson et al.'s supplementary Figure~10 (17.53 and 25.24~s; Supplementary Section~S7).
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 17.53: results/stage7_paper_numbers.json: triggers.levels.tau_s[0] = 17.5332
   - 25.24: results/stage7_paper_numbers.json: triggers.levels.tau_s[2] = 25.2399
9. Each test has its own trigger: the $E_\mathrm{b}$ that puts the model's trigger at the test's measured trigger peak at the central contact (below), 9.0 to 54.3~kJ (Table~ ).
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
10. Thirteen of these exceed 33.2~kJ, the largest body energy the Battery Failure Databank measured in the ten nail tests of this cell~ , perhaps because the trigger's flame heats the thermocouple the energy is matched to, and two lie below its smallest, 18.7~kJ; the eight largest are therefore also run without delivered heat with the body energy held to 33.2~kJ (Section~ ).
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 18.7 (new): results/stage14_inputs.csv: range_lo where {'key': 'db_Ebody_max'} = 18.6715
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
11. A trigger whose fitted body energy is 31.6 to 54.3~kJ is called strong here, and the two of 9.0 and 16.6~kJ weak.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
12. The Databank's median energy carried by this cell's ejecta is 76.74~kJ and its largest 89.34~kJ; each test's ejected energy is taken as 3.105 times its fitted body energy, the Databank's median ratio for this cell, and sets only the searches' grids.
   - 76.74: results/stage14_inputs.csv: value where {'key': 'db_Eej_median'} = 76.7412
   - 89.34 (new): results/stage14_inputs.csv: value where {'key': 'db_Eej_max'} = 89.3378
   - 3.105: results/stage8_ejected.csv: ratio_central where {'id': 'M50_PT_Exp1'} = 3.10529
13. The lumped neighbour is one temperature $T$: [display] where $T_1$ is the trigger's temperature, $C=61.75$~J\,K$^{-1}$ the cell's heat capacity and $m$ its mass, $G_c$ the conductance of the contact and its air wedge integrated over the can, $G_t$ that of the welded tabs, $F$ the view factor between the cans, $\varepsilon$ their emissivity and $A_\ell$ the lateral area, $h_a$, $A_a$ and $A_r$ the room's convection coefficient and the areas that convect and radiate to the room at $T_a=25$\degC{} (both cells start at it), $\dot q_r$ the reaction heat per unit mass (Section~ ) and $P(t)$ the delivered heat (Section~ ).
   - 61.75: results/manuscript_numbers.json: constants.C_cell_J_K = 61.75
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
14. The resolved neighbour is a three-dimensional half model, symmetric about the plane through both axes, of linear tetrahedral finite elements on 19,355 nodes: an anisotropic roll inside a 0.25~mm steel can, [display] with the conductivity $\mathbf{k}$ 1.3~W\,m$^{-1}$\,K$^{-1}$ across the layers and 25~W\,m$^{-1}$\,K$^{-1}$ along them and the same total heat capacity.
   - 19,355: results/stage8_paper_numbers.json: v3.base.n_nodes = 19355
   - 0.25: results/manuscript_numbers.json: constants.can_thickness_mm = 0.25
   - 1.3: results/manuscript_numbers.json: constants.k_radial_W_mK = 1.3
   - 25: results/manuscript_numbers.json: constants.k_axial_W_mK = 25
15. On the can, within 45\textdegree{} of the line of contact the heat flux to the trigger is $h(\theta)(T-T_1)$ with [display] a steel-on-steel contact conductance $h_c$ in series with the air in the wedge of width $\delta$ at angle $\theta$ from the line of contact, $a=10.55$~mm being the cell's radius; $h_c$ is 2,000 or 3,700~W\,m$^{-2}$\,K$^{-1}$ for the central and high contact, the two ends of a textbook's range for stainless steel on stainless steel in air, and 200~W\,m$^{-2}$\,K$^{-1}$ for the low contact, its lowest value with the gap evacuated~ , since no conductance between cylindrical cells in contact was found.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
   - 10.55 (new): results/manuscript_numbers.json: constants.cell_radius_mm = 10.55
   - 2,000: results/manuscript_numbers.json: constants.h_contact_W_m2K.central = 2000
   - 3,700: results/manuscript_numbers.json: constants.h_contact_W_m2K.high = 3700
   - 200: results/manuscript_numbers.json: constants.h_contact_W_m2K.low = 200
16. The sector, 45\textdegree{} either side, is the earlier two-cell study's~ , an assumption (Table~ ); beyond the sector the can loses heat to the room by convection; everywhere it radiates to the room and receives the trigger's radiation shared over $\theta$ by the local view factor.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
17. Three criteria read the neighbour's runaway, each at 255.7\degC, the lower edge of the internal-short band of the kinetic source~ , within 900~s of the trigger's release, a window chosen here (Fig.~ b); the level lies above the ignition temperature of Section~ , past which a lumped neighbour's reaction heat outruns its losses, while a hottest point that reaches it need not run the cell away.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
18. (a) The pair at mid-length: the trigger is one temperature; the neighbour is solved as one temperature and as a resolved half model, symmetric about the dash-dotted plane; heat is delivered through the half of its can that faces the trigger; within 45\textdegree{} of the line of contact the cans exchange heat through the contact and its air wedge.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
19. The model's five surface probes are mesh nodes at mid-length, at 0, 0.33, 88.3, 94.4 and 180\textdegree{} from the line of contact: the nodes on the line and next to it, the two either side of 90\textdegree{} and the far face; three are drawn (on the line of contact, on the side and on the far face), and they span the possible angles of the measured thermocouple, which the tests do not report.
   - 0: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 0.325853
   - 0.33: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 0.325853
   - 88.3: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 88.2771
   - 94.4 (new): src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 94.392
   - 180: src/stage10_inputs.py: NODES and EXTRA_PROBES, theta_deg of the five probes = 180
   - 90: DECISIONS.md: /the node nearest (90) degrees from the line/ = 90
20. (b) One run, PT-Exp4 with 7.4~kJ delivered over 21.4~s: the resolved neighbour's hottest point reaches 255.7\degC{} at 8~s, the lumped neighbour at 107~s and the resolved neighbour's mean at 182~s.}
   - 7.4 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: E_J = 7.41562
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 8: results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: C1_t_s = 8.27672
   - 107: results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: lumped_C2_t_s = 106.51
   - 182 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
21. Reaction $j$ runs at $r_j=\exp\!\big(\sum_s n_{sj}\ln c_s+\ln A_j+b_j\ln T-E_{a,j}/(RT)\big)$, its species change as $\mathrm{d}c_s/\mathrm{d}t=\sum_j\nu_{sj}r_j$, and its heat enters per unit cell mass as $\dot q_r=\sum_j\Delta H_j r_j m_j/M_\mathrm{ref}$, with $M_\mathrm{ref}$ the mass of the source's 720~g reference cell and $m_j$ its reactant masses.
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
22. The model is the mean of each parameter over the source's posterior particles; in an emulation of the accelerating-rate calorimetry that the source simulated for its 720~g reference cell (Supplementary Section~S2) it gives an exotherm onset of 179.3\degC, inside the source's band of two standard deviations about its main cluster's mean, 169.0 to 198.0\degC, but reaches the source's internal-short rate, 1~K\,min$^{-1}$ of self-heating, at 199.8\degC, below that event's band of 255.7 to 302.1\degC, a difference not resolved here.
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
   - 179.3: results/note_numbers.json: V1.T_in_C = 179.252
   - 169.0: DECISIONS.md: /main-cluster mean, (169\.0) to 198\.0/ = 169
   - 198.0: DECISIONS.md: /main-cluster mean, 169\.0 to (198\.0)/ = 198
   - 1: DECISIONS.md: /T_on at the paper's stated trigger \((1) C/min\)/ = 1
   - 199.8: results/note_numbers.json: V1.T_on_1_C_per_min_C = 199.794
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 302.1: DECISIONS.md: /below the paper's band of 255\.7 to (302\.1)/ = 302.1
23. Of the 200 posterior draws described below, the 164 whose emulated test reaches the internal-short rate within 4,000~min, the source's main cluster, give an exotherm onset of 146.3 to 191.4\degC{} (central 95\,\%); the check recorded for the draws against the source's band failed, and passed only as amended after the failure (Supplementary Section~S2).
   - 200: results/stage3_v4.json: n_draws = 200
   - 164: results/stage3_v4.json: main_cluster_T_in_C.n = 164
   - 4,000 (new): DECISIONS.md: /no later than (4000) min after the test starts is in the main cluster/ = 4000
   - 146.3 (new): results/stage3_numbers.json: V4_registered/T_in_p2.5_C = 146.3
   - 191.4 (new): results/stage3_numbers.json: V4_registered/T_in_p97.5_C = 191.4
   - 95: predictions_stage13.md: /the central (95) % of the 200 draws/ = 95
24. The posterior enters as 200 joint draws, each taking one posterior particle of each of the three submodels (anode and electrolyte, cathode, separator), which treats them as independent.
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
25. Its shape in time is a triangular pulse over 21.39~s from the start of the trigger's release, rising to its peak at half its length, a constant power over 120, 240 or 360~s, spanning the measured times, or, in one test, a pulse followed by a constant power.
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 120: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 120
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 360
26. For a test that propagated, its need is the least energy with which a criterion is met within 10~s of the measured time, counted as delivered by the time it is met.
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
27. Where the least energy run that meets the criterion meets it before the measured time and the next lower run, 0.5\,\% of the test's ejected energy below, does not meet it, no run reproduces the measured time, and the need is the higher, the threshold to within that resolution, counted to the time it is met (marked t in Supplementary Tables S3 and S7; b marks one interpolated between two runs bracketing the measured time).
   - 0.5: results/stage15_cross_section.json: settings.width_ft = 0.5
28. In three dimensions a need is bracketed instead, between the highest energy run whose mean reaches 255.7\degC{} more than 10~s after the measured time, or not within 900~s, and the lowest whose mean reaches it no later, the two at most 0.125\,\% of the test's ejected energy apart, counted to 10~s after the measured time (Supplementary Section~S17).
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 10: src/stage16_run.py: /WINDOW_S = ([0-9.]+)/ = 10
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 0.125 (new): src/stage16_run.py: /FINAL_FRAC = ([0-9.]+)/ = 0.125
   - 10: src/stage16_run.py: /WINDOW_S = ([0-9.]+)/ = 10
29. For a test that did not propagate, the need is the energy at which the far face peaks at the measured maximum (within 5~K).
   - 5: predictions_stage9.md: /within (5) K of it/ = 5
30. The two-body model runs the trigger and the lumped neighbour without reaction and asks when the neighbour reaches $T_\mathrm{ign}$ with enough heat of the low-temperature cathode reaction left to reach 255.7\degC.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
31. For each path by which the trigger's ejecta or its circuit can heat the facing half, an upper bound was set on the energy delivered within the pulse's 21.4~s and in total, every lower bound being zero, from published inputs alone, each read at its source and labelled as measured on this cell or on another (Table~ ; the inputs in Supplementary Table~S5).
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
32. The study registered 109 predictions in all, of which 65 held and 44 failed (Supplementary Table~S1, step by step); Supplementary Table~S2 lists, with their expectations, the 63 that the runs reported here and in the supplement bear on, and every prediction, with its file and its verdict, is in the public archive at doi:10.5281/zenodo.23279455~ .
   - 109: manuscript/rebuild/data/predictions_registry.csv: rows = 109
   - 65: manuscript/rebuild/data/predictions_registry.csv: rows with verdict held = 65
   - 44 (new): manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed = 44
   - 63 (new): manuscript/rebuild/data/predictions_registry.csv: rows, listed in Table S2 = 63
33. Of the 63, 43 held, seven of them known beforehand to be fixed, or nearly, by earlier records or by construction, and 20 failed, seven of them foreseen, three in the files' analyses and four in their expectations; two departures from this order are in Supplementary Section~S2.
   - 20: manuscript/rebuild/data/predictions_registry.csv: rows with verdict failed, listed in Table S2 = 20
34. The per-test triggers (step~7), the delivered heat (step~8) and the reading of the resolved neighbour as a whole (step~15) entered after earlier predictions failed, and the needs in three dimensions (step~16) last, each registered before its runs.
   - 7: manuscript/rebuild/data/steps.csv: the step of predictions_stage7.md (the per-test triggers) = 7
   - 8: manuscript/rebuild/data/steps.csv: the step of predictions_stage8.md (the delivered fraction) = 8
   - 15: manuscript/rebuild/data/steps.csv: the step of predictions_stage15.md (the resolved neighbour's own runaway) = 15
   - 16: manuscript/rebuild/data/steps.csv: the step of predictions_stage16.md = 16
35. Halving the mesh spacing and every step limit moved the hottest point's peak rise by at most 0.52\,\%; at both ends of PT-Exp4's threshold search's bracket, refining the mesh by a factor of 1.5 and halving every step limit left the outcome unchanged and moved the runaway time by at most 1.5\,\%, and at both ends of PP-Exp4's need, refining both together delayed the runaway by 1.1 and 2.7\,\% and left the need's bracket unchanged.
   - 0.52: results/stage8_paper_numbers.json: checks.V3.v3mesh.relative_change = 0.515385
   - 1.5: predictions_stage15.md: /the mesh refined by (1\.5)/ = 1.5
   - 1.5: results/stage15_checks.json: V4/s15_B1_PT_Exp4_s+1_r1.5/rel_change = 1.48397
   - 1.1 (new): results/stage16_scorecard.json: V, C8_change of the upper and lower end (rel) = 1.1163
   - 2.7 (new): results/stage16_scorecard.json: V, C8_change of the upper and lower end (rel) = 2.69017
36. With body energies up to 33.2~kJ and the cans in contact, conduction and radiation take neither neighbour to 255.7\degC{} within 900~s in any of 5,248 runs over the brackets of contact, tab conductance, the trigger's release (over 10 or 30~s, the earlier study's two) and connection and under the 200 kinetic draws (Supplementary Section~S2): the hottest point peaks at most at 226.7\degC, 29.0~K short, and the lumped neighbour at 180.6\degC.
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
38. Held to 33.2~kJ, those eight tests, whose inputs then differ only in their connection, ignite neither neighbour: the hottest point peaks at 191.9 and 192.2\degC{} at the central contact and at 226.4 and 226.7\degC{} at the high contact, and the lumped neighbour at most at 177.4\degC.
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 191.9: results/stage12_paper_numbers.json: part_a.central.hot_spot_peak_C[0] = 191.9
   - 192.2: results/stage12_paper_numbers.json: part_a.central.hot_spot_peak_C[1] = 192.16
   - 226.4: results/stage12_paper_numbers.json: part_a.high.hot_spot_peak_C[0] = 226.39
   - 226.7: results/stage12_paper_numbers.json: part_a.high.hot_spot_peak_C[1] = 226.69
   - 177.4: results/stage12_paper_numbers.json: part_a.high.lumped_peak_C[1] = 177.4
39. Even with the fitted triggers and no delivery, the resolved neighbour as a whole runs away in no test at any contact (Supplementary Table~S15), while nine tests propagated in the rig: at the low contact its hottest point peaks at most at 162.6\degC, and at the high contact ten of the outcomes rest on the reactive cross-section alone, whose mean peaks there at most at 199.2\degC{} and which was checked only at the central contact (Section~ ).
   - 162.6 (new): results/stage7_crossings.csv: hot_peak_C, the largest of the per-test runs at the low contact = 162.614
   - 199.2 (new): smallest and largest of results/stage15_nodelivery.csv: mean_peak_xs_C, high contact, outcome from the cross-section = 199.206
40. Within this model, then, heat beyond what the trigger's body conducts and radiates must reach the neighbour: for all three readings under every kinetic draw with the body energy no larger than calorimetry measured and released over 10 or 30~s, and for the resolved reading under the posterior mean with the fitted triggers.
   - 10: manuscript/data/parameters.csv: /Release durations, Stage 5",tau,(10) and 30/ = 10
   - 30: manuscript/data/parameters.csv: /Release durations, Stage 5",tau,10 and (30)/ = 30
41. With the 21.4~s pulse the lumped neighbour runs away at the measured time with 0.26 to 5.96~kJ in seven propagated tests, and at its threshold in two (PT-Exp4, 4.66 to 4.85~kJ; ST-Exp3, 11.95 to 12.11~kJ); leaving out ST-Exp3's, after its weak trigger, the largest, 5.96~kJ in PP-Exp2, is about 23 times the smallest, 0.26~kJ in SP-Exp3.
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
42. Of the five tests that did not propagate and report low maxima, four need none, since with no delivery the far face already peaks 13.8 to 56.3~K above their maxima at the central contact, and PT-Exp1 needs 2.09~kJ.
   - 13.8: smallest and largest of results/stage9_paper_numbers.json: part_a.A3: overshoot_K = 13.7556
   - 56.3: smallest and largest of results/stage9_paper_numbers.json: part_a.A3: overshoot_K = 56.3217
   - 2.09: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp1'} = 2.0907
43. In the held-out test (Section~ ) none of the three quantities predicts the outcomes better than one probability for every test by the registered margin of 0.1 in the mean log score (the largest gain is 0.062; Supplementary Table~S9), and both thresholds fall as the trigger's fitted energy rises (Table~ and Supplementary Table~S3), so that much of what they carry may be the trigger's energy.
   - 0.1: predictions_stage10.md: /by more than (0\.1) in the mean log score/ = 0.1
   - 0.062: results/stage10_paper_numbers.json: part_c.largest_d_log = 0.0624263
44. After the eight strong triggers among the tests that propagated, the three-dimensional resolved neighbour needs 4.45 to 7.54~kJ with the pulse for its mean to reach 255.7\degC{} by 10~s after the measured time, more than the lumped neighbour in each test, by 1.46 to 4.33~kJ across the brackets, and most in proportion in SP-Exp3 (4.45 to 4.58 against 0.26~kJ).
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 10: src/stage16_run.py: /WINDOW_S = ([0-9.]+)/ = 10
   - 1.46 (new): results/stage16_scorecard.json N against results/stage15_table.csv C2_E_by_t_J: the smallest lower end and the largest upper end of the resolved need less the lumped need, rounded outward (rebuild_headline.differences_kJ) = 1.46
   - 4.33 (new): results/stage16_scorecard.json N against results/stage15_table.csv C2_E_by_t_J: the smallest lower end and the largest upper end of the resolved need less the lumped need, rounded outward (rebuild_headline.differences_kJ) = 4.33
   - 4.45 (new): results/stage16_scorecard.json: N, SP_Exp3, lo_J = 4.45052
   - 4.58 (new): results/stage16_scorecard.json: N, SP_Exp3, hi_J = 4.58171
   - 0.26: results/stage15_table.csv: C2_E_by_t_J where {'test': 'M50_SP_Exp3', 'delivery': '21.39 s pulse'} = 0.2635
45. In PT-Exp4 and ST-Exp4 no run reproduces the measured time: the bracket's lower end does not run away within 900~s and its upper end runs away at 250.8 and 254.6~s, against the measured 272 and 342~s, so these two needs are their thresholds.
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 250.8 (new): results/stage16_scorecard.json: N, PT_Exp4, hi_t_C8_s = 250.784
   - 254.6 (new): results/stage16_scorecard.json: N, ST_Exp4, hi_t_C8_s = 254.647
   - 272: inputs/fransson2024/m50_tests.csv: time_to_propagation_s where {'test': 'M50_PT_Exp4'} = 272
   - 342: inputs/fransson2024/m50_tests.csv: time_to_propagation_s where {'test': 'M50_ST_Exp4'} = 342
46. These needs are 5.8 to 9.8\,\% of the Databank's median energy of this cell's ejecta, 76.74~kJ~ , and the lumped needs 0.3 to 7.8\,\%.
   - 5.8 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end, over results/stage14_inputs.csv db_Eej_median = 5.79938
   - 9.8 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end, over results/stage14_inputs.csv db_Eej_median = 9.82013
   - 76.74: results/stage14_inputs.csv: value where {'key': 'db_Eej_median'} = 76.7412
   - 0.3: smallest and largest of results/stage15_table.csv: C2_E_by_t_J, the eight strong-trigger needs with the pulse, over results/stage14_inputs.csv db_Eej_median = 0.343362
   - 7.8 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J, the eight strong-trigger needs with the pulse, over results/stage14_inputs.csv db_Eej_median = 7.76949
47. The reactive cross-section supplies the needs under the other delivery shapes (Fig.~ ; Supplementary Table~S7): 4.1 to 8.1~kJ, delivered by its runaway, under each of the four shapes, where the lumped neighbour needs 0.2 to 6.0~kJ in the same thirty-two cases; in seven of them the cross-section's need is its threshold, no energy on its grid reproducing the measured time.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 8.11583
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 5.9624
48. After ST-Exp3's weak trigger the cross-section needs 10.3 to 13.8~kJ under three of the shapes, no energy on its grid bringing the runaway early enough with the 360~s delivery, and the lumped neighbour 11.5 to 12.3~kJ under all four.
   - 10.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 10.3125
   - 13.8: smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 13.8435
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_ST_Exp3'} = 360
   - 11.5: smallest and largest of results/stage15_table.csv: ST_Exp3, C2_E_by_t_J = 11.4655
   - 12.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C2_E_by_t_J = 12.2592
49. With constant power, three-dimensional searches bracketed the needs over 240~s in all eight tests and over 120~s in six (Table~ ): 3.88 to 7.67~kJ delivered by 10~s after the measured time, above the lumped need in each; SP-Exp3's over 240~s, 3.88 to 4.01~kJ, is below the least the cross-section gives under any shape.
   - 240: src/stage16_run.py: X_SHAPES, the constant-power durations X searched (s) = 240
   - 120: src/stage16_run.py: X_SHAPES, the constant-power durations X searched (s) = 120
   - 3.88 (new): results/stage16_scorecard.json: X, the closed searches' smallest lower end and largest upper end by the runaway (lo_by_t_J, hi_by_t_J) = 3.87617
   - 7.67 (new): results/stage16_scorecard.json: X, the closed searches' smallest lower end and largest upper end by the runaway (lo_by_t_J, hi_by_t_J) = 7.67168
   - 10: src/stage16_run.py: /WINDOW_S = ([0-9.]+)/ = 10
   - 240: src/stage16_run.py: X_SHAPES, the constant-power durations X searched (s) = 240
   - 3.88 (new): results/stage16_scorecard.json: X, SP_Exp3 over 240 s, lo_by_t_J and hi_by_t_J = 3.87617
   - 4.01 (new): results/stage16_scorecard.json: X, SP_Exp3 over 240 s, lo_by_t_J and hi_by_t_J = 4.00606
50. (a) For the nine tests that propagated, in order of the measured time: the energy delivered to the facing half by the time at which the lumped neighbour (blue) or the resolved neighbour's mean (green; hollow, reactive cross-section; filled, the three-dimensional bracket's midpoint, after strong triggers, where searched) reaches 255.7\degC, within 10~s of the measured time (by 10~s after it in three dimensions), for the four delivery shapes; where no energy on the search's grid reproduces the measured time, the least whose runaway comes before it is shown, the threshold to within the search's resolution, which can lie above the threshold of Fig.~ by up to that resolution (a dot inside the marker; t in Supplementary Table~S7), and a dash marks a need interpolated between two runs (b in Table~S7); in ST-Exp3 with the 360~s delivery no energy on the grid brings the resolved runaway within 10~s of the measured time.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
   - 360: results/stage15_table.csv: tau_s where {'test': 'M50_ST_Exp3'} = 360
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
51. The reactive cross-section's runaway came 5.5~s earlier to 34.5~s later than the three-dimensional model's in the runs of Section~ , more than the 10~s of a match.
   - 5.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.min, negated = 5.48377
   - 34.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.max = 34.5232
   - 10: predictions_stage9.md: /crossing lies within (10) s of the measured time/ = 10
52. (b) For the seven tests that did not propagate: the energy delivered over 21.4~s that puts the far face's peak at the measured maximum; hollow, the two maxima that may not be the neighbour's surface, which the far face reaches only where the model's neighbour runs away; at the bottom, tests whose far face exceeds the maximum with no delivery.}
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
53. With the 21.4~s pulse the three criteria have different thresholds (Fig.~ ; Supplementary Table~S3), except that in PP-Exp1 and SP-Exp3 the local and lumped are both zero.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
54. The local threshold is zero in the eight tests whose fitted trigger alone carries the hottest point over 255.7\degC, and at most 4.53~kJ (PT-Exp1).
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 4.53 (new): results/stage14_needs.csv: threshold_C1_hi_J where {'test': 'M50_PT_Exp1'} = 4.5298
55. The lumped threshold is zero in two tests and at most 12.89~kJ (PT-Exp1).
   - 12.89 (new): results/stage14_needs.csv: threshold_C2_hi_J where {'test': 'M50_PT_Exp1'} = 12.8924
56. By the reactive cross-section, the resolved threshold is 3.5 to 10.8~kJ in all sixteen tests: above the lumped threshold's bracket in thirteen of the fourteen with strong triggers, including 4.5 and 3.5~kJ in the two where the lumped threshold is zero, above its midpoint in the fourteenth, PT-Exp3, whose two brackets overlap, and below it in the two with weak triggers.
   - 3.5: smallest and largest of results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J = 3.52778
   - 10.8 (new): smallest and largest of results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J = 10.7812
   - 4.5 (new): results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J of the two tests whose lumped neighbour needs no delivery = 4.54167
   - 3.5: results/stage15_cross_section.json: A2, the 21.39 s pulse, E_star_J of the two tests whose lumped neighbour needs no delivery = 3.52778
57. The threshold searches opened 5\,\% either side of the cross-section's value, so that a bracket closed by its first two runs, as in PT-Exp4, PP-Exp2, ST-Exp3 and PT-Exp1, has that value as its midpoint.
   - 5: predictions_stage15.md: /less (5) % and plus 5 %/ = 5
58. The resolved threshold lies between 6.51 and 7.20~kJ in PP-Exp2 and between 7.06 and 7.15~kJ in PT-Exp4, where the need's runs, read after them, narrowed the threshold search's 6.71 to 7.42~kJ, 1.36 to 2.27 and 1.45 to 1.54 times the lumped thresholds across the brackets (3.18 to 4.77 and 4.66 to 4.85~kJ), rounded outward, so the order holds at either end.
   - 6.51 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.lo_J = 6.51146
   - 7.20 (new): results/stage15_paper_numbers.json: B1.M50_PP_Exp2.bracket.hi_J = 7.19687
   - 7.06 (new): rebuild_headline.thresholds_3d: PT_Exp4 (B1 narrowed by N) = 7.0625
   - 7.15 (new): rebuild_headline.thresholds_3d: PT_Exp4 (B1 narrowed by N) = 7.15078
   - 6.71 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.lo_J = 6.70937
   - 7.42 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 2.27 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the upper end rounded up = 2.27
   - 1.45 (new): rebuild_headline.threshold_ratio_spans: PT_Exp4, rounded outward = 1.45
   - 1.54 (new): rebuild_headline.threshold_ratio_spans: PT_Exp4, rounded outward = 1.54
   - 3.18 (new): results/stage14_needs.csv: threshold_C2_lo_J where {'test': 'M50_PP_Exp2'} = 3.18
   - 4.77 (new): results/stage14_needs.csv: threshold_C2_hi_J where {'test': 'M50_PP_Exp2'} = 4.77
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 4.85: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_PT_Exp4'} = 4.851
59. In ST-Exp4 the two runs that bracket the need bracket the threshold too, between 5.32 and 5.51~kJ, at least 2.80 times the lumped threshold, which is at most 1.89~kJ (a reading made after the runs).
   - 5.32 (new): rebuild_headline.thresholds_3d: ST_Exp4 (N) = 5.31889
   - 5.51 (new): rebuild_headline.thresholds_3d: ST_Exp4 (N) = 5.50833
   - 2.80 (new): rebuild_headline.strong_unbounded_lower: ST_Exp4 = 2.8
   - 1.89 (new): results/stage14_needs.csv by rebuild_brackets: ST_Exp4's lumped bracket, upper end = 1.8944
60. In SP-Exp3 it lies between 3.70 and 4.06~kJ, while the lumped neighbour runs away with no delivery.
   - 3.70 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.lo_J = 3.70417
   - 4.06 (new): results/stage15_paper_numbers.json: B1.M50_SP_Exp3.bracket.hi_J = 4.05694
61. After ST-Exp3's weak trigger (16.6~kJ) the resolved threshold lies between 9.77 and 10.80~kJ, 0.80 to 0.91 times the lumped 11.95 to 12.11~kJ, and at 10.80~kJ the resolved neighbour runs away at 61.5~s while the lumped neighbour does not; after PT-Exp1's (9.0~kJ), searched in step~16, it lies between 10.24 and 11.32~kJ, 0.79 to 0.89 times the lumped 12.85 to 12.89~kJ (0.84 by the midpoints, inside the 0.75 to 0.95 registered for it), and at 11.32~kJ the resolved neighbour runs away at 45.8~s while the lumped neighbour peaks at 204.2\degC.
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
   - 9.77 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.lo_J = 9.76719
   - 10.80 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.hi_J = 10.7953
   - 0.80 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, rounded outward = 0.8
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, rounded outward = 0.91
   - 11.95: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_ST_Exp3'} = 11.95
   - 12.11: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_ST_Exp3'} = 12.1115
   - 10.80 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3.bracket.hi_J = 10.7953
   - 61.5 (new): results/stage15_paper_numbers.json: B1.M50_ST_Exp3, the run at the bracket's upper end: t_C8_s = 61.5222
   - 9.0: results/stage7_triggers.csv: E_J of PT_Exp1 = 8.97677
   - 10.24 (new): results/stage16_scorecard.json: T, lo_J and hi_J = 10.2422
   - 11.32 (new): results/stage16_scorecard.json: T, lo_J and hi_J = 11.3203
   - 0.79 (new): results/stage16_scorecard.json: T, ratio_lo rounded down and ratio_hi rounded up = 0.79
   - 0.89 (new): results/stage16_scorecard.json: T, ratio_lo rounded down and ratio_hi rounded up = 0.89
   - 12.85 (new): results/stage16_scorecard.json: T, lumped_bracket_J = 12.8488
   - 12.89 (new): results/stage16_scorecard.json: T, lumped_bracket_J = 12.8924
   - 0.84 (new): results/stage16_scorecard.json: T.ratio_mid = 0.837664
   - 0.75: predictions_stage16.md: /holds if (0\.75) <= R <= 0\.95/ = 0.75
   - 0.95 (new): predictions_stage16.md: /holds if 0\.75 <= R <= (0\.95)/ = 0.95
   - 11.32 (new): results/stage16_scorecard.json: T, lo_J and hi_J = 11.3203
   - 45.8 (new): results/stage16_scorecard.json: T.t_C8_hi_s = 45.7863
   - 204.2 (new): results/stage16_runs.csv: s16_T_PT_Exp1_s+1, lumped_peak_C = 204.178
62. \caption{The thresholds of the sixteen tests with the 21.4~s pulse at the central contact, in order of the trigger's fitted body energy (top axis): the least energy delivered to the facing half at which the resolved neighbour's hottest point (triangles), the lumped neighbour (squares) and the resolved neighbour's mean (circles, reactive cross-section; diamonds, three-dimensional model, where bracketed: by threshold searches, and in ST-Exp4, and more narrowly in PT-Exp4, by the runs that bracket the need) reach 255.7\degC.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
63. Up to pulses of 120~s, in the three tests searched, the local threshold agrees with conduction alone (Fig.~ a; Supplementary Table~S8): searches started at the cross-section conduction model's value with a step of 3\,\% (PT-Exp1 at 5, 40 and 120~s, ST-Exp3 and PT-Exp3 at 10 and 60~s) end within one step of it, the skin model agreeing for the two shortest pulses, at Fourier numbers $\alpha\tau/a^2$ of 0.025 to 0.60 ($\alpha$ the roll's diffusivity across its layers, $\tau$ the pulse's duration, $a$ the cell's radius; ); with the reaction switched off at the upper end of each such search, the hottest point still reaches 255.7\degC{} or falls short by at most 1.1~K.
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 3: src/stage13_inputs.py: /FIRST_STEP = (0\.03)/ = 3
   - 5: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 5
   - 40: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 40
   - 120: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 120
   - 10: results/stage13_skin.csv: tau_d_s where {'test': 'M50_ST_Exp3', 'region': 'half'} = 10
   - 60: results/stage13_skin.csv: tau_d_s where {'test': 'M50_ST_Exp3', 'region': 'half'} = 60
   - 0.025: results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '5.0'} = 0.0250038
   - 0.60 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '120.0'} = 0.600091
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 1.1 (new): results/stage13_skin.csv: the largest shortfall of inert_peak_minus_level_K up to a Fourier number of 0.6 = 1.13572
64. Over 360~s (Fourier number 1.80), in PT-Exp1, the threshold falls below the conduction model, the crossing coming at 316.5~s on the cell's axis with the mean at 240.1\degC, as if the cell had heated through.
   - 360: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 360
   - 1.80 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 1.80027
   - 316.5 (new): results/stage13_skin.csv: res_t_cross_hi_s where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 316.544
   - 240.1 (new): results/stage13_skin.csv: res_mean_at_cross_hi_C where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 240.119
65. PT-Exp1's ratio of lumped to local threshold falls from 2.90 at a Fourier number of 0.11 to 1.16 at 0.60 and 0.94 at 1.80.
   - 2.90 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/21.39 = 2.89706
   - 0.11: results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '21.38651984299561'} = 0.106949
   - 1.16 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/120 = 1.15999
   - 0.60 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '120.0'} = 0.600091
   - 0.94 (new): results/stage13_paper_numbers.json: scorecard/P9/ratio/360 = 0.938279
   - 1.80 (new): results/stage13_skin.csv: fourier where {'test': 'M50_PT_Exp1', 'region': 'half', 'tau_d_s': '360.0'} = 1.80027
66. The lumped neighbour's reaction heat, with the separator molten, equals its losses at $T_\mathrm{ign}=218.5$\degC{} with the trigger at the neighbour's own temperature; over the 200 kinetic draws $T_\mathrm{ign}$ runs from 215.3 to 221.4\degC{} (central 95\,\%), and there, with every reactant at its initial amount, the low-temperature cathode reaction gives 73.3\,\% of the reaction heat under the posterior mean.
   - 218.5 (new): results/stage13_paper_numbers.json: scorecard.P7.mean_C = 218.484
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 215.3 (new): results/stage13_paper_numbers.json: scorecard/P7/p2.5_C = 215.257
   - 221.4 (new): results/stage13_paper_numbers.json: scorecard/P7/p97.5_C = 221.395
   - 95: predictions_stage13.md: /the central (95) % of the 200 draws/ = 95
   - 73.3 (new): results/stage13_tign.csv: carrying_share where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 73.3174
67. The two-body model (Section~ ; that reaction's heat is 2,667~J in all) lies within the larger of 10\,\% and 300~J of the lumped threshold in all 32 searches at the low and high contacts registered for it, nine of them with both zero (Supplementary Table~S10), but at the low contact above the bracket's midpoint after every strong trigger, by 0.25 to 0.48~kJ, and below it after the two weak ones (Supplementary Section~S12).
   - 2,667 (new): results/stage13_tign.csv: cat1_heat_total_J where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 2667.2
   - 10: predictions_stage13.md: /within the larger of (10) % and 300 J/ = 10
   - 300 (new): predictions_stage13.md: /within the larger of 10 % and (300) J/ = 300
   - 32: results/stage13_paper_numbers.json: scorecard.P8.n_within = 32
   - 0.25: smallest and largest of results/stage13_twobody.csv: low contact, strong triggers, B2 less the midpoint = 0.249186
   - 0.48 (new): smallest and largest of results/stage13_twobody.csv: low contact, strong triggers, B2 less the midpoint = 0.482264
68. Where the trigger's energy was shifted, the threshold falls by 393 to 456~J for each kJ added (PT-Exp3, ST-Exp2, PP-Exp3), more steeply than the 150 to 300~J per kJ registered beforehand, which failed; the steeper fall is not explained here.
   - 393 (new): smallest and largest of results/stage13_paper_numbers.json: scorecard.P10.cases: slope_J_per_kJ = 393.034
   - 456 (new): smallest and largest of results/stage13_paper_numbers.json: scorecard.P10.cases: slope_J_per_kJ = 456.135
   - 150: predictions_stage13.md: /falls by (150) to 300 J per kJ/ = 150
   - 300 (new): predictions_stage13.md: /falls by 150 to (300) J per kJ/ = 300
69. With no delivery, in PT-Exp4, PP-Exp3 and ST-Exp2 at the central contact, the lumped neighbour has taken in 2.1 to 2.3~kJ more than the resolved one by 250~s through the same conductance, as the resolved cell's contact patch heats toward the trigger's temperature while its mean lags (a post hoc reading).
   - 2.1: smallest and largest of results/stage15_accounts.json: lumped_less_resolved.contact_and_wedge at 250 s = 2.05166
   - 2.3 (new): smallest and largest of results/stage15_accounts.json: lumped_less_resolved.contact_and_wedge at 250 s = 2.30888
   - 250 (new): results/stage15_accounts.json: the accounts' rows at t_s 250 = 250
70. In PT-Exp4 the kinetic draws and a shift of the rate laws test the gap from the resolved side (Fig.~ d) with 5.04~kJ over 21.4~s, the upper end of an earlier bracket on the lumped threshold, 4.66 to 5.04~kJ, that a later search narrowed to 4.66 to 4.85~kJ (Supplementary Section~S4 and Table~S3); with it the lumped neighbour runs away at 215.6~s under the posterior mean.
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 4.85: results/stage14_needs.csv: need_21s_hi_J where {'test': 'M50_PT_Exp4'} = 4.851
   - 215.6 (new): results/stage15_readings.json: 1.PT_Exp4.lumped_cross_s = 215.6
71. The resolved neighbour runs away under none of four kinetic draws, ranked 5, 50, 151 and 196 of 200 by when the hot spot's self-heating starts in a case of step~3, on the earlier study's geometry (Supplementary Sections~S1 and~S2), its mean peaking at 191.2 to 192.4\degC, nor with an aged SEI, its initial amount set to zero (188.3\degC); the lumped neighbour runs away under the first two draws, at 191.0 and 196.5~s, and not under the others.
   - 5: results/stage11_draws.csv: rank of the four kinetic draws = 5
   - 50: results/stage11_draws.csv: rank of the four kinetic draws = 50
   - 151: results/stage11_draws.csv: rank of the four kinetic draws = 151
   - 196: results/stage11_draws.csv: rank of the four kinetic draws = 196
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
   - 191.2 (new): smallest and largest of results/stage15_paper_numbers.json: B4.draws: peak_mean_C = 191.164
   - 192.4: smallest and largest of results/stage15_paper_numbers.json: B4.draws: peak_mean_C = 192.397
   - 188.3 (new): results/stage15_paper_numbers.json: B4.aged.peak_mean_C = 188.294
   - 191.0 (new): results/stage15_paper_numbers.json: B4 draws of rank 5 and 50, lumped_C2_t_s = 191.012
   - 196.5: results/stage15_paper_numbers.json: B4 draws of rank 5 and 50, lumped_C2_t_s = 196.5
72. With every rate law evaluated at the local temperature plus a shift, the resolved neighbour needs more than 17.5~K to run away: at 17.5~K its mean peaks at 221.1\degC, and at 20~K it runs away at 270.3~s.
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
   - 221.1 (new): results/stage15_paper_numbers.json: B4.shift_runs, the run shifted by 17.5 K: peak_mean_C = 221.105
   - 20: results/stage15_paper_numbers.json: B4.shift.least_shift_K = 20
   - 270.3 (new): results/stage15_paper_numbers.json: B4.shift.t_C8_s = 270.338
73. (b) The lumped threshold of three tests with the trigger's fitted body energy (hollow) and shifted by 2~kJ either way (filled), with the fall per kJ.
   - 2: src/stage13_inputs.py: /for d in \(-2000\.0, (2000\.0)\)/ = 2
74. (c) The lumped neighbour's ignition temperature over the 200 kinetic draws.
   - 200: results/stage13_paper_numbers.json: scorecard.P7.n_draws = 200
75. (d) PT-Exp4's resolved neighbour under 5.04~kJ over 21.4~s, with which the lumped neighbour runs away under the posterior mean: the peak of its mean against the shift added to the temperature in every rate law (crosses, no runaway; circle, runaway, at 20~K), and with no shift under the four kinetic draws and the aged SEI (grey), none of which runs it away.}
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 20: results/stage15_paper_numbers.json: B4.shift.least_shift_K = 20
76. PT-Exp4's thermocouple starts at 32.2\degC, against the model's 25\degC, reaches 141.0\degC{} by 45~s and 197.3\degC{} at 271.5~s, where the figure marks the neighbour's jump.
   - 32.2 (new): inputs/fransson2024/pt_exp4_history.csv: T_neighbour_C where {'t_s': '0.0'} = 32.1676
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
   - 141.0: results/stage10_paper_numbers.json: measured.at_45_s_C = 140.997
   - 45: results/stage10_paper_numbers.json: /"at_(45)_s_C"/ = 45
   - 197.3: results/stage10_paper_numbers.json: measured.at_onset_C = 197.254
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
77. With 4.66 and 5.04~kJ over 21.4~s, the ends of the earlier bracket on the lumped threshold, the model's far face lies 16.3 and 16.8~K from the record (the root mean square over 0 to 271.5~s), but the resolved neighbour does not run away: with 5.04~kJ its mean peaks at 190.6\degC{} and cools.
   - 4.66: results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp4'} = 4.6569
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 16.3: results/stage10_paper_numbers.json: part_a.tri21_C2_lo_hcentral.nodes.away.window.rms_K = 16.2554
   - 16.8: results/stage10_paper_numbers.json: part_a.tri21_C2_hi_hcentral.nodes.away.window.rms_K = 16.8348
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 190.6 (new): results/stage15_readings.json: 1.PT_Exp4.mean_peak_C = 190.6
78. At 7.42~kJ, the upper end of its threshold search's bracket, it runs away at 181.9~s, and its far face's jump, by the rule in Fig.~ 's caption, begins at 173~s and 234.1\degC, 36.8~K above the measured 197.3\degC{} and 47.6~K above the record's own jump read by the same rule (Supplementary Section~S7); over 0 to 181.9~s its far face lies 51.4~K from the record.
   - 7.42 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4.bracket.hi_J = 7.41562
   - 181.9 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
   - 173 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: far_jump.t_s = 173
   - 234.1 (new): results/stage15_paper_numbers.json: B3a.run.far_jump.T_C = 234.101
   - 36.8 (new): results/stage15_scorecard.json: scorecard/predictions/P5/above_197.3_K = 36.8008
   - 197.3: results/stage10_paper_numbers.json: measured.at_onset_C = 197.254
   - 47.6: results/stage15_paper_numbers.json: B1 PT_Exp4's upper run, far_jump.T_C, less the record's jump by the same rule (stage15_archive.far_face_jump on inputs/fransson2024/pt_exp4_history.csv from 24.16 s) = 47.563
   - 181.9 (new): results/stage15_paper_numbers.json: B1.M50_PT_Exp4, the run at the bracket's upper end: t_C8_s = 181.923
   - 51.4 (new): results/stage15_paper_numbers.json: B3a.history.rms_K = 51.4421
79. At 7.15~kJ, the upper end of its need's bracket, it runs away at 250.8~s.
   - 7.15 (new): results/stage16_scorecard.json: N, PT_Exp4, hi_J = 7.15078
   - 250.8 (new): results/stage16_scorecard.json: N, PT_Exp4, hi_t_C8_s = 250.784
80. A search for the constant power that after a 5.04~kJ pulse brings the resolved runaway within 10~s of 271.5~s, ended between 10~W (the runaway at 369.3~s) and 12.5~W (at 255.9~s, the far face's jump beginning at 233.6\degC).
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 10: results/stage15_paper_numbers.json: B3b.result.P_lo_W = 10
   - 271.5: results/stage10_paper_numbers.json: measured.onset_figure_s = 271.5
   - 10: results/stage15_paper_numbers.json: B3b.result.P_lo_W = 10
   - 369.3 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold10.0W: t_C8_s = 369.329
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.result.P_hi_W = 12.5
   - 255.9 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: t_C8_s = 255.856
   - 233.6 (new): results/stage15_paper_numbers.json: B3b run s15_B3_PT_Exp4_hold12.5W: far_jump.T_C = 233.595
81. A run of 6.2~kJ at constant power over 240~s, made in the step that compared the model with this history (step~10 of Supplementary Table~S1) and stopped there at 332~s, does not run away when carried on to 900~s, its mean peaking at 241.4\degC: the prediction registered for it, a runaway, failed, while the reactive cross-section's value registered beside it, no runaway with the mean peaking at 220.5\degC, matched the outcome, 20.9~K below that run's peak over 900~s (Supplementary Table~S2).
   - 6.2 (new): results/stage15_paper_numbers.json: B2/0.05/E_J = 6.20922
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 10: results/stage15_cross_section.json: A1_rows, the archived 6,209 J run's id, s10_... = 10
   - 332 (new): results/stage15_cross_section.json: A1_rows, the archived 6,209 J run: t_end_s = 332
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 241.4 (new): results/stage15_paper_numbers.json: B2/0.05/peak_mean_C = 241.354
   - 220.5 (new): predictions_stage15.md: /6,209 J no C8 \(mean peak (220\.5) C\)/ = 220.5
   - 20.9: results/stage15_paper_numbers.json: B2 0.05 peak_mean_C less the reduced model's registered peak (predictions_stage15.md) = 20.8544
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
82. (a) The measured thermocouple (black; Fransson et al.~ , supplementary Figure~10, read from the figure) against the model's far face under five deliveries at the central contact, keyed in the legend below; the circles mark where the measured jump and the model's jumps begin, at the upper end of the resolved threshold search's bracket and with the 12.5~W hold.
   - 12.5 (new): results/stage15_paper_numbers.json: B3b.result.P_hi_W = 12.5
83. (b) The resolved neighbour's mean temperature under the same deliveries: 5.0~kJ over 21.4~s, the upper end of the earlier bracket on the lumped threshold; 6.7 and 7.4~kJ over 21.4~s, the ends of the resolved threshold search's bracket; the 5.0~kJ pulse followed by 12.5~W; and 6.2~kJ over 240~s.
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
88. By estimates from published inputs, what the ejecta can release is at most 225.8~kJ, with the heat of burning their gas taken from another cell, and every path of the ejecta is bounded in total by that alone; the holder's conduction is not determinable, energy conservation alone capping it at 247.3~kJ, all that published inputs let the trigger release (Table~ , Fig.~ ).
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 247.3 (new): results/stage14_corrections.json: E_global_J = 247.333
89. Within 21.4~s, radiation can deliver at most 27.9~kJ, a black body at 1500\degC{} filling the facing half's view (a flame held on the vent's axis would send about 0.38\,\% of its radiation there, about 0.85~kJ of the 225.8~kJ, but no source places the flame); gas beside the neighbour, a breach's jet facing it and solids and melt on it at most 195.5, 225.8 and 225.8~kJ; and the neighbour's own discharge in the parallel tests, from inside, 65.5~kJ.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 0.38 (new): results/stage14_independent_read.md: /gives (0\.003759) \+- 0\.000022 at 0\.85 R/ = 0.3759
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 195.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A2', 'window_s': '21.39'} = 195.516
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 65.5 (new): results/stage14_bounds_corrected.csv: upper_J where {'path': 'A6', 'window_s': '21.39'} = 65.52
90. Within 21.4~s gas, the jet and solids and melt each reach all twelve of the needs with the pulse in Section~ that are not zero, the lumped neighbour's nine and three at the far face, and radiation all but the two exploratory maxima, 32.7 and 75.8~kJ (Supplementary Table~S7).
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 32.7 (new): results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_SP_Exp4'} = 32.667
   - 75.8 (new): results/stage14_needs.csv: need_21s_lo_J where {'test': 'M50_PT_Exp2'} = 75.8149
91. Every delivery of Supplementary Table~S7 with which the resolved neighbour runs away carries 4.1 to 19.5~kJ in all over its shape, below 27.9~kJ, the least bound within 21.4~s of a path through the facing half.
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_J, every delivery with which the cross-section runs away = 4.06435
   - 19.5 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_J, every delivery with which the cross-section runs away = 19.5167
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
92. \caption{What each path can deliver to the neighbour's facing half, from published inputs alone (upper bounds within the pulse's 21.4~s and in total; every lower bound is zero), against what the neighbour models need: the needs by the measured times with the pulse after strong triggers, of the lumped neighbour and of the resolved neighbour in three dimensions (after ST-Exp3's weak trigger the lumped need is 12.1~kJ, left out), and the energy calorimetry measured in this cell's ejecta.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 12.1 (new): results/stage15_table.csv: C2_E_by_t_J where {'test': 'M50_ST_Exp3', 'delivery': '21.39 s pulse'} = 12.111
93. At the central contact, against the 151 three-dimensional runs of the sixteen tests made in earlier steps without a stop at the hottest point's crossing, six of them repeating another's configuration in a different step, carried to 900~s or, in twelve, to 332~s (Supplementary Tables~S11 and~S14), the reactive cross-section gave the same outcome, the mean's runaway or none by the run's end, in all 151 (Fig.~ ).
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
   - 332 (new): results/stage15_cross_section.json: A1_rows, the earliest end of a run = 332
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
94. In the 92 runs in which both run away, 82 of them in the two exploratory tests at deliveries of 15 to 135~kJ, far above any threshold, its runaway comes 1.0~s later on average (5.5~s earlier to 34.5~s later); in the 59 in which neither does, its mean peaks 1.9~K lower on average, from 3.8~K higher to 20.7~K lower, the last in PT-Exp4's run of 6.2~kJ over 240~s against the 241.2\degC{} of the three-dimensional run stopped at 332~s (20.9~K below its peak over 900~s, Section~ ).
   - 92 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.n = 92
   - 82 (new): results/stage15_cross_section.json: A1_rows of PT_Exp2 and SP_Exp4 in which both run away = 82
   - 15: smallest and largest of results/stage15_cross_section.json: A1_rows of PT_Exp2 and SP_Exp4 in which both run away, E_J = 15.3727
   - 135 (new): smallest and largest of results/stage15_cross_section.json: A1_rows of PT_Exp2 and SP_Exp4 in which both run away, E_J = 134.782
   - 1.0: results/stage15_cross_section.json: A1_summary.dt_C8_s.mean = 1.03766
   - 5.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.min = 5.48377
   - 34.5 (new): results/stage15_cross_section.json: A1_summary.dt_C8_s.max = 34.5232
   - 59 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.n = 59
   - 1.9 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.mean = 1.87063
   - 3.8 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.max = 3.80973
   - 20.7 (new): results/stage15_cross_section.json: A1_summary.d_mean_peak_K.min = 20.6721
   - 6.2 (new): results/stage15_paper_numbers.json: B2/0.05/E_J = 6.20922
   - 240: results/stage15_table.csv: tau_s where {'test': 'M50_PT_Exp4'} = 240
   - 241.2 (new): results/stage15_cross_section.json: A1_rows, the archived 6,209 J run over 240 s: mean_peak_3d_C = 241.179
   - 332 (new): results/stage15_cross_section.json: A1_rows, the archived 6,209 J run: t_end_s = 332
   - 20.9: results/stage15_paper_numbers.json: B2 0.05 peak_mean_C less the reduced model's registered peak (predictions_stage15.md) = 20.8544
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
95. A run took 17 to 71~s, against 246 to 512~s for the three-dimensional runs of the same searches, on one two-core machine.
   - 17: smallest and largest of results/stage15_xs/*.json: wall_s = 16.9846
   - 71: smallest and largest of results/stage15_xs/*.json: wall_s = 71.3495
   - 246: smallest and largest of results/stage15_runs/*.json: wall_s of the B1 runs = 245.934
   - 512 (new): smallest and largest of results/stage15_runs/*.json: wall_s of the B1 runs = 512.452
96. At the needs with the pulse, against the three-dimensional searches of step~16 (Table~ ), the cross-section's need, the upper end of its own search's bracket, 0.62 to 0.84~kJ wide, lies 1.5\,\% below to 8.6\,\% above the three-dimensional bracket's midpoint, within the 10\,\% registered, but not above it in every test as registered: at SP-Exp1's cross-section need, 5.96~kJ, the three-dimensional runaway came at 250.6~s against the measured 223~s (Supplementary Table~S2, step~16, P1 and P2).
   - 0.62 (new): results/stage15_cross_section.json: settings.width_ft times results/stage8_ejected.csv: E_e_J, the smallest and the largest over the eight needs of step 16 (results/stage16_scorecard.json: N) = 0.620922
   - 0.84 (new): results/stage15_cross_section.json: settings.width_ft times results/stage8_ejected.csv: E_e_J, the smallest and the largest over the eight needs of step 16 (results/stage16_scorecard.json: N) = 0.843143
   - 1.5: results/stage16_scorecard.json: N, d (the cross-section's need against the bracket's midpoint), the smallest negated and the largest = 1.50032
   - 8.6 (new): results/stage16_scorecard.json: N, d (the cross-section's need against the bracket's midpoint), the smallest negated and the largest = 8.60726
   - 10: predictions_stage16.md: /Scored: \|d\| <= (0\.10) in each of the eight/ = 10
   - 5.96: results/stage16_scorecard.json: N, SP_Exp1, xs_E_by_t_J = 5.96468
   - 250.6 (new): results/stage16_scorecard.json: N, SP_Exp1, lo_t_C8_s (the run at the cross-section's need) = 250.62
   - 223: inputs/fransson2024/m50_tests.csv: time_to_propagation_s where {'test': 'M50_SP_Exp1'} = 223
   - 16: manuscript/rebuild/data/steps.csv: the step whose file is predictions_stage16.md = 16
97. At the thresholds after strong triggers the three-dimensional value lay above the cross-section's wherever the two are not equal by construction, by up to 15\,\% (Table~ ).
   - 15: rebuild_headline.thresholds_3d against results/stage15_cross_section.json A2's E_star_J: the largest upper end over the cross-section's value, among PT_Exp4, ST_Exp4 and SP_Exp3 = 15
98. With constant power, where its runaway can lag, the cross-section's need lay 0.9 to 15.7\,\% above the three-dimensional midpoint in the fourteen searches closed, beyond the 10\,\% registered in PP-Exp1 over 240~s and PP-Exp4 over 120~s (P10, failed, as its file expected).
   - 0.9 (new): results/stage16_scorecard.json: X, d of the closed searches, the smallest and the largest = 0.943548
   - 15.7 (new): results/stage16_scorecard.json: X, d of the closed searches, the smallest and the largest = 15.7493
   - 10: predictions_stage16.md: /Scored: \|d\| <= (0\.10) for every X search closed/ = 10
   - 240: src/stage16_run.py: X_SHAPES, the constant-power durations X searched (s) = 240
   - 120: src/stage16_run.py: X_SHAPES, the constant-power durations X searched (s) = 120
99. (a) The time the resolved neighbour's mean reaches 255.7\degC, in the runs where both models run away.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
100. (c) The thresholds with the 21.4~s pulse of the six tests bracketed in three dimensions, in order of the trigger's energy; the threshold searches opened 5\,\% either side of the cross-section's value, so that PP-Exp2's, ST-Exp3's and PT-Exp1's brackets, closed by their first two runs, agree with it by construction, and ST-Exp4's bracket and PT-Exp4's, narrower than its threshold search's, are those of the need's search.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 5: predictions_stage15.md: /less (5) % and plus 5 %/ = 5
101. (d) The needs with the pulse by the measured times after strong triggers: the three-dimensional bracket, the cross-section's need (the upper end of its search's bracket, 0.5\,\% of the test's ejected energy wide) and the lumped need.
   - 0.5: results/stage15_cross_section.json: settings.width_ft = 0.5
102. Through the model, each test's outcome and time set the least of it that the model's neighbour must receive by the measured time: after strong triggers, with the pulse, 4.45 to 7.54~kJ read through a resolved neighbour in three dimensions and 0.26 to 5.96~kJ read through a lumped one, and over the four shapes 4.1 to 8.1~kJ by the reactive cross-section (3.88 to 7.67~kJ in three dimensions where searched, counted to 10~s after the measured time) and 0.2 to 6.0~kJ lumped; after the weak one, 10.3 to 13.8 and 11.5 to 12.3~kJ.
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
   - 4.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 4.06435
   - 8.1 (new): smallest and largest of results/stage15_table.csv: C8_xs_E_by_t_J, every case outside ST_Exp3 (matched, or within the search's resolution of the threshold) = 8.11583
   - 3.88 (new): results/stage16_scorecard.json: X, the closed searches' smallest lower end and largest upper end by the runaway (lo_by_t_J, hi_by_t_J) = 3.87617
   - 7.67 (new): results/stage16_scorecard.json: X, the closed searches' smallest lower end and largest upper end by the runaway (lo_by_t_J, hi_by_t_J) = 7.67168
   - 10: src/stage16_run.py: /WINDOW_S = ([0-9.]+)/ = 10
   - 0.2: smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 0.218747
   - 6.0 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J of the same thirty-two cases = 5.9624
   - 10.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 10.3125
   - 13.8: smallest and largest of results/stage15_table.csv: ST_Exp3, C8_xs_E_by_t_J = 13.8435
   - 11.5: smallest and largest of results/stage15_table.csv: ST_Exp3, C2_E_by_t_J = 11.4655
   - 12.3 (new): smallest and largest of results/stage15_table.csv: ST_Exp3, C2_E_by_t_J = 12.2592
103. Either way the needed energies are at most about a quarter of the Databank's median ejected energy for this cell, 76.74~kJ~ : the lumped neighbour needs at most 12.3~kJ by its runaway, and the deliveries with which the resolved neighbour runs away carry 5.3 to 25.4\,\% of it in all over their shapes.
   - 76.74: results/stage14_inputs.csv: value where {'key': 'db_Eej_median'} = 76.7412
   - 12.3 (new): results/stage15_table.csv: C2_E_by_t_J, the largest = 12.2592
   - 5.3 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 5.29617
   - 25.4 (new): smallest and largest of results/stage15_table.csv: C8_xs_share_of_76.74kJ = 25.4319
104. Torres-Castro et al.'s estimate for pouch cells, 2.0~kJ absorbed on average by the next cell before it failed~ , lies inside the lumped range found here, though a different cell cannot choose between the readings of this one.
   - 2.0: manuscript/data/comparators.csv: value where {'key': 'torrescastro2020passive', 'quantity': 'energy the next cell absorbs before it fails, mean'} = 2
105. Since the resolved threshold is at least 1.36 times the lumped one in the three strong-trigger tests bracketed in three dimensions whose lumped threshold is not zero and at most 0.91 times after both weak triggers, a heat share calibrated in this model with either neighbour could not be carried to the other in these tests without a correction whose sign went with the trigger.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
106. At the central contact the reactive cross-section reproduced the outcomes it was set against afterwards, most of them far from a threshold, and the needs with the pulse to within 10\,\% of the three-dimensional brackets' midpoints, at a small part of the cost (Section~ ).
   - 10: predictions_stage16.md: /Scored: \|d\| <= (0\.10) in each of the eight/ = 10
107. A heat flux measured at several points of the neighbour's facing side, away from the line of contact and through the venting, less what the trigger's body sends there, would give the heat delivered to that half in place of a need inferred through a model; set against the needs, it could show which reading's need a test meets, if the model is otherwise right (Section~ ) and if it resolves that heat to well within the 1.46 to 4.33~kJ by which the readings' needs differ with the pulse after strong triggers.
   - 1.46 (new): results/stage16_scorecard.json N against results/stage15_table.csv C2_E_by_t_J: the smallest lower end and the largest upper end of the resolved need less the lumped need, rounded outward (rebuild_headline.differences_kJ) = 1.46
   - 4.33 (new): results/stage16_scorecard.json N against results/stage15_table.csv C2_E_by_t_J: the smallest lower end and the largest upper end of the resolved need less the lumped need, rounded outward (rebuild_headline.differences_kJ) = 4.33
108. The flame's position and temperature, with whether the holder reflects, would bound radiation: a flame on the vent's axis would send about 0.85~kJ onto the facing half if the holder does not reflect, but up to a quarter of its radiation from in front of the trigger's end face near the line of contact, and with a reflecting holder the geometry stops mattering (Supplementary Section~S6); which way a breach faces and what it carries would bound the jet and the melt; and calorimetry of the tests' own triggers would replace a body energy fitted to a thermocouple's peak.
   - 0.85 (new): results/stage14_independent_read.md: /at most about (\d+) J \(1\.11 %\)/ = 0.849
109. One cell type, in one laboratory's rig, carries the comparison, and one published history of a neighbour that propagated, from a test whose trigger ruptured its sidewall; that history was read from a figure, and its opening 8.5~s, a spike to 102\degC, are taken as the thermocouple's exposure at the trigger's runaway.
   - 8.5: results/stage10_paper_numbers.json: measured.dip_after_spike_t_s = 8.5
   - 102: results/stage10_paper_numbers.json: measured.spike_on_the_samples_C = 101.711
110. The triggers are fitted to one surface thermocouple's peak: thirteen of the sixteen fitted energies lie above the range of body energies the Databank measured for this cell, 18.7 to 33.2~kJ, two below it and one inside, and every threshold and need above rests on them.
   - 18.7 (new): results/stage14_inputs.csv: range_lo where {'key': 'db_Ebody_max'} = 18.6715
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
111. Where the trigger's energy was shifted, by 2~kJ in three tests, the lumped threshold fell as it rose (Section~ ), which suggests that triggers held within that range would raise the lumped needs after the thirteen and lower them after the two; no need was computed with a shifted trigger, and with the body energy held to 33.2~kJ only the runs of Section~ were made.
   - 2: src/stage13_inputs.py: /for d in \(-2000\.0, (2000\.0)\)/ = 2
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
112. The reactive cross-section has neither the cell's ends nor its tabs and was checked only at the central contact, yet it gives ten of the sixteen resolved thresholds, the resolved needs over 360~s and two over 120~s, those after the weak trigger, and ten of the high-contact outcomes; the two-body model was scored at the low and high contacts only.
   - 360: src/stage16_run.py: X_SHAPES, the constant-power durations X searched (s) = 360
   - 120: src/stage16_run.py: X_SHAPES, the constant-power durations X searched (s) = 120
113. In coarser searches made in the step that repeated the main searches under draws of the kinetics and the properties (step~11 of Supplementary Table~S1), ST-Exp2's lumped threshold, 2.70~kJ on that grid under the posterior mean, was at most 1.80~kJ under two of four kinetic draws and zero with the smallest specific heat of four thermal draws, and PP-Exp3's ran from 0.85 to 4.26~kJ over the eight (Supplementary Table~S12); every comparison of the two thresholds above is at the posterior mean and the nominal properties of Table~ , and the resolved threshold was searched under no draw.
   - 11: manuscript/rebuild/data/predictions_registry.csv: the step of P1 under every kinetic draw = 11
   - 2.70 (new): results/stage11_scorecard.json: P1, ST_Exp2's posterior-mean f*, times its ejected energy (results/stage8_ejected.csv) = 2.7049
   - 1.80 (new): results/stage11_thresholds.csv: hi of ST_Exp2's C2 brackets under draws 188 and 83, times its ejected energy = 1.80326
   - 0.85 (new): smallest and largest of results/stage11_thresholds.csv: E_star_J of PP_Exp3's C2 under the eight draws = 0.851923
   - 4.26 (new): smallest and largest of results/stage11_thresholds.csv: E_star_J of PP_Exp3's C2 under the eight draws = 4.25961

## main.tex: Conclusions

114. \item In the model, with the trigger's body energy no larger than the largest that calorimetry gives for this cell, conduction and radiation leave the neighbour's hottest point at least 28.9~K short of 255.7\degC{} at every contact conductance considered (Supplementary Section~S3).
   - 28.9: results/manuscript_numbers.json: constants.level_propagation_C less the highest hottest-point peak with at most 33.2 kJ and no delivery, over step 5 (results/v12_numbers.json: all_runs.res_peak_hottest_C.max), step 6 (results/stage6_runs/*_hhigh_*_E33.22.json: resolved.peak_hottest_C) and step 12 (results/stage12_paper_numbers.json: part_a.high.hot_spot_peak_C) = 28.9299
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
115. \item By the tests' measured times after strong triggers, with the 21.4~s pulse, the resolved neighbour needs 4.45 to 7.54~kJ in three dimensions, in two tests its threshold, and the lumped neighbour 0.26 to 5.96~kJ; published inputs cannot bound at least four delivery paths below 27.9~kJ within 21.4~s, so the bounds exclude neither.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
116. \item With 21.4~s of delivered heat the resolved neighbour's threshold is at least 1.36 times the lumped neighbour's in the four strong-trigger tests bracketed in three dimensions, 1.36 to 2.27 times across the brackets in PT-Exp4 and PP-Exp2, and 0.79 to 0.91 times in the two with weak triggers, all at the posterior mean and the nominal properties.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 2.27 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the upper end rounded up = 2.27
   - 0.79 (new): rebuild_headline.weak_range: ST_Exp3 (B1) and PT_Exp1 (T), rounded outward = 0.79
   - 0.91 (new): rebuild_headline.weak_range: ST_Exp3 (B1) and PT_Exp1 (T), rounded outward = 0.91
117. \item In PT-Exp4, with 5.04~kJ, which runs the lumped neighbour away under the posterior mean and under two of four kinetic draws, the resolved neighbour runs away under none of these and only once every rate law is shifted by more than 17.5~K.
   - 5.04 (new): results/stage15_paper_numbers.json: B4.draws.5.E_J = 5.04499
   - 17.5: results/stage15_paper_numbers.json: B4.shift_runs: the largest shift_K without the mean's runaway = 17.5
118. \item At the central contact a reactive cross-section gave the outcome of the three-dimensional model in all 151 archived runs it was set against afterwards, most of them far from a threshold, and needs with the pulse, at its own coarser resolution, within 10\,\% of the three-dimensional brackets' midpoints, at a small part of its cost.
   - 151: results/stage15_cross_section.json: A1_summary.runs = 151
   - 10: predictions_stage16.md: /Scored: \|d\| <= (0\.10) in each of the eight/ = 10
119. \noindent A heat flux measured on the facing side of a neighbour, away from the line of contact, to well within the 1.46 to 4.33~kJ by which the readings' needs differ, could test the resolved and the lumped reading of these tests, if the model is otherwise right.
   - 1.46 (new): results/stage16_scorecard.json N against results/stage15_table.csv C2_E_by_t_J: the smallest lower end and the largest upper end of the resolved need less the lumped need, rounded outward (rebuild_headline.differences_kJ) = 1.46
   - 4.33 (new): results/stage16_scorecard.json N against results/stage15_table.csv C2_E_by_t_J: the smallest lower end and the largest upper end of the resolved need less the lumped need, rounded outward (rebuild_headline.differences_kJ) = 4.33

## main.tex: appendices

120. The resolved neighbour's mesh is graded toward the line of contact, the roll is homogeneous and anisotropic, the can is a shell of steel with its own conductance and heat capacity, and the contact sector spans 45\textdegree{} either side of the line of contact, where room convection is removed.
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
121. Time is stepped by backward Euler with a lumped capacity in steps of 0.1~s, halved up to sixteen times so that no node's reaction heating exceeds about 1~K a step, a step that heats a node by more than 4~K being repeated at half its length; the reaction is integrated node by node within each step, and room radiation is lagged one step.
   - 0.1: src/reactive.py: /DT_BASE = (0\.1)/ = 0.1
   - 1: src/reactive.py: /DT_TARGET = (1)\.0/ = 1
   - 4: src/reactive.py: /DT_ACCEPT = (4)\.0/ = 4
122. Every run's energy account, the heat taken in through each boundary against the change in stored heat and the reaction heat released, closes to within $2\times10^{-11}$ of the heat taken in.
   - 2\times10^{-11}: results/stage8_paper_numbers.json: checks.V4.largest_relative.resolved = 1.9747e-11
123. For a bare semi-infinite solid under the triangular pulse, the surface's peak rise is $\Phi E''/(e\sqrt{\tau})$, with $E''$ the delivered energy per unit area, $\tau$ the pulse's duration and $e=(k_r\rho c)^{1/2}=1,743$~J\,m$^{-2}$\,K$^{-1}$\,s$^{-1/2}$ the roll's effusivity across its layers, $k_r$ its conductivity there and $\rho c$ the cell's heat capacity less the can's 4.5~J\,K$^{-1}$, over the cell's volume, which also gives $\alpha=k_r/\rho c$; the peak comes at two thirds of the pulse, and $\Phi=1.2284$ is [display] The skin model adds the can as a surface layer, its 4.5~J\,K$^{-1}$ over the cell's outer area, 841.7~J\,m$^{-2}$\,K$^{-1}$, and a linear surface loss, at the hot spot the contact's coefficient of Eq.~ (the room's convection beyond the sector) plus radiation taken as the secant from the temperature with no delivery to 255.7\degC, and is solved in closed form.
   - 1,743 (new): results/stage13_readings.json: reading_1.e_roll_as_resolved = 1742.5
   - 4.5 (new): manuscript/data/parameters.csv: /9; 500 \((4\.5) J/K\)/ = 4.5
   - 1.2284 (new): results/stage13_checks.json: V5.Phi00 = 1.22842
   - 4.5 (new): manuscript/data/parameters.csv: /9; 500 \((4\.5) J/K\)/ = 4.5
   - 841.7 (new): results/stage13_readings.json: reading_1.C_s_J_m2K = 841.736
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
124. The two-body model follows the lumped neighbour without reaction under the trigger's history and the delivery; once past $T_\mathrm{ign}$, with $Q$ its reaction heat there, the neighbour crosses if the heat of that cathode reaction still unreleased along its path covers $C(T_L-T)+CQ/(\mathrm{d}Q/\mathrm{d}T)$, the heat that carries it to $T_L=255.7$\degC{} and its loss over one induction time at the balance point; that reaction's whole heat, 2,667~J, is its posterior-mean enthalpy, 164.9~J per gram of cathode, times the cathode's 179.12~g in the source's 720~g reference cell, scaled to this cell's 65~g.
   - 255.7: results/manuscript_numbers.json: constants.level_propagation_C = 255.682
   - 2,667 (new): results/stage13_tign.csv: cat1_heat_total_J where {'kinetics': 'mean', 'connection': 'parallel', 'trigger': 'own'} = 2667.2
   - 164.9 (new): inputs: the posterior-mean kinetics (src/bcrnn.py): dH of cat1, J/g = 164.942
   - 179.12 (new): src/bcrnn.py: /M_IVV = (179\.12)/ = 179.12
   - 720: results/manuscript_numbers.json: constants.M_ref_g = 720
   - 65: src/stage13_tign.py: /the reaction heat of the (65) g cell/ = 65
125. Both cross-section models are solved on 3,034 cells over the half section, graded toward the surface and the line of contact; their grid was not refined in a separate check, so the error of their values, quoted to the searches' resolution, is not known beyond their agreement with the three-dimensional model.
   - 3,034 (new): src/stage13_section.py: Section(): nr x nt = 3034

## manuscript/rebuild/tables/t1_tests.tex: caption

126. \caption{The sixteen two-cell tests of LG M50 cells of Fransson et al.~ (their Tables 3 and 4), named as they name them without the prefix M50 (PT and PP connected in parallel, ST and SP in series, the second letter naming the cell in the X-ray camera's field of view, the trigger or the propagating cell), and the body energy $E_\mathrm{b}$ that puts the model's trigger at the measured trigger peak at the central contact when released over 21.39~s.
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
127. Category, Fransson et al.'s failure category: 1, the trigger's nail-penetration failure; 2, failure in the propagating cell; 4, sidewall rupture of the trigger (3, sidewall melting, is given for none of these tests); c.m., ``cell movement'' in the X-ray camera's field of view, given in place of a category; a dash, none given.
   - 1: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 1
   - 2: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 2
   - 4: inputs/fransson2024/m50_tests.csv: the failure categories the tests report (Fransson et al.'s codes) = 4
   - 3: inputs/fransson2024/SOURCE.md: /; (3), \"Representation of sidewall melting/ = 3

## manuscript/rebuild/tables/t2_parameters.tex

128. >{\raggedright\arraybackslash} >{\raggedright\arraybackslash} } \toprule Quantity & Value & Source \\ \midrule {\textit{Geometry and cells}} \\ Cell diameter and length & 21.1 and 70.1 mm & \\ Can wall & 0.25 mm & \\ Can: conductivity; mass and specific heat & 15 W\,m$^{-1}$\,K$^{-1}$, a stainless steel's (no source gives the grade); 9 g, 500 J\,kg$^{-1}$\,K$^{-1}$ & assumed$^{a}$ \\ Roll conductivity across and along the layers & 1.3 and 25 W\,m$^{-1}$\,K$^{-1}$ & \\ Cell heat capacity & 61.75 J\,K$^{-1}$ (65 g at 950 J\,kg$^{-1}$\,K$^{-1}$; the Databank's cells weighed 68.05 to 68.52 g before their tests~ ) & ; mass assumed$^{a}$ \\ Resolved neighbour & half model, 19,355 nodes & this study \\ {\textit{Heat paths}} \\ Contact conductance between the cans, $h_c$ & 200, 2,000, 3,700 W\,m$^{-2}$\,K$^{-1}$ (low, central, high) & \\ Air in the wedge beside the contact & 0.03 W\,m$^{-1}$\,K$^{-1}$ & assumed$^{a}$ \\ Contact sector, either side of the line of contact & 45\textdegree & assumed$^{a}$ \\ Welded tabs: series one, parallel two & 6.8 mW\,K$^{-1}$ per tab (5 and 10 as brackets) & assumed$^{a}$ \\ View factor between the cans; emissivity & 0.1817; 0.8 & ; assumed$^{a}$, as in \\ Room convection; ambient and start & 10 W\,m$^{-2}$\,K$^{-1}$; 25\textdegree C & assumed$^{a}$ \\ {\textit{Trigger}} \\ Model and release & one temperature; triangular over 21.39 s, the mean of the two rise times derived from the two published records, each a peak rise over a printed heating rate (17.53 and 25.24 s; Supplementary Section~S7) & derived from \\ Body energy $E_\mathrm{b}$ & 9.0 to 54.3 kJ, one per test (Table 1); 33.2 kJ, the most calorimetry measured for this cell, in the runs of Section~ & \\ {\textit{Kinetics}} \\ Model & Bayesian chemical reaction neural network: posterior mean, and 200 joint draws & \\ Reactant masses; initial SEI amount & per 720 g reference cell; 0.15 of the source's normalised amount (fresh), 0 (aged) & \\ Runaway level; window & 255.7\textdegree C; within 900 s & ; this study \\ {\textit{Delivered heat}} \\ Region & the half of the neighbour's can facing the trigger, a uniform flux & this study \\ Shapes & triangular over 21.39 s; constant power over 120, 240 or 360 s, the last outlasting the longest combustion reported for a 21700 cell, about 300 s~ ; in PT-Exp4 also the pulse followed by a constant power; for Section~ , triangular over 5 to 360 s & this study \\ \bottomrule
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
   - 68.05 (new): smallest and largest of inputs/databank/databank_m50_used.csv: Pre-Test-Cell-Mass-g = 68.05
   - 68.52 (new): smallest and largest of inputs/databank/databank_m50_used.csv: Pre-Test-Cell-Mass-g = 68.52
   - 19,355: results/stage8_paper_numbers.json: v3.base.n_nodes = 19355
   - 200: results/manuscript_numbers.json: constants.h_contact_W_m2K.low = 200
   - 2,000: results/manuscript_numbers.json: constants.h_contact_W_m2K.central = 2000
   - 3,700: results/manuscript_numbers.json: constants.h_contact_W_m2K.high = 3700
   - 0.03: results/manuscript_numbers.json: constants.k_air_W_mK = 0.03
   - 45: src/v12_mesh.py: SECTOR = math.pi / 4, the wedge sector's half-angle, in degrees = 45
   - 6.8: results/manuscript_numbers.json: constants.g_tab_mW_K.central = 6.8
   - 5: results/manuscript_numbers.json: constants.g_tab_mW_K.low = 5
   - 10: results/manuscript_numbers.json: constants.g_tab_mW_K.high = 10
   - 0.1817: results/manuscript_numbers.json: constants.view_factor_cans_in_contact = 0.18169
   - 0.8: results/manuscript_numbers.json: constants.emissivity = 0.8
   - 10: results/manuscript_numbers.json: constants.h_conv_W_m2K = 10
   - 25: results/manuscript_numbers.json: constants.T_amb_C = 25
   - 21.39: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 17.53: results/stage7_paper_numbers.json: triggers.levels.tau_s[0] = 17.5332
   - 25.24: results/stage7_paper_numbers.json: triggers.levels.tau_s[2] = 25.2399
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
   - 300 (new): results/stage14_inputs.csv: value where {'key': 't_flame_max'} = 300
   - 5: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 5
   - 360: results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 360

## manuscript/rebuild/tables/t3_bounds.tex

129. \centering \scriptsize \caption{What each path can deliver to the neighbour's facing half, from published inputs alone (Supplementary Table~S5): the upper bound within the pulse's 21.4~s and in total (every lower bound is zero), what sets it, and the measurement that would bound it more tightly; the bounds are estimates of the most the published inputs allow rather than strict limits (Supplementary Section~S6).
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
130. The ejecta can release at most 225.8~kJ: the most calorimetry measured for this cell's ejecta, 89.34~kJ~ , with the heat of burning the vent gas in open air, at most 136.5~kJ on another 21700 cell~ ; gas and flame are taken at up to 1500\textdegree C~ , the vent gas at up to 398.5~m\,s$^{-1}$~ .
   - 225.8 (new): results/stage14_corrections.json: E_avail_J = 225.838
   - 89.34 (new): results/stage14_inputs.csv: value where {'key': 'db_Eej_max'} = 89.3378
   - 136.5 (new): results/stage14_inputs.csv: value where {'key': 'vendra_Qt_max'} = 136.5
   - 1500 (new): results/stage14_inputs.csv: value where {'key': 'T_flame_max'} = 1500
   - 398.5 (new): results/stage14_inputs.csv: value where {'key': 'u_vent_max'} = 398.5
131. With the fitted triggers' own energies, up to 168.6~kJ ejected and 222.9~kJ in all, the bounds set by the ejecta's energy and the holder's cap would only rise.
   - 168.6: results/stage8_ejected.csv: the largest E_e_J of the sixteen tests = 168.629
   - 222.9 (new): results/stage8_ejected.csv: the largest E_b_J plus E_e_J of the sixteen tests = 222.932
132. rr>{\raggedright\arraybackslash} >{\raggedright\arraybackslash} } \toprule Path & {21.4 s} & {Total} & What sets the bound & Measurement that would bound it \\ & (kJ) & (kJ) & & \\ \midrule Radiation from a vent's jet or flame & 27.9 & 225.8 & a black body at 1500\textdegree C filling the facing half's view (the holder may reflect); a flame held on the vent's axis, about 0.85~kJ & the flame's position and temperature beside the cells \\ Gas beside the neighbour, burning or not & 195.5 & 225.8 & convection by Churchill and Bernstein's relation~ at 398.5~m\,s$^{-1}$~ , at the film temperature of gas at 1500\textdegree C over a can at 25\textdegree C, with hydrogen's properties at 1000~K, the highest tabulated, which give a larger coefficient than air's~ , at most twice the whole-cylinder mean on one half, as the other half's cannot be negative; radiation at 1500\textdegree C & the gas's temperature and velocity in the wedges beside the line of contact \\ A breach's jet facing the neighbour & 225.8 & 225.8 & what the ejecta can release; a narrow jet strikes only from within 30\textdegree{} of the line of centres, a sixth of the circumference & where breaches face and what they carry \\ Solids and melt on or against the facing half & 225.8 & 225.8 & what the ejecta can release; melt falls onto it from a breach on the trigger's lower half, half of the circumference & the debris left on the neighbour \\ Conduction through the cell holder & -- & -- & not determinable: the inserts' material and contact are not given; energy conservation alone caps it at 247.3~kJ, all the trigger can release, the most measured for this cell in all (110.8~kJ~ ) with the vent gas burning & the holder's inserts and their contact \\ The neighbour's own discharge (parallel tests; for comparison) & 65.5 & 65.5 & heats from inside: the stored energy, 18.2~Wh, in every window; beside it, a short across 24~m$\Omega$~ at 4.189~V and 25\textdegree C, 731~W or 15.6~kJ within 21.4~s & the current between parallel cells \\ \bottomrule
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

## manuscript/rebuild/tables/t4_3d.tex

133. Needs after the eight strong triggers whose tests propagated, by measured time: the least energy delivered to the facing half that runs the neighbour away by 10~s after the measured time, bracketed in three dimensions and counted to that time, and for the other two counted to their own runaways (the same with the pulse); the cross-section's is the upper end of a bracket 0.5\,\% of the test's ejected energy wide, set against the bracket's midpoint. $^{t}$: no run reproduces the measured time, so the need is the threshold (Supplementary Table~S7); $^{b}$: interpolated between two runs.
   - 10: src/stage16_run.py: /WINDOW_S = ([0-9.]+)/ = 10
134. Thresholds with the pulse, by the trigger's fitted energy: the least energy that runs the neighbour away within 900~s, and the ratio of resolved to lumped across the brackets, rounded outward; 0: runs away with none; $^{n}$: bracketed by the need's two runs, read after them (PT-Exp4's threshold search gave (6.71, 7.42]).}
   - 900: results/manuscript_numbers.json: constants.run_end_s = 900
135. \toprule {\textit{Needs with the 21.4~s pulse}} \\ Test & Time (s) & Three-dimensional & Cross-section & Difference (\%) & Lumped \\ \midrule PP-Exp2 & 147 & (7.42, 7.54] & 7.65 & +2.3 & 5.96 \\ SP-Exp2 & 149 & (6.33, 6.50] & 6.50 & +1.3 & 3.78 \\ PP-Exp1 & 152 & (5.46, 5.65] & 6.04 & +8.6 & 2.97 \\ SP-Exp3 & 210 & (4.45, 4.58] & 4.58 & +1.5 & 0.26 \\ SP-Exp1 & 223 & (5.96, 6.15] & 5.96 & $-$1.5 & 2.73 \\ PT-Exp4 & 272 & (7.06, 7.15]$^{t}$ & 7.44$^{t}$ & +4.7 & 4.85$^{t}$ \\ PP-Exp4 & 275 & (5.52, 5.65] & 6.05$^{t}$ & +8.3 & 1.82 \\ ST-Exp4 & 342 & (5.32, 5.51]$^{t}$ & 5.51$^{t}$ & +1.7 & 1.18 \\ \midrule {\textit{Needs with constant power over 240~s}} \\ PP-Exp2 & 147 & (7.57, 7.67] & 8.04 & +5.5 & 4.85 \\ SP-Exp2 & 149 & (6.09, 6.18] & 6.32 & +3.0 & 3.40 \\ PP-Exp1 & 152 & (5.12, 5.24] & 6.00 & +15.7 & 2.42 \\ SP-Exp3 & 210 & (3.88, 4.01] & 4.18 & +6.0 & 0.23$^{b}$ \\ SP-Exp1 & 223 & (5.54, 5.67] & 5.78 & +3.2 & 2.12 \\ PT-Exp4 & 272 & (6.40, 6.50] & 6.77 & +5.0 & 3.49 \\ PP-Exp4 & 275 & (4.48, 4.66] & 5.03 & +9.9 & 1.36$^{t}$ \\ ST-Exp4 & 342 & (4.10, 4.29]$^{t}$ & 4.48$^{t}$ & +6.8 & 0.95$^{t}$ \\ \midrule {\textit{Needs with constant power over 120~s}} \\ PP-Exp2 & 147 & (7.09, 7.19] & 7.74 & +8.5 & 4.77 \\ PP-Exp1 & 152 & (4.88, 4.99] & 5.42 & +9.8 & 1.98 \\ SP-Exp1 & 223 & (5.30, 5.40] & 5.40 & +0.9 & 2.17$^{b}$ \\ PT-Exp4 & 272 & (6.57, 6.68]$^{t}$ & 7.20$^{t}$ & +8.6 & 3.88$^{t}$ \\ PP-Exp4 & 275 & (4.71, 4.84]$^{t}$ & 5.46$^{t}$ & +14.4 & 1.46$^{b}$ \\ ST-Exp4 & 342 & (4.55, 4.67]$^{t}$ & 4.92$^{t}$ & +6.7 & 0.95 \\ \midrule {\textit{Thresholds}} \\ Test & Trigger & Three-dimensional & Cross-section & Lumped & Ratio \\ \midrule SP-Exp3 & 54.3 & (3.70, 4.06] & 3.53 & 0 & \\ ST-Exp4 & 48.8 & (5.32, 5.51]$^{n}$ & 5.04 & (0.00, 1.89] & $\geq$2.80 \\ PP-Exp2 & 41.0 & (6.51, 7.20] & 6.85 & (3.18, 4.77] & 1.36--2.27 \\ PT-Exp4 & 40.0 & (7.06, 7.15]$^{n}$ & 7.06 & (4.66, 4.85] & 1.45--1.54 \\ ST-Exp3 & 16.6 & (9.77, 10.80] & 10.28 & (11.95, 12.11] & 0.80--0.91 \\ PT-Exp1 & 9.0 & (10.24, 11.32] & 10.78 & (12.85, 12.89] & 0.79--0.89 \\ \bottomrule
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## manuscript/rebuild/highlights.txt

136. Conduction and radiation alone run the resolved neighbour away in no test Strong-trigger tests need 4.45 to 7.54 kJ resolved, 0.26 to 5.96 kJ lumped Resolved threshold above lumped after four strong triggers, below after two weak A heat share calibrated lumped may need a trigger-dependent correction if resolved Published inputs rule out no path; a facing-side heat flux could test the needs
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624

## manuscript/rebuild/ga_text.txt

137. failing cell neighbour heat delivered to the facing half with no more energy than calorimetry measured for this cell, conduction and radiation leave the modelled neighbour at least 28.9 K short of runaway heat the model's neighbour needs over 21.4 s to run away by the measured times, after strong triggers (kJ) resolved neighbour (three-dimensional): 4.45 to 7.54 kJ, 5.8 to 9.8 % of the Databank's median for this cell's ejecta lumped neighbour: 0.26 to 5.96 kJ, 0.3 to 7.8 % of the Databank's median for this cell's ejecta To run away at all, the resolved neighbour needs at least 1.36 times the lumped neighbour's energy after the four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs.
   - 28.9: results/manuscript_numbers.json: constants.level_propagation_C less the highest hottest-point peak with at most 33.2 kJ and no delivery, over step 5 (results/v12_numbers.json: all_runs.res_peak_hottest_C.max), step 6 (results/stage6_runs/*_hhigh_*_E33.22.json: resolved.peak_hottest_C) and step 12 (results/stage12_paper_numbers.json: part_a.high.hot_spot_peak_C) = 28.9299
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 5.8 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end, over results/stage14_inputs.csv db_Eej_median = 5.79938
   - 9.8 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end, over results/stage14_inputs.csv db_Eej_median = 9.82013
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
   - 0.3: smallest and largest of results/stage15_table.csv: C2_E_by_t_J, the eight strong-trigger needs with the pulse, over results/stage14_inputs.csv db_Eej_median = 0.343362
   - 7.8 (new): smallest and largest of results/stage15_table.csv: C2_E_by_t_J, the eight strong-trigger needs with the pulse, over results/stage14_inputs.csv db_Eej_median = 7.76949
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
138. Published inputs do not exclude any path delivering 27.9 kJ to the facing half within 21.4 s; a heat flux measured there could test the needs.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## manuscript/rebuild/letters/Cover_letter_Fire_Safety_J.txt

139. Each failing cell's energy is fitted to its own measured peak temperature, 31.6 to 54.3 kJ in fourteen tests (strong triggers), mostly above the 33.2 kJ that calorimetry measured at most for this cell, and 9.0 and 16.6 kJ in two (weak), and the neighbour is solved both as one temperature and as a three-dimensional field; in each, the heat it needs through its side facing the failing cell to run away by the test's measured time is searched, and the bounds that published inputs set on each path that could deliver it are worked out.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 9.0: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_PT_Exp1'} = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
140. With heat delivered over 21.4 s, the mean rise time derived from the two published records, the eight tests that propagated after strong triggers need, by their measured times, 4.45 to 7.54 kJ if the neighbour is resolved in three dimensions, two of them its threshold, and 0.26 to 5.96 kJ if it is lumped.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
141. To run away at all, the resolved neighbour needs at least 1.36 times the lumped neighbour's energy after the four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs, so in these tests a heat share calibrated with one representation may need a correction that depends on the trigger before it can serve the other.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
142. Published inputs rule out no path delivering 27.9 kJ to the facing side within 21.4 s.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
143. The code, inputs and run records are archived openly, with the study's 109 predictions, each committed before its runs.
   - 109: manuscript/rebuild/data/predictions_registry.csv: rows = 109

## manuscript/rebuild/letters/Cover_letter_J_Energy_Storage.txt

144. Each failing cell's energy is fitted to its own measured peak temperature, 31.6 to 54.3 kJ in fourteen tests (strong triggers), mostly above the 33.2 kJ that calorimetry measured at most for this cell, and 9.0 and 16.6 kJ in two (weak), and the neighbour is solved both as one temperature and as a three-dimensional field; in each, the heat it needs through its side facing the failing cell to run away by the test's measured time is searched, and the bounds that published inputs set on each path that could deliver it are worked out.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 9.0: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_PT_Exp1'} = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
145. With heat delivered over 21.4 s, the mean rise time derived from the two published records, the eight tests that propagated after strong triggers need, by their measured times, 4.45 to 7.54 kJ if the neighbour is resolved in three dimensions, two of them its threshold, and 0.26 to 5.96 kJ if it is lumped.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
146. To run away at all, the resolved neighbour needs at least 1.36 times the lumped neighbour's energy after the four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs, so in these tests a heat share calibrated with one representation may need a correction that depends on the trigger before it can serve the other.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
147. Published inputs rule out no path delivering 27.9 kJ to the facing side within 21.4 s.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
148. The code, inputs and run records are archived openly, with the study's 109 predictions, each committed before its runs.
   - 109: manuscript/rebuild/data/predictions_registry.csv: rows = 109

## manuscript/rebuild/letters/Cover_letter_J_Power_Sources.txt

149. Each failing cell's energy is fitted to its own measured peak temperature, 31.6 to 54.3 kJ in fourteen tests (strong triggers), mostly above the 33.2 kJ that calorimetry measured at most for this cell, and 9.0 and 16.6 kJ in two (weak), and the neighbour is solved both as one temperature and as a three-dimensional field; in each, the heat it needs through its side facing the failing cell to run away by the test's measured time is searched, and the bounds that published inputs set on each path that could deliver it are worked out.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 9.0: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_PT_Exp1'} = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
150. With heat delivered over 21.4 s, the mean rise time derived from the two published records, the eight tests that propagated after strong triggers need, by their measured times, 4.45 to 7.54 kJ if the neighbour is resolved in three dimensions, two of them its threshold, and 0.26 to 5.96 kJ if it is lumped.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
151. To run away at all, the resolved neighbour needs at least 1.36 times the lumped neighbour's energy after the four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs, so in these tests a heat share calibrated with one representation may need a correction that depends on the trigger before it can serve the other.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
152. Published inputs rule out no path delivering 27.9 kJ to the facing side within 21.4 s.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
153. The code, inputs and run records are archived openly, with the study's 109 predictions, each committed before its runs.
   - 109: manuscript/rebuild/data/predictions_registry.csv: rows = 109

## manuscript/rebuild/letters/Enquiry_Fire_Safety_J.txt

154. Fitted to peak temperatures, failing-cell energies are 31.6 to 54.3 kJ in fourteen (strong triggers), mostly above calorimetry's 33.2 kJ maximum, and 9.0 and 16.6 kJ in two (weak); conduction and radiation run no resolved neighbour away at either energy.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
155. Over 21.4 s, the two published records' mean rise time, 4.45 to 7.54 kJ through the facing side runs the resolved neighbour away by the eight propagating strong-trigger tests' measured times (two at its threshold, the least that runs it away at all), and 0.26 to 5.96 kJ the lumped one.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
156. The resolved threshold is at least 1.36 times the lumped one after four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs, so here a heat share calibrated with either may need a trigger-dependent correction for the other.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
157. Published inputs rule out no path delivering 27.9 kJ within 21.4 s; a facing-side heat flux could test the needs.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## manuscript/rebuild/letters/Enquiry_J_Energy_Storage.txt

158. Fitted to peak temperatures, failing-cell energies are 31.6 to 54.3 kJ in fourteen (strong triggers), mostly above calorimetry's 33.2 kJ maximum, and 9.0 and 16.6 kJ in two (weak); conduction and radiation run no resolved neighbour away at either energy.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
159. Over 21.4 s, the two published records' mean rise time, 4.45 to 7.54 kJ through the facing side runs the resolved neighbour away by the eight propagating strong-trigger tests' measured times (two at its threshold, the least that runs it away at all), and 0.26 to 5.96 kJ the lumped one.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
160. The resolved threshold is at least 1.36 times the lumped one after four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs, so here a heat share calibrated with either may need a trigger-dependent correction for the other.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
161. Published inputs rule out no path delivering 27.9 kJ within 21.4 s; a facing-side heat flux could test the needs.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865

## manuscript/rebuild/letters/Enquiry_J_Power_Sources.txt

162. Fitted to peak temperatures, failing-cell energies are 31.6 to 54.3 kJ in fourteen (strong triggers), mostly above calorimetry's 33.2 kJ maximum, and 9.0 and 16.6 kJ in two (weak); conduction and radiation run no resolved neighbour away at either energy.
   - 31.6: results/stage7_triggers.csv: the smallest E_J of the tests whose body energy exceeds 30 kJ = 31.5878
   - 54.3: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 54.3037
   - 33.2: results/manuscript_numbers.json: constants.E_body_stage5_J = 33.2229
   - 9.0: smallest and largest of results/stage7_triggers.csv: E_J of the sixteen tests = 8.97677
   - 16.6: results/stage7_triggers.csv: E_J where {'kind': 'test', 'test': 'M50_ST_Exp3'} = 16.6412
163. Over 21.4 s, the two published records' mean rise time, 4.45 to 7.54 kJ through the facing side runs the resolved neighbour away by the eight propagating strong-trigger tests' measured times (two at its threshold, the least that runs it away at all), and 0.26 to 5.96 kJ the lumped one.
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
   - 4.45 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 4.45052
   - 7.54 (new): results/stage16_scorecard.json: N, the smallest lower end and the largest upper end of the eight brackets = 7.53609
   - 0.26: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 0.2635
   - 5.96: smallest and largest of results/stage14_needs.csv: need_21s_lo_J of the propagated tests read at the measured time = 5.9624
164. The resolved threshold is at least 1.36 times the lumped one after four strong triggers searched in three dimensions and at most 0.91 times after both weak ones, at nominal inputs, so here a heat share calibrated with either may need a trigger-dependent correction for the other.
   - 1.36 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): PP_Exp2, the lower end rounded down, a lower bound (the ratio of the shown ends, 6.51 and 4.77 kJ) = 1.36
   - 0.91 (new): results/stage15_paper_numbers.json B1 against the lumped bracket (rebuild_brackets): ST_Exp3, the upper end rounded up, an upper bound = 0.91
165. Published inputs rule out no path delivering 27.9 kJ within 21.4 s; a facing-side heat flux could test the needs.
   - 27.9: results/stage14_bounds_corrected.csv: upper_J where {'path': 'A1', 'window_s': '21.39'} = 27.8564
   - 21.4 (new): results/stage13_skin.csv: tau_d_s where {'test': 'M50_PT_Exp1', 'region': 'half'} = 21.3865
