#!/usr/bin/env python3
"""Apply the preview-only iPhone navigation and video-edge corrections.

Run this from the BitChord source root. A build must not start until the user
has reviewed the visual preview. Every replacement fails loudly if the source
has changed, rather than silently producing a partially patched application.
"""
from pathlib import Path

ROOT = Path.cwd()
UI = Path("AppleApp/Sources/UI")

def load(name):
    path = ROOT / UI / name
    return path, path.read_text(encoding="utf-8")

def put(path, content):
    path.write_text(content, encoding="utf-8")

def replace_one(content, old, new, description):
    n = content.count(old)
    if n != 1:
        raise RuntimeError(f"{description}: expected 1 match, found {n}")
    return content.replace(old, new, 1)

# 1. The system tab bar owns its vertical area again. The mini-player is
# inserted *inside each phone tab page*, so safe-area layout reserves real
# space above the bottom navigation controls rather than overlaying their text.
path, root = load("RootView.swift")
for tab, content in (
    ("Home", "HomeView(feed: homeFeed)"),
    ("Explore", "ExploreView()"),
    ("Library", "LibraryView()"),
    ("Search", "SearchView()"),
):
    symbol = {
        "Home": "house.fill",
        "Explore": "square.grid.2x2.fill",
        "Library": "square.stack.fill",
        "Search": "magnifyingglass",
    }[tab]
    role = ", role: .search" if tab == "Search" else ""
    old = f'''                Tab("{tab}", systemImage: "{symbol}", value: RootPage.tab(.{tab.lower()}){role}) {{\n                    {content}\n                }}'''
    new = f'''                Tab("{tab}", systemImage: "{symbol}", value: RootPage.tab(.{tab.lower()}){role}) {{\n                    {content}\n                        .modifier(iPhonePlaybackChrome())\n                }}'''
    root = replace_one(root, old, new, f"{tab} phone tab")

root = replace_one(
    root,
    "        .tabViewSidebarBottomBar { IPadSidebarFooter() }\n        .modifier(PlaybackPillMount())",
    "        .tabViewSidebarBottomBar { IPadSidebarFooter() }",
    "Remove tab-level floating accessory",
)
start = root.index("/// The shared playback pill (UI spec")
end = root.index("/// iPad per-tab pill mount.", start)
new_chrome = '''#if os(iOS)
/// iPhone: reserve height above the native tab bar rather than drawing a
/// floating accessory across the tab labels. The extra bottom gap ensures
/// Explore, Library and Search remain visible and tappable on smaller phones.
struct iPhonePlaybackChrome: ViewModifier {
    @Environment(\\.horizontalSizeClass) private var sizeClass

    @ViewBuilder
    func body(content: Content) -> some View {
        if sizeClass == .compact {
            content.safeAreaInset(edge: .bottom, spacing: 0) {
                PlaybackPill()
                    .frame(maxWidth: 720)
                    .padding(.horizontal, 12)
                    .padding(.top, 8)
                    .padding(.bottom, 18)
                    .frame(maxWidth: .infinity)
            }
        } else {
            content
        }
    }
}

'''
root = root[:start] + new_chrome + root[end:]
put(path, root)

# 2. Respect the status bar and Dynamic Island. Only the *backdrops*
# ignore the screen safe area. The interactive player layout must not.
path, layout = load("NowPlaying/NowPlayingView+Layouts.swift")
layout = replace_one(
    layout,
    "                    .animation(isIPad ? .easeInOut(duration: 0.22) : nil, value: pane)",
    "                    .animation(.smooth(duration: 0.32), value: pane)",
    "Smooth player-pane changes",
)
layout = replace_one(
    layout,
    """            // Keep the established edge-to-edge phone artwork. The iPad page
            // respects its system top inset so the player has room for chrome.
            .ignoresSafeArea(.container, edges: isIPad ? [] : .top)""",
    "            // Backgrounds remain full bleed; controls respect Dynamic Island.",
    "Respect top safe area",
)
put(path, layout)

