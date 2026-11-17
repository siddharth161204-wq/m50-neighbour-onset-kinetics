# Stage 14 survey: what published sources give for the paths by which a venting cell can deliver energy to its neighbour

This file is written in two steps. The list of searches below was written and committed before any of them was run. The record of what was found, read and recorded follows it once the searches have been made; the machine-readable record is `results/stage14_survey.json`, and every value that enters a bound is in `results/stage14_inputs.csv`.

## What is looked for

For cells of this format (21700) and chemistry (a nickel-rich layered oxide positive and a graphite or silicon-graphite negative) at full charge where such data exist, and otherwise for the nearest cells, each labelled as measured on another cell:

1. the amount and composition of the vent gas;
2. its temperature at the vent;
3. the split of the ejected mass between gas, liquid and solids, and the temperature of the solids;
4. the duration of the jet and its velocity or mass-flow history;
5. the heat of combustion of the gas, and whether it burns in a rig such as the one of Fransson et al. (2024);
6. the radiant fraction of such flames, or a radiant flux measured near a venting cell;
7. any heat flux or deposited energy measured at a neighbouring cell's position;
8. the relations for a jet striking a cylinder and for flow past one;
9. for the rig itself: the holder, its material and what touches the neighbour, the enclosure and its atmosphere, and the references Fransson et al. give for the chamber and the holder;
10. for the parallel tests: the cell's internal resistance, the resistance of the tabs and of the trigger's internal short, the duration of the short, and any current or voltage measured in parallel-connected cells during a neighbour's failure;
11. where a sidewall breaches and how often, for this cell;
12. the emissivity of the cans' black carbon paint.

## The searches, written before any was run

Each is a query for the web search tool. A search added after this list was run is recorded below the list with the reason it was added.

The rig and its references
1. "Exploring thermal runaway propagation in Li-ion batteries through high-speed X-ray imaging and thermal analysis" supplementary material
2. in situ test chamber battery failure high-speed synchrotron X-ray imaging ESRF nail penetration Pfaff Schopferer
3. cell holder stacking cylindrical cells high-speed X-ray radiography thermal runaway propagation ESRF ID19
4. Fransson Finegan Shearing thermal runaway propagation 21700 high-speed radiography cell holder CO2

What the calorimeter counts
5. Walker Darst Finegan 2019 "Decoupling of heat generated from ejected and non-ejected contents" 18650
6. fractional thermal runaway calorimeter ejecta mating assembly combustion nitrogen purge copper mesh
7. "Battery Failure Databank" Finegan 2024 open access 234106

The vent gas's amount and composition
8. LG M50 INR21700 thermal runaway vent gas composition
9. 21700 NMC811 thermal runaway gas volume composition full charge
10. high-nickel cylindrical 21700 thermal runaway gas generation mmol hydrogen carbon monoxide
11. Baird Archibald Marr Ezekoye 2020 explosion hazards from lithium-ion battery vent gas
12. Golubkov 2014 thermal runaway experiments consumer Li-ion batteries metal-oxide olivine cathodes vent gas

The gas's temperature at the vent
13. 21700 thermal runaway jet temperature measured at vent thermocouple
14. cylindrical lithium-ion cell venting gas temperature cap thermocouple NMC full charge

The split of the ejected mass, and the solids
15. 21700 thermal runaway ejecta particles mass fraction gas solid NMC811
16. thermal runaway ejected particles temperature measurement cylindrical cell
17. thermal runaway ejecta particle size distribution 18650 21700 composition

The jet's duration and its velocity or mass flow
18. 21700 lithium-ion cell venting jet velocity high-speed schlieren
19. 18650 venting mass flow rate thermal runaway measured duration
20. Mier Hargather 18650 vent mechanism flow parameters

The heat of combustion, and whether the gas burns
21. heat of combustion lithium-ion battery vent gas NMC kJ per cell
22. lithium-ion vent gas limiting oxygen concentration CO2 dilution flammability
23. thermal runaway jet fire ignition reduced oxygen CO2 atmosphere chamber

