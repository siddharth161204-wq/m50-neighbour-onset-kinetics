"""Stage 14, Part A0.4: every value recorded from the survey, with its source, page and conditions.

Writes results/stage14_inputs.csv. Each row is one value read at a source. The column `cell` says
whose value it is: "this cell" (an LG M50 measured in the rig of Fransson et al. or in calorimetry),
"this rig" (a fact about the rig), "other cell" (measured on another cell, which widens a range and
never sets a value for this cell), "relation" (a published relation or property table), "model"
(a choice the earlier stages made, used here unchanged) or "limit" (no source gives the quantity;
physics caps it, a share or fraction at one). The column `enters` names the bound a value enters,
or "survey" where it is recorded and enters none.

`words` holds the source's own words, kept short, or a paraphrase marked "paraphrase:".
Pages are the printed pages of the version named in `source` unless the locator says otherwise.

Nothing here is computed but the Databank's per-test sums, which are recomputed from its rows.
"""
import csv
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Sources, by short key: full reference and the copy read.
SOURCES = {
    "Fransson2024": "Fransson et al., J. Power Sources 617 (2024) 234916, CC BY 4.0; copy read: https://docs.nlr.gov/docs/fy24osti/87353.pdf (journal pages 1 to 11)",
    "FranssonSupp": "Fransson et al. 2024, supplementary material, 1-s2.0-S0378775324008681-mmc1.pdf, SHA-256 e96713ef58e8dc13df8810034c7ee8b47fb3e2fdcdb398a5095ecdfb64dfc0ef (pages 28 to 32)",
    "Fransson2023": "Fransson et al., J. Energy Storage 71 (2023) 108088 (reference [20] of Fransson 2024); copy read: the authors' manuscript Buckwell_Sidewall-breach_manuscript.pdf, SHA-256 dbf0cbce6dcff891ac212b4be93f8472ec11e091ecbcb62ced487ed4d8ec5650 (manuscript pages 1 to 13)",
    "Pfaff2023": "Pfaff et al., J. Synchrotron Radiat. 30 (2023) 192-199 (reference [19] of Fransson 2024); copy read: https://docs.nlr.gov/docs/fy23osti/82686.pdf",
    "Databank": "Battery Failure Databank, battery-failure-databank-revision2-feb24.xlsx (NREL and NASA), SHA-256 18a6b0ed0bbc881295ef9c832e4dd1937b653702ec6481834e3c6ee50c86a7c4; sheets ReadMe and Battery Failure Databank; the ten rows of inputs/databank/databank_m50_used.csv with Trigger-Mechanism Nail",
    "Finegan2024": "Finegan et al., J. Power Sources 597 (2024) 234106; copy read: finegan2024.pdf (9,394,391 bytes, SHA-256 6f567059ff5b31da9890315a1e054d400641ab71ffb3b8972da7946e472925b7), from https://nrel.gov/docs/fy24osti/87431.pdf",
    "WalkerPart1": "Walker et al., 'The Effect of Cell Geometry and Trigger Mechanism on the Risks Associated with Thermal Runaway of Lithium-ion Batteries: Part 1' (manuscript; cells include the LG 21700-M50); copy read: https://discovery.ucl.ac.uk/10144748/1/Manuscript%20Draftl.pdf (manuscript pages)",
    "Vendra2022": "Vendra et al., Process Saf. Environ. Prot. 160 (2022) 153-165; copy read: the accepted manuscript at https://wrap.warwick.ac.uk/id/eprint/163033 (manuscript pages)",
    "Chen2020": "Chen et al., J. Power Sources 472 (2020) 228585, CC BY 4.0; copy read: https://wrap.warwick.ac.uk/id/eprint/139049 (published version)",
    "Chen2023": "Chen et al., Applied Energy 349 (2023) 121610, CC BY; copy read: https://wrap.warwick.ac.uk/179422/1/1-s2.0-S0306261923009741-main.pdf",
    "Gillich2024": "Gillich et al., Batteries 10 (2024) 142, CC BY; copy read: https://www.mdpi.com/2313-0105/10/4/142",
    "Sharp2022": "Sharp et al., J. Electrochem. Soc. 169 (2022) 020526, open access; copy read: https://eprintspublications.npl.co.uk/9736/1/eid9736.pdf",
    "Read2024": "Read, Jones and Marco, J. Power Sources Advances 30 (2024) 100162, CC BY; copy read: https://wrap.warwick.ac.uk/id/eprint/188615",
    "NASA21700": "NASA, Sidewall Rupture Characterization 21700, Update 2 (slides); https://ntrs.nasa.gov/api/citations/20240012828/downloads/Sidewall%20Rupture%20Characterization%2021700-Update2.pdf",
    "Lienhard": "J.H. Lienhard IV and J.H. Lienhard V, A Heat Transfer Textbook, 6th edition, version 6.00 (Phlogiston Press, 2024), AHTTv600.pdf, SHA-256 d318176a9cac997d415ec5ee95b30979dcdaed0392705185393735c7d59a447a (printed pages; the PDF page is the printed page plus 14)",
    "LGsheet": "LG Chem, Product Specification, Lithium Ion INR21700 M50 18.2Wh (2017-09, tentative); copy read: https://asset.conrad.com/media10/add/160267/c1/-/en/002114679DS01/datenblatt-2114679-lg-chem-inr21700-50t-spezial-akku-21700-flat-top-li-ion-36-v-5000-mah.pdf (pages n/13)",
    "Popp2020": "Popp et al., Elektrotech. Inftech. 137 (2020) 169-176, open access; https://link.springer.com/article/10.1007/s00502-020-00814-9",
    "Cardenas2014": "Cardenas-Garcia, Rev. Mex. Fis. 60 (2014) 305-308; https://scielo.org.mx/pdf/rmf/v60n4/v60n4a10.pdf",
    "Hiden": "Hiden Analytical, project summary of Abbott et al., J. Power Sources 539 (2022) 231585 (the paper itself was not read: subscription); https://www.hidenanalytical.com/wp-content/uploads/2023/07/AP-HPR-20-202377_Project-Summary.pdf",
    "KarpSica2022": "Karp and Sica, FAA report DOT/FAA/TC-22/12 on lithium battery vent gas (2022); https://rosap.ntl.bts.gov/view/dot/66669/dot_66669_DS1.pdf",
    "SandiaECN": "Sandia National Laboratories, Engine Combustion Network, battery safety, 21700-M50LT; https://ecn.sandia.gov/battery-safety/21700-m50lt/",
    "Mier": "Mier et al., slides on 18650 venting (Sandia, 2019); https://www.sandia.gov/app/uploads/sites/163/2022/02/2b_Mier_ESS_2019.pdf and https://www.osti.gov/servlets/purl/1592298",
    "Lugaresi2026": "Lugaresi et al., Fire Safety J. 162 (2026) 104750; https://eprints.whiterose.ac.uk/id/eprint/239432",
    "Feng2015": "Feng et al., J. Power Sources 275 (2015) 261-273; https://public.websites.umich.edu/~racelab/static/Webpublication/2015-JPS-XuningF.pdf",
    "Csernyei2016": "Csernyei and Straatman, Applied Thermal Engineering 105 (2016) 290-303; https://core.ac.uk/download/395738649.pdf",
    "Model": "This repository's earlier decisions (DECISIONS.md), unchanged",
}

