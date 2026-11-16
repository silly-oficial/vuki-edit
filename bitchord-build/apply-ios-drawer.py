#!/usr/bin/env python3
"""Install the production SwiftUI track drawer into a freshly cloned BitChord.

The staging repository only holds this application-specific patch script; the
modified Swift sources are written to the BitChord clone before Xcodegen runs.
"""
from pathlib import Path

root = Path.cwd() / "AppleApp" / "Sources" / "UI"
staged = Path(__file__).resolve().parent / "swift" / "PlayerSideDrawer.swift"
assert staged.is_file(), "Missing actual drawer source file"

def replace_once(path, before, after):
    file = root / path
    original = file.read_text(encoding="utf-8")
    count = original.count(before)
    if count != 1:
        raise RuntimeError(f"{path}: expected one source anchor, got {count}")
    file.write_text(original.replace(before, after, 1), encoding="utf-8")

replace_once(
    "NowPlaying/NowPlayingView.swift",
    "    @State var showLyricsOffset = false",
    """    @State var showLyricsOffset = false
    #if os(iOS)
    @State var songDrawerPresented = false
    #endif""",
)
replace_once(
    "NowPlaying/NowPlayingView+Transport.swift",
    """    var moreMenu: some View {
        Menu {""",
    """    var moreMenu: some View {
        #if os(iOS)
        Button {
            withAnimation(.easeInOut(duration: 0.30)) {
                songDrawerPresented = true
            }
        } label: {
            Image(systemName: "ellipsis")
                .scaledFont(size: 15, weight: .semibold)
                .foregroundStyle(.white)
                .frame(width: 34, height: 34)
                .background(.white.opacity(0.18), in: Circle())
                .contentShape(Circle())
        }
        .buttonStyle(.plain)
        .help("More")
        .accessibilityLabel("Track actions")
        #else
        Menu {""",
)
replace_once(
    "NowPlaying/NowPlayingView+Transport.swift",
    """        .buttonStyle(.plain)
        .help("More")
    }

    static func timestamp""",
    """        .buttonStyle(.plain)
        .help("More")
        #endif
    }

    static func timestamp""",
)
replace_once(
    "NowPlaying/NowPlayingView+Layouts.swift",
    """            .toolbar(.hidden, for: .navigationBar)
            .toolbarTitleDisplayMode(.inline)""",
    """            // Keep Now Playing mounted and animating beneath the action drawer.
            // Inset/size is inherited from the player viewport, not the tab bar.
            .overlay {
                PlayerSideDrawer(
                    isPresented: $songDrawerPresented,
                    onLyricsOffset: { showLyricsOffset = true }
                )
            }
            .toolbar(.hidden, for: .navigationBar)
            .toolbarTitleDisplayMode(.inline)""",
)
destination = root / "NowPlaying" / "PlayerSideDrawer.swift"
if destination.exists():
    raise RuntimeError(f"Unexpected existing source: {destination}")
destination.write_text(staged.read_text(encoding="utf-8"), encoding="utf-8")
print("Installed production side drawer in 4 Swift files.")