The radiant fraction, or a measured radiant flux
24. lithium-ion battery jet fire radiant heat flux measurement 21700
25. 18650 thermal runaway jet flame radiation heat flux gauge distance
26. radiative fraction turbulent jet flame hydrogen methane mixture correlation

A heat flux or deposited energy at a neighbour's position
27. heat flux measured adjacent cell thermal runaway propagation cylindrical
28. heat transfer pathways thermal runaway propagation 18650 module jet fire contribution quantitative
29. 21700 module thermal runaway propagation heat flux sensor between cells

A jet striking a cylinder, and flow past one
30. heat transfer round jet impinging on circular cylinder correlation average Nusselt number
31. slot jet impinging on circular cylinder heat transfer correlation
32. Churchill Bernstein correlation circular cylinder cross flow

Where and how often a sidewall breaches
33. LG M50 sidewall rupture nail penetration frequency
34. Read Jones Marco 2024 sidewall rupture propensity thermal runaway propagation small module
35. sidewall breach location cylindrical cell thermal runaway radiography 21700 nail

Solids and melt on the neighbour
36. molten aluminium droplets thermal runaway ejecta deposition adjacent cell
37. thermal runaway ejecta deposition heat transfer neighbouring cell experiment

The circuit of the parallel tests
38. parallel connected cells thermal runaway current neighbouring cell discharge nail penetration
39. LG M50 INR21700 internal resistance DC pulse
40. nail penetration internal short circuit resistance measured cylindrical cell
41. LG INR21700 M50 current interrupt device CID

The surface
42. emissivity carbon black paint surface
43. LG M50 can material nickel-plated steel emissivity

Besides the searches, the sources already named by the repository's decisions and manuscript (Fransson et al. 2024 and its supplement; Finegan et al. 2024; Walker et al. 2019; Read, Jones and Marco 2024; Read et al. 2024; Allen et al. 2025; Kim et al. 2021; Said et al. 2019; Coman et al. 2017; Torres-Castro et al. 2020; Lienhard and Lienhard 2024; Bergman et al. 2011), the Project's own files and the author's folder of downloaded references are read where they bear on a path.

## The record, written after the searches

The 43 searches were run on 16 November 2026 with the web search tool (standard mode), after the list above had been committed (c8172e2) and pushed (11:13:23 UTC). The candidate sources each returned are in `results/stage14_survey.json` (`searches_run`), with every source read, how it was read, under what conditions, and what it gave and did not give (`sources`). One search was added, to find the full reference of a resistance study that a page found under search 39 cites (Popp et al. 2020). The shell of this machine cannot reach most publishers, so web sources were read through a text reader; the supplement, the 2023 manuscript, the Databank's workbook and Lienhard's textbook were downloaded by the author and read here in full. Walker et al. (2019) and Abbott et al. (2022) are behind subscriptions and were not read.

What was found, item by item. A value measured on another cell is marked so; it widens a range and sets no value for this cell.

