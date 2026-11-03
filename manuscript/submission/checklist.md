# Submission checklist: Journal of The Electrochemical Society

Checked against the journal's instructions page, "Welcome to the ECS Publishing Journey" (https://www.electrochem.org/?p=57625, last modified 7 October 2026), as read on 3 November 2026, and against Brief 21. Read the page again on the day of submission; anything changed since is the author's to apply. Submission is through ScholarOne, mc04.manuscriptcentral.com/jes-ecs.

Status: **done** (in this folder), **author** (the author's step), **note** (a departure or a judgement, with the reason).

## The manuscript

| Item | The journal's instruction | Status |
|---|---|---|
| Title | 15 words or fewer | **done**: 15 words, hyphenated words counted as one; two alternatives in `manuscript/titles.md` |
| Abstract | At most 200 words; no undefined abbreviations; no references to tables, figures, equations or citations | **done**: 198 words (`manuscript/word_count.py`); none of these |
| Corresponding author | Marked with a superscript "z" and an e-mail address | **author**: marked; the e-mail is a red placeholder in the PDF and the source, added at submission (it is not in the public repository) |
| Sections | Not numbered; the text does not refer to section titles | **done**: `\setcounter{secnumdepth}{0}`; no reference to a section in the text |
| Contents of the manuscript file | Title, authors, abstract, main text, acknowledgments, references; no highlights, graphical abstract, keywords or cover letter | **done** |
| Initial submission | One PDF with the figures and tables where they are cited | **done**: `Satte_JES_manuscript.pdf` (35 pages) |
| Source file | A .tex or .doc source is required; LaTeX has limited support, and a clean Word source is encouraged | **done**: `Satte_JES_manuscript.tex`, one file with the tables and references written in, which builds alone with `figures/figure1.pdf` to `figure8.pdf` to the same text as the PDF. **note**: after the author's pass the chat can write a clean Word source from the revised LaTeX, if the journal asks for one |
| References | Numbered in the order cited; CAS journal abbreviations; authors' initials; full article titles need not be included | **done**: elsarticle-num, numbered in order of citation, CAS abbreviations and initials; titles kept, which the page allows; DOIs printed as text, no live links |
| Acknowledgments | Conflicts of interest, sources of financial support, authors' contributions | **done**: conflicts (none), funding (none), contributions (CRediT, drafted for the author's confirmation), data availability (all-versions DOI, version 1.8.0), use of generative AI |
| Generative AI | Disclose in the Methods and/or Acknowledgments the tool, its version and model, its provider and how it was used; keep prompts and drafts; drafted text is allowed only when the authors critically review and substantially revise it; AI may not create or alter primary research data, and AI output may not be presented as the authors' own work | **done**: disclosed in both places (Claude, model Claude Opus 5.5, Anthropic, through the Claude application with code execution, 10 October to 3 November 2026; what it did). **author**: the pass over `manuscript/main_for_author.docx`, after which the declaration's red sentence ("the author revised the text, and no finding or interpretation was accepted without the author's validation") is made true and its brackets removed. The instructions given to the model are kept in the author's project. The measured data (Fransson et al.'s tests, the Databank's rows) are used as published; the model's outputs are simulation results of the archived code |
| Not under consideration elsewhere | The corresponding author confirms it | **author** |

## Files uploaded beside the manuscript

| Item | The journal's instruction | Status |
|---|---|---|
| Figure files | One composite file per figure, named by its number; EPS, TIFF or JPEG; 300 dpi; one-column width (3.25 in, 8.26 cm) wherever possible; lettering at least 1.6 mm; only one set of figure files; not required for the initial review | **done**: `figures/figure1.tif` to `figure8.tif`, 300 dpi, LZW; smallest lettering 8.73 pt, 2.25 mm capital height (`figures/sizes.json`). **note**: every figure is set at the full width, 17.1 cm, because each has panels side by side or a table, which at 8.26 cm would put the lettering below 1.6 mm. Upload the TIFF set only; the PDFs beside them are the vector files the .tex source uses |
| Supplementary material | Separate files, each with a descriptive caption, cited in the text; published as submitted | **done**: `Satte_JES_supplementary_material.pdf` (23 pages). Caption for the upload: "Supplementary material: the digitisation of the published histories; every pre-registered prediction of Stages 1 to 12 with its expectation and verdict; mesh and step convergence; Stage 12, the trigger held to the calorimetry (runs, thresholds and fractions); the energy accounts; the delivery's brackets; the survey of other datasets; the decisions that fix an input." |
| Graphical abstract | Mandatory since 1 April 2025; one image, JPEG, JPG, PNG or TIF; file name beginning "GA"; uploaded separately as a source file | **done**: `GA_two_cell_propagation.png` (16 by 7 cm, 300 dpi), drawn by `src/make_graphical_abstract.py` from the results files; its one-sentence caption in `GA_caption.txt` |
| Highlights | Optional for this journal; three to five, at most 85 characters each with spaces, no jargon or acronyms; a separate Word document named "Highlights", uploaded as a source file | **done**: `Highlights.docx` (five, 78 to 83 characters), from `manuscript/highlights.txt` |
| Keywords | At least three, chosen in the submission system; not in the manuscript | **author**: six suggested in `keywords.txt` |
| Cover letter | Not part of the manuscript file | **author**: `cover_letter_draft.md` and `.docx`, for the author's own words; its sentence "I revised the text" is true after the pass |
| Suggested reviewers | Not described on the page | **author**: `suggested_reviewers.md`, seven candidates to pick from and check, e-mails from their institutional pages |
| File names | Letters, numbers and underscores | **done** |
| ORCID | Each author links an ORCID iD to the ScholarOne account | **author**: 0009-0001-3584-1008 |
| Copyright form | Signed before acceptance | **author**, at acceptance |

## Before pressing submit

1. The author's pass over `manuscript/main_for_author.docx`; the chat applies it, re-checks every number, rebuilds, rewords the AI declaration, and regenerates this folder.
2. Zenodo version 1.8.0 published (the data statement names it; `FINISH_RELEASE`), with the manuscript as submitted in its zip. Depositing the author's own version is a preprint. This page does not address preprints; ECS's open access policy, as read earlier in this study, permits depositing a version that is not in the journal's format.
3. The e-mail address, the title, the CRediT roles and the cover letter in the author's words.
4. Re-read the instructions page on the day; check the abstract's word count in the submission system.
