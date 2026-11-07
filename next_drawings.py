"""Writes next/drawings.js, the colouring pages on /next, from the app's own drawings.

    python3 next_drawings.py [path to the app repo, default ../gentleskin]

Compiles ColouringDrawings.swift and StarGeometry.swift from the app with a small
exporter (macOS, Xcode's swiftc) and writes each region as SVG path data in the
app's 200x200 space: r = outlines, bottom to top; c = the part of each region
nothing sits over (the app's PaintRender.clip, so a stroke's clip matches the
app's); d = loose lines. Rerun when the app's drawings change.
"""
import json, os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
APP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "gentleskin"))
SRC = os.path.join(APP, "Gentleskin")
ORDER = ["starfish", "sea", "shell", "plant", "flower"]

EXPORTER = r'''
import SwiftUI
func f(_ v: CGFloat) -> String { let r = (v*10).rounded()/10; return r == r.rounded() ? String(Int(r)) : String(format: "%.1f", r).replacingOccurrences(of: "0+$", with: "", options: .regularExpression) }
func svg(_ p: Path) -> String {
  var o: [String] = []
  p.forEach { e in
    switch e {
    case .move(let a): o.append("M\(f(a.x)) \(f(a.y))")
    case .line(let a): o.append("L\(f(a.x)) \(f(a.y))")
    case .quadCurve(let a, let c): o.append("Q\(f(c.x)) \(f(c.y)) \(f(a.x)) \(f(a.y))")
    case .curve(let a, let c1, let c2): o.append("C\(f(c1.x)) \(f(c1.y)) \(f(c2.x)) \(f(c2.y)) \(f(a.x)) \(f(a.y))")
    case .closeSubpath: o.append("Z")
    }
  }
  return o.joined()
}
func clips(_ regions: [Path]) -> [Path] {
  var above = Path(); var out = Array(repeating: Path(), count: regions.count)
  for i in regions.indices.reversed() {
    out[i] = above.isEmpty ? regions[i] : regions[i].subtracting(above)
    above = above.isEmpty ? regions[i] : above.union(regions[i])
  }
  return out
}
var json: [String: Any] = [:]
for d in ColouringDrawing.all {
  json[d.id] = ["r": d.regions.map(svg), "c": clips(d.regions).map(svg), "d": d.details.map(svg)]
}
let data = try! JSONSerialization.data(withJSONObject: json, options: [.sortedKeys])
FileHandle.standardOutput.write(data)
'''


def main():
    with tempfile.TemporaryDirectory() as tmp:
        drawings = open(os.path.join(SRC, "Views", "Activities", "ColouringDrawings.swift")).read()
        # the localized names need the app's strings; the site has its own
        drawings = re.sub(r"    var name: String \{.*?\n    \}\n\n", "", drawings, flags=re.S)
        files = {"star.swift": open(os.path.join(SRC, "StarGeometry.swift")).read(), "drawings.swift": drawings, "main.swift": EXPORTER}
        for name, text in files.items():
            open(os.path.join(tmp, name), "w").write(text)
        exe = os.path.join(tmp, "export")
        subprocess.run(["swiftc", "-O", "-o", exe] + [os.path.join(tmp, n) for n in files], check=True)
        data = json.loads(subprocess.run([exe], check=True, capture_output=True).stdout)
    out = ("/* The app's colouring pages (ColouringDrawings.swift), exported as SVG paths in a 200x200 space by next_drawings.py.\n"
           "   r: each region's outline, bottom to top; c: the part of it nothing sits over (a stroke's clip); d: loose lines.\n"
           "   Regenerate from the app, never edit by hand. */\nwindow.GS_DRAWINGS = [\n")
    out += ",\n".join(json.dumps(dict(id=k, **data[k]), separators=(",", ":")) for k in ORDER) + "\n];\n"
    open(os.path.join(ROOT, "next", "drawings.js"), "w").write(out)


if __name__ == "__main__":
    main()
