#!/usr/bin/env python3
"""Pending video unavailable/loading notice visibility fix.
Apply after apply-ios-layout-v2.py. Not included in IPA workflow yet.
"""
from pathlib import Path

path = Path.cwd() / "AppleApp/Sources/UI/VideoSurface.swift"
source = path.read_text(encoding="utf-8")
old = '''    private func caption(_ text: String, loading: Bool) -> some View {
        VStack {
            Spacer()
            HStack(spacing: 6) {
                if loading {
                    ProgressView().controlSize(.small)
                } else {
                    Image(systemName: "video.slash")
                        .font(.caption)
                }
                Text(text)
                    .font(.caption.weight(.medium))
            }
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(.ultraThinMaterial, in: Capsule())
            .padding(10)
        }
        .allowsHitTesting(false)
        .transition(.opacity)
    }'''
new = '''    private func caption(_ text: String, loading: Bool) -> some View {
        VStack {
            // Keep notices clear of the artwork's bottom fade, and below
            // the status-bar chrome in the full-bleed hero.
            HStack(spacing: 9) {
                if loading {
                    ProgressView()
                        .tint(.white)
                        .controlSize(.small)
                } else {
                    Image(systemName: "video.slash")
                        .font(.system(size: 14, weight: .semibold))
                }
                Text(text)
                    .font(.system(size: 13, weight: .semibold))
                    .lineLimit(2)
                    .fixedSize(horizontal: false, vertical: true)
            }
            .foregroundStyle(.white)
            .padding(.horizontal, 14)
            .padding(.vertical, 11)
            .background(.black.opacity(0.78), in: RoundedRectangle(cornerRadius: 14, style: .continuous))
            .overlay {
                RoundedRectangle(cornerRadius: 14, style: .continuous)
                    .strokeBorder(.white.opacity(0.18), lineWidth: 0.5)
            }
            .shadow(color: .black.opacity(0.45), radius: 12, y: 5)
            .padding(.horizontal, 20)
            .padding(.top, presentation == .fill ? 70 : 18)
            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        .allowsHitTesting(false)
        .transition(.opacity)
        .zIndex(10)
    }'''
if source.count(old) != 1:
    raise RuntimeError(f"Video notice: expected one source block, found {source.count(old)}")
path.write_text(source.replace(old,new,1),encoding="utf-8")
print("Video notices now use high contrast and appear near top of player")
