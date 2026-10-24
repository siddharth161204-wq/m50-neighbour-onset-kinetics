# Battery Failure Databank rows

The three files here are copied unchanged from `inputs/databank/` of the two-cell study (S. Satte, doi:10.5281/zenodo.23253738, v1.0.0, commit 2b35ac7aa1a2cc822ed59f61fc73128b220bdd1c), whose `SOURCE.txt` gives the workbook's address, its SHA-256 and its retrieval, and whose `extract_databank.py` regenerates the rows from the workbook.

| File | SHA-256 |
|---|---|
| `DATABANK_NOTICE.txt` | 1d3f14554a23fc47674fd26dea7200923190375f57d06fce692328f38d4f11b1 |
| `databank_m50_rows.csv` | b5a8792d390acd7031c555ac3230a3206405309c4a663887ffc9b9b17e57c000 |
| `databank_m50_used.csv` | 7e80d4c08fdf64f94e19ec08877f46c2a9fc97e9c4384a791858ec5d3e5c3ede |

Source: Battery Failure Databank, revision 2 (February 2024), National Renewable Energy Laboratory (now National Laboratory of the Rockies), U.S. Department of Energy; described in D.P. Finegan et al., Journal of Power Sources 597 (2024) 234106, doi:10.1016/j.jpowsour.2024.234106.

Stages 1 to 4 read no file here. Their energies, 8.75, 21.5 and 33.2 kJ through the cell body, are the minimum, median and maximum of `Energy-Fraction-Cell-Body-kJ` over the 17 tests at 100 % state of charge in `databank_m50_used.csv`; they reach those stages only through the two-cell study's archived temperature histories, which were computed with them. Stage 5 reads `databank_m50_used.csv` for the cell-body energies of its ten nail tests (the sensitivities of DECISIONS.md D38), and Stage 6 for their `Corrected-Total-Energy-Yield-kJ` (D53). The rows are here so that the Databank's notice accompanies them, as it requires.

The Battery Failure Databank is provided by the U.S. Department of Energy's National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC (DOE/NREL/ALLIANCE); its notice accompanies the rows used, in inputs/databank/.
