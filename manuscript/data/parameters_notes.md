# Notes to parameters.csv (Table 2)

`parameters.csv` holds 86 rows in 14 groups: geometry (9), cell thermal properties (10), paths between the cells (10), room (3), trigger (8), kinetics (16), criteria and levels (6), thermocouple nodes (5), the Stage 7 event (2), the Stage 8 delivery (5), the Stage 8 brackets (4), search rules (3), the Stage 11 draws (1) and numerics (4). Each value was read from the code constant or the DECISIONS.md entry named in its `file_evidence` column. Code values were printed with `python3 -c` from `src/`, through the named modules (`v12_model`, `bcrnn`, `stage7_inputs` to `stage11_inputs`). The resolved Stage 5 cell was built once, at the central contact (`v12_model.Cell2Contact(h_c=2000)`), to read its mesh volume, the roll's volumetric heat capacity and the probe angles. No model was run and no repository file was changed; the Python runs wrote only bytecode caches, which `.gitignore` excludes.

Where a value is derived (an area, the integrated contact conductance G, the roll's heat capacity), the `source` column says "computed" and names the study's own code that computes it. "Conditional" marks the values that DECISIONS.md labels conditional.

## Files read beyond the named list

The named modules take some constants from other modules. I read those lines so that the table could give exact line numbers:

1. `src/reactive.py` lines 39 to 47: the time-step and sub-step constants, which `src/v12_model.py` imports as `RX`.
2. `src/v12_mesh.py` lines 21 to 36: the sector's half-angle, the tab disc's radius and the mesh spacings, imported as `MS`.
3. `src/stage6_inputs.py` lines 23 to 24, 57 to 69 and 73 to 77: the Stage 6 durations, the 150 C level and the Databank energies. `src/stage7_inputs.py` delegates to these.
4. `src/stage3b.py` line 38: the ranges of the thermal draws.
5. `src/stage7_model.py` lines 37 to 51 and 104, `src/stage7_run.py` line 66, `src/stage8_run.py` line 59 and `src/stage8_model.py` lines 56 to 66: the event's pulse and placement, the sub-step limit of 4,096 and the facing half.
6. `src/onset_kinetics.py` lines 29 to 36, `src/stage7_criteria.py` line 97, `src/v0_dsc_check.py` line 15 and `src/stage7_numbers.py` lines 93 to 104: where the 0.15 K/min level, the 5 C/min DSC rate and the density 2938.7 kg/m3 are defined.
7. `results/stage3_thermal_draws.csv`: read through `stage11_inputs.thermal_draws()`, and once directly for the extremes of the 30 draws.

I did not open the two-cell study's own DECISIONS file, `inputs/kinetics/SOURCE.md`, `inputs/fransson2024/SOURCE.md` or the Databank CSV. The ten ratios were printed through `stage8_inputs.ratios()`, which reads that CSV.

## What I could not find

1. **A source for the can's conductivity.** The value is 15 W/(m K) (`lumped_two_cell.py` line 57, `K_CAN`). The code comment, DECISIONS.md and README.md give no source and no D number for it.
2. **A full citation for the can thickness.** The two-cell study's code cites "Finegan et al. 2024, Table 1: 250 um for the M50" for the 0.25 mm can wall (`lumped_two_cell.py` line 56). The only Finegan et al. 2024 article cited in full in the repository is the Battery Failure Databank's description (Journal of Power Sources 597 (2024) 234106). None of the files read says that the 250 um comes from that article's Table 1.
3. **Some of the two-cell study's D numbers.** No D number is recorded for:
   - the cell's diameter and length. The cell block of `lumped_two_cell.py` is headed "from O'Regan et al. 2022 via PyBaMM "ORegan2022" (D3)", but `D_CELL` and `L_CELL` have no source of their own;
   - the wedge air's conductivity, 0.03 W/(m K). D36 (3) calls it "the two-cell study's value";
   - the ambient, 25 C. D38 says "as the two-cell study";
   - the can conductivity (item 1).

   The room convection (10 W/(m2 K)), the emissivity (0.8) and the release shape and durations are marked "(brief)" in the two-cell code, so they were set by that study's brief. The table cites them that way. The two-cell study's DECISIONS file was not among the files to read, so I did not look these numbers up there.
4. **Full citations for four sources named only by author.** None of these has a reference in README.md's "Sources and credits" or in DECISIONS.md:
   - Incropera, the parallel-cylinder view-factor formula (D38; README Stage 5 table);
   - Feng et al. 2015, the origin of the masses in Koenig et al.'s Table 1 (D1, D4; `src/bcrnn.py` line 38);
   - Hatchard et al., behind Chen et al.'s assumed emissivity of 0.8 (D27 (f));
   - PyBaMM's parameter set "ORegan2022", the route by which the two-cell study read O'Regan et al. (its D3).
5. **O'Regan et al. (2022)'s published page numbers.** D73 records them as still missing. Their values are cited by table and section, from the accepted manuscript.
6. **What Fransson et al. (2024) do not report** (D33 (4)): the state of charge, the tabs' material and dimensions, the holder's material, the ambient, the nail's material and diameter, and the thermocouple's type and sampling rate. They also give no thermocouple angle (D89 (2), D102 (4)). The table's values for these are this study's choices or the two-cell study's. The state of charge is assumed to be 100 %.
7. **Left out of the model** (D36 (5); README Stages 5 to 7): the paint layers, the load between the cells, the holder, and convection in the wedge beyond 45 degrees. Venting, ejecta and flame are also absent, except as the delivered fraction from Stage 8 on.
8. **Not checked against the file.** D57 (2) says that 18.2 Wh agrees with the Databank's `Cell-Energy-Wh` for these cells. I did not check this, because the Databank CSV is not among the named files.

## Values that differ between files, or could be misread

1. **Propagation level.** The texts give 255.7 C. The code uses 255.681575 C, which is 278.9 x (1 - 0.1665/2) (`lumped_two_cell.py` line 90; `stage7_inputs.py` line 30, commented "255.68 C"). D101 quotes 255.681575 C. The table gives both.
2. **Central tab conductance.** D37's formula, 90 x 1.6e-6 / 0.0211, gives 6.82 mW/K. The code uses exactly 6.8 mW/K (`v12_model.py` line 37), and so do the runs.
3. **The facing sector.** D36 (3), D38 and the README call it "the 45 degree sector". `lumped_two_cell.py` line 70 and `v12_model.py` line 41 call the same region "the 90 degree sector". Both mean within 45 degrees either side of the line of centres (`v12_mesh.py` line 22: "half-angle"), which is a quarter of the lateral area.
4. **Stage 5's trigger energy.** The code uses 33,222.9 J, the two-cell study's `E_BODY_LIST` maximum. The Databank row (SPR2021_ESTA_8B100-01_SOC_RUN195) reads 33.2229118 kJ, about 0.012 J more (`stage6_inputs.energies()`, `body_max_J`). D53 says Stage 5 takes the value "as the two-cell study recorded it".
5. **Minimum and median energies over two different sets of tests.**
   - The two-cell study's `E_BODY_LIST` minimum and median, 8,751.3 and 21,495.3 J, are over its 17 M50 tests at 100 % state of charge: 7 heater tests and 10 nail tests (`lumped_two_cell.py` line 78).
   - Stage 5's sensitivity energies, 18.67 and 25.88 kJ, are the minimum and median of the 10 nail tests alone (D38).

   The maximum, RUN195, is the same in both.
6. **The roll's mass and density.**
   - `lumped_two_cell.py`'s comment (lines 42 to 47) gives the jelly roll as 56.4 g in a P2D volume of 1.918e-5 m3 at 2938.7 kg/m3, and the datasheet total as 68 g.
   - The model instead uses a 65 g cell and a 56 g roll (65 g less the 9 g can). It spreads the roll's 57.25 J/K over the whole cylinder's mesh volume, 2.4479e-5 m3, so the roll's effective volumetric heat capacity is 2.3387e6 J/(m3 K).
   - The density of 2938.7 kg/m3 (D7; `onset_kinetics.py` line 29) enters only Stage 1's passive integration. In the Stage 5 to 11 loops the reactant mass comes from the 65 g cell mass, spread by volume (`v12_model.py` line 301). D7 shows that the self-heating rate does not depend on the density.
7. **Release durations: two readings of the same figure disagree.**
   - D52 computes the durations from the printed Section I mean rates (37.70 and 23.97 C/s), Table 3's trigger maxima (686 and 630 C) and an assumed 25 C start. That gives 17.53 s (M50_PP_Exp3) and 25.24 s (M50_PT_Exp4), with a median of 21.39 s.
   - Stage 10 later read Figure 10's vector paths directly (D102 (2) and (3)). That reading ends Section I at 15.82 s (M50_PP_Exp3) and 24.16 s (M50_PT_Exp4; `stage10_inputs.py` line 18).
   - The same reading also differs from D52's inputs. M50_PT_Exp4's trigger trace starts at 28.9 C, not 25 C. M50_PP_Exp3's plotted trigger maximum is 671.41 C, against Table 3's 686 C.
   - Every run from Stage 6 on uses D52's durations. I did not re-derive anything; I flag the difference for the manuscript.
8. **The median release.** The texts give 21.39 s. The code uses 21.38652 s, the mean of 17.53316 and 25.23988 s (`stage6_inputs.durations()`). It is the median of two times read from two parallel tests, not a measured time (D62 (3)).
9. **Room radiation is written two ways.**
   - The lumped pair that makes cell 1's history uses A_rad = A_outer - eps F A_lat = 4.6707e-3 m2, with the exchange in (T1^4 - T2^4) (`v12_model.py` lines 43 and 115 to 121).
   - The one-way neighbour loops use the whole outer area, 5.3461e-3 m2, with a gain in (T1^4 - T_amb^4) (lines 268 to 269 and 484 to 485).

   For the neighbour the two are the same exchange rearranged. I note it because a reader comparing the files will see two areas.
10. **Rounding only.** The view factor is 0.1817 in D38 and the README, and 0.181690 in the code. The ratio is 3.105285 in D77 (2), and 3.1052850377 in the code. Stage 10's probe angles are 88.277, 0.326 and 94.392 degrees in D102 (4), and 88.277117, 0.325853 and 94.391976 degrees in `stage10_inputs.py`. The built mesh gives the same angles.
11. **Fransson et al.'s citation.** D33 gives the title without its subtitle. D59 records that error, and that three authors' initials were wrong in the README, `CITATION.cff` and `SOURCE.md` of that time. The citation below follows README.md line 956, which carries both corrections.
12. **Caveats the files record, which a reader of Table 2 should see:**
    - The emissivity stays 0.8 although the tested cells were painted black (D38).
    - 138.5 C is the peak of the posterior-mean separator melting at 5 C/min, not an onset. The source paper's Fig. 3(e) shows 139 C (D5, D67 (2)).
    - At the paper's stated trigger of 1 C/min, the study's emulation of the source paper's ARC test puts the posterior-mean model's internal-short temperature at 199.8 C. That is below the paper's band of 255.7 to 302.1 C, from which the propagation level is taken. The cause is not resolved (D21, D23).
    - The kinetics' cathode submodel matches the M50's NMC811. Its anode and electrolyte submodels were trained on graphite with an EC, DEC and DMC electrolyte (Lenz et al. 2023), not on the M50's silicon-graphite. The reactant mass fractions are those of the 25 Ah reference cell (D1, D7).

## The sixteen trigger energies

The table gives the sixteen per-test trigger energies as a range. These are the values `stage8_inputs.triggers()` prints from `results/stage7_triggers.json` (D65, D74), rounded to 0.1 J:

| Test | E_b (J) |
|---|---|
| M50_PT_Exp1 | 8,976.8 |
| M50_ST_Exp3 | 16,641.2 |
| M50_PT_Exp3 | 31,587.8 |
| M50_SP_Exp4 | 39,604.0 |
| M50_PT_Exp4 | 39,991.3 |
| M50_PP_Exp2 | 40,962.0 |
| M50_PT_Exp2 | 43,404.1 |
| M50_PP_Exp3 | 43,895.4 |
| M50_ST_Exp2 | 46,456.7 |
| M50_SP_Exp1 | 46,811.8 |
| M50_PP_Exp4 | 46,860.8 |
| M50_SP_Exp2 | 48,734.7 |
| M50_ST_Exp4 | 48,805.7 |
| M50_PP_Exp1 | 51,085.4 |
| M50_ST_Exp1 | 51,105.7 |
| M50_SP_Exp3 | 54,303.7 |

Each energy times the central ratio, 3.105285, gives the test's ejected energy (D77 (3); `results/stage8_ejected.csv`).

## Full citations of the sources the table names, as the repository writes them

From README.md, "Sources and credits" (lines 951 to 960), unless stated otherwise:

1. **Koenig, Zhao and Deng 2025** (line 951): B.C. Koenig, P. Zhao, S. Deng, Comprehensive thermal-kinetic uncertainty quantification of lithium-ion battery thermal runaway via Bayesian chemical reaction neural networks, Chemical Engineering Journal 507 (2025) 160402, doi:10.1016/j.cej.2025.160402, and its supplementary material (the trained B-CRNN particles), which is not redistributed here. The supplementary files are An_Ele.csv, NCM811.csv, Separator.csv and CSV_model_key.docx (`src/bcrnn.py`, docstring).
2. **The two-cell study, Satte 2026** (line 952): S. Satte, Where and when a neighbour cell first reaches thermal-runaway onset temperatures: resolved against lumped, a pre-registered two-cell LG M50 pilot (v1.0.0), Zenodo (2026), doi:10.5281/zenodo.23253738.
3. **O'Regan et al. 2022** (line 953): K. O'Regan, F. Brosa Planella, W.D. Widanage, E. Kendrick, Thermal-electrochemical parameters of a high energy lithium-ion cylindrical battery, Electrochimica Acta 425 (2022) 140700, doi:10.1016/j.electacta.2022.140700 (read in the authors' accepted manuscript, WRAP 196287).
4. **Chen et al. 2021** (line 954): H. Chen, J.E.H. Buston, J. Gill, D. Howard, R.C.E. Williams, E. Read, A. Abaza, B. Cooper, J.X. Wen, A simplified mathematical model for heating-induced thermal runaway of lithium-ion batteries, Journal of The Electrochemical Society 168 (2021) 010502, doi:10.1149/1945-7111/abd64c (accepted manuscript, WRAP 146838).
5. **Gaitonde, Nimmagadda and Marconnet 2017** (line 955): A. Gaitonde, A. Nimmagadda, A. Marconnet, Experimental characterization of thermal conductance across the separator-shell interface in dry cylindrical lithium ion batteries, ITHERM 2017, doi:10.1109/ITHERM.2017.7992602.
6. **Fransson et al. 2024** (line 956): M. Fransson, J. Pfaff, L. Broche, M. Buckwell, C. Kirchner-Burles, H.T. Reid, S. Schopferer, A. Rack, D.P. Finegan, P.R. Shearing, Exploring thermal runaway propagation in Li-ion batteries through high-speed X-ray imaging and thermal analysis: Impact of cell chemistry and electrical connections, Journal of Power Sources 617 (2024) 234916, doi:10.1016/j.jpowsour.2024.234916, CC BY 4.0, and its supplementary material (Appendix A). D52 records the supplement's file as `1-s2.0-S0378775324008681-mmc1.pdf`, 10,240,301 bytes, SHA-256 e96713ef58e8dc13df8810034c7ee8b47fb3e2fdcdb398a5095ecdfb64dfc0ef.
7. **Hoelle, Zimmermann and Hinrichsen 2023** (line 957): S. Hoelle, S. Zimmermann, O. Hinrichsen, 3D thermal simulation of thermal runaway propagation in lithium-ion battery cell stack: review and comparison of modeling approaches, Journal of The Electrochemical Society 170 (2023) 060516, doi:10.1149/1945-7111/acd966, CC BY 4.0.
8. **LG Chem 2017** (line 958): LG Chem, Product Specification, Rechargeable Lithium Ion Battery, Model INR21700 M50 (document LRB-PS-CY18.2Wh-M50, tentative, 22 September 2017), section 2.1: the nominal energy, 18.2 Wh, and the minimum, 17.6 Wh; section 2.2 gives the average voltage, 3.63 V.
9. **Lienhard V and Lienhard IV 2024** (line 959): J.H. Lienhard V and J.H. Lienhard IV, A Heat Transfer Textbook, 6th edition (version 6.00), Phlogiston Press, Cambridge, Massachusetts (2024), Table 2.1 (Section 2.3, p. 76).
10. **Battery Failure Databank** (line 960): Battery Failure Databank, revision 2 (February 2024), National Renewable Energy Laboratory (now National Laboratory of the Rockies), U.S. Department of Energy; described in D.P. Finegan et al., Journal of Power Sources 597 (2024) 234106. The README adds the credit that must accompany the rows used: "The Battery Failure Databank is provided by the U.S. Department of Energy's National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC (DOE/NREL/ALLIANCE); its notice accompanies the rows used, in `inputs/databank/`." The rows used are copied with the Databank's notice (`inputs/databank/DATABANK_NOTICE.txt`; D17).
11. **This study**, wherever the table says "this study's choice" (README.md line 7): Satte, S. (2026). Onset kinetics on a resolved neighbour cell: where a whole-cell threshold and a local one disagree (v1.6.0). Zenodo. https://doi.org/10.5281/zenodo.23279455. D117 makes Stage 11 version 1.7.0, and from that version the texts say "A pre-registered study" rather than "pilot". The README's citation line is still at v1.6.0.

The table also names five sources with no full citation in the files read: Incropera (the view factor), Feng et al. 2015, Hatchard et al., PyBaMM "ORegan2022", and "Finegan et al. 2024, Table 1" for the can thickness. See items 2 and 4 under "What I could not find".