# The ten LG M50 nail tests of the Databank: (Test-ID, body, positive ejecta, negative ejecta [kJ],
# corrected total [kJ], pre-test OCV [V], pre-test mass, post-test body mass, unrecovered mass [g],
# theoretical energy of the unrecovered mass, positive and negative [kJ], failure mechanism).
# Read from the workbook's sheet "Battery Failure Databank" (columns named in A0.2, D150).
DATABANK_NAIL = [
    ("ESRF18_Oct_Run063", 20.639838954003867, 2.771930387847004, 73.47931993449417, 96.89108927634503, 4.164, 68.3714, 27.52, 13.301400000000001, 0.11507235167521798, 2.1018261121904342, "Top and Bottom Vent"),
    ("ESRF18_Oct_Run065", 28.36386465254093, 38.60186903843655, 40.630363306483474, 107.5960969974609, 4.174, 68.1684, 34.66, 22.808400000000013, 2.9620041162415935, 0.9587434456592284, "Top and Bottom Vent"),
    ("ESRF18_Oct_Run067", 24.717739582151253, 36.05990481584218, 41.171352175087165, 101.94899657308058, 4.17, 68.4834, 34.49, 12.9234, 1.5597845144195583, 0.4440410200341361, "Top and Bottom Vent"),
    ("DLS19_Feb_Run045", 27.029659757930204, 6.285350831821065, 57.87441546855796, 91.18942605830925, 4.174, 68.4844, 32.5, 16.384399999999992, 0.2796078523678079, 1.9531221433997152, "Top and Bottom Vent"),
    ("DLS19_Feb_Run047", 18.671451686107915, 0.4873333399988276, 74.54874547834919, 93.70753050445593, 4.189, 68.4189, 26.7, 16.21889999999999, 0.0, 4.962776340440013, "Bottom Vent"),
    ("SPR2021_ESTA_8B100-01_SOC_RUN194", 33.0761080784505, 68.0178186288345, 5.36019645203987, 106.454123159325, 4.1797, 68.46, 28.59, 20.56, 2.4384227377176, 0.2996828137104, "Top and Bottom Vent"),
    ("SPR2021_ESTA_8B100-01_SOC_RUN195", 33.2229118228995, 74.6753119701417, 1.4714930375432, 109.369716830584, 4.1768, 68.36, 27.96, 22.18, 6.5662625305272, 0.0, "Top Vent"),
    ("SPR2021_ESTA_8B100-01_SOC_RUN196", 27.0408810395301, 83.0611455134069, 0.388164727805354, 110.490191280742, 4.1757, 68.52, 26.88, 20.23, 6.5054123915466, 0.0, "Top Vent"),
    ("SPR2021_ESTA_8B100-01_SOC_RUN197", 21.4952545814092, 89.3261016522013, 0.0116780710954399, 110.833034304706, 4.176, 68.05, 20.97, 13.78, 4.289128986636, 0.0, "Top Vent"),
    ("SPR2021_ESTA_8B100-01_SOC_RUN198", 24.7390417936356, 84.1607484057353, 0.563048244377881, 109.462838443749, 4.1727, 68.23, 19.38, 12.13, 3.7633498395924, 0.0, "Top Vent"),
]


