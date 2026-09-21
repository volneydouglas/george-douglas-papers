import Foundation
import Vision
import ImageIO
let args=CommandLine.arguments
let paths=try String(contentsOfFile:args[1],encoding:.utf8).split(separator:"\n").map(String.init)
let output=URL(fileURLWithPath:args[2],isDirectory:true)
try FileManager.default.createDirectory(at:output,withIntermediateDirectories:true)
let orientations:[(CGImagePropertyOrientation,Int)]=[(.up,0),(.right,90),(.down,180),(.left,270)]
func recognize(_ path:String,_ orientation:CGImagePropertyOrientation,_ degrees:Int,_ correction:Bool)->[String:Any]{
 let req=VNRecognizeTextRequest();req.recognitionLevel = .accurate;req.recognitionLanguages=["en-US"];req.usesLanguageCorrection=correction
 var record:[String:Any] = ["file":URL(fileURLWithPath:path).lastPathComponent,"clockwise_rotation":degrees,"usesLanguageCorrection":correction,"revision":req.revision]
 do {
  try VNImageRequestHandler(url:URL(fileURLWithPath:path),orientation:orientation,options:[:]).perform([req])
  record["lines"]=(req.results ?? []).map{obs -> [String:Any] in ["box":[obs.boundingBox.minX,obs.boundingBox.minY,obs.boundingBox.width,obs.boundingBox.height],"candidates":obs.topCandidates(3).map{["text":$0.string,"confidence":$0.confidence] as [String:Any]}]}
  record["orientation_score"]=(req.results ?? []).reduce(0.0){sum,obs in guard let top=obs.topCandidates(1).first else{return sum};return sum+Double(top.confidence)*Double(top.string.filter{$0.isLetter}.count)}
 }catch{record["error"]=String(describing:error);record["orientation_score"]=0.0}
 return record
}
for path in paths{
 autoreleasepool{
  let key=String(URL(fileURLWithPath:path).lastPathComponent.prefix(6));let dest=output.appendingPathComponent(key+".json")
  if FileManager.default.fileExists(atPath:dest.path){return}
  var records=orientations.map{recognize(path,$0.0,$0.1,false)}
  let best=records.indices.max{(records[$0]["orientation_score"] as! Double)<(records[$1]["orientation_score"] as! Double)}!
  let o=orientations[best]
  records.append(recognize(path,o.0,o.1,true))
  let contrast=path.replacingOccurrences(of:"-original.png",with:"-contrast.png")
  records.append(recognize(contrast,o.0,o.1,false));records.append(recognize(contrast,o.0,o.1,true))
  let result:[String:Any] = ["page_id":key,"engine":"Apple Vision","os":ProcessInfo.processInfo.operatingSystemVersionString,"best_clockwise_rotation":o.1,"records":records]
  do{try JSONSerialization.data(withJSONObject:result,options:[.prettyPrinted,.sortedKeys]).write(to:dest)}catch{print(error)}
  print("Completed \(key): 7 runs, orientation \(o.1)");fflush(stdout)
 }
}
