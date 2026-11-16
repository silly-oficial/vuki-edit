#!/usr/bin/env python3
"""Pending video chrome polish; intentionally NOT wired into the IPA workflow.
Apply after apply-ios-layout-v2.py, alongside pending-video-overlay-fix.py.
"""
from pathlib import Path

root = Path.cwd()
def replace_once(path, old, new, label):
    source = path.read_text(encoding="utf-8")
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected 1 occurrence, found {count}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")

stage = root / "AppleApp/Sources/UI/NowPlaying/NowPlayingView+Stage.swift"
replace_once(stage, """            .overlay(alignment: .top) {
                if let caption = playbackOriginCaption {
                    Text(caption)
                        .font(.subheadline.weight(.semibold))
                        .foregroundStyle(.white.opacity(0.92))
                        .shadow(color: .black.opacity(0.55), radius: 5, y: 1)
                        .padding(.top, 22)
                }
            }
            .accessibilityLabel(controller.current?.title ?? "Nothing playing")""",
"""            .accessibilityLabel(controller.current?.title ?? "Nothing playing")""",
"Remove redundant Playing from YouTube hero caption")

video = root / "AppleApp/Sources/UI/VideoSurface.swift"
replace_once(video, """                        .buttonStyle(.bordered)
                        .controlSize(.small)
                        .padding(10)""",
"""                        .font(.system(size: 15, weight: .semibold))
                        .foregroundStyle(.white)
                        .buttonStyle(.plain)
                        .labelStyle(.iconOnly)
                        .frame(minHeight: 44)
                        .padding(.horizontal, 6)
                        .background(.ultraThinMaterial, in: Capsule())
                        .overlay {
                            Capsule().strokeBorder(.white.opacity(0.14), lineWidth: 0.5)
                        }
                        .padding(12)""",
"Use unified native glass video toolbar")
replace_once(video, """                                Image(systemName: "arrow.up.left.and.arrow.down.right")
                                    .accessibilityLabel("Open video theater")""",
"""                                Image(systemName: "arrow.up.left.and.arrow.down.right")
                                    .frame(width: 42, height: 44)
                                    .contentShape(Rectangle())
                                    .accessibilityLabel("Open video theater")""",
"Give theater control a 44-point hit target")
replace_once(video, """                                    Image(systemName: "pip.enter")
                                        .accessibilityLabel("Start Picture in Picture")""",
"""                                    Image(systemName: "pip.enter")
                                        .frame(width: 42, height: 44)
                                        .contentShape(Rectangle())
                                        .accessibilityLabel("Start Picture in Picture")""",
"Give PiP control a 44-point hit target")
print("Pending video caption and toolbar changes applied")
