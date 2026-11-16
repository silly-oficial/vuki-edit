#!/usr/bin/env python3
"""Repair visible iOS issues after earlier staged patches; fail on upstream drift."""
from pathlib import Path
root=Path("AppleApp/Sources/UI")
def replace(file,old,new):
 p=root/file;s=p.read_text(encoding="utf-8")
 if s.count(old)!=1: raise RuntimeError(f"{file}: expected exactly one anchor, got {s.count(old)}")
 p.write_text(s.replace(old,new,1),encoding="utf-8")

# iOS 26 scroll-edge transparency ignores the SwiftUI toolbar material in some contexts.
# Configure UIKit before the first TabView is constructed, including the scroll-edge state.
replace("RootView.swift", "    var body: some View {\n        shell",
'''    init() {
        #if os(iOS)
        let appearance = UITabBarAppearance()
        appearance.configureWithOpaqueBackground()
        appearance.backgroundEffect = nil
        appearance.backgroundColor = UIColor.systemBackground
        appearance.shadowColor = UIColor.separator.withAlphaComponent(0.35)
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
        UITabBar.appearance().isTranslucent = false
        #endif
    }

    var body: some View {
        shell''')
# Remove the generated 32px artwork continuation that creates conspicuous horizontal bands.
# The existing MeshBackdrop remains, and the hero itself still fades into that backdrop.
replace("NowPlaying/NowPlayingView+Layouts.swift",
'''                    if !isIPad && pane == .main && !PlayerLayout.takesLandscapeShape(width: geo.size.width, height: geo.size.height) && fullBleedOn && !videoShowing {
                        ArtworkContinuation(entry: controller.current, seam: geo.size.width)
                            .ignoresSafeArea()
                    }
''',
'''                    // Do not stretch a 32-pixel artwork texture across the screen.
                    // The continuous MeshBackdrop already fills the area behind the cover.
''')
# Avoid duplicated legacy App Language selector and keep the new accessible native picker.
replace("Settings/SettingsView.swift",
'["Hide Volume Bar", "Hide Song Status", "Hide Status Bar in Player", "App Language"]',
'["Hide Volume Bar", "Hide Song Status", "Hide Status Bar in Player"]')
# Long translations must wrap rather than clip behind a trailing chevron or badge.
p=root/"Settings/SettingsRows.swift"
s=p.read_text(encoding="utf-8")
old='''                    Text(LocalizedStringKey(title))
                    if let badge {'''
new='''                    Text(LocalizedStringKey(title))
                        .fixedSize(horizontal: false, vertical: true)
                        .layoutPriority(1)
                    if let badge {'''
if old not in s: raise RuntimeError("SettingsLine wrapping anchor missing")
p.write_text(s.replace(old,new,1),encoding="utf-8")
# The drawer should use the same wrapping for every existing named action, never create labels for icons.
p=root/"NowPlaying/PlayerSideDrawer.swift"
s=p.read_text(encoding="utf-8")
s=s.replace('Text(LocalizedStringKey(title))','Text(LocalizedStringKey(title)).fixedSize(horizontal: false, vertical: true)')
p.write_text(s,encoding="utf-8")
print("Applied opaque UIKit tab bar, removed banded artwork continuation, improved label wrapping")
