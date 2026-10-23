# Fransson et al. (2024): the measured two-cell LG M50 tests

M. Fransson, J. Pfaff, L. Broche, M. Buckwell, C. Kirchner-Burles, H.T. Reid, S. Schopferer, A. Rack, D.P. Finegan, P.R. Shearing, Exploring thermal runaway propagation in Li-ion batteries through high-speed X-ray imaging and thermal analysis: Impact of cell chemistry and electrical connections, Journal of Power Sources 617 (2024) 234916, doi:10.1016/j.jpowsour.2024.234916. Open access under CC BY 4.0. (Subtitle and three authors' initials corrected on 24 October 2026, DECISIONS.md D59.)

Copies read on 21 October 2026:
- Version of Record on ORA (University of Oxford): https://ora.ox.ac.uk/objects/uuid:4a6edaf0-c309-40b5-b863-cf32243fa7ec (file s3t945s923);
- the copy on the document server of the National Laboratory of the Rockies: https://docs.nlr.gov/docs/fy24osti/87353.pdf.

Both were read as text through a web reader, because this machine cannot download either file. The rows, the quotations and the definitions of the sections below come from that text; the figures were not seen. The reading of the time to propagation (DECISIONS.md D34) rests on the text.

## `m50_tests.csv`

Tables 3 (M50, parallel) and 4 (M50, series), one row per test: the test name, the connection, the trigger cell's and the propagation cell's maximum temperatures (C), whether the neighbour propagated, the time to propagation (s) and the failure category ("cell movement" where the paper gives it in place of a category, empty where the table has a dash). The tables' average rows (parallel: 603 ± 195 C, 414 ± 290 C, 4/8, 212 ± 72 s; series: 686 ± 174 C, 506 ± 256 C, 5/8, 220 ± 74 s) recompute from these rows (sample standard deviations).

## Quotations used (DECISIONS.md D33, D34, D39)

- Setup: "The cells were placed directly in contact with each other." "electrically connected via welded cell tabs. The wires for the voltage reading were welded onto the tabs." "The trigger cell was penetrated around the center with a speed of 6 mm s−1 to an approximate depth of 1–3 mm, and propagation awaited." "Thermocouples were fastened in the middle of the cell surface using Kapton tape and heat conductive glue." "Each cell was coated with black carbon paint to reduce reflectivity and improve the quality of the thermal images." "a 15% CO2 ratio was used for fire retention."
- Sections of the temperature record: "The time between the temperature increase caused by the TR of the cell and the maximum measured temperature is classified as Section 1." In Section 2 "the trigger cell starts to cool down and the dissipated heat is conducted to the propagation cell that heats up." "For experiments with propagation, the second section ends at the onset of the TR in the second cells"; "for experiments without propagation, this section ends at the temperature maximum of the propagation cell". "Section 3 contains the TR temperature response of the second cell."
- Time reference: "propagation occurred 156 s after TR in the trigger cell" (discussion of Fig. 5).
- Propagation outcome: "The propagation outcome can be determined by the temperature spikes in the thermocouple readings, where only one spike is present if no propagation occurred and two spikes visible if propagation occurred."
- Threshold and heat rate: "a minimum of 150 ◦C is required in the neighboring cell in order for propagation to occur" (from Fig. 3a); "the average heat rate for propagation to occur was 0.4 ◦C/s compared to 0.1 for non propagating cells", the heat rates "calculated from measured temperatures in Section 2".
- Categories: 1, "Quintessential representation of nail penetration failures in trigger cells"; 2, "Quintessential representation of failure in propagating cells"; 3, "Representation of sidewall melting in trigger and propagating cells"; 4, "Representation of sidewall rupture in trigger cell".
- Cell movement and outliers: "In 4 of the M50 tests, the cell moved within the FoV and neither failure classification nor speed calculations were not possible." "Due to movement of cells and thermocouples during failure, some outlier temperature values are still represented in the tables for consistency reasons."

## `fig10_section_rates.csv` (Stage 6, DECISIONS.md D52)

The paper's supplementary material (Appendix A, `1-s2.0-S0378775324008681-mmc1.pdf`, 10,240,301 bytes, SHA-256 e96713ef58e8dc13df8810034c7ee8b47fb3e2fdcdb398a5095ecdfb64dfc0ef), read on 23 and 24 October 2026 through its text layer and as rendered. Its Figure 10 shows the thermocouple records of M50_PT_Exp4 (propagated) and M50_PP_Exp3 (not propagated). The caption explains that each record is divided into sections, that the mean heat rate of each cell in each section is computed from them and printed in boxes beside the plot, and that Section I is "the region of TR in the trigger cell"; Section II is the heat exchange while propagation is awaited, Section III the second cell's runaway (only where it occurred), Section IV the cooling. One row per test, section and cell (trigger, propagation): the mean heat rate in C/s as printed.
