# Complete uncertainty processing run and revision 1.1

20 September 2026. Private, AI-assisted review; no independent human verification or ACU endorsement.

The run processed **all 1,200 original uncertainty items on all 193 affected scan pages**. Seven Apple Vision OCR passes per page completed: **1,351 runs, zero errors**. It then applied supported image decisions from the earlier 50-item pilot and 31 additional item checks. **81 items have focused image adjudications; 1,119 were machine-processed but did not receive a new individual image adjudication.** This is a complete machine run, not a claim that every difficult passage has now been reread or resolved.

## Applied results

| Outcome among the original 1,200 items | Count | Treatment |
| --- | ---: | --- |
| Image-supported literal reading | 28 | Remove that uncertainty marker |
| Partly recovered reading | 2 | Recover Guthrie; retain unread given name |
| Clearer duplicate or continuation | 16 | Add cross-reference; preserve the physical gap in this scan |
| Individually checked, still unresolved | 33 | Retain marker |
| Context-only completion | 2 | Retain marker |
| No new individual image adjudication | 1,119 | Retain marker |

The first five outcome groups total 81; their selection was purposive. These counts cannot estimate the recovery rate of the remaining collection. Some entries refer to repeated versions of the same passage.

Thirty annotation replacements (28 full and two partial), six additional changes to surrounding text, eleven family-text corrections and seven synchronized editorial notes are recorded. Three newly recognized doubts were added. The current register has **1,175 entries = 1,200 − 28 + 3**. Existing uncertainty IDs remain stable; resolved IDs are retired, and new IDs are above the former maximum on their page. All 387 supplied source pages and 971 transcript blocks remain accounted for.

Examples include Gunter, Timmons, Fayette, A. Lasswell and H. C. Wise. Corrections also preserve discrepancies: the docket says 91 while a separate certificate says 92; the difficult heading reads Sat without establishing a month. An initially tempting reading of flee was not accepted and remains tentative. The Alfred death/wounding dates in the family edition now match June 5 and May 18 in the annotated source reading. This does not establish Nathaniel Lynn Douglas's father.

## Method and limits

Native embedded scan images were extracted without upscaling. Each page received four quarter-turn OCR passes with language correction off, followed by three passes at the highest OCR-score orientation: original with language correction on, and a grayscale 1-percent autocontrast version with correction off/on. Top-three OCR candidates, boxes, rotations, engine revision, operating-system version and settings are retained. No candidate vocabulary was supplied. Apple Vision can internally orient text: the highest score is a diagnostic, not a reliable handwriting orientation or accuracy score.

Literal OCR matches and nearby two-word anchors generated a triage list. Matches can refer to a different occurrence or a later archive label. No uncertain reading was accepted automatically or solely because OCR agreed. Selected regions were inspected against native pixels, neighboring text and identified duplicate scans. Rotation and deterministic contrast do not create missing ink. No generative image restoration, external image upload or trained handwriting recognizer was used. The review was informed by earlier AI proposals and is not blinded.

Ordinary OCR frequently misreads this handwriting. Many surviving marks remain too faint or ambiguous; other passages have not yet received fresh focused inspection. Further manual image adjudication, an independently evaluated handwriting-recognition model, or a human paleographic review may improve the result. No claim is made that all possible recovery work is exhausted.

## Evidence and audit files

- `baseline.json`: original 1,200 rows and annotated master frozen at commit `ef7651971ca60e27cf1d18695ab3d376311c4a64`.
- `image-manifest.json`: all 193 page identities, source checksums, extraction/contrast checksums and original item IDs.
- `ocr/`: complete raw results for all 193 pages. `machine-triage.json` contains diagnostics for every item.
- `adjudications.json`: 31 additional decisions with reasons, region coordinates, rotation and image checksum. The prior 50 are in `../image-pilot-2026-09/decisions.json`.
- `evidence/` and `support-image-provenance.json`: 31 decision images plus three complete supporting witness images. Original scans remain outside the repository.
- `item-ledger.json`: explicit machine-processing and image-review status for every original item. `review_record` paths are relative to the repository's `review/` directory.
- `applied-changes.json`, `family-changes.json`, `editorial-note-changes.json`: exact accepted text changes. Apply annotation edits by stable item occurrence, not global text substitution. Whole-line entries describe text after annotation replacement.
- `page-changes.json`: full before/after annotated page records, including witness notes and review metadata, for exact reconstruction.
- `validation.json`, `visual-review.json`, `font-map-corrections.json`, `font-repair-visual-check.json`: export, coverage, layout and PDF encoding checks. Layout checks do not validate handwriting accuracy.
- `verify_revision.py`: portable read-only check of coverage, decisions, current master, review images and package checksums. Run with Python 3 and Git from any directory in this checkout.
- `method/`: preparation, OCR, triage, application and export scripts retained as the execution record; see its README before reuse.

All eight Word documents and matching searchable PDFs were regenerated as revision 1.1. The offline HTML, plain text, structured data, uncertainty register, source-to-PDF map and both ZIP packages were rebuilt. Original editions remain recoverable at `v1.0-review`; the earlier contextual review and pilot are historical evidence and are not rewritten to look like this revision.
