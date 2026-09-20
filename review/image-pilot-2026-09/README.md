# Image review of 50 uncertain readings

**19 September 2026 · Private review addendum · AI-assisted, not independently human verified**

The image review found worthwhile improvements. Sixteen items have a supported literal reading, twelve have a verified link to a clearer overlapping scan, and two can be partly read. Two other completions remain conjectural because paper is missing; eighteen items remain unresolved.

These are **register items, not unique words or discoveries**. Several refer to the same signature or overlapping acknowledgment. The fifty were deliberately selected to test different methods; their results cannot predict a recovery percentage for the other 1,150 items.

## Read and inspect

- [Printable review report](George-Douglas-50-Item-Image-Review.pdf): findings, method, and all fifty decisions.
- [Image evidence viewer](evidence.html): download this folder, then open the HTML file locally. Each item links to original crops and processing variants. GitHub displays HTML source rather than running the viewer.
- [Corrected pilot excerpts](corrected-excerpts.md): an explicitly labeled draft overlay for the selected paragraphs, with supported literal changes and separate witness notes. Other words in these paragraphs have not been newly certified.
- [Decision data](decisions.json), [patch overlay](corrections.json), [frozen sample](sample.json), and [image manifest](image-manifest.json).
- [OCR diagnostic results](ocr-diagnostic.json) and [raw OCR outputs](vision-results.json).

The v1.0 PDFs, Word files, text and packages remain intact for comparison. This addendum does not silently update one of those exports. The 1,200-row register still describes the earlier edition; **do not subtract 30 from it**. The next edition should apply the reviewed overlay to its structured source and regenerate every export together.

## What the images changed

- `04-079-U002`: **Brushy**, from the visible letters, replacing the tentative Burky reading.
- `04-080-U001`: **build**, supported by a second occurrence of build in the same hand on the same page.
- `04-043-U002` and `04-044-U003`: **Wm L** before Hancock, with comparable signatures on `05-151` and `05-157`.
- `05-024-U001`: **F** immediately before Hawkins, matching the F in Benj. F. Hawkins. The preceding word, currently transcribed By, may itself be an abbreviated Benj and needs whole-line review. The proposed B is not supported for the selected initial.
- `05-035-U001`: the later slip says **Sat**. A proposed change to Sep would overwrite its visible lettering. The companion letter’s date needs its own assessment.
- `06-008-U003`: the docket says **91** while the separate recording certificate on `06-011` says **92**. Record that disagreement rather than harmonizing it.
- `05-149-U001` and `U003`: **Guthrie** is readable, but the notary’s given name remains unread. Neither earlier full-name proposal is established.
- `06-063-U001`: **Claunch** is supported by the enlarged image and another letter’s wording. The reported murder remains a historical allegation by the writer, not a finding independently established here.

`04-002-U007` supports **Alfred** in “Uncle Alfred.” This does not establish Nathaniel Lynn Douglas’s parentage.

## How this review was done

The sample contains 29 tentative readings, nine unread spans, nine physical losses and three obstructions, across nineteen selected scan pages in four PDFs. Supporting scans were inspected where relevant. Its selection was saved before image adjudication in `sample.json` against repository snapshot `ae16c74`.

The other agent’s [contextual review](../uncertain-text-review-2026-09.md) was read first. This review is therefore **not blinded**. Its proposals were tested, not treated as evidence that the letters must say those words. The family and annotated editions are AI-assisted readings from this project, not independently verified human witnesses. The earlier review’s description of a “separate reader” must not be used to give their agreement extra evidentiary weight.

Four source PDFs were checked against their recorded SHA-256 hashes. Their embedded images were extracted at native pixel dimensions, converted to RGB, and rotated in exact 90-degree steps as needed. Forty-three regions are supplied as lossless PNG crops. Every region has its source filename, scan number in the page ID, source checksum, rotation, pixel rectangle, and derivative checksums in `image-manifest.json`.

