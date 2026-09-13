import AppKit
import LinkPresentation

let url = URL(string: CommandLine.arguments[1])!
let out = CommandLine.arguments[2]
let app = NSApplication.shared
app.setActivationPolicy(.prohibited)
let provider = LPMetadataProvider()
provider.timeout = 30
var done = false
provider.startFetchingMetadata(for: url) { meta, err in
    if let err = err { print("ERROR: \(err)"); done = true; return }
    guard let meta = meta else { print("ERROR: no metadata"); done = true; return }
    print("title=\(meta.title ?? "<nil>")")
    print("url=\(meta.url?.absoluteString ?? "<nil>") original=\(meta.originalURL?.absoluteString ?? "")")
    print("hasImage=\(meta.imageProvider != nil) hasIcon=\(meta.iconProvider != nil)")
    DispatchQueue.main.async {
        let view = LPLinkView(metadata: meta)
        let w: CGFloat = 420
        view.frame = NSRect(x: 0, y: 0, width: w, height: 10)
        let fit = view.fittingSize
        view.frame = NSRect(x: 0, y: 0, width: w, height: max(fit.height, 60))
        view.layoutSubtreeIfNeeded()
        // let the image load
        DispatchQueue.main.asyncAfter(deadline: .now() + 3.0) {
            let fit2 = view.fittingSize
            view.frame = NSRect(x: 0, y: 0, width: w, height: max(fit2.height, 60))
            view.layoutSubtreeIfNeeded()
            let rep = view.bitmapImageRepForCachingDisplay(in: view.bounds)!
            view.cacheDisplay(in: view.bounds, to: rep)
            let png = rep.representation(using: .png, properties: [:])!
            try! png.write(to: URL(fileURLWithPath: out))
            print("rendered \(Int(view.bounds.width))x\(Int(view.bounds.height)) -> \(out)")
            done = true
        }
    }
}
while !done { RunLoop.main.run(mode: .default, before: Date(timeIntervalSinceNow: 0.1)) }