# 3. More gradual hero-to-blurred-backdrop dissolve; remove the
# continuation's hard texture boundary and stale artwork on song changes.
path, art = load("NowPlaying/PlayerArtwork.swift")
art = replace_one(
    art, "private let fadeFraction: CGFloat = 0.42",
    "private let fadeFraction: CGFloat = 0.58",
    "Expand artwork blend region",
)
art = replace_one(
    art,
    """                        .init(color: .white, location: 0),
                        .init(color: .white, location: 1 - fadeFraction),
                        .init(color: .clear, location: 1),""",
    """                        .init(color: .white, location: 0),
                        .init(color: .white, location: 1 - fadeFraction),
                        .init(color: .white.opacity(0.82), location: 0.58),
                        .init(color: .white.opacity(0.42), location: 0.75),
                        .init(color: .white.opacity(0.12), location: 0.91),
                        .init(color: .clear, location: 1),""",
    "Smooth hero-mask steps",
)
art = replace_one(
    art,
    """                VStack(spacing: 0) {
                    Image(decorative: edge, scale: 1).resizable()
                        .frame(height: min(seam, geo.size.height))
                    Image(decorative: texture, scale: 1).resizable()
                        .frame(height: max(0, geo.size.height - seam))
                }
                .frame(width: geo.size.width)""",
    """                let headerHeight = min(seam, geo.size.height)
                let fadeHeight = min(96, max(0, geo.size.height - headerHeight))
                let totalHeight = headerHeight + fadeHeight
                ZStack(alignment: .top) {
                    Image(decorative: texture, scale: 1)
                        .resizable()
                        .frame(width: geo.size.width, height: geo.size.height)
                    Image(decorative: edge, scale: 1)
                        .resizable()
                        .frame(width: geo.size.width, height: totalHeight)
                        .mask {
                            LinearGradient(
                                stops: [
                                    .init(color: .white, location: 0),
                                    .init(color: .white, location: totalHeight > 0 ? headerHeight / totalHeight : 1),
                                    .init(color: .clear, location: 1),
                                ],
                                startPoint: .top,
                                endPoint: .bottom
                            )
                        }
                }
                .frame(width: geo.size.width, height: geo.size.height)
                .clipped()""",
    "Avoid abrupt artwork/texture seam",
)
art = replace_one(
    art,
    '''        .task(id: entry?.thumbnailUrl ?? entry?.id) {
            guard let entry else { return }''',
    '''        .task(id: "\\(entry?.id ?? "")|\\(entry?.thumbnailUrl ?? "")") {
            texture = nil
            guard let entry else { return }'''.replace("\\\\(", "\\("),
    "Drop stale artwork texture on track changes",
)
put(path, art)