Each crop has an original RGB version and a grayscale version with 1% autocontrast at each tail. Six difficult crops also have a documented gamma adjustment: exponent 0.45 to brighten shadows or 2.0 to darken faint gray strokes. Comparisons always retained the original. These operations can expose existing contrast; they cannot reconstruct absent paper or ink. No generative image restoration, invented strokes or image upscaling was used.

Duplicate scans were matched using repeated text, line breaks, signatures and physical layout. A match can supply a cited witness note. It does not make hidden writing visible in the damaged scan. Conjectural completions such as [C]rop and [se]ttlement remain explicitly separate from transcription.

## OCR test and limits

Apple Vision was run locally on nineteen crop regions, each in original and contrast form, with language correction off and on: **76 completed runs**. No custom vocabulary or proposed reading was provided to the recognizer; up to three candidate strings per detected line were retained. No scan was uploaded to an outside recognition service.

A diagnostic checked nine image-supported target readings in the top-ranked output: Of, Alfred, Denmark, Brushy, build, Sat, Chadsey’s, 91 and Claunch. In each of the four configurations, only **Sat** was recovered as an exact target. This small, deliberately difficult crop test is not a character-error rate, word-error rate, full-page benchmark, or comparison with a trained handwriting model. A failed target match does not mean every OCR character was wrong. The raw output is retained so the conclusion can be audited.

OCR supplied no additional accepted reading in this pilot. Rotating and enlarging the view, inspecting line breaks, comparing the same writer’s letter forms and checking overlapping images were more useful. Tonal adjustments made some marks easier to see but did not settle the darkest signatures or the five sampled gaps on `06-116`.

Transkribus, Kraken and a trained handwriting model were **not tested**. They remain a possible next experiment after preparing image-checked training/validation text from clear pages by the same writer. This pilot does not establish that all useful tools have been exhausted.

## Next work with the strongest rationale

1. Map the remaining overlaps and duplicate leaves. Apply the same witness-note method before spending time on physically hidden spans. Do not count a duplicated passage as multiple independent discoveries.
2. Build a small letter-form sheet for each recurring hand, using clear source examples. Recheck names, numbers and signatures against it; use contextual leads to direct attention, not to choose missing letters.
3. Audit whole lines around the densest uncertainty clusters. On `06-063` and `06-116`, some previously confident surrounding words also look questionable. Filling only the marked gaps could preserve a wrong sentence framework.
4. If a handwriting-specific recognizer is trialed, use a fixed held-out sample, keep its output blind to existing proposals, and compare its errors with image-checked human reference text. Never train on unchecked AI transcription.
5. Obtain independent human paleographic review of the supported changes and the hardest cases before presenting a new edition as a university reference contribution. A clearer photographic witness, if one exists, may help where the supplied photocopy has lost detail.

Method references previously consulted in this project: [Smithsonian historical handwriting guide](https://transcription.si.edu/sites/default/files/uploads/transcribing_historical_handwriting_in_the_smithsonian_transcription_center_1.pdf), [Transkribus data preparation](https://help.transkribus.org/data-preparation), [Kraken documentation](https://kraken.re/main/index.html), and [OCR-D workflows](https://ocr-d.de/en/workflows). These explain methods; they do not validate this pilot’s readings.

## Provenance and reuse

Source: George Douglas Papers, 1830–1939, Center for Restoration Studies MS 5, ACU Special Collections and Archives, Brown Library, Abilene Christian University. The source PDFs remain outside this repository. This private addendum includes attributed crops for verification and does not grant new rights over the scans. See [repository rights notice](../../RIGHTS.md). No ACU review, endorsement or correspondence is represented.

`reproduce_images.py` rebuilds the crops from the supplied PDFs and verifies source hashes. `vision_probe.swift` records the local OCR procedure. `build_review.py` rebuilds the readable outputs from the decision data. The retained decisions are an AI-assisted editorial record, not an assertion of independent human verification.
