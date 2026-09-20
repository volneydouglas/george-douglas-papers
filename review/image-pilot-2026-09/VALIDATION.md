# Validation record

19 September 2026. This record describes file and presentation checks, not independent verification of handwriting accuracy.

- All 50 frozen sample item IDs appear exactly once in `decisions.json`. Outcomes sum to 50 and all decisions cite existing evidence regions.
- Four source PDFs matched their recorded SHA-256 checksums before extraction. All 92 delivered image derivatives matched their manifest checksums and opened as valid PNGs.
- All 18 literal/partial patch records were located against the unchanged baseline paragraph text. Positional replacement handles the two identical Ellis markers in the same paragraph separately. The draft overlay covers 31 selected paragraphs and retains uncertainty on partially read names.
- Apple Vision produced 76 completed runs without recognition errors after macOS model access was permitted. An earlier sandbox-only attempt could not load the recognizer; it was superseded, not counted as a failed reading.
- The 12-page PDF was rendered to PNG and every page visually inspected. Text bounds were checked, and every selected item ID was found in the PDF’s extracted text. No page text lay outside the intended margins.
- The HTML viewer’s data, source-image links and JavaScript syntax were checked statically. Browser UI testing was blocked by the browser’s local-file URL policy. No visual or interaction check of the HTML viewer is claimed. The printable PDF and ordinary PNG files provide independently usable access to the review.
- Original source scans, edition files, earlier contextual review and research files were not edited by this pilot. Repository visibility and remote publication are checked separately at push time.

The retained source crops allow readers to challenge any decision. A human reviewer has not independently checked this addendum.
