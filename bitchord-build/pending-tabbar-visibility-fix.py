#!/usr/bin/env python3
"""Pending iPhone tab-bar visibility fix. Do NOT add to workflow until user requests IPA.
Run after apply-ios-layout-v2.py. Keep the mini player above native tabs.
"""
from pathlib import Path

path = Path.cwd() / "AppleApp/Sources/UI/RootView.swift"
source = path.read_text(encoding="utf-8")
old = """        .tabViewStyle(.sidebarAdaptable)
        .tabViewCustomization($tabCustomization)"""
new = """        .tabViewStyle(.sidebarAdaptable)
        // Search and scrolling pages may ask UIKit to make the tab bar
        // transparent. Keep the native system bar's background visible,
        // independently of the playback pill's safe-area inset.
        .toolbarBackground(.visible, for: .tabBar)
        .toolbarBackground(.regularMaterial, for: .tabBar)
        .tabViewCustomization($tabCustomization)"""
if source.count(old) != 1:
    raise RuntimeError(f"Tab bar background: expected one match, found {source.count(old)}")
path.write_text(source.replace(old, new, 1), encoding="utf-8")
print("Persistent native iPhone tab-bar material configured")
