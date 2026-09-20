import Foundation
import Vision
import ImageIO

// Local diagnostic only: no uploads, no dictionaries or supplied candidate words.
let args = CommandLine.arguments
let input = URL(fileURLWithPath: args[1])
let output = URL(fileURLWithPath: args[2])
let paths = try String(contentsOf: input, encoding: .utf8).split(separator: "\n").map(String.init)
var records: [[String: Any]] = []
for path in paths {
    for correction in [false, true] {
        let req = VNRecognizeTextRequest()
        req.recognitionLevel = .accurate
        req.recognitionLanguages = ["en-US"]
        req.usesLanguageCorrection = correction
        var record: [String: Any] = ["file": URL(fileURLWithPath: path).lastPathComponent,
                                   "usesLanguageCorrection": correction,
                                   "revision": req.revision]
        do {
            try VNImageRequestHandler(url: URL(fileURLWithPath: path), options: [:]).perform([req])
            record["lines"] = (req.results ?? []).map { obs -> [String: Any] in
                ["box": [obs.boundingBox.minX, obs.boundingBox.minY, obs.boundingBox.width, obs.boundingBox.height],
                 "candidates": obs.topCandidates(3).map { ["text": $0.string, "confidence": $0.confidence] as [String: Any] }]
            }
        } catch {
            record["error"] = String(describing: error)
        }
        records.append(record)
    }
}
let result: [String: Any] = ["engine": "Apple Vision VNRecognizeTextRequest", "os": ProcessInfo.processInfo.operatingSystemVersionString, "records": records]
try JSONSerialization.data(withJSONObject: result, options: [.prettyPrinted, .sortedKeys]).write(to: output)
print("Wrote \(records.count) OCR diagnostic runs")
