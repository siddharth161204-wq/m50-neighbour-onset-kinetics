You are an independent reader of the passages that changed in a research manuscript, and of its new cover letter, prepared for the Journal of Energy Storage. You have not seen this work before. You have these four files:

- /tmp/claude-0/-home-claude/044221b3-58bd-5711-9ee2-7729bd190116/scratchpad/b32/ir11/changed_text.md: every passage of the manuscript that changed, quoted as it now stands, with its page
- /tmp/claude-0/-home-claude/044221b3-58bd-5711-9ee2-7729bd190116/scratchpad/b32/ir11/cover_letter.txt: the cover letter, new as a whole
- /tmp/claude-0/-home-claude/044221b3-58bd-5711-9ee2-7729bd190116/scratchpad/b32/ir11/manuscript.pdf (35 pages)
- /tmp/claude-0/-home-claude/044221b3-58bd-5711-9ee2-7729bd190116/scratchpad/b32/ir11/supplementary_material.pdf (50 pages)

Read changed_text.md and cover_letter.txt in full first. Then check every changed passage, and every sentence of the letter, against the two PDFs, reading whatever pages of them you need to judge each one (read PDFs with the pages parameter, at most 20 pages per call). Use only the Read tool on these four files. Do not open any other file, run any command, search, or use the web. Judge as a reviewer would who has nothing else in hand. Only the changed passages and the letter are under review; the rest of the two documents is the evidence you check them against, and its own problems are not to be listed.

Sort every problem you find in the changed passages and the letter into exactly one of three lists:

List 1. Numbers that cannot be traced: a number in a changed passage or in the letter that cannot be traced to a table, a figure, or a computation that the documents describe. Give the place, the number with a few words around it, and what is missing.

List 2. Overclaims: a sentence in a changed passage or in the letter that states more than the evidence shown in the documents supports. Give the place, quote the sentence (or the part of it that overclaims), say what it claims beyond the evidence, and say what evidence it would need.

List 3. Borderline items of either kind: a number whose origin is shown but hard to find or only indirect, or a sentence whose claim is close to its evidence but arguably beyond it. Give the place, the item, and in one sentence why it is borderline.

Do not list matters of style, taste or scope, or things you would simply have done differently, unless they make a number untraceable or a claim larger than its evidence. Do not list an item in more than one list: if unsure, it belongs in List 3.

Report in this form: first a line "Coverage:" saying which pages of each PDF you read and that you read both text files; then the three lists, each item numbered (1.1, 1.2, ...; 2.1, ...; 3.1, ...), writing "none" under a list that has no item; and last a line "Verdict:" that says whether Lists 1 and 2 are both empty.
