---
name: theo-circle-vocab
description: Extract and organize English vocabulary visibly circled or otherwise specifically marked in the user's reading photos, screenshots, scans or PDFs. Use when the user asks to identify 圈出的单词、生词、标记词 or create a readable vocabulary list with pronunciation, common Chinese meanings and sense-matched synonyms without relying on the article context, and optionally append the result to a printable cumulative PDF. Preserve uncertainty from messy handwriting and distinguish marks from annotations or answer choices.
---

# Theo 圈词整理

Turn the user's markings into a readable, accurate study list. The user's photo is the source of truth for what was selected. Use the photo to identify marked word forms, and use dictionary-style common meanings independently of the article context.

## Inspect the markings

1. Inspect the entire supplied image or document, in page and reading order. Zoom or crop individual regions for closer inspection when necessary; use OCR only as a reading aid, and visually check both the word and its marking. Do not claim exhaustive detection if part of the image is cut off, blurred or obscured. Process multiple pages when supplied.
2. By default, extract clearly circled printed or handwritten English words and circled word groups. Include other markings, such as highlights or underlines, only if the user asks for them or when the mark clearly singles out a word as vocabulary. Long underlined sentences, handwritten explanatory synonyms, proper names and circled multiple-choice answers are not automatically vocabulary; include them if explicitly requested. Do not mistake the author's surrounding handwriting for additional selected words.
3. Keep a separate short **待确认** group for legible words where the outline or target is ambiguous. If the word itself cannot be read, describe its approximate position instead of guessing. Continue with the certain items first; ask for a clearer close-up only if necessary. Include plausible marked words even if they are simple or unusual, rather than filtering by difficulty.
4. Preserve the exact marked form and give the dictionary headword when different: e.g. `propelling → propel`; deduplicate repeated headwords while retaining the photographed forms. For a marked phrase, explain the phrase and, when helpful, separately identify its key word. Give the most useful common dictionary meanings independently of the photographed sentence. Do not use the article to select, limit or explain a sense unless the user explicitly asks for contextual interpretation.

## Build the vocabulary list

- Default to American IPA for the **headword**, label it 美音, and identify the headword so its pronunciation is not mistaken for the photographed inflection. Follow any requested accent or format. Verify uncertain pronunciation, spelling, rare terminology and nuanced meaning against a reputable dictionary when available; provide the actual source links when consulted. Do not fabricate references or audio. If a pronunciation cannot be verified confidently, mark it for verification rather than inventing it.
- Give the part of speech and one to three common Chinese meanings independent of the article. Match two or three useful English synonyms to the relevant sense and part of speech, grouping by sense if needed; add brief Chinese glosses where useful. Synonyms may not be interchangeable in every sentence; mention an important distinction if needed. Do not pad a technical term with false equivalents; instead label an accurate **英文释义** as a paraphrase or state that no common exact synonym is available.
- Default to a vertically arranged, numbered list readable on a phone: `marked form → headword | IPA | 词性`, followed by separate short lines for 常见意思 and 近义词. Use a table only if the user requests one or it clearly improves readability. Preserve the text's reading order. Keep uncertain candidates clearly apart, with their own pronunciation and meaning only when the word is legible.
- Briefly explain distinctive collocations or easily confused distinctions only when they help learning. Prefer the selected words to a long generic vocabulary lesson. State image limitations without excessive caveats.
- If the user wants a cumulative PDF, save each new batch as described below. Follow any different output format the user explicitly requests. Do not upload images externally or create public repositories without authorization.

## Maintain a printable vocabulary book

When the user wants a running PDF, append each new image batch to their chosen workbook. Do not use a hard-coded personal file, account, or identifier. If no workbook has been designated, create an appropriately named one in the user's chosen or default destination, and retain its identity for later updates. Follow any request for a different output format.

1. Obtain the latest version of the user's chosen PDF using the tools available in the current environment. Preserve its identity and any version information. If the file is unavailable or a conflict prevents safe replacement, do not silently create an unrelated replacement; explain the problem.
2. Generate the new batch as A4, grayscale-friendly, single-column pages with generous margins and readable embedded Chinese and IPA fonts. Include original word form and headword, American IPA, part of speech, common Chinese meanings, sense-matched synonyms or a clearly labeled explanatory paraphrase, and uncertainty where appropriate. Include a batch number and date. Use batch-relative page numbering so earlier page numbers stay correct. Preserve previous entries, order and pages; do not automatically remove duplicates across batches.
3. Use the PDF tools available in the current environment to render and inspect the new pages. Append them with `python3 <skill-dir>/scripts/append_pdf.py --base <existing.pdf> --batch <new-batch.pdf> --output <candidate.pdf>`; the helper requires `pypdf`, refuses to overwrite either input and checks page text and dimensions. Verify page counts and inspect for missing glyphs, clipping and overlap.
4. Save the validated candidate back to the chosen workbook using the applicable version-aware workflow. Give the user a link to the updated PDF and state how many words or pages were added. If the user requests the newest batch separately, provide it in addition to the cumulative book.
