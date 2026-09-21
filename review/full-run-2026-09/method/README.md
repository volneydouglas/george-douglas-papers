# Execution record

These are the scripts used in the local workspace, retained for inspection rather than as an unattended installer. They use workspace-specific absolute paths, the private iCloud originals, local book masters and bundled Python/LibreOffice/Poppler dependencies. The Swift OCR program uses Apple Vision on macOS. It records its engine revision, OS and request settings in each result. No API key is used.

Order: freeze baseline/extract native images; compile and run the Swift OCR tool on the saved input list; generate candidate diagnostics; record selected image decisions; apply the accepted annotation/whole-line changes; prepare and run both document builders; synchronize explanatory notes (and rerun both builders); render; repair family PDF Unicode maps; validate content, navigation and layout; package. Source image adjudication is a separate judgment step, not a script result.

`apply_full_review.py` uses temporary `%GD[...]%` tokens to retain stable item identities. The final published `applied-changes.json` expands those tokens in whole-line before/after strings; the temporary tokens are not transcript text. `synchronize_notes.py` records a final explanatory-note correction and the eleventh family edit after the initial build preparation. These scripts must not be rerun over a revised baseline without adapting the paths and checking the exact before strings.

The portable `../verify_revision.py` is the preferred read-only audit. `../page-changes.json` preserves exact before/after page records independent of local build paths. Private source files are deliberately not bundled.
