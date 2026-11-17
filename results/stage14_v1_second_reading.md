# Stage 14 inputs: second reading (v1)

Read on 16 and 17 November 2026. All 89 rows of `results/stage14_inputs.csv` were checked: the 80 first rows and the nine Table A.6 rows added later (`air_1000K_nu` to `h2_1000K_Pr`). Each row was opened at the place it cites. The `db_` rows were recomputed from the workbook. Row by row, the findings are in `results/stage14_v1_second_reading.csv`.

## Copies read

- Local copies, each with the SHA-256 given in `results/stage14_inputs_sources.csv`: the Fransson 2024 supplement (pages 28 to 32, with Figs. 9, 12 and 14 rendered); the Fransson 2023 manuscript; the Battery Failure Databank workbook (sheets ReadMe and Battery Failure Databank); and Lienhard's textbook (PDF and text, where the printed page is the PDF page less 14). Finegan 2024 was read from the local PDF, which the sources file gives no hash for. The Model rows were checked against `DECISIONS.md` (D36, D52, D68, D77).
- Web copies, read through the fetch tool at the URLs in the sources file: Fransson 2024, Pfaff 2023, Walker Part 1, Vendra 2022, Chen 2020, Chen 2023, Gillich 2024, Sharp 2022, Read 2024, the NASA 21700 slides, the LG datasheet, Popp 2020, Cardenas-García 2014, the Hiden summary, Karp and Sica, the Sandia ECN page, Mier (both copies), Lugaresi 2026, Feng 2015 and Csernyei 2016. For Vendra, Chen 2020, Read and Lugaresi, the PDF linked from the record page was read.
- The fetch tool answers from a model's reading of each page, so quotations and pages from web copies are as it returned them. Where two answers disagreed (Vendra's pages, the NASA slide numbers, the page of Csernyei's Eq. 16), I asked again and kept the reading that the page-number lines support.

## Counts

89 rows: 71 agree, 17 corrected, 1 could not be traced.

## Corrections

- `rig_atmosphere`: the fire sentence quoted from p. 7 describes the Category 3 example, a sidewall melt. The paper reports sidewall melts only in P42A cells. The other fire statements (p. 6; pp. 7 to 8) do not name the cell. So fire at the vent is a fact of the rig, but no sentence ties it to an M50 test by name.
- `rig_chamber`: "heat-resistant and gas-tight design" is in Pfaff's abstract on p. 192; the rest is on p. 193. The walls are three 6 mm stainless-steel sidewalls, welded to 8 mm top and bottom panels.
- `rig_holder`: the holder sentences are on Pfaff p. 194, not p. 193.
- `rig_categories`: the category text and "In 4 of the M50 tests, the cell moved within the FoV" are on p. 4. Only the Fig. 2 caption is on p. 5.
- `fr2023_gap`: the caption runs onto p. 6 ("separating the two"), so the locator is pp. 5 to 6.
- `vendra_Qt_1`, `vendra_Qt_3`: the values agree (Table 2, p. 10), but Table 1 gives the anode as carbon, not graphite.
- `vendra_Qt_2`: Table 2 prints Qt as 136.5 kJ for test 2, but its printed parts sum to 127.3 kJ (85.6 + 41.7). The source does not say which number is wrong. The anode is carbon.
- `vendra_Qt_max`: the largest printed Qt is test 2's, which does not add up. From the parts, the range is 96.2 to 127.3 kJ. The anode is carbon.
- `karp_gas`: pages traced to pp. 3, 4, 5, 8, 10, 11 and 12. The combustion energy is calculated, not measured. p. 13 gives the 18650 cell as 2.5 Ah, against 2.6 Ah in Table 2.
- `ecn_electrolyte`: the page does not attribute 5.6 % and 78 % to a teardown of the M50LT. It points to an inventory "from similar M50 cells" and cites nothing for the figures. It does not call the M50LT a later variant.
- `mier_jet`: located. The 150 m/s leading edge is in the OSTI document, not the slides. Mach 1 is on slide 19, and 21 degrees on slides 11 and 20 of the sandia.gov slides.
- `lugaresi_flux`: 50 to 150 kW/m2 is the first flaming event of most cells of both formats, not the 18650 peak. The 18650 cells' second peak was about 150 kW/m2, and the 26650 cells reached 350 to 500 kW/m2. The range of 50 to 500 kW/m2 stands.
- `csernyei_jet`: Eq. 16 is on p. 302, not p. 301.
- `t_vent_min`: Gillich measured 1.131 s (± 0.291 s) for the LG MJ1. "Lower than 1.5 s" is only a bound, so the shortest published duration is about 1.13 s, not 1.5 s. Sharp's phrase is on the eighth or ninth page; the copy has no page numbers.
- `chen2023_rupture`: the count is on p. 5 only. The six cells were penetrated by a 4 mm nail at 6 mm/s through the top cover. At other nail speeds the paper reports 1 of 5 (0.5 mm/s) and 4 of 5 (100 mm/s).
- `nasa_rupture`: slides traced: 19, 21, 23 and 25 (one per cell), 27 or 28 (bottom ruptures), 31 (summary) and 13 (hot plate).

## Could not be traced

- `chi_rad`: no source is cited, so there is nothing to trace. 1.0 is a limit by definition.

## Other points (not counted as corrections)

- `db_no_breach`: no row in the whole Databank uses a sidewall category in Cell-Failure-Mechanism. The ten M50 rows record top and/or bottom vents.
- The ten Databank rows used are the M50 nail rows at 4.164 to 4.189 V. The other seven M50 nail rows (RUN199 to RUN205) are at about 3.82 V and 3.44 V.
- Chen 2020's cell (21700 NMC, 5 Ah, 3.63 V, 68.3 g, 266 Wh/kg) matches the M50's rating, but the paper does not name it, so "other cell" stands.
- The note on `db_bottom_vent` holds: Fransson 2024 says nothing about a bottom vent.
- Pages not confirmed: Popp 2020's p. 172, because the web copy has no page numbers. Pfaff's pages come from a single reading.
- The sources file: Cardenas-García 2014 has one author (Rev. Mex. Fís. 60 (2014) 305 to 308), not "et al.". Csernyei and Straatman is Applied Thermal Engineering 105 (2016) 290 to 303.
