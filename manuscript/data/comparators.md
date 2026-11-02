# Comparators: energy partition and cell-to-cell propagation times

Collected on 2 November 2026 for the Discussion. Every number below was read on the page named under "Sources read" for that paper. Nothing comes from memory.

How to read this file:

- Quotes are verbatim and at most 40 words. "[...]" marks a cut.
- The page reader returns long sentences in pieces. Quotes marked "(joined)" were returned as consecutive pieces and are printed here joined with a single space. Check those against the PDF before final citation.
- Superscripts were lost in some PDF extractions (for example "4 × 105 Wm−2" means 4 × 10^5 W m^-2). Quotes keep the extracted form; the plain value is given beside them.
- "My arithmetic" marks a number I derived. The paper does not print it.
- Access: FULL means the full text was read (open-access version of record or the authors' repository copy). ABSTRACT means only the abstract could be read. Failed attempts are listed under each paper.

## At a glance

| # | Paper | DOI | Read | Most relevant numbers |
|---|---|---|---|---|
| 1 | Feng et al. 2015, Appl. Energy 154, 74-91 | 10.1016/j.apenergy.2015.04.118 | ABSTRACT | No propagation times or heat shares in the abstract. Thresholds that stop propagation in a 6-cell model of fully charged 25 Ah NCM cells: trigger temperature above 469 °C; short-circuit electric energy at 75% or less of its original value; h above 70 W m-2 K-1; 1 mm layer with k below 0.2 W m-1 K-1 |
| 2 | Coman et al. 2017, J. Electrochem. Soc. 164, A587-A593 | 10.1149/2.0341704jes | ABSTRACT | 28% of the electrical energy leaves with the effluent (18650 NCA/graphite, 2.4 Ah, internal short circuit device). The efficiency factor value is not in the abstract (72% retained is my arithmetic) |
| 3 | Walker et al. 2019, J. Power Sources 415, 207-218 | 10.1016/j.jpowsour.2018.10.099 | ABSTRACT | 20% to 30% of the total energy goes out through the cell casing, the rest through the ejecta (18650 cells of many makes) |
| 4 | Kim et al. 2021, J. Power Sources 489 | not verified | ABSTRACT | No numbers in the abstract. Higher SOC gives more heat and gas, higher internal pressure and more risk of sidewall breaching |
| 5 | Mishra and Jain 2021, J. Electrochem. Soc. 168, 020504 | 10.1149/1945-7111/abdc7b | FULL | Neighbours reach runaway about 40 s and 90 s after the trigger cell with natural convection modelled, and 95 s and 310 s without it (simulated 5 by 5 array of 18650 cells, 1 mm air gap, heater trigger). No energy fraction |
| 6 | Hoelle et al. 2023, J. Electrochem. Soc. 170, 060516 | 10.1149/1945-7111/acd966 | ABSTRACT | No times in the abstract. A gas layer between jelly roll and can is "crucial to reproduce experimental results" (stack of 5 prismatic cells above 60 Ah) |
| 7 | Lamb et al. 2015, J. Power Sources 283, 517-523 | 10.1016/j.jpowsour.2014.10.081 | ABSTRACT | Pouch modules with cells in contact: the whole battery failed within 60 to 80 s, in series or parallel. 18650 modules: 10S1P did not propagate; 1S10P was consumed "minutes after" the trigger |
| 8 | Said et al. 2019, Appl. Energy 248, 415-428 | 10.1016/j.apenergy.2019.04.141 | ABSTRACT | Row-to-row speed 0.08 s-1 in nitrogen and 0.7 s-1 in air. Chemical heat 56.6 ± 2.5 kJ per cell; flaming combustion of ejecta 60.1 ± 17.5 kJ per cell (LCO 18650, 2.6 Ah, fully charged) |
| 9 | Finegan et al. 2024, J. Power Sources 597, 234106 | 10.1016/j.jpowsour.2024.234106 | FULL | No body versus ejecta percentage is printed. Ejected mass gives about 2.6 kJ/g against 0.21 kJ/g for the cell body; 50% to 85% of cell mass is ejected; 100% SOC |
| 10 | Read, Jones, Marco 2024, J. Power Sources Adv. 30, 100162 | 10.1016/j.powera.2024.100162 | FULL | LG INR21700-M50, 100% SOC, 7 cells, 3 mm gaps, nail trigger. With sidewall rupture all six neighbours went into runaway 2 to 5 s after penetration; without rupture there was no propagation |
| 11 | Fransson et al. 2024, J. Power Sources 617, 234916 | 10.1016/j.jpowsour.2024.234916 | FULL | No heat transferred or fraction is reported. Propagation needed at least 150 °C in the neighbour; mean heating rate 0.4 °C/s in propagating cells against 0.1 in non-propagating ones. M50 times 147 to 342 s; P42A times 123 to 464 s (two cells in contact, nail trigger) |
| 12 | Feng et al. 2018, Energy Storage Mater. 10, 246-267 | 10.1016/j.ensm.2017.05.013 | ABSTRACT | Nothing relevant in the abstract; the full text could not be reached |

## Points to carry into the Discussion

1. None of the papers I could read reports the fraction of a failing cell's energy that ends up in a neighbour. The closest numbers are: the energy that leaves through the casing versus the ejecta (paper 3); electrical energy that leaves with the effluent (paper 2); the absolute heat from flaming ejecta versus in-cell chemistry (paper 8); and heat per gram of body versus ejecta (paper 9). The full text of paper 6 might have such a number, but it could not be read.
2. These energy numbers do not share a basis. Paper 3 gives a share of total thermal runaway heat. Paper 2 gives a share of the electrical energy only. Paper 8 gives absolute kJ per cell. Paper 9 gives fitted kJ per gram. Paper 9's slopes should not be turned into a body share: they are slopes of heat against mass, not averages, and the paper does not make that conversion.
3. Propagation times are also measured from different starting events:
   - Paper 10 measures from nail penetration, which it takes as the trigger cell's runaway onset, to the onset in the neighbour: 2 to 5 s.
   - Paper 11 does not state its start point. The text implies trigger-cell runaway to neighbour runaway: 123 to 464 s.
   - Paper 5 (simulations) measures from trigger-cell runaway to neighbour runaway: 40 to 310 s.
   - Paper 7 gives the time to consume the whole module: 60 to 80 s for pouch modules.
   - Paper 8 gives a row-to-row speed in s-1.
4. The 147 to 342 s range in the brief is the LG M50 subset of paper 11. P42A cells propagated as fast as 123 s. By its tables the paper's overall range is 123 to 464 s, but its conclusion says 467 s, so the paper is inconsistent with itself there.
5. A correction to the brief: the first author of paper 10 is Elliott Read (E. Read), not J. Read. The authors are Elliott Read, Simon Jones and James Marco.
6. Paper 10 also states that nail penetration sends a higher fraction of the energy out through the casing than thermal abuse does, citing W.Q. Walker et al., J. Power Sources 2022, "The effect of cell geometry and trigger method on the risks associated with thermal runaway of lithium-ion batteries". I have not read that paper. If a trigger-dependent casing share is needed, it is the paper to read.

---

## 1. Feng, He, Ouyang, Lu, Wu, Kulp, Prasser 2015, Applied Energy 154, 74-91

- Title: "Thermal runaway propagation model for designing a safer battery pack with 25Ah LiNixCoyMnzO2 large format lithium ion battery"
- DOI: 10.1016/j.apenergy.2015.04.118 (read on the IDEAS record)
- Read: ABSTRACT only.
- Sources read:
  - S1: https://ideas.repec.org/a/eee/appene/v154y2015icp74-91.html (abstract)
- Failed: no open full text turned up in two searches. The University of Michigan PDF that the search returned (https://public.websites.umich.edu/~racelab/static/Webpublication/2015-JPS-XuningF.pdf) is a different paper: Feng et al., J. Power Sources 275 (2015) 261-273, 10.1016/j.jpowsour.2014.11.017, on penetration-induced propagation in a module. I did not extract numbers from it.
- Conditions in the abstract: a lumped thermal model of a module of six fully charged 25 Ah NCM (LiNixCoyMnzO2) large-format cells. The trigger is not stated in the abstract.

Numbers:

- Model setup, 6 fully charged cells (S1, joined): "The TR propagation model consists of 6 fully-charged single batteries connected through thermal resistances and can fit experiment data well."
- Thresholds 469 °C and 75% (S1, joined): "(1) raise the TR triggering temperature to higher than 469°C; (2) reduce the total electric energy released during massive internal short circuit to 75% or less of its original value;"
  - The 75% is a design target for the short-circuit electrical energy. It is not a measured energy partition.
- Thresholds 70 W m-2 K-1, 1 mm and 0.2 W m-1 K-1 (S1, joined): "(3) enhance the heat dissipation by increasing the heat dissipation coefficient to higher than 70Wm−2K−1; (4) add extra thermal resistant layers between adjacent batteries with a thickness of 1mm and a thermal conductivity less than 0.2Wm−1K−1."
- Delay versus prevention (S1, joined): "it might be better to choose proper parameters that help prevent TR propagation rather than just postpone it, because a delay in the TR propagation process leads to a higher level of heat gathering which may cause severer thermal hazards"
- Experimental check (S1, joined): "One implementation, which is verified by experiment, is to insert thermal resistant layer between adjacent batteries to prevent TR propagation in the battery module."

Not found in what could be read: propagation times, neighbour temperatures, and the share of heat transferred.

## 2. Coman, Darcy, Veje, White 2017, J. Electrochem. Soc. 164(4), A587-A593

- Title: "Modelling Li-Ion Cell Thermal Runaway Triggered by an Internal Short Circuit Device Using an Efficiency Factor and Arrhenius Formulations"
- DOI: 10.1149/2.0341704jes. It was shown on the Zhenzhi record, and it is the DOI link for this entry on the White group's publication list (https://research.cec.sc.edu/ralph-white/publications?page=2).
- Read: ABSTRACT only.
- Sources read:
  - S1: https://research.cec.sc.edu/ralph-white/publications/modelling-li-ion-cell-thermal-runaway-triggered-internal-short-circuit-device-using (abstract)
  - S2: https://data.zhenzhi.com/details/1/894065170 (abstract, DOI, and the line "(C) The Author(s) 2017. Published by ECS")
- Failed:
  - https://doi.org/10.1149/2.0341704jes was refused by the publisher (robots_disallowed).
  - The IOP Publishing SDG page carried no text.
  - Peeref requires a login.
  - Note: the copyright line suggests the article is open access on the publisher's site, so it can be read in a browser to get the efficiency factor value.
- Conditions: an 18650 NCA/graphite cell, 2.4 Ah, triggered by an implanted internal short circuit device. A 0D and a 3D single-cell model were compared with experiments (paraphrase of S1). SOC is not stated in the abstract.

Numbers and definition:

- Definition fragment (S1): "adding an efficiency factor for the conversion of electric energy into thermal energy"
- Definition (S1, S2): "The efficiency factor also accounts for the energy vented from the cell."
- 28% leaves with the effluent (S1, joined): "It was found that for an 18650 NCA/graphite cell with a 2.4 Ah capacity, 28% of the electrical energy leaves with the effluent."
- Fraction that stays in the cell: the value is not printed in the abstract. If the efficiency factor is the complement of the 28%, it is 72% of the electrical energy (my arithmetic). Note that the share refers to the electrical (short-circuit) energy, not to the total heat of thermal runaway.

Related document (not the paper): Coman's PhD summary at SDU, https://www.sdu.dk/-/media/files/om_sdu/institutter/mci/phd+forsvar/paul_coman_abstract_english.pdf. It gives no value, but it defines the factor as "implementing an efficiency factor term in the energy equation which accounts for the energy leaving with the gas and solids".

## 3. Walker, Darst, Finegan, Bayles, Johnson, Darcy, Rickman 2019, J. Power Sources 415, 207-218

- Title: "Decoupling of Heat Generated from Ejected and Non-Ejected Contents of 18650-Format Lithium-Ion Cells Using Statistical Methods"
- DOI: 10.1016/j.jpowsour.2018.10.099 (read on the NLR/NREL research hub record; NREL ID NREL/JA-5400-73198)
- Read: ABSTRACT only.
- Sources read:
  - S1: https://research-hub.nlr.gov/en/publications/decoupling-of-heat-generated-from-ejected-and-non-ejected-content-2/ (abstract)
  - S1b: https://research-hub.nrel.gov/en/publications/decoupling-of-heat-generated-from-ejected-and-non-ejected-content-2/ (same record)
- Failed: no open full text was found. The record links only to the DOI and Scopus.
- Conditions: fractional thermal runaway calorimetry (FTRC) on 18650 cells of several makes, chemistries, capacities and safety features. The abstract does not state SOC or trigger (see the related slides below).

Numbers:

- Casing versus ejecta (S1, joined): "Typically 20%–30% of the total energy yield is released through the cell casing with the remainder through the ejecta material."
  - The ejecta share is therefore 70% to 80% of the total (my arithmetic, from "the remainder").
- Cells tested (S1, joined): "was utilized to examine the TR behavior of 18650-format Li-ion cells representing a variety of manufacturers, chemistries, capacities, and safety features."
- Design variables (S1, joined): "Primarily, the impacts of bottom vent (BV) safety features, varied cell casing thickness, and Dreamweaver cellulose based separators were assessed for select cell types."
- Bottom vents (S1): "Inclusion of a BV feature reduces the overall severity of the TR event and can increase the predictability."
- Statistics (S1, joined): "Statistical analysis of the results for each cell configuration reveals that a lognormal distribution effectively characterizes the variation of total TR energy release."

Not found in the abstract: casing fractions per cell type.

Related document (same authors, not the paper): NASA JSC slides "Coupling Fractional Thermal Runaway Calorimetry (FTRC) Results with Statistical Analysis Methods", https://ntrs.nasa.gov/api/citations/20190000824/downloads/20190000824.pdf. The slides say the analysis was "submitted to J. Power Sources August 2018". They list LG MJ1, Sony VC7, an LG test cell, Panasonic BE, LG HG2, Samsung 30Q, LG HE2 and Molicel J 18650 cells.

- "Standard cells typically release 20-30% through the cell casing and the remainder through the ejecta material"
- "Bottom vent cells tend to release the energy in a three-way split between the casing and the top and bottom ejecta materials"
- "All cells were tested at 100% state of charge"
- "Most experiments are conducted with high flux heaters for a trigger mechanism"

## 4. Kim, Mallarapu, Finegan, Santhanagopalan 2021, J. Power Sources 489

- Title: "Modeling cell venting and gas-phase reactions in 18650 lithium ion batteries during thermal runaway"
- DOI: NOT VERIFIED. The OSTI record shows no DOI or article number. It gives J. Power Sources volume 489, OSTI ID 1772455 (alternate 1811053) and report number NREL/JA--5700-78814.
- Read: ABSTRACT only.
- Sources read:
  - S1: https://www.osti.gov/biblio/1811053 (abstract)
- Failed:
  - The OSTI record has no full-text link.
  - Peeref requires a login.
  - Two search hits were other papers: https://core.ac.uk/download/519717661.pdf is Sharp et al. 2022, J. Electrochem. Soc., and https://www.osti.gov/servlets/purl/2002464 is Qatramez et al., ASME 2022.
  - The DOE Code record (https://www.osti.gov/doecode/biblio/58096) is the software, with DOI 10.11578/dc.20210805.2.
- Conditions: CFD of a single 18650 cell at several SOCs, with a single-step lumped reaction model.

Numbers and statements:

- SOC cases (S1): "Then, a series of computational fluid dynamics (CFD) simulations are conducted on a single 18650 cell at various states-of-charge (100%, 50%, 25%)"
- Model (S1): "Thermal abuse reactions and gas generation kinetics are described by a single-step lumped reaction model."
- Stages (S1): "Venting events are categorized into two stages: i) breaching of the cell container and ii) thermal runaway reactions."
- Gas mostly generated during thermal runaway (S1, joined): "It is found that the cell response is dominated by the second stage since most of the gases are generated during thermal runaway."
- SOC effect (S1, joined): "Cells at higher SOCs produce more heat and gas during the venting event, owing to higher mass and concentrations of reacting gases, and consequently reach higher internal cell pressures which increase the risk of side-wall breaching."

Not found in what could be read: any share of energy carried by vent gas, heat released by gas-phase reactions, vent gas temperatures, or times. The abstract has none, and the full text was not reached.

## 5. Mishra and Jain 2021, J. Electrochem. Soc. 168, 020504

- Title: "Multi-Mode Heat Transfer Simulations of the Onset and Propagation of Thermal Runaway in a Pack of Cylindrical Li-Ion Cells"
- DOI: 10.1149/1945-7111/abdc7b (printed on the authors' copy)
- Read: FULL, from the authors' lab copy.
- Sources read:
  - S1: https://mtl.uta.edu/files/2021/02/Mishra-JECS2021.pdf, which redirects to https://bpb-us-e1.wpmucdn.com/websites.uta.edu/dist/0/4801/files/2021/02/Mishra-JECS2021.pdf
- Conditions:
  - Finite-volume simulation of a 5 by 5 array of 18650 cells with the trigger cell at a corner and a sleeve heater on the trigger cell.
  - Heat comes from four decomposition reactions. No cathode chemistry is named in the parts I extracted.
  - The Fig. 13 case used a 1 mm gap, interstitial k of 0.02 W m-1 K-1 (air), external h of 10 W m-2 K-1, and heating at 4 × 10^5 W m-2 from 0 to 400 s.

Numbers:

- With natural convection, 40 s and 90 s (S1, joined): "For example, as shown in Fig. 13a, the neighboring cells 2 and 7 enter thermal runaway roughly 40 s and 90 s after runaway in the trigger cell when natural convection is modeled."
- Without natural convection, 95 s and 310 s (S1, joined): "[...] when natural convection is not accounted for, the reduced inter-cell heat transfer causes a delay in thermal runaway propagation [...] cells 2 and 7 now enter thermal runaway 95 s and 310 s after runaway in the trigger cell"
- Fig. 13 conditions (S1, caption, joined; "105" is 10^5): "[...] the cell-to-cell is 1 mm, thermal conductivity of interstitial material is 0.02 Wm−1 K−1, external convective heat transfer coefficient is 10 Wm−2 K−1, trigger cell is at a corner, and heating rate is 4 × 105 Wm−2 for 0–400 s."
  - "cell-to-cell" is printed this way in the extraction and presumably means the gap.
  - Elsewhere the paper uses a 4 mm gap for other cases: "In these simulations, the cell-to-cell gap is held constant at 4 mm".
- Radiation (S1, joined): "This shows that radiation modeling is of critical importance, and that neglecting radiation may result in an erroneous prediction of no thermal runaway propagation"
  - I did not pin down which heating case this radiation comparison used. Other cases in the paper include 5 × 10^5 W m-2 for 400 s with adiabatic outer walls, and 3 × 10^5 W m-2 with adiabatic walls.
- Natural convection (S1, joined): "Thermal runaway is found to propagate both with and without natural convection. However, when natural convection is not modeled, a milder propagation is predicted."
- Abstract (S1): "Finally, it is shown that radiation and natural convection play a key role in thermal runaway propagation."
- Pack (S1, joined): "Finite-volume simulations are carried out on a 5 by 5 array of 18650 cells surrounded by an interstitial material with a uniform gap between cells."
- Trigger (S1, joined): "A 1 mm thick heater is wrapped around one of the cells, referred to as the trigger cell."
- Chemistry (S1): "Heat generation due to four specific decomposition reactions are considered"

Not found: any fraction of the failing cell's energy that goes to neighbours, and any split of the heat between radiation, convection and conduction in W, J or percent. The paper compares these modes only by switching them on and off.

## 6. Hoelle, Zimmermann, Hinrichsen 2023, J. Electrochem. Soc. 170(6), 060516

- Title: "3D Thermal Simulation of Thermal Runaway Propagation in Lithium-Ion Battery Cell Stack: Review and Comparison of Modeling Approaches"
- DOI: 10.1149/1945-7111/acd966 (read on the TUM research portal)
- Read: ABSTRACT only.
- Sources read:
  - S1: https://portal.fis.tum.de/en/publications/3d-thermal-simulation-of-thermal-runaway-propagation-in-lithium-i/ (abstract)
- Failed:
  - https://doi.org/10.1149/1945-7111/acd966 was refused by the publisher (robots_disallowed).
  - mediaTUM (https://mediatum.ub.tum.de/node?id=1716549 and https://mediatum.ub.tum.de/doc/1744027/1744027.pdf) returned a bot-protection "access denied" page.
- Conditions: an experiment on a stack of five prismatic cells above 60 Ah. Chemistry, SOC and trigger are not given in the abstract.

Statements:

- Stack (S1): "a battery cell stack experiment consisting of five prismatic lithium-ion batteries (>60 Ah)"
- Gas layer (S1, joined): "the proposed model takes into account detailed phenomena such as the formation of a gas layer between jelly roll and cell can due to electrolyte vaporization which is crucial to reproduce experimental results."
- Approaches (S1, joined): "Only two of the three modeling approaches are suitable for TR propagation simulation of the cell stack experiment investigated in this study."
- Approaches (S1): "These approaches either use time-dependent or spatially resolved temperature-dependent heat release rates."

Not found, because the full text could not be read: propagation times between cells in the experiment or the models, and the size of the gas layer's effect.

## 7. Lamb, Orendorff, Steele, Spangler 2015, J. Power Sources 283, 517-523

- Title: "Failure propagation in multi-cell lithium ion batteries"
- DOI: 10.1016/j.jpowsour.2014.10.081 (read on the Sandia publication page; SAND2014-17489J)
- Read: ABSTRACT only.
- Sources read:
  - S1: https://www.osti.gov/servlets/purl/1235277 (OSTI record, abstract only)
  - S2: https://sandia.gov/research/publications/details/failure-propagation-in-multi-cell-lithium-ion-batteries-2015-06-01 (metadata and DOI)
- Failed: the OSTI record holds no manuscript text, and no other copy was found.
- Conditions in the abstract: small modules of cylindrical cells and of stacked pouch cells. Runaway was started in one cell by nail penetration. Chemistry, capacity and SOC are not in the abstract.

Numbers:

- Cylindrical, limited contact (S1, joined): "Cylindrical cells are observed to be less prone to propagate, if failure propagates at all, owing to the limited contact between neighboring cells."
- Series versus parallel (S1, joined): "[...] the electrical connectivity is found to be impactful as the 10S1P cylindrical cell module did not show failure propagation through the module, while the 1S10P module had an energetic thermal runaway consuming the module minutes after the initiation failure trigger."
- Pouch (S1): "Modules built using pouch cells conversely showed the impact of strong heat transfer between cells."
- Pouch, 60 to 80 s (S1, joined): "In this case, a large surface area of the cells was in direct contact with its neighbors, allowing failure to propagate through the entire battery within 60-80 seconds for all configurations (parallel or series) tested."
- Trigger (S1): "after thermal runaway is induced in a single cell through nail penetration trigger [1] within the module."
- Spaced (gapped) arrangements are not described in the abstract. The contrast it draws is limited contact (cylindrical) against large-area direct contact (pouch).

Related document (same authors, not the paper): Sandia report SAND2014-17053, "Propagation Testing Multi-Cell Batteries" (Orendorff, Lamb, Steele, Spangler, October 2014), https://www.osti.gov/servlets/purl/1177076. Its configurations (10S1P and 1S10P 18650; 5S1P and 1S5P pouch) match the paper's, but the report does not say it is the basis of the paper. The quotes below are short verbatim fragments.

- 18650 cells: "built using commercial-off-the-shelf 2.2 Ah 18650 cells." Chemistry: LiCoO2/graphite (Table 3, per the reader).
- Pouch cells: "built using commercial-off-the-shelf 3.0 Ah pouch cells." Chemistry: LiCoO2/graphite (Table 3, per the reader).
- SOC: "All tests are performed at 100% SOC at 25 °C"
- 10S1P: "there is no evidence of thermal runaway in any cell other than Cell 6."
- 10S1P: "Approximately 15 seconds after the initiation, an electrolyte fire ignites"
- 1S10P: "Pack voltage is lost at approximately 200 s (Figure 12)."
- 1S10P: "At approximately 420 s, Cells 2 and 9 go into an energetic thermal runaway,"
- 1S10P: "this failure quickly propagates through the rest of the battery (approximately 290 s after the initiation at Cell 6)."
- 5S1P, initiated at the end cell: "The total propagation time is approximately 80 s."
- 5S1P, initiated at the centre cell: "over the course of approximately 60 s."
- 1S5P: "However, the propagation times through both batteries are comparable (approximately 50-60 s)."
- Pouch heat path: "dominated by heat transfer from cell-to-cell because of the good thermal contact over the largest surface area of the cells."
- The report does not describe cell spacing.
- Trigger (paraphrase by the reader): cylindrical cells were nailed axially from the bottom, pouch cells through the edge.

## 8. Said, Lee, Stoliarov, Marshall 2019, Applied Energy 248, 415-428

- Title: "Comprehensive analysis of dynamics and hazards associated with cascading failure in 18650 lithium ion cell arrays"
- DOI: 10.1016/j.apenergy.2019.04.141 (read on the IDEAS record)
- Read: ABSTRACT only.
- Sources read:
  - S1: https://ideas.repec.org/a/eee/appene/v248y2019icp415-428.html (abstract)
- Failed:
  - The ScienceDirect link on the IDEAS page (http://www.sciencedirect.com/science/article/pii/S0306261919307561) was refused (client_error).
  - The core.ac.uk PDF returned by the search is C. Lee's 2018 MS thesis, not the paper.
  - The DRUM item is A. Said's 2020 PhD dissertation; I did not read it.
- Conditions: arrays of 12 to 18 LCO 18650 cells, 2.6 Ah, fully charged, in a wind tunnel under nitrogen or air. Runaway was started in one cell by a small electric heater.

Numbers:

- Cells and arrays (S1, joined): "using 12–18 cell arrays constructed from lithium cobalt oxide (LCO) cells of 18650 form factor and 2600 mA h nominal electrical capacity."
- SOC and setup (S1, joined): "The arrays, consisting of fully charged cells, were mounted in a specially designed wind tunnel, which provided well controlled environmental conditions."
- Trigger (S1, joined): "Thermal runaway was initiated in one cell using a small electric heater and observed to propagate through the array using temperature sensors attached to individual cells."
- Speed in nitrogen (S1, joined): "In the nitrogen tests, row-to-row propagation speed (SP) showed no significant dependence on the size of the array and was estimated to be 0.08 s−1."
  - About 12.5 s per row (my arithmetic, 1/0.08).
- Speed in air, the role of flaming ejecta (S1, joined): "When cell arrays were tested in air, SP increased to 0.7 s−1 (about 9 times the nitrogen value) in late stages of cascading failure due to the impact of flaming combustion of ejected materials."
  - About 1.4 s per row (my arithmetic, 1/0.7).
- In-cell chemistry (S1, joined): "The chemical heat generation resulting from reactions between battery materials inside and outside the bodies of cells was computed to be 56.6 ± 2.5 kJ per cell."
- Flaming ejecta (S1, joined): "The total amount of heat released from flaming combustion of ejected battery materials during air tests was found to be 60.1 ± 17.5 kJ per cell."
- Combustion efficiency (S1): "The efficiency with which these battery materials were combusted was estimated to be about 56%."
- Share released by flaming ejecta: about 51% of the total in air, from 60.1 / (56.6 + 60.1) (my arithmetic). Note that the two heats come from different atmospheres (chemical heat from nitrogen tests, flaming heat from air tests).

Not found in the abstract: the heat transferred to neighbouring cells.

Related documents (not the paper; do not cite as the paper):

- C. P. Lee, 2018 MS thesis, University of Maryland, "Analysis and Quantification of Hazards Associated with Cascading Thermal Runaway Propagation in Lithium Ion Battery Cell Arrays", https://core.ac.uk/download/212855071.pdf. It covers Tenergy ICR18650 LCO cells of 2600 mAh. The conduction-share passage comes from 15-cell arrays at 100% SOC in nitrogen, comparing a 5 mm gap with no gap.
  - Conduction share (joined): "conduction only contributed about one third of the overall heating before thermal runaway of row 3 and about one fourth of the overall heating after thermal runaway of row 3."
  - "failure propagation speed was 7.5 times faster in air than in nitrogen,"
  - "8.5 times slower at 50% SOC than at 100% SOC,"
  - The thesis's energy values differ slightly from the paper's: about 59 kJ chemical and 62.8 ± 18.4 kJ flaming per cell.
- Said, Lee, Stoliarov, conference abstract "Experimental Investigation of Cascading Failure in 18650 Lithium Ion Cell Arrays: Impact of Cathode Chemistry", https://www.fire.tc.faa.gov/2019Conference/files/Battery_IV/SaidFailureLithiumIonCell/SaidFailureLithiumIonCellAbs.pdf. The document itself gives no venue or year.
  - "the row-to-row thermal runaway propagation speed increased by factors of 9, 2, and 7, respectively" (air against nitrogen). I took the order LCO, NMC, LFP from the context, so check it before citing.
  - "was found to be 3.2, 1.9, or 2.5 times greater than the electrical energy stored for LCO, NMC, or LFP cell" (total chemical plus flaming heat against stored electrical energy).

## 9. Finegan et al. 2024, J. Power Sources 597, 234106

- Title: "The battery failure databank: Insights from an open-access database of thermal runaway behaviors of Li-ion cells and a resource for benchmarking risks"
- Authors: Finegan, Billman, Darst, Hughes, Trillo, Sharp, Benson, Pham, Kesuma, Buckwell, Reid, Kirchner-Burles, Fransson, Petrushenko, Heenan, Jervis, Owen, Patel, Broche, Rack, Magdysyuk, Keyser, Walker, Shearing, Darcy.
- DOI: 10.1016/j.jpowsour.2024.234106 (printed on the NREL copy)
- Read: FULL, from the NREL repository copy.
- Sources read:
  - S1: https://nrel.gov/docs/fy24osti/87431.pdf
- Conditions:
  - FTRC tests on commercial or near-commercial cylindrical cells at 100% SOC.
  - Three triggers: heating, heating with an internal short circuit device, and nail penetration.
  - The reader reported 364 FTRC tests and 23 cell types in Table 1 (paraphrase, not a quote).

Numbers:

- Percentage of heat through the body versus the ejecta: NOT REPORTED. I searched the text twice. The methods only say the calorimeter measures "the fractions of heat released through the cell casing and through the ejected material from the positive and negative ends of cylindrical cells." (S1, Section 2.1, joined). Fig. 5 plots heat against mass for each fraction, but the text gives no percentages.
- Per-gram slopes (S1, Section 3.3, joined): "The slopes for the positive and negative ejected masses were 2.41 and 2.82 kJ/g, whereas the slope for the cell body mass was 0.21 kJ/g."
- Interpretation (S1, joined): "This indicates that ejected mass contributes more than 10 × the heat output per gram of material than the mass contained within the cell body"
- Conclusion (S1, joined): "Non-ejected mass emitted around 0.21 kJ/g whereas ejected mass emitted around 2.6 kJ/g, i.e., >10 × more heat per gram was emitted by ejected mass."
- Mass ejected (S1, Section 3.3): "this equated to between 50 and 85 % of each cell's mass being ejected"
  - The sentence does not name cell types. Per the reader, the surrounding text contrasts narrow spreads (Saft VES16, MOLICEL) with wide ones (Samsung 26J, some LG cells).
- Heat per Ah (S1): "Most other cells displayed an average of ~18 kJ/Ah."
- Heat per Ah by cell (S1): "the Sanyo 18650-A showing an average of ~13 kJ/Ah and the LG MJ1 and MOLICEL P28A showing an average of ~25 kJ/Ah"
- SOC (S1): "For this manuscript, we focus on commercial or near-commercial cells at 100 % SOC."
- Triggers (S1, joined): "Thermal runaway was induced for each cell using 3 different methods: (1) thermal abuse, where the cell was heated until thermal runaway occurred, (2) thermal abuse where the cell contained an internal short circuiting (ISC) device"
  - The list ends with "(3) nail penetration abuse."
- Caution: do not turn the slopes and the 50% to 85% ejected mass into a body share. The slopes are fits of heat against mass, not averages, and the paper does not make that conversion.

## 10. Read, Jones, Marco 2024, J. Power Sources Advances 30, 100162

- Title: "The effect of sidewall rupture on the propensity for thermal runaway propagation in a small lithium-ion battery module"
- Authors: Elliott Read, Simon (Benedict) Jones, James Marco. The brief's "Read, J." should be "Read, E."
- DOI: 10.1016/j.powera.2024.100162 (read on the WRAP record)
- Read: FULL, from the open-access (CC BY 4.0) version of record.
- Sources read:
  - S1: https://wrap.warwick.ac.uk/id/eprint/188615/1/1-s2.0-S2666248524000283-main.pdf (record: https://wrap.warwick.ac.uk/id/eprint/188615)
  - S2: https://doaj.org/article/226a3a3225ba491b9e20d477759afcdb (abstract)
- Conditions: LG INR21700-M50, NMC811 with graphite-silicon oxide anode, 4.85 Ah, 100% SOC. Seven cells, not electrically connected, in a hexagonal arrangement with 3 mm gaps, at ambient temperature and pressure. An 8 mm nail went through the positive terminal of the centre cell, at depths of about 10 or 35 mm.

Cell and setup (S1):

- "Commercially available LG INR21700-M50 cells were used for this study."
- "These are high-energy density cells, with a nominal energy and capacity of 18.20 Wh and 4.85 Ah, respectively."
- "The cell chemistry is comprised of a nickel-rich NMC 811 cathode and a graphite-silicon oxide anode."
- "The cells were charged to 100 % state of charge before testing using a constant current constant voltage strategy"
- "For each test, there were 7 cells used in an open circuit configuration, i.e., the cells were not electrically connected."
- "The cells were arranged in a hexagonal packing arrangement, with a 3 mm gap between adjacent cells."
- "Nail penetration was performed using a hydraulic press with an 8 mm stainless steel nail with a 40◦ point angle"
- "The nail penetrated through the positive terminal of the cell in the centre of the test module."
- "The programmed penetration depth varied across the six tests, with values of approximately 10 mm and 35 mm into cell 1"
- "All tests were conducted in the same environmental conditions, at ambient temperature and pressure."

Outcome and times:

- Propagation with rupture (S1, abstract, joined): "In all tests where the trigger cell experienced sidewall rupture, there was thermal runaway propagation to the remaining six cells in the module;"
- No propagation without rupture (S1, abstract, joined): "in all tests where the trigger cell did not experience sidewall rupture, there was no thermal runaway propagation to any other cells in the module."
- Which tests ruptured (S1): "Sidewall rupture is visible on the three trigger cells for tests 4–6, whereas it is absent in the cells for tests 1–3."
- Definition of the time (S1, Table 4 caption, joined): "Thermal runaway propagation speeds for the secondary cells in tests 4–6. The speed is defined by a time difference between TR onset of the secondary cell and the trigger cell, equation (1)."
- Trigger onset (S1, joined): "The TR onset time of the trigger cell can be defined by the time of penetration."
- Table 4 rows (S1, cells 2 to 7, verbatim rows):
  - "Test 4 3 s 4 s 3 s 2 s 2 s 2 s"
  - "Test 5 3 s 3 s 3 s 3 s 5 s 4 s"
  - "Test 6 3 s 2 s 2 s 2 s 2 s 3 s"
  - That is 2 to 5 s from penetration to neighbour onset, for all 18 neighbour cells in the three rupture tests.
- Speed (S1): "The values indicate rapid TR propagation."
- Speed (S1): "TR propagation is so rapid that there is no discernible difference between TR onset for each individual cell."
- Trigger-cell peak surface temperatures for tests 1 to 6 (S1, Table 2 row for cell 1): "315.1 ◦C 582.2 ◦C 595.1 ◦C 1248.1 ◦C 1051.5 ◦C 1118.2 ◦C"
- Neighbours without rupture (S1): "the maximum surface temperatures of the secondary cells for tests 1–3 is below the self-heating onset value"

Heat transfer statements (no number for heat transferred or a fraction; S1):

- "Some heat is transferred via radiation from the hot failed trigger cell body to the adjacent secondary cells"
- "In an open design, most of the radiative heat, Qrad, from the jet fire is directed away from the secondary cells."
- "A rupture on the side of the trigger cell casing impinges jet fire directly on the adjacent secondary cells"
- (joined) "Nail penetration tests are also known to have higher fractions of energy to be released through the cell casing compared to thermal abuse tests [38]."
  - Reference [38] is W.Q. Walker et al., J. Power Sources 2022 (not read).

## 11. Fransson, Pfaff, Broche, Buckwell, Kirchner-Burles, Reid, Schopferer, Rack, Finegan, Shearing 2024, J. Power Sources 617, 234916

- Title: "Exploring thermal runaway propagation in Li-ion batteries through high-speed X-ray imaging and thermal analysis: Impact of cell chemistry and electrical connections"
- DOI: 10.1016/j.jpowsour.2024.234916 (read on the ORA record)
- Read: FULL, from the open-access (CC BY) version of record.
- Sources read:
  - S1: https://ora.ox.ac.uk/objects/uuid:4a6edaf0-c309-40b5-b863-cf32243fa7ec/files/s3t945s923 (record: https://ora.ox.ac.uk/objects/uuid:4a6edaf0-c309-40b5-b863-cf32243fa7ec)
  - S2: https://research-hub.nrel.gov/en/publications/exploring-thermal-runaway-propagation-in-li-ion-batteries-through/ (abstract)
- Conditions:
  - Two 21700 cells (Molicel P42A or LG M50) placed in direct contact, horizontal in a holder, connected in series or parallel by welded tabs, with no enclosure.
  - The trigger cell was nail-penetrated at 6 mm/s to a depth of 1 to 3 mm.
  - 16 tests per cell model, 32 in all.
  - SOC is not stated in the text the reader saw (check the supplementary material).

Heat and fraction:

- No heat transferred and no fraction of energy is reported.
- 150 °C threshold (S1): "In Fig. 3(a) it is observed that a minimum of 150 ◦C is required in the neighboring cell in order for propagation to occur."
- Heating rate (S1, joined): "the average heat rate for propagation to occur was 0.4 ◦C/s compared to 0.1 for non propagating cells and it has been statistically validated that propagation generally occurred in cells experiencing a higher heat rate."
- Conduction (S1): "the dissipated heat is conducted to the propagation cell that heats up"

Times:

- Abstract (S1): "a propagation outcome of 56% was measured from the 32 conducted tests"
- Abstract (S1): "a minimum temperature of 150 °C was required to initiate propagation"
- Abstract (S1): "the fastest propagation occurred in 123 s."
- Conclusion (S1): "The propagation time will determine the time for mitigation, and we measured propagation between 123s and 467s."
  - Table 1's largest value is printed as 464 s, so the paper is inconsistent with itself.
- M50 versus P42A (S1, joined): "The propagation time is consistently shorter for M50, and appears independent of the type of electrical connection since the difference is less prominent."
- Definition: not stated explicitly. The closest statements:
  - (S1) "In this example, propagation occurred 156 s after TR in the trigger cell."
  - (S1) "For experiments with propagation, the second section ends at the onset of the TR in the second cells."
  - These imply a time from trigger-cell runaway to neighbour runaway.
- Table caption (S1, Table 3; Table 4 is the same for series, joined): "Experimental results from M50 Parallel tests, including maximum temperature in both trigger and propagating cell, propagation statistics, time to propagation and assignment to failure category group."
- Test names (S1):
  - "‘PT’ stands for ‘Parallel Trigger’, meaning the cells are connected in parallel and the X-ray FoV cover the trigger cell"
  - "accordingly ‘PP’ refers to parallel connection with X-ray FoV covering the propagating cell."
  - ST and SP are the series equivalents.

Times to propagation in s, as printed in Tables 1 to 4 (S1; "none" means no propagation):

| Cell, connection | Tests (s) | Propagated |
|---|---|---|
| P42A, parallel (Table 1) | PT1 226, PT2 none, PT3 464, PT4 none, PP1 none, PP2 123, PP3 145, PP4 none | 4 of 8 |
| P42A, series (Table 2) | ST1 238, ST2 298, ST3 none, ST4 269, SP1 none, SP2 none, SP3 331, SP4 313 | 5 of 8 |
| M50, parallel (Table 3) | PT1 none, PT2 none, PT3 none, PT4 272, PP1 152, PP2 147, PP3 none, PP4 275 | 4 of 8 |
| M50, series (Table 4) | ST1 none, ST2 none, ST3 177, ST4 342, SP1 223, SP2 149, SP3 210, SP4 none | 5 of 8 |

- The M50 range is 147 to 342 s, which matches the brief. My arithmetic for the M50 means: 212 s parallel, 220 s series.
- The P42A tables print summary values of 240 s (SD 156) for parallel and 290 s (SD 37) for series. These match the means of the listed values.

Setup quotes (S1):

- "The cells were placed directly in contact with each other as in Figure 9(b) in Supplementary Materials."
- "The cells were aligned horizontally within the cell holder [20]"
- "electrically connected via welded cell tabs."
- "there is no compartment enclosing the two cells, which will allow heat dissipation through the surrounding air."
- "The trigger cell was penetrated around the center with a speed of 6 mm s−1to an approximate depth of 1–3 mm,"
- (joined) "Several abusive tests were conducted, combining two different cell models (Molicel P42A and LG M50, both 21700s) in series and parallel connections (16 tests per configuration)."

## 12. Feng, Ouyang, Liu, Lu, Xia, He 2018, Energy Storage Materials 10, 246-267

- Title: "Thermal runaway mechanism of lithium ion battery for electric vehicles: A review"
- DOI: 10.1016/j.ensm.2017.05.013 (read on the Scilit and Zhenzhi records). Scilit gives the online date as 29 May 2017.
- Read: ABSTRACT only.
- Sources read:
  - S1: https://data.zhenzhi.com/details/1/880768423 (abstract)
  - S2: https://www.scilit.net/publications/338e28b3b94000c0749b46f1b89353a0 (metadata; it shows "No abstract available")
- Failed: https://doi.org/10.1016/j.ensm.2017.05.013 redirected to https://linkinghub.elsevier.com/retrieve/pii/S2405829716303464, which returned an empty page. No open copy was found.

Statements:

- Propagation is mentioned only as a hazard to reduce (S1): "by reducing the secondary hazard like thermal runaway propagation."
- Chain reactions (S1, joined): "The thermal runaway follows a mechanism of chain reactions, during which the decomposition reaction of the battery component materials occurs one after another."
- Energy release diagram (S1, joined): "A novel energy release diagram, which can quantify the reaction kinetics for all the battery component materials, is proposed to interpret the mechanisms of the chain reactions during thermal runaway."

Not found in what could be read: anything on the share of thermal runaway heat carried away by ejecta, or a ratio of heat passed to neighbours. The abstract has none, and the full text was not reached.

## 13. Torres-Castro, Kurzawski, Hewson, Lamb 2020, J. Electrochem. Soc. 167(9), 090515

Added after the review (DECISIONS.md D121). The numbers below were read on the open-access IOP article page (https://iopscience.iop.org/article/10.1149/1945-7111/ab84fa) for references_verified.json, item 18, and are copied from its comparator_numbers; they are not re-quoted verbatim here.

- Conditions: five 3 Ah LiCoO2/graphite pouch cells (203 Wh/kg) at 100 % state of charge, cell 1 nailed; stacks without plates, and with aluminium or copper plates of 0.8, 1.6 and 3.2 mm between the cells.
- Total time, no plates: the entire five-cell string consumed within about 90 s (Results, baseline, Fig. 2).
- Gap crossing (one cell's failure to the next's): around 10 s without plates at 100 % state of charge; 20 to 30 s at 80 %; usually over 30 s with plates (Discussion, "Propagation speed", Fig. 11).
- Energy the next cell absorbs before it fails: 2.0 kJ on average without plates; with 0.8 mm plates 2.6 kJ (Al) or 2.5 kJ (Cu) in the next cell and about 3.2 kJ (Al) or 4.1 kJ (Cu) in the plates (Discussion, "Cell heating during gap-crossing"). The paper gives a nominal 45 kJ stored per cell ("Propagation speed") but does not express the 2.0 kJ as a fraction.
- How the manuscript uses it: as the closest published estimate of what reaches a neighbour, beside this study's 0.27 to 5.96 kJ, for a different cell and stack; an order-of-magnitude comparison only.
