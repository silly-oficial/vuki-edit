#!/usr/bin/env python3
"""Pending iPhone video/cover compositing fix. Apply after apply-ios-layout-v2.py.

Intentionally not included in the build workflow yet: user requested that
this change be saved together with another forthcoming fix before building.
"""
from pathlib import Path

root = Path.cwd()
path = root / "AppleApp/Sources/UI/NowPlaying/PlayerArtwork.swift"
source = path.read_text(encoding="utf-8")

def once(old, new):
    global source
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"Video/cover fix: expected one match, found {count}")
    source = source.replace(old, new, 1)

# Hero artwork and CanvasPlayer currently remain mounted behind the live
# AVPlayerLayer. Its native Core Animation fade reveals the cover underneath,
# resulting in two different pictures superimposed in video mode.
# Only show the still/canvas fallback while a playable video is NOT ready.
once(
    """                ArtworkView(entry: entry, side: max(geo.size.width, geo.size.height))
                    .frame(width: geo.size.width, height: geo.size.height)
                    .clipped()
                    .allowsHitTesting(false)
                if let canvasURL {
                    CanvasPlayer(url: canvasURL, fallbackURL: fallbackURL, isPlaying: isPlaying && canvasActive)
                        .frame(width: geo.size.width, height: geo.size.height)
                        .allowsHitTesting(false)
                }
                // The picture takes the artwork's place edge to edge""",
    """                if !VideoPlayback.shared.showsVideo {
                    ArtworkView(entry: entry, side: max(geo.size.width, geo.size.height))
                        .frame(width: geo.size.width, height: geo.size.height)
                        .clipped()
                        .allowsHitTesting(false)
                    if let canvasURL {
                        CanvasPlayer(url: canvasURL, fallbackURL: fallbackURL, isPlaying: isPlaying && canvasActive)
                            .frame(width: geo.size.width, height: geo.size.height)
                            .allowsHitTesting(false)
                    }
                }
                // The picture takes the artwork's place edge to edge""",
)
path.write_text(source, encoding="utf-8")
print("Pending video/cover compositing fix applied")
