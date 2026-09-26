# New scan additions and release checks

26 September 2026 · version 2.0

This addition covers all 545 pages newly supplied in Folder 4 (111), the daybook (167), Folder 6 (134), and Folder 7 poems and other writings (133). Combined with the earlier 387 pages, the edition accounts for 932 pages, 2,183 annotated blocks and 3,415 unresolved-reading entries. No original source PDF or rendered scan image is published here.

## Reading method and independence

Every new source page received an initial AI visual reading. Local Apple Vision OCR was run at four orientations for all 545 pages as a reading aid; it performed poorly on much of the handwriting and was not accepted as authoritative. Selected passages were enlarged, rotated or contrast-adjusted and compared with related passages or clearer copies in the collection. Manuscript wording, later typed copies, repository labels and editorial interpretation are distinguished in the transcript.

The other agent’s transcription was excluded from this addition. Reference and family readings were prepared together from the scans, so these two new versions are not independent readings of each other. Prior review records document the separate history of sources 01–06. No independent human verification or institutional endorsement is claimed.

## Evidence in this directory

- `replacement-comparison.json`: filenames, checksums and comparison results for the replacement copies of sources 01–06. They add no manuscript pages; PDF bytes may differ.
- `prebuild-review.json`: twelve selected before/after corrections and clearer-witness notes incorporated before export. It is not an exhaustive log of every reading decision.
- `export-audit.json`: source counts and checksums, Word/master agreement, PDF paragraph checks, HTML anchors and visual-review completion. One PDF raised-number extraction issue was verified with a second extractor.
- `visual-review.json`: SHA-256 hashes and completed visual-review status for all 584 final rendered new pages. PNGs are retained locally for QA and are not in this repository.
- `preserved-files.json`: hashes of 398 earlier document, Markdown, research and review files retained without changes, with the baseline commit.
- `verify_release.py`: portable package, coverage, link, checksum and historical-preservation checks. Run with Python 3 from any directory. Git is needed for comparisons against the recorded baseline commit.
- `release-validation.json`: results from the final package validation. The validator does not repeat the source-image reading or visual inspection.
- `final-checks.json`: byte comparison between the new release documents and verified outputs, complete PDF page totals, and offline HTML search checks.

## What the checks establish

All eight new DOCX files match the structured master; each non-empty document paragraph is present in its PDF after Unicode and whitespace normalization. All 584 new PDF pages were visually inspected for layout and legibility. The 313 earlier PDF pages and their documented inspection history remain unchanged. Checksums, page coverage, paragraph locators, HTML anchors and ZIP contents are checked separately.

The expanded uncertainty register preserves all 1,175 earlier rows and adds 2,240 rows. It includes doubtful readings, illegible text and explicitly missing or obscured passages. One row may cover multiple words. It is neither a count of errors nor proof of exhaustive recovery.

Export consistency is distinct from accurate handwriting interpretation. Damaged passages, identities, dates and literary allusions remain open to specialist review. Earlier machine-only uncertainty items retain their stated limits. The additions have not been reconciled word by word with the other agent’s complete version.