# 4. AVPlayerLayer is backed by Core Animation. SwiftUI's outer .mask may
# not reliably fade live video pixels, so give the underlying player layer
# an explicit native alpha gradient on the full-bleed player surface.
path, video = load("VideoSurface.swift")
video = replace_one(
    video,
    """        case .fill:
            VideoLayerView(player: player, gravity: .resizeAspectFill)
                .allowsHitTesting(false)
                .transition(.opacity)""",
    """        case .fill:
            #if os(iOS)
            VideoLayerView(player: player, gravity: .resizeAspectFill, softBottomEdge: true)
                .allowsHitTesting(false)
                .transition(.opacity)
            #else
            VideoLayerView(player: player, gravity: .resizeAspectFill)
                .allowsHitTesting(false)
                .transition(.opacity)
            #endif""",
    "Fade full-bleed native video",
)
video = replace_one(
    video,
    """        .animation(.easeInOut(duration: 0.25), value: VideoPlayback.shared.showsVideo)
        .animation(.easeInOut(duration: 0.25), value: VideoPlayback.shared.isLoading)""",
    """        .animation(.smooth(duration: 0.35), value: VideoPlayback.shared.showsVideo)
        .animation(.smooth(duration: 0.32), value: VideoPlayback.shared.isLoading)""",
    "Smooth video surface transitions",
)
video = replace_one(
    video,
    """struct VideoLayerView: UIViewRepresentable {
    let player: AVPlayer
    var gravity: AVLayerVideoGravity = .resizeAspect""",
    """struct VideoLayerView: UIViewRepresentable {
    let player: AVPlayer
    var gravity: AVLayerVideoGravity = .resizeAspect
    var softBottomEdge = false""",
    "Expose iPhone video edge fade",
)
video = replace_one(
    video,
    """        view.player = player
        view.gravity = gravity
        VideoPlayback.shared.registerPictureInPictureLayer(view.playerLayer)
        return view""",
    """        view.player = player
        view.gravity = gravity
        view.softBottomEdge = softBottomEdge
        VideoPlayback.shared.registerPictureInPictureLayer(view.playerLayer)
        return view""",
    "Set video fade at UIView creation",
)
video = replace_one(
    video,
    """    func updateUIView(_ view: VideoLayerHost, context: Context) {
        view.player = player
        view.gravity = gravity
        VideoPlayback.shared.registerPictureInPictureLayer(view.playerLayer)
    }""",
    """    func updateUIView(_ view: VideoLayerHost, context: Context) {
        view.player = player
        view.gravity = gravity
        view.softBottomEdge = softBottomEdge
        VideoPlayback.shared.registerPictureInPictureLayer(view.playerLayer)
    }""",
    "Update video fade for UIView",
)
old_host_start = video.index("final class VideoLayerHost: UIView {")
old_host_end = video.index("\n#else\nstruct VideoLayerView: NSViewRepresentable {", old_host_start)
new_host = '''final class VideoLayerHost: UIView {
    override class var layerClass: AnyClass { AVPlayerLayer.self }
    var playerLayer: AVPlayerLayer { layer as! AVPlayerLayer }

    // Native alpha mask: video frames often bypass the mask drawn around
    // a SwiftUI UIViewRepresentable, leaving a sharp rectangular cutoff.
    private lazy var bottomFadeMask: CAGradientLayer = {
        let gradient = CAGradientLayer()
        gradient.startPoint = CGPoint(x: 0.5, y: 0)
        gradient.endPoint = CGPoint(x: 0.5, y: 1)
        gradient.colors = [
            UIColor.white.cgColor,
            UIColor.white.cgColor,
            UIColor.white.withAlphaComponent(0.82).cgColor,
            UIColor.white.withAlphaComponent(0.38).cgColor,
            UIColor.clear.cgColor
        ]
        gradient.locations = [
            NSNumber(value: 0.0), NSNumber(value: 0.48),
            NSNumber(value: 0.64), NSNumber(value: 0.82),
            NSNumber(value: 1.0)
        ]
        return gradient
    }()

    var softBottomEdge = false {
        didSet { updateBottomFade() }
    }

    override func layoutSubviews() {
        super.layoutSubviews()
        updateBottomFade()
    }

    private func updateBottomFade() {
        guard softBottomEdge else {
            if playerLayer.mask === bottomFadeMask { playerLayer.mask = nil }
            return
        }
        CATransaction.begin()
        CATransaction.setDisableActions(true)
        bottomFadeMask.frame = playerLayer.bounds
        if playerLayer.mask !== bottomFadeMask {
            playerLayer.mask = bottomFadeMask
        }
        CATransaction.commit()
    }

    var player: AVPlayer? {
        get { playerLayer.player }
        set { playerLayer.player = newValue }
    }
    var gravity: AVLayerVideoGravity {
        get { playerLayer.videoGravity }
        set { playerLayer.videoGravity = newValue }
    }
}'''
video = video[:old_host_start] + new_host + video[old_host_end:]
put(path, video)

print("Applied staged iOS UI v2 changes (RootView, PlayerArtwork, NowPlaying layouts, VideoSurface).")
