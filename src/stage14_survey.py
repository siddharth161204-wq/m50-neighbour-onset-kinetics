"""Stage 14, Part A0.4: the survey's record (written after the searches were run).

Reads the planned searches committed in c8172e2 (results/stage14_survey.json, written before any search
was run), and writes the same file with the record added: the candidate sources each search returned,
the search added later with its reason, and every source read, with what it gave and did not give.
The values themselves, with pages, are in results/stage14_inputs.csv (src/stage14_inputs.py).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The candidate sources each planned search returned (web search tool, standard mode, 16 November 2026).
RUN = {
1: ["https://docs.nlr.gov/docs/fy24osti/87353.pdf (Fransson 2024, NLR copy)", "https://ora.ox.ac.uk/objects/uuid:4a6edaf0-c309-40b5-b863-cf32243fa7ec (ORA record)"],
2: ["https://pmc.ncbi.nlm.nih.gov/articles/PMC9814060 (Pfaff et al. 2023, J. Synchrotron Radiat. 30, 192-199)", "https://www.nrel.gov/docs/fy23osti/82686.pdf (Pfaff 2023 NREL copy)", "https://journals.iucr.org/s/issues/2023/01/00/ye5024/", "https://esrf.fr/home/news/tech-talk/content-news/tech-talk/techtalk05.html"],
3: ["https://opus4.kobv.de/opus4-bam/... (BAM sodium-ion radiography, not this cell)", "ESRF highlights 2017 (18650 ISC device)"],
4: ["https://core.ac.uk/download/519717661.pdf and https://eprintspublications.npl.co.uk/9736/1/eid9736.pdf (Sharp et al. 2022, J. Electrochem. Soc. 169 020526, open access)"],
5: ["https://research-hub.nrel.gov/en/publications/decoupling-of-heat-generated-from-ejected-and-non-ejected-content-2/ (Walker 2019 record)", "https://discovery.ucl.ac.uk/id/eprint/10069640/1/1-s2.0-S0378775319300874-main.pdf (Finegan et al. 2019 JPS, ISC device, bottom vent)", "https://nrel.gov/docs/fy24osti/87431.pdf (Finegan 2024 Databank paper)"],
6: ["https://ntrs.nasa.gov/api/citations/20190000824/downloads/20190000824.pdf (NASA FTRC slides)", "https://ntrs.nasa.gov/api/citations/20190028810/downloads/20190028810.pdf", "https://ntrs.nasa.gov/api/citations/20205010300/downloads/... (Trigger format comparison)", "https://incompliancemag.com/thermal-runaway-energy-release-as-a-function-of-the-state-of-charge/"],
7: ["https://nrel.gov/docs/fy24osti/87431.pdf (Databank paper, CC BY-NC-ND)", "https://www.nlr.gov/transportation/battery-failure (Databank page: exhaust ports)"],
8: ["https://ecn.sandia.gov/battery-safety/21700-m50lt/ (M50LT: NMC811, 1 % Si, 5.6 % electrolyte by mass, 78 % DMC)", "https://discovery.ucl.ac.uk/10144748/1/Manuscript%20Draftl.pdf (FTRC Part 1 incl. LG 21700-M50)"],
9: ["https://www.hidenanalytical.com/wp-content/uploads/2023/07/AP-HPR-20-202377_Project-Summary.pdf (Abbott et al. 2022 summary: 6.5 L at 100 % SoC)", "Abbott et al. 2022 J. Power Sources 231585 (subscription)", "https://riunet.upv.es/... (Garcia et al., NMC811 combustion modelling)"],
10: ["Hiden summary (as 9)", "https://core.ac.uk/download/327071519.pdf (Chen et al. 2020 J. Power Sources 472 228585, 21700 266 Wh/kg)", "https://wrap.warwick.ac.uk/id/eprint/146838 (Chen et al. 2021 JES, simplified model 21700)"],
11: ["https://www.osti.gov/servlets/purl/1574807 (Baird et al. 2020 accepted manuscript)"],
12: ["https://pubs.rsc.org/en/content/articlehtml/2014/ra/c3ra45748f (Golubkov et al. 2014 RSC Adv. 4, 3633, CC BY)"],
13: ["https://wrap.warwick.ac.uk/id/eprint/194215 (Gulsoy et al. 2025 Data in Brief 63: vent temperatures 5 and 10 mm from the vent cap, 21700)", "https://wrap.warwick.ac.uk/id/eprint/163033 (Vendra et al. 2022 PSEP 160 153, 4.8 Ah 21700 NMC)", "https://www.icheme.org/media/17627/hazards-31-paper-43-abbott.pdf (Abbott et al. Hazards 31, 21700 failure modes)"],
14: ["https://pubs.rsc.org/en/content/articlehtml/2018/ra/c8ra06458j (Golubkov et al. 2018, large automotive cells, vent gas temperature)", "https://nmt.edu/academics/mecheng/faculty/mhargather/docs/Mier2019.pdf", "https://www.frontiersin.org/articles/10.3389/fenrg.2021.788239 (Li et al. 2021 vent CFD)"],
15: ["Hiden summary", "Sharp et al. 2022", "https://ecn.sandia.gov/?p=7295"],
16: ["https://www.frontiersin.org/articles/10.3389/fenrg.2023.1230429 (21700? jet zone temperatures near valve, N2 chamber)", "https://mdpi.com/2313-0105/10/4/142 (Gillich et al. 2024 Batteries 10 142)", "https://www.icheme.org/media/17627/hazards-31-paper-43-abbott.pdf"],
17: ["https://ntrs.nasa.gov/api/citations/20180003307/downloads/20180003307.pdf (18650 particulate analysis)", "https://publikationen.bibliothek.kit.edu/1000176049/155441724 (Hoelle et al. 2024 Batteries 10 173, particle deposition, prismatic)", "Claassen et al. 2024 Batteries 10 366"],
18: ["https://www.osti.gov/servlets/purl/1592298 (Mier: leading edge of jet ~150 m/s, 18650)", "https://www.sandia.gov/app/uploads/sites/163/2022/02/2b_Mier_ESS_2019.pdf (core velocity ~Mach 1; flow projected outward at 21 deg)", "https://mdpi.com/2313-0105/10/4/142 (Gillich 2024: 22.15 and 27.92 g/s; peak 398.5 m/s)", "Kim et al. pouch PIV 123.8 m/s"],
19: ["https://mdpi.com/2313-0105/10/4/142 (Gillich 2024, Table 1 review)", "https://nmt.edu/academics/mecheng/faculty/mhargather/docs/Mier2019.pdf"],
20: ["https://www.osti.gov/pages/biblio/1498760 (Mier et al. 2019 J. Fluids Eng. 141, accepted manuscript)", "https://nmt.edu/academics/mecheng/faculty/mhargather/Mier2020_dissertation_finals.pdf"],
21: ["https://rosap.ntl.bts.gov/view/dot/66669/dot_66669_DS1.pdf (Karp and Sica 2022, FAA: vent gas volume and combustion energy)", "https://mtl.uta.edu/files/2022/11/Mishra-JECS2022.pdf (Mishra, Zhao, Jain 2022 JES 169 100520)"],
22: ["https://pmc.ncbi.nlm.nih.gov/articles/PMC7643196 (flammability limits of vent gas, CHEMKIN)", "https://research.chalmers.se/publication/549553/file/549553_Fulltext.pdf (Lipatnikov 2025: CO2 does not exclude fire)", "https://www.fire.tc.faa.gov/pdf/TC-TT16-55.pdf (FAA flammability limits)", "PolyU: effects of oxygen level and dilution gas, JPS 509 230340"],
23: ["https://pmc.ncbi.nlm.nih.gov/articles/PMC8102908 (fire triangle boundaries, minimum O2)", "https://rosap.ntl.bts.gov/view/dot/57686/dot_57686_DS1.pdf (FAA, reduced oxygen)"],
24: ["https://eprints.whiterose.ac.uk/id/eprint/239432 (Lugaresi et al. 2026 Fire Safety J. 162 104750, radiative heat flux LFP)", "https://wrap.warwick.ac.uk/id/eprint/139049 (Chen et al. 2020 JPS 472, published version)", "WRAP Vendra 2022"],
25: ["Lugaresi 2026", "https://doaj.org/article/99063680301d4a039a0759dcec55af7c (radiation-induced propagation, Applied Sciences 2023)", "Mishra 2022"],
26: ["Zhou et al. 2018 Int. J. Hydrogen Energy 43 9870 (radiative fraction correlation, subscription)", "https://thesis.library.adelaide.edu.au/... (radiant fraction H2 blends)"],
27: ["https://www.osti.gov/servlets/purl/2431996 (Sandia propagation/mitigation boundary)", "Mishra 2022", "Sandia Lamb 2015 record"],
28: ["https://wrap.warwick.ac.uk/id/eprint/161908 (Kong et al. 2022 eTransportation 12 100157)", "https://public.websites.umich.edu/~racelab/static/Webpublication/2015-JPS-XuningF.pdf (Feng et al. 2015 JPS 275 261: 12 % of the heat triggers the neighbour)", "https://ira.lib.polyu.edu.hk/bitstream/10397/89493/1/53_FT_2020_linear_LIB_fire_spread.pdf (Niu et al. 2020)"],
29: ["https://discovery.ucl.ac.uk/10144748/1/Manuscript%20Draftl.pdf (FTRC Part 1, heat flux)", "https://core.ac.uk/download/520520047.pdf (Shelke et al. 2022 IJHMT 21700)"],
30: ["https://core.ac.uk/download/395738649.pdf (Csernyei and Straatman 2016, multiple impinging round jets on a cylinder)", "Singh, Premachandran, Kohli 2013 (subscription)", "NASA TN D-7127 (concave surface)", "Applied Thermal Eng. 162 114308 (round jets on cylinder)"],
31: ["Olsson, Ahrne, Tragardh 2004 J. Food Eng. 63 393 (abstract gives Num = 0.14 Re^0.65 (H/d)^-0.077 (d/D)^0.32)", "Nada 2006 Heat Mass Transfer (slot jets on cylinder)"],
32: ["Churchill and Bernstein 1977 J. Heat Transfer 99 300 (via textbook)", "https://ahtt.mit.edu (Lienhard textbook, open access)"],
33: ["https://ntrs.nasa.gov/api/citations/20210024752/downloads/... (NASA side wall rupture rates, 18650)", "https://ntrs.nasa.gov/api/citations/20240012828/downloads/Sidewall%20Rupture%20Characterization%2021700-Update2.pdf (NASA 21700 SWR)"],
34: ["https://wrap.warwick.ac.uk/id/eprint/188615 (Read, Jones and Marco 2024 JPS Advances 30 100162, CC BY)", "https://wrap.warwick.ac.uk/186891 (Read et al. 2024 J. Energy Storage 95 112491)", "https://wrap.warwick.ac.uk/193824 (Allen et al. 2025)", "https://wrap.warwick.ac.uk/188614 (Allen, Jones, Marco 2025 J. Energy Storage 105)"],
35: ["https://wrap.warwick.ac.uk/179422/1/1-s2.0-S0306261923009741-main.pdf (Chen et al. 2023 Applied Energy 349 121610, CC BY)", "https://wrap.warwick.ac.uk/172264/ (Chen et al. 2022, radial nail penetration, CC BY)"],
36: ["nothing relevant (aluminium smelting, aerogel white papers)"],
37: ["Srinivasan et al. 2020 JES 167 020559? (condensed esters on adjacent cells; open access)", "Hoelle et al. 2024 (particle deposition)", "Mishra et al. 2021 JES (venting of hot gases)"],
38: ["Plunkett et al. 2021 Applied Energy 286 (current dumping, 18650 NMC packs)", "https://publikationen.bibliothek.kit.edu/1000173243/155178633 (Kim et al., needle penetration, ISC current measured)", "Feng et al. 2015"],
39: ["https://asset.conrad.com/media10/add/160267/c1/-/en/002114679DS01/... (LG Chem INR21700 M50 product specification 2017)", "https://aws.robu.in/wp-content/uploads/2021/11/DATASHEET-LGM50T.pdf (M50T datasheet)", "batterydesign.net (Popp et al. DCIR)", "forum tests (not used)"],
40: ["Long, Liu and Zhang 2023 Energy Adv. (ISC resistance)", "JES 2023 dynamic ISC resistance (Zhang group)", "Abaza et al. 2018 J. Energy Storage 16 211 (internal and external short circuits)", "core.ac.uk 519560045 (21700 nail TR model with ISC resistance)"],
41: ["https://ecn.sandia.gov/battery-safety/21700-m50lt/ (CID and burst disk described in ECN9.18 slides)", "M50LT and M50T datasheets (CID activation)", "Li, Crompton, Ostanek 2022 J. Energy Storage 46 (CID activation pressure, 18650)"],
42: ["https://scielo.org.mx/pdf/rmf/v60n4/v60n4a10.pdf (Cardenas-Garcia 2014: high-emissivity black paint 0.972 +- 0.012, 8-14 um, 50-150 C)", "FLIR tables (carbon, lampblack 0.95 to 0.97)"],
43: ["camera emissivity tables (nickel-plated steel 0.11; not used: the cans were painted)"],
}

ADDED = [
    {"query": "Popp 2020 LG M50 internal resistance 10 °C 45 °C 400 % DC pulse 21700",
     "reason": "to find the full reference of the resistance study that the page found under search 39 cites (Popp et al. 2020); found: Elektrotech. Inftech. 137 (2020) 169-176"},
]

# Every source read for the survey: how, under what conditions, what it gave and what it did not give.
SOURCES = [
    dict(key="Fransson2024", how="whole text, through a text reader (journal pages 1 to 11)", cond="LG M50 and Molicel P42A pairs, nail, 15 % CO2, the ESRF chamber",
         gave="the rig (orientation, contact, tabs, thermocouples, paint, nail, atmosphere), fire at the vent, the categories and the tables of outcomes",
         not_gave="state of charge, tab and holder material, ambient, which end vented, any current or voltage, any per-test account of ejection, any heat flux"),
    dict(key="FranssonSupp", how="whole file, text layer and as rendered (pages 28 to 32)", cond="as the article",
         gave="Fig. 9(b) the holder with the trigger above, Fig. 10 two thermocouple records with section rates, Fig. 11 photographs of melt, rupture and movement, Fig. 12 the parallel circuit, Fig. 13 rates and temperatures by outcome, Fig. 14 thermal images",
         not_gave="the holder's dimensions or material, flame temperatures (the thermal images saturate at 500 C), test names on the photographs"),
    dict(key="Fransson2023", how="whole manuscript (13 pages)", cond="Molicel INR21700-P42A pair in parallel, 100 % charge, the same chamber",
         gave="the holder's photograph, a small air gap between the sidewalls in one radiograph, the contact and the tabs named as the two heat paths, a temperature-induced breach of the propagating cell (147.65 and 148.00 s)",
         not_gave="anything on the M50, the holder's material or dimensions"),
    dict(key="Pfaff2023", how="whole text, through a text reader", cond="the chamber of the tests",
         gave="aluminium frame, 3D-printed inserts, about 2 mm of contact per fixture, a 343 l gas-tight chamber with exhaust and CO2 purge",
         not_gave="the inserts' material, the holder's dimensions in the text"),
    dict(key="Databank", how="ReadMe sheet in full; the ten M50 nail rows of the data sheet", cond="LG 21700-M50 (BV), nail, 100 % SOC, FTRC",
         gave="per-test body and ejecta energies, masses, voltages, failure mechanisms, the definitions of every column",
         not_gave="how the energy of the unrecovered mass is computed (given by WalkerPart1)"),
    dict(key="Finegan2024", how="whole text (local copy)", cond="the Databank's cells",
         gave="what the calorimeter captures (particles and flames arrested), less excess oxygen than in an open volume, the ejected mass's heat per gram",
         not_gave="the method of the unrecovered mass's energy"),
    dict(key="WalkerPart1", how="through a text reader, the method and results", cond="FTRC; cells include the LG 21700-M50",
         gave="the unrecovered mass's energy is a sensible heat from the baffles' temperatures; the M50's negative side took 59 % of the energy in its nail tests",
         not_gave="vent gas temperature, velocity, radiant heat"),
    dict(key="Walker2019", how="not read: subscription (record page only)", cond="", gave="nothing", not_gave="everything; the Part 1 manuscript stands in for the calorimeter's method"),
    dict(key="Sharp2022", how="through a text reader", cond="LG 21700-M50 and others, nail, 100 % SOC, FTRC with radiography",
         gave="both vents of the M50 activated; ejected mass about 30 to 54 g; a runaway of about 2 s; molten copper seen in most M50 tests; volatiles lost through the fume extraction",
         not_gave="venting duration or velocity, any gas or ejecta temperature"),
    dict(key="SandiaECN", how="web page", cond="LG INR21700-M50LT teardown", gave="5.6 % of the mass is electrolyte, 78 % of it DMC (given without a citation, for similar M50 cells); NMC811 with about 1 % Si; CID and burst disc at the top", not_gave="gas amounts"),
    dict(key="Hiden", how="project summary, 2 pages", cond="21700 NMC811 (maker not named), 50 l vessel", gave="6.5 l of gas at 100 % SoC, hydrogen and CO2 more than half of it", not_gave="the full composition, the cell's model; the paper itself is behind a subscription"),
    dict(key="Vendra2022", how="accepted manuscript, through a text reader", cond="21700 NMC, 4.8 Ah, 100 % SOC; cone calorimeter and a sealed canister",
         gave="total heat release in open air 96.2 to 136.5 kJ (test 2's printed parts sum to 127.3 kJ), peak heat release rate 3.33 to 3.79 kW, vent gas 0.53 mol with its composition, internal temperatures up to 1109.3 C; NMC cathode, carbon anode",
         not_gave="any measured gas or flame temperature, any duration"),
    dict(key="Chen2020", how="published version, through a text reader", cond="21700 NMC, 5 Ah, 68.3 g, vertical, ventilated chamber",
         gave="flame temperatures cited up to 1069 C (single cells) and 1500 C (a module), combustion of 11.1 to 16.3 s, flame heights up to 333 mm, peak heat release rates near 3 kW",
         not_gave="radiant fraction, heat flux at a neighbour"),
    dict(key="Chen2023", how="published version, through a text reader", cond="21700 NCA/graphite-Si, 4.8 Ah, nail",
         gave="sidewall rupture in 2 of 6 cells at 100 % SoC and 6 mm/s (1 of 5 at 0.5 mm/s, 4 of 5 at 100 mm/s), cracks near the bottom, a jet fire of about 110 s and combustion of about 5 min, mass loss above 45 %", not_gave="temperatures of the jet"),
    dict(key="Gillich2024", how="web text", cond="LG MJ1 and Sony VTC5A 18650, 100 % SOC",
         gave="peak gas velocities 398.5 and 260.9 m/s, mass flows 27.92 and 22.15 g/s, a measured runaway of 1.131 +- 0.291 s (LG MJ1)", not_gave="any 21700 velocity (its review table did not extract)"),
    dict(key="Mier", how="slides and accepted manuscript, through a text reader", cond="18650 cells", gave="jet leading edge about 150 m/s, core near Mach 1, flow projected outward at 21 degrees", not_gave="21700 data"),
    dict(key="KarpSica2022", how="through a text reader", cond="LCO 18650 and pouch cells, nitrogen vessel", gave="vent gas volumes 3.75 and 9.9 l and the energy of their combustion, calculated for complete combustion", not_gave="NMC 21700 data"),
    dict(key="Baird2020", how="accepted manuscript, through a text reader", cond="review of vent gas data", gave="no NMC 21700 values in the text", not_gave="values for this format"),
    dict(key="Golubkov2014", how="found, not read in full", cond="18650 cells", gave="not used: no bound uses a gas amount (E_avail rests on measured heat releases)", not_gave=""),
    dict(key="Lugaresi2026", how="through a text reader", cond="LFP 18650 and 26650 cells", gave="radiative heat flux 150 mm from the cell: about 50 to 150 kW/m2 in the first flaming event of most cells, later peaks of about 150 (18650) and 350 to 500 kW/m2 (26650); no radiant fraction", not_gave="NMC or 21700 data"),
    dict(key="Feng2015", how="through a text reader", cond="25 Ah prismatic NMC cells in a module", gave="the heat reaching a neighbour by shell, connector and fire (fire 162 J of 605 kJ)", not_gave="cylindrical-cell data"),
    dict(key="Read2024", how="published version, through a text reader", cond="LG INR21700-M50, 100 % SOC, nail through the positive terminal, open module with 3 mm gaps",
         gave="sidewall rupture in 3 of 3 with a 35 mm nail and none with 10 mm, ruptures on the bottom half of the casing, a jet fire impinging on the neighbours, which ran away 2 to 5 s later, trigger surfaces of 1051.5 to 1248.1 C with rupture", not_gave="heat flux"),
    dict(key="NASA21700", how="slides", cond="LG M52V, Molicel P45B, Samsung 50S and 53G, hot plate", gave="sidewall rupture in 1.1 to 5.2 %, bottom rupture in 4.4 to 48.9 %", not_gave="M50 data"),
    dict(key="Csernyei2016", how="through a text reader", cond="air jets on a heated cylinder", gave="an average Nusselt number for round jets on a cylinder (Eq. 16, Re 2.06e5 to 1.236e6)", not_gave="anything for a jet that starts against the can"),
    dict(key="Olsson2004", how="abstract only (subscription)", cond="slot jets on cylinders", gave="Nu = 0.14 Re^0.65 (H/d)^-0.077 (d/D)^0.32", not_gave="the paper's ranges"),
    dict(key="Lienhard", how="the relevant sections of the authors' PDF", cond="relations and properties", gave="Churchill and Bernstein, eqns (7.65) to (7.68), pp. 390-391; Table A.6 (air, hydrogen and other gases); the constants", not_gave=""),
    dict(key="LGsheet", how="whole datasheet", cond="LG INR21700 M50 (2017, tentative)", gave="18.2 Wh, 3.63 V, dimensions, AC impedance at most 25 mOhm, DC resistance 30 +- 6 mOhm at 25 C", not_gave="resistance above 25 C, a CID statement"),
    dict(key="Popp2020", how="through a text reader", cond="LG M50, 50 % SOC, 10 to 45 C", gave="the resistance falls about fivefold from 10 to 45 C", not_gave="the resistance above 45 C"),
    dict(key="Cardenas2014", how="abstract", cond="a high-emissivity black paint", gave="emissivity 0.972 +- 0.012 at 8 to 14 um", not_gave="the rig's carbon paint, absorptivity for flame radiation"),
    dict(key="Gulsoy2025", how="through a text reader", cond="Sony VTC6A", gave="nothing usable", not_gave=""),
    dict(key="KimKIT", how="through a text reader", cond="prismatic cells", gave="not this format", not_gave=""),
]


def main():
    path = os.path.join(ROOT, "results", "stage14_survey.json")
    d = json.load(open(path))
    d["written"] = "2026-11-16, before commit c8172e2 (11:13:19 UTC), pushed at 11:13:23 UTC as the branch's first push; the record below was added after the searches"
    d["searches_run"] = [{"n": n, "run": "2026-11-16, web search tool, standard mode", "candidates": RUN[n]} for n in sorted(RUN)]
    d["searches_added"] = ADDED
    d["sources"] = SOURCES
    d["not_found"] = [
        "a radiant fraction for a battery vent flame",
        "a heat flux or deposited energy measured at a neighbouring cylindrical cell's place",
        "a gas temperature measured at a 21700 cell's vent",
        "a vent velocity or mass flow for a 21700 cell",
        "the share of vent gas that passes a neighbour, or a velocity or temperature beside it",
        "the share of the ejecta that leaves through a breach, a breach's opening or its jet's velocity",
        "the temperature of ejected solids, or the mass of solids and melt found on a neighbour",
        "the material of the holder's inserts, or any temperature of the holder",
        "a current or voltage history of parallel cells during a neighbour's failure, or the resistance of a nail's short",
    ]
    with open(path, "w") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
    print(f"wrote {path}: {len(d['searches_planned'])} planned, {len(d['searches_run'])} run, {len(ADDED)} added, {len(SOURCES)} sources")


if __name__ == "__main__":
    main()