def median(xs):
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else 0.5 * (s[n // 2 - 1] + s[n // 2])


def rows():
    R = []

    def add(key, enters, inp, value, unit, lo, hi, src, loc, words, cond, cell, note=""):
        R.append(dict(key=key, enters=enters, input=inp, value=value, unit=unit, range_lo=lo, range_hi=hi,
                      source=src, locator=loc, words=words, conditions=cond, cell=cell, note=note))

    # ---- The rig (A0.1) -----------------------------------------------------------------------------
    add("rig_orientation", "all paths (geometry)", "orientation of the two cells", "horizontal, in contact, trigger above the neighbour", "", "", "",
        "Fransson2024; FranssonSupp", "p. 3; supplement p. 28, Fig. 9(b)",
        "\"aligned horizontally within the cell holder\"; \"placed directly in contact with each other\"; Fig. 9(b) labels the trigger cell above the propagating cell",
        "LG M50 pairs in the ESRF chamber", "this rig")
    add("rig_nail", "survey", "nail", "from above, near the centre, 6 mm/s, 1 to 3 mm deep", "", "", "",
        "Fransson2024; FranssonSupp", "p. 3; supplement p. 28, Fig. 9(b)",
        "\"penetrated around the center with a speed of 6 mm s-1 to an approximate depth of 1-3 mm\"; Fig. 9(b) draws the nail above the trigger",
        "trigger cell", "this rig")
    add("rig_atmosphere", "A1, A2 (whether the gas burns)", "chamber atmosphere", "15 % CO2 for fire retention; fire observed", "", "", "",
        "Fransson2024", "p. 3; p. 6 (Category 1); p. 7 (Category 3 example, Fig. 6); pp. 7-8 (Category 4, Fig. 7)",
        "\"a 15% CO2 ratio was used for fire retention\"; \"fire and gas are ejected from the vent region\"; \"gas and fire release through the vent opening\"",
        "the chamber of the tests", "this rig",
        "Fire at the vent is a fact of this rig, but no sentence ties it to an M50 test by name: the p. 7 sentence describes a P42A sidewall melt, and the other statements do not name the cell. The upper bounds allow the gas to burn; the lower bounds do not assume it.")
    add("rig_chamber", "survey", "chamber", "gas-tight, 343 l, steel walls, exhaust to an extraction unit", "", "", "",
        "Pfaff2023", "p. 192 (abstract: heat-resistant, gas-tight); p. 193 (the rest)",
        "\"The chamber has a total internal volume of 343 l\"; paraphrase: three 6 mm stainless-steel sidewalls, an exhaust pipe to an extraction unit, a CO2 bottle purged to suppress fire",
        "the chamber of reference [19] of Fransson 2024", "this rig")
    add("rig_holder", "A5", "holder: material and contact", "aluminium frame with 3D-printed inlets; about 2 mm of contact per fixture", "", "", "",
        "Pfaff2023", "p. 194",
        "\"The basic structure is an aluminium frame\"; \"inserted 3D-printed inlets\"; \"only 2 mm contact area\"",
        "the chamber's cell holder", "this rig",
        "The inlets' material, their shape and the holder's temperature are not given (no source). The supplement's Fig. 9(b) shows the cells' ends in windows of the two end plates, lined by black inserts.")
    add("rig_thermocouple", "B3", "thermocouple position", "middle of the cell surface (angle not given)", "", "", "",
        "Fransson2024", "p. 3",
        "\"Thermocouples were fastened in the middle of the cell surface\"",
        "both cells", "this rig")
    add("rig_paint", "survey", "surface finish", "black carbon paint on each cell", "", "", "",
        "Fransson2024", "p. 3", "\"coated with black carbon paint\"", "both cells", "this rig")
    add("rig_categories", "A3, B2", "failure categories", "1 nail-penetration failure of the trigger; 2 propagation failures; 3 sidewall melting; 4 sidewall rupture of a trigger cell; four M50 tests 'cell movement'", "", "", "",
        "Fransson2024", "p. 4 (the categories' text and the cell-movement sentence); p. 5 (Fig. 2 caption)",
        "\"Cases where sidewall rupture occurred as a result of TR (trigger cells)\" (category 4); \"In 4 of the M50 tests, the cell moved within the FoV\"",
        "all tests", "this rig")
    add("rig_breach_count", "A3 (share of events)", "trigger sidewall ruptures among the sixteen M50 tests", 3, "tests of 16", "", "",
        "Fransson2024", "p. 7, Tables 3 and 4 (failure cat. 4: M50_PT_Exp3, M50_PT_Exp4, M50_ST_Exp2)",
        "paraphrase: category 4 in three of the sixteen rows", "LG M50 in this rig", "this cell")
    add("rig_breach_only_trigger", "A3", "where ruptures occurred", "in trigger cells only", "", "", "",
        "Fransson2024", "p. 10", "\"ruptures only occurred in trigger cells\"", "all cells of the study", "this rig")
    add("rig_letters", "survey", "test names", "PT Parallel Trigger, PP Parallel Propagation, ST Series Trigger, SP Series Propagation (second letter: the cell in the X-ray field of view)", "", "", "",
        "Fransson2024", "p. 3", "\"'PT' stands for 'Parallel Trigger'\"", "all tests", "this rig")
    add("rig_discharge", "A6", "the neighbour discharges through the failed trigger in parallel", "stated by the authors", "", "", "",
        "Fransson2024; FranssonSupp", "p. 2; p. 5; supplement p. 31, Fig. 12",
        "\"As the neighboring cell discharges through the trigger cell, this dumps its current in the already failed cell\"",
        "parallel tests (8 of 16)", "this rig", "No current or voltage history is reported.")
    add("rig_parallel_count", "A6 (share of events)", "parallel tests", 8, "tests of 16", "", "",
        "Fransson2024", "p. 7, Table 3", "paraphrase: Table 3 holds the eight parallel M50 tests", "LG M50 in this rig", "this cell")
    add("fr2023_gap", "survey", "contact seen in a 2023 radiograph of the same chamber", "a small air gap between the two sidewalls (Molicel P42A pair)", "", "", "",
        "Fransson2023", "manuscript pp. 5-6, Fig. 1 caption", "\"with a small air gap separating the two\"",
        "Molicel INR21700-P42A, parallel, 100 % charge", "other cell")
    add("fr2023_paths", "survey", "heat paths named in the 2023 study", "the contact between the cells and the connection tabs", "", "", "",
        "Fransson2023", "manuscript p. 6", "\"two major heat transfer pathways, the contact area between the cells and the electrical connection tabs\"",
        "Molicel INR21700-P42A", "other cell")
    add("fr2023_breach_time", "A3 (time)", "time from the first to the second sidewall breach", 0.35, "s", 0.35, 0.35,
        "Fransson2023", "manuscript p. 9, Fig. 3 caption", "paraphrase: breach at 147.65 s, second breach at 148.00 s, contents pushed out continuously",
        "Molicel P42A propagating cell (temperature-induced breach)", "other cell")

    # ---- The Databank and its calorimeter (A0.2) -------------------------------------------------------
    e_ej = []
    for (tid, body, pos, neg, tot, ocv, m0, mbody, munrec, thp, thn, mech) in DATABANK_NAIL:
        e = (pos + neg) * 1000.0
        e_ej.append(e)
        add(f"db_Eej_{tid}", "E_ej range (A1 to A4)", f"ejected energy, positive plus negative ejecta, {tid}", round(e, 2), "J", "", "",
            "Databank", f"row {tid}: Energy-Fraction-Positive-Ejecta-kJ + Energy-Fraction-Negative-Ejecta-kJ",
            f"paraphrase: {pos:.4f} + {neg:.4f} kJ; failure mechanism '{mech}'",
            "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell")
    add("db_Eej_max", "A1 to A4 (E_avail)", "largest ejected energy of the ten", round(max(e_ej), 2), "J", round(min(e_ej), 2), round(max(e_ej), 2),
        "Databank", "rows of the ten nail tests (max: SPR2021_ESTA_8B100-01_SOC_RUN197)", "paraphrase: computed from the rows",
        "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell")
    add("db_Eej_median", "P1 (2 % of it)", "median ejected energy (the manuscript's E_fix)", round(median(e_ej), 2), "J", round(min(e_ej), 2), round(max(e_ej), 2),
        "Databank", "rows of the ten nail tests", "paraphrase: computed from the rows (the mean of 76.25 and 77.23 kJ)",
        "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell")
    bodies = [d[1] * 1000 for d in DATABANK_NAIL]
    totals = [d[4] * 1000 for d in DATABANK_NAIL]
    add("db_Ebody_max", "A5 (cap stated beside)", "largest cell-body energy", round(max(bodies), 2), "J", round(min(bodies), 2), round(max(bodies), 2),
        "Databank", "column Energy-Fraction-Cell-Body-kJ (max: RUN195)", "ReadMe: \"Fraction of the total energy released through the cell casing.\"",
        "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell")
    add("db_Etotal_max", "A5 (cap stated beside)", "largest corrected total energy", round(max(totals), 2), "J", round(min(totals), 2), round(max(totals), 2),
        "Databank", "column Corrected-Total-Energy-Yield-kJ (max: RUN197)",
        "ReadMe: \"corrected for both conductive heat loss and also for the heat associated with unrecovered cell mass\"",
        "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell")
    mej = [d[6] - d[7] for d in DATABANK_NAIL]
    mun = [d[8] for d in DATABANK_NAIL]
    add("db_mass_ejected", "survey", "mass that left the cell body (pre-test mass less post-test body mass)", "", "g", round(min(mej), 2), round(max(mej), 2),
        "Databank", "columns Pre-Test-Cell-Mass-g and Post-Test-Mass-Cell-Body-g", "paraphrase: computed from the rows",
        "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell")
    add("db_mass_unrecovered", "survey", "unrecovered mass (gas and smoke)", "", "g", round(min(mun), 2), round(max(mun), 2),
        "Databank; Finegan2024", "column Post-Test-Mass-Unrecovered-g; Finegan 2024 p. 2",
        "Finegan 2024: unrecovered mass \"is thought to be mostly gas and smoke\"",
        "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell")
    ratios = [((d[9] + d[10]) / d[8]) for d in DATABANK_NAIL if d[8] > 0]
    add("db_unrecovered_per_gram", "A0.2 (what the calorimeter counts)", "theoretical energy of the unrecovered mass per gram of it", "", "kJ/g", round(min(ratios), 4), round(max(ratios), 4),
        "Databank", "columns Theoretical-Energy-Positive/Negative-Unrecovered-Mass-kJ over Post-Test-Mass-Unrecovered-g",
        "ReadMe: the theoretical energy is \"accounted for in the Corrected Total Energy Yield and in the energy fractions\"; its method is not given",
        "LG 21700-M50 (BV), nail, 100 % SOC, FTRC", "this cell",
        "Computed from the rows. Two orders of magnitude below the heat of combustion of such gases, so the Databank's ejected energy does not hold the heat of burning the escaped gas in air.")
    add("db_ocv", "A6", "open-circuit voltage before the test", 4.189, "V", 4.164, 4.189,
        "Databank", "column Pre-Test-Cell-Open-Circuit-Voltage-V", "paraphrase: 4.164 to 4.189 V over the ten rows",
        "LG 21700-M50 (BV), 100 % SOC", "this cell")
    add("db_stored_energy", "A6", "stored energy at 100 % state of charge", 65520.0, "J", 63360.0, 65520.0,
        "Databank; LGsheet", "column Cell-Energy-Wh (18.2) and ReadMe; datasheet p. 4/13 (nominal 18.2 Wh, minimum 17.6 Wh)",
        "ReadMe: Cell-Energy-Wh is the \"Stored energy at 100% state-of-charge.\"",
        "LG M50", "this cell", "18.2 Wh = 65,520 J; 17.6 Wh = 63,360 J (D68).")
    add("db_bottom_vent", "survey", "bottom vent", "yes, for the Databank's M50 (BV)", "", "", "",
        "Databank; Finegan2024", "column Bottom-Vent-Yes-No; Finegan 2024 p. 4, Table 1",
        "paraphrase: the Databank's cells are 'LG 21700-M50 (BV)', with a bottom vent", "LG M50 (BV)", "this cell",
        "Whether the commercial cells of Fransson et al. had a bottom vent is not stated.")
    add("walker_unrecovered", "A0.2 (what the calorimeter counts)", "how the energy of the unrecovered mass is estimated", "its mass times a specific heat times a temperature change read from the baffles", "", "", "",
        "WalkerPart1", "manuscript p. 7",
        "\"The maximum theoretical temperature change of the unrecovered mass is approximated\" from the baffle temperatures; Cp is a specific heat",
        "FTRC, the cells of the study including the LG 21700-M50", "relation",
        "A sensible heat: the heat of burning the escaped gas is not in it.")
    add("finegan_oxygen", "A0.2", "oxygen in the calorimeter", "less excess oxygen than in an open volume", "", "", "",
        "Finegan2024", "p. 7", "\"the amount of excess oxygen is expected to be less inside the enclosed volume of the FTRC\"",
        "FTRC", "relation")
    add("finegan_mesh", "A0.2", "what the calorimeter does to the ejecta", "baffles and copper mesh capture particles and arrest flames", "", "", "",
        "Finegan2024", "p. 2", "paraphrase: aluminium baffles, copper mesh and exhaust end caps capture ejected particles and arrest flames",
        "FTRC", "relation")

    # ---- Open-air combustion (A0.4 item 5) --------------------------------------------------------------
    for i, (q, qs, qt) in enumerate(((74.1, 22.1, 96.2), (85.6, 41.7, 136.5), (69.1, 41.7, 110.8)), start=1):
        add(f"vendra_Qt_{i}", "A1 to A4 (E_avail)", f"total heat release in open air, test {i}", qt * 1000.0, "J", "", "",
            "Vendra2022", "manuscript p. 10, Table 2 and eqn (1)",
            f"paraphrase: Qt = Q + Qs, with Q = {q} kJ from oxygen consumption and Qs = {qs} kJ for combustion with oxygen released by the cathode",
            "21700, NMC cathode and carbon anode (Table 1), 4.8 Ah, 68.2 g, 100 % SOC, cone calorimeter, oxygen consumption", "other cell",
            "Test 2's printed parts sum to 127.3 kJ, not the printed 136.5 kJ; the source does not say which is wrong." if i == 2 else "")
    add("vendra_Qt_max", "A1 to A4 (E_avail)", "largest total heat release in open air", 136500.0, "J", 96200.0, 136500.0,
        "Vendra2022", "manuscript p. 10, Table 2", "paraphrase: 96.2, 136.5 and 110.8 kJ as printed",
        "21700, NMC cathode and carbon anode, 4.8 Ah, 100 % SOC", "other cell",
        "Widens the energy available in an open rig; sets no value for this cell. Test 2's printed parts sum to 127.3 kJ; the bound keeps the printed 136.5 kJ, the larger, since the source does not say which number is wrong.")
    add("vendra_gas", "survey", "vent gas amount and composition", "0.53 mol peak; H2 22 %, CO 17.70 %, CO2 42.33 %, CH4 14.8 %, C2H4 1.46 %, C3H8 1.3 %, O2 0.38 %", "", "", "",
        "Vendra2022", "manuscript pp. 15-16 (composition, amount); p. 12 (9717 cm3 at STP)",
        "\"The peak number of moles for the vent gases released is 0.53\"",
        "21700 NMC, 4.8 Ah, 100 % SOC, canister under argon or nitrogen", "other cell")
    add("vendra_internal_T", "survey", "peak internal temperatures", "1109.3 and 1051.5", "C", 1051.5, 1109.3,
        "Vendra2022", "manuscript p. 13", "\"The peak internal temperatures were 1109.3 °C and 1051.5 °C.\"",
        "21700 NMC, 4.8 Ah, 100 % SOC", "other cell")

    add("abbott_gas", "survey", "vent gas volume at 100 % SoC", 6.5, "l", "", "",
        "Hiden", "p. 2", "paraphrase: hydrogen and carbon dioxide made up more than half of 6.5 l of gas",
        "21700 NMC811 (maker and model not stated), 50 l vessel, air and nitrogen", "other cell")
    add("karp_gas", "survey", "vent gas volume and its combustion energy", "18650 2.6 Ah: 3.75 l, up to 42 kJ; pouch 4.8 Ah: 9.9 l, 114 kJ", "", "", "",
        "KarpSica2022", "pp. 3-5, 8, 10-12 (vessel p. 4; Table 2 p. 5; 9.9 l p. 8; 114 kJ p. 10; 3.75 l p. 11; 42 kJ p. 12)",
        "\"to 3.75 L, for a cylindrical cell charged to 100% SOC and heated at 20°C/min\"",
        "LiCoO2 18650 and pouch cells, 100 % SOC, heated at 20 C/min, 21.7 l vessel filled with nitrogen", "other cell",
        "The combustion energy is calculated for complete combustion (p. 3), not measured; p. 13 gives the 18650 cell as 2.5 Ah against 2.6 Ah in Table 2.")
    add("ecn_electrolyte", "survey", "electrolyte share of the cell's mass", "5.6 % of the mass; 78 % of it DMC", "", "", "",
        "SandiaECN", "web page 21700-M50LT, main text", "\"the cell mass is 5.6% electrolyte (electrolyte mass is 78% dimethyl carbonate)\"",
        "inventories reported for similar M50 cells", "this cell",
        "The page gives the figures without a citation, pointing to inventories from similar M50 cells.")
    add("mier_jet", "survey", "vent jet of an 18650 cell", "leading edge about 150 m/s; core about Mach 1; flow projected outward at 21 degrees", "", "", "",
        "Mier", "OSTI 1592298 document, Schlieren results (150 m/s); sandia.gov slides 19 (Mach 1), 11 and 20 (21 degrees)",
        "\"Core velocity ~Mach 1\"; \"Projected outward at 21\u02da\"", "18650 cells (chemistry and charge not given)", "other cell")
    add("lugaresi_flux", "survey", "radiative heat flux 150 mm from a venting cell", "", "kW/m2", 50.0, 500.0,
        "Lugaresi2026", "p. 3 (gauges 150 mm from the cell); p. 10 (peaks)",
        "\"The peak heat flux of the first flaming event was approximately 50-150 kW/m2 for most cells\"; paraphrase: second peaks about 150 kW/m2 (18650) and 350 to 500 kW/m2 (26650); no radiant fraction",
        "LFP 18650 (1.6 Ah) and 26650 (3.3 Ah) cells, 100 % SOC", "other cell")
    add("feng_split", "survey", "heat reaching a neighbour by each path", "shell 68,881 J; connector 14,586 J; fire 162 J of 605,088 J; under 12 % drove propagation", "", "", "",
        "Feng2015", "pp. 269-270", "paraphrase: as recorded", "25 Ah prismatic NMC cells in a module", "other cell")
    add("csernyei_jet", "survey", "average Nusselt number of round jets impinging on a cylinder", "Eq. 16", "", "", "",
        "Csernyei2016", "p. 302, Section 5.4, Eq. 16", "paraphrase: Nu = 0.041 Re^0.862 (d/D)^-0.317 (y/d)^-0.0729 (z/d)^-0.186 exp(-0.00134 x/d), Re 2.06e5 to 1.236e6",
        "air jets on a heated cylinder", "relation",
        "Not used: a breach's opening, its jet's velocity and its distance from the neighbour have no source, and the contact distance lies outside the correlation's range.")

    # ---- Radiation (A1) -----------------------------------------------------------------------------------
    add("chi_rad", "A1", "radiant fraction of a vent flame", 1.0, "", 0.0, 1.0,
        "none found (searches 24 to 26)", "", "paraphrase: no radiant fraction for a battery vent flame was found", "", "limit",
        "Capped at 1: the radiated energy cannot exceed the energy released.")
    add("absorptivity", "A1, A2", "absorptivity of the facing half", 1.0, "", 0.0, 1.0,
        "Cardenas2014 (survey); limit", "Cardenas 2014: abstract",
        "paraphrase: a high-emissivity black paint measured at 0.972 +- 0.012 over 8 to 14 um, 50 to 150 C",
        "a black paint, not the carbon paint of the rig", "limit",
        "The carbon paint's absorptivity for flame radiation is not given; capped at 1.")
    add("T_flame_max", "A1, A2 (rate)", "largest published flame temperature", 1500.0, "C", 1069.0, 1500.0,
        "Chen2020", "p. 2", "\"Measured flame temperatures as high as 1069 °C for single cells [8] and 1500 °C for a battery module [9]\"",
        "[8] Ping et al. 2018 (single cells, over-heating); [9] Ping et al. 2015 (full-scale burning test)", "other cell")
    add("T_surface_max_M50", "survey", "trigger surface temperature with rupture", "", "C", 1051.5, 1248.1,
        "Read2024", "p. 5, Table 2", "paraphrase: trigger surface 1051.5 to 1248.1 C in the tests with sidewall rupture",
        "LG INR21700-M50, 100 % SOC, nail through the positive terminal, open module", "this cell")
    add("sigma", "A1, A2 (rate)", "Stefan-Boltzmann constant", 5.670374419e-8, "W/(m2 K4)", "", "",
        "Lienhard", "p. 760, Appendix A constants; eqn (1.28), p. 30", "paraphrase: sigma = 5.670 374 419 x 10^-8 W/m2 K4", "", "relation")
    add("t_vent_min", "A1, A2, A3, A4 (time)", "shortest published duration of a cell's runaway or venting", 1.131, "s", 0.8401, 2.0,
        "Gillich2024; Sharp2022", "Gillich Section 5 (Discussion); Sharp, 'Internal temperature estimations', after Fig. 6 (eighth or ninth page; the copy has no page numbers)",
        "Gillich: \"1.131 \u00b1 0.2909 s for high-energy LIBs\"; Sharp: \"thermal runaway lasts for around 2 s\"",
        "Gillich: LG MJ1 18650, NMC811, 100 % SOC, measured from the recoil force; Sharp: nail tests including LG 21700-M50 (general statement)", "other cell",
        "The range's lower end is the printed mean less its printed spread (1.131 - 0.2909 s).")
    add("t_combustion", "A1, A2 (time)", "combustion durations of a 21700 NMC cell", "15.2, 16.3, 11.1", "s", 11.1, 16.3,
        "Chen2020", "p. 3, Table 2", "paraphrase: combustion lasted about 15.2, 16.3 and 11.1 s at 100 % SOC",
        "21700 NMC, 5 Ah, 68.3 g, 266 Wh/kg, vertical, ventilated chamber", "other cell")
    add("t_jet_fire", "A1, A2 (time)", "duration of a jet fire", 110.0, "s", "", "",
        "Chen2023", "p. 11", "\"a jet of fire with sparks was sprayed outside lasting for about 110 s\"",
        "21700 NCA/graphite-Si, 4.8 Ah, 100 % SoC, nail", "other cell")
    add("t_flame_max", "A1, A2 (time)", "longest published combustion of a 21700 cell", 300.0, "s", 1.5, 300.0,
        "Chen2023", "p. 11", "\"The process of battery combustion was lasted for about 5 mins\"",
        "21700 NCA/graphite-Si, 4.8 Ah, 100 % SoC, nail", "other cell", "About 5 min, taken as 300 s.")

    # ---- Convection (A2) ----------------------------------------------------------------------------------
    add("u_vent_max", "A2 (rate)", "largest published vent gas velocity", 398.5, "m/s", 50.0, 398.5,
        "Gillich2024", "abstract; Introduction (up to 50 m/s cited for 18650 cells)",
        "paraphrase: the high-energy cell's gas velocity peaks at 398.5 m/s; the high-power cell's at 260.9 m/s",
        "LG MJ1 18650, NMC811, 3.5 Ah, 100 % SOC", "other cell")
    add("CB_765", "A2 (rate)", "Churchill-Bernstein correlation, cylinder in cross flow", "eqn (7.65)", "", "", "",
        "Lienhard", "p. 390, eqn (7.65)", "paraphrase: Nu = 0.3 + 0.62 Re^1/2 Pr^1/3 / [1 + (0.4/Pr)^2/3]^1/4 [1 + (Re/282,000)^5/8]^4/5",
        "for the entire range of the available data; properties at the film temperature (p. 391)", "relation")
    add("CB_768", "A2 (rate)", "Churchill-Bernstein correlation for 40,000 < Re < 400,000", "eqn (7.68)", "", "", "",
        "Lienhard", "p. 391, eqn (7.68)", "paraphrase: as (7.65) with [1 + (Re/282,000)^1/2] in place of the last factor",
        "40,000 < Re_D < 400,000", "relation")
    add("CB_accuracy", "A2 (rate)", "accuracy of eqn (7.65)", "underpredicts most data by about 20 % for 40,000 < Re < 400,000", "", "", "",
        "Lienhard", "p. 391", "\"This expression underpredicts most of the data by about 20%\"", "", "relation",
        "The rate bound takes the larger of 1.2 times (7.65) and (7.68) in that range.")
    add("props_air", "A2 (rate)", "air at 1 atm: rho, cp, mu, nu, k, alpha, Pr by temperature", "Table A.6, 100 to 1500 K", "", "", "",
        "Lienhard", "p. 755, Table A.6 (Air)", "paraphrase: the tabulated rows, interpolated linearly in temperature", "", "relation")
    add("props_h2", "A2 (rate)", "hydrogen at 1 atm: the same properties", "Table A.6, 50 to 1000 K", "", "", "",
        "Lienhard", "p. 758, Table A.6 continued (Hydrogen)", "paraphrase: the tabulated rows; the highest is 1000 K", "", "relation",
        "Hydrogen is 22 % of the vent gas of Vendra et al.; its high conductivity gives the larger coefficient.")
    # The rows of Table A.6 that the rate bound of A2 uses (nu in m2/s, k in W/(m K), Pr).
    for gas, T, nu, k, pr, page in (("air", 1000, 12.27e-5, 0.0677, 0.730, 755), ("air", 1100, 14.36e-5, 0.0727, 0.734, 755),
                                    ("hydrogen", 1000, 84.38e-5, 0.460, 0.675, 758)):
        for q, val, unit in (("nu", nu, "m2/s"), ("k", k, "W/(m K)"), ("Pr", pr, "")):
            add(f"{'air' if gas == 'air' else 'h2'}_{T}K_{q}", "A2 (rate)", f"{gas} at {T} K, 1 atm: {q}", val, unit, "", "",
                "Lienhard", f"p. {page}, Table A.6 ({'Air' if gas == 'air' else 'Hydrogen'}), row {T} K",
                f"paraphrase: the tabulated value", "1 atm", "relation")
    add("T0", "A1, A2 (rate)", "the neighbour's starting temperature", 25.0, "C", "", "",
        "Model", "D52 (2), Stage 5", "paraphrase: the model's ambient, at which every need was computed", "", "model")

    # ---- Breach (A3) --------------------------------------------------------------------------------------
    add("read_rupture", "A3 (share of events)", "sidewall rupture with a nail through the positive terminal", "3 of 3 at 35 mm depth; none at 10 mm", "", "", "",
        "Read2024", "p. 3", "paraphrase: deep penetration ruptured the sidewall in all three tests; 10 mm penetration in none",
        "LG INR21700-M50, 100 % SOC, seven-cell open module", "this cell")
    add("read_rupture_place", "A3", "where the casing ruptured", "the bottom half of the casing; in one test almost its whole length", "", "", "",
        "Read2024", "p. 3", "\"on the bottom half of the cell casing\"", "LG INR21700-M50, 100 % SOC", "this cell")
    add("read_jet", "A3", "what the rupture did to the neighbours", "a jet fire impinging on the adjacent cells; neighbours ran away 2 to 5 s later", "", "", "",
        "Read2024", "p. 5; p. 7, Table 4", "\"impinges jet fire directly on the adjacent secondary cells\"",
        "LG INR21700-M50, 3 mm gaps", "this cell")
    add("db_no_breach", "A3 (share of events)", "sidewall breaches in the ten Databank nail tests", 0, "tests of 10", "", "",
        "Databank", "column Cell-Failure-Mechanism", "paraphrase: top and/or bottom vents in every row", "LG 21700-M50 (BV), FTRC", "this cell")
    add("chen2023_rupture", "A3 (share of events)", "sidewall rupture at 100 % SoC", "2 of 6", "", "", "",
        "Chen2023", "p. 5 (the SoC series); p. 8 and p. 9 (the speed series)", "\"Sidewall rupture was only observed in two of six cells tested at 100% SoC\"",
        "21700 NCA/graphite-Si, 4.8 Ah, 4 mm nail at 6 mm/s through the middle of the top cover; at 0.5 mm/s 1 of 5, at 100 mm/s 4 of 5", "other cell")
    add("nasa_rupture", "A3 (share of events)", "sidewall rupture rates of 21700 cells", "", "%", 1.1, 5.2,
        "NASA21700", "slides 19, 21, 23, 25 (each cell), 27 or 28 (bottom ruptures), 31 (summary), 13 (hot plate)", "paraphrase: sidewall ruptures in 1.1 to 5.2 % of tests; bottom ruptures 4.4 to 48.9 %",
        "LG M52V, Molicel P45B, Samsung 50S and 53G; hot plate", "other cell")

    # ---- The circuit (A6) ---------------------------------------------------------------------------------
    add("R_dc", "A6 (rate, conditional)", "initial DC resistance", 0.030, "ohm", 0.024, 0.036,
        "LGsheet", "p. 6/13, item 4.2.2", "paraphrase: 30 +- 6 mOhm at 50 % SOC, 0.5 C for 30 s, 25 C",
        "LG INR21700 M50, new cell, 25 C", "this cell")
    add("R_ac", "survey", "initial AC impedance at 1 kHz", 0.025, "ohm", "", 0.025,
        "LGsheet", "p. 6/13, item 4.2.1", "paraphrase: at most 25 mOhm at 1 kHz after charge", "LG INR21700 M50, new cell", "this cell")
    add("R_temperature", "A6", "temperature dependence of the resistance", "resistance at 10 C about five times that at 45 C", "", "", "",
        "Popp2020", "p. 172", "paraphrase: the M50's resistance at 10 C is about 400 % higher than at 45 C (50 % SOC pulses)",
        "LG M50, 50 % SOC, pulses of 0.5 to 2 C", "this cell",
        "No source gives the resistance above 45 C, so the datasheet's lower end bounds the rate only at 25 C. The page could not be confirmed at the second reading (the web copy has no page numbers).")

    # ---- Geometry and model (unchanged) ------------------------------------------------------------------
    add("R_cell", "all paths (geometry)", "cell radius", 0.01055, "m", "", 0.01055,
        "Model; LGsheet", "D36 (3); datasheet p. 5/13 (diameter at most 21.10 mm)", "paraphrase: R = 10.55 mm", "", "model")
    add("L_cell", "all paths (geometry)", "cell length", 0.0701, "m", "", 0.07015,
        "Model; LGsheet", "D36 (4); datasheet p. 5/13 (height at most 70.15 mm)", "paraphrase: L = 70.1 mm", "", "model")
    add("A_facing", "all paths", "area of the facing half (theta <= 90 degrees)", 3.141592653589793 * 0.01055 * 0.0701, "m2", "", "",
        "Model", "D77 (4)", "paraphrase: pi R L, the half of the can within 90 degrees of the line of contact", "", "model")
    return R


def main():
    R = rows()
    # The second reading (V1, DECISIONS D152 (3)): every row's verdict; its corrections are applied above.
    v1 = os.path.join(ROOT, "results", "stage14_v1_second_reading.csv")
    if os.path.exists(v1):
        with open(v1, newline="") as fh:
            verd = {r["key"]: r["verdict"] for r in csv.DictReader(fh)}
        names = {"agree": "agrees", "corrected": "corrected; the correction is applied", "could not trace": "no source to trace (a limit)"}
        for r in R:
            r["second_reading"] = names.get(verd.get(r["key"], ""), "not read")
    out = os.path.join(ROOT, "results", "stage14_inputs.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(R[0].keys()))
        w.writeheader()
        w.writerows(R)
    src = os.path.join(ROOT, "results", "stage14_inputs_sources.csv")
    with open(src, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["source", "reference_and_copy_read"])
        for k, v in SOURCES.items():
            w.writerow([k, v])
    print(f"wrote {out} ({len(R)} rows) and {src} ({len(SOURCES)} sources)")


if __name__ == "__main__":
    main()