1. The vent gas's amount and composition: 6.5 l at 100 % state of charge from a 21700 NMC811 cell, more than half hydrogen and CO2 (Abbott et al., through the vendor's summary; other cell or model not named); 0.53 mol from a 4.8 Ah 21700 NMC cell, 22 % hydrogen, 17.7 % CO, 42.3 % CO2, 14.8 % methane (Vendra et al., other cell). For this cell, the calorimetry's unrecovered mass, "mostly gas and smoke", is 12.13 to 22.81 g.
2. The gas's temperature at the vent: no measurement found for this format. Internal temperatures up to 1109.3 C (Vendra et al., other cell); this cell's trigger surface reached 1051.5 to 1248.1 C in tests with a rupture (Read et al.).
3. The split of the ejected mass and the solids' temperature: for this cell, 33.51 to 48.85 g left the cell body and 12.13 to 22.81 g of it was not recovered (Databank); molten copper was seen in 90 % of the LG 21700 tests (Sharp et al.). No temperature of the ejected solids was found.
4. The jet's duration and velocity: peak gas velocities of 398.5 and 260.9 m/s, and a measured runaway of 1.131 +- 0.291 s for the first, for two 18650 cells (Gillich et al., other cells); about 150 m/s at an 18650 jet's leading edge (Mier et al.); combustion of 11.1 to 16.3 s (Chen et al. 2020), a jet fire of about 110 s and combustion of about 5 min (Chen et al. 2023), all on other 21700 cells. No velocity for a 21700 vent was found.
5. The heat of combustion and whether the gas burns: 96.2 to 136.5 kJ of heat released in open air by a 4.8 Ah 21700 NMC cell (Vendra et al., other cell; the printed parts of the 136.5 kJ sum to 127.3 kJ); the energy of burning the vent gas of LCO cells, calculated for complete combustion (Karp and Sica). In this rig, in a 15 % CO2 atmosphere, fire was seen at the vent (Fransson et al. pp. 6 to 8), though no sentence ties a fire to an M50 test by name. The calorimetry of the Databank does not hold the heat of burning the escaped gas in air (DECISIONS D150 (3)).
6. The radiant fraction, or a radiant flux: no radiant fraction for a battery vent flame was found. 150 mm from venting LFP cells, the first flaming event gave about 50 to 150 kW/m2 for most cells, and the 26650 cells' later peaks 350 to 500 kW/m2 (Lugaresi et al., other cells). Flame temperatures as high as 1069 C for single cells and 1500 C for a module are cited by Chen et al. (2020).
7. A heat flux or deposited energy at a neighbour's place: none found for cylindrical cells. For 25 Ah prismatic cells in a module, the fire carried 162 J of the heat that reached the neighbour against 68.9 kJ through the shell (Feng et al., other cells). With an LG M50 trigger whose sidewall ruptured, a jet fire struck the neighbours, which ran away 2 to 5 s later (Read et al.).
8. Relations: Churchill and Bernstein for a cylinder in cross flow, with its stated accuracy (Lienhard, pp. 390 to 391); for round jets on a cylinder, Csernyei and Straatman (Eq. 16, p. 302, for Reynolds numbers of 2.06e5 to 1.236e6), which no breach's jet can be set in, since no source gives its opening, velocity or distance; Olsson et al. for slot jets (abstract only).
9. The rig: the holder is an aluminium frame with 3D-printed inserts touching each cell over about 2 mm (Pfaff et al.); the supplement's Figure 9(b) shows it, with the trigger above. The inserts' material is not given.
10. The circuit: the datasheet's DC resistance, 30 +- 6 mOhm at 25 C, and AC impedance of at most 25 mOhm; the resistance falls about fivefold from 10 to 45 C (Popp et al.); the stored energy at full charge, 18.2 Wh. No current or voltage of parallel cells during a neighbour's failure, and no resistance of a nail's short, was found.
11. Where and how often a sidewall breaches, for this cell: in 3 of the 16 tests of the rig, all in trigger cells (category 4); in none of the Databank's 10 nail tests; in 3 of 3 tests with a 35 mm nail through the positive terminal and in none with 10 mm, on the bottom half of the casing (Read et al.). On other cells: 2 of 6 at 6 mm/s, 1 of 5 at 0.5 mm/s and 4 of 5 at 100 mm/s (Chen et al. 2023), and 1.1 to 5.2 % (NASA).
12. The paint's emissivity: 0.972 +- 0.012 at 8 to 14 um for a high-emissivity black paint (Cardenas-Garcia et al.), not the rig's carbon paint; no absorptivity for flame radiation was found.

What no source gives, and so what each bound lacks, is listed in the JSON (`not_found`).

## The second reading

A separate agent read every recorded value again at its source (check V1; DECISIONS D152 (3)), on 16 and 17 November: of the 89 rows of `results/stage14_inputs.csv`, 71 agree, 17 needed a correction and one cites no source (the radiant fraction's cap of 1, a limit). Its account and its row-by-row findings are `results/stage14_v1_second_reading.md` and `.csv`. The corrections were applied before the predictions were pushed; the items above are written as corrected. The one that moves a number used later is the shortest published runaway, Gillich et al.'s measured 1.131 +- 0.291 s rather than the bound of 1.5 s, which moves the lower end of the time bounds to 0.84 s.
