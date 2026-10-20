# Vuki — light glass editor

Scope: native phone editor and the existing web interface preview. The supplied Apple-style reference takes precedence over the Skyglass palette and typography. No engine, project format, export pipeline, or tool callback was replaced.

| Decision | Source | Classification | Purpose |
| --- | --- | --- | --- |
| Cool neutral atmosphere, restrained blue | User reference; Skyglass §§1–2 | Adaptation | Separate the preview from controls |
| System font on web; bundled Hanken on native | User Apple direction; §3 fallback | Adaptation | Work offline without remote fonts |
| 26px cards, 32px sheets, pill actions | Reference; §§5,7 | Adaptation | Consistent progressive corners |
| Single blur per web surface, solid fallback | §§2,11,13 | Derived | Keep labels legible without backdrop-filter |
| Native translucent colour fallback | Existing Slint renderer | Adaptation | Avoid unsupported live backdrop-blur properties |
| Native transport in two rows | §13 | Derived | Fit 44px controls without overlap |
| Light/Sky for new phone installs | User reference | Adaptation | Open in the requested appearance; saved settings win |

The web page is a labelled, local interactive preview. It can import one photo/video and one audio file, preview text/shapes/filters, adjust frame/speed/volume and undo/redo visual settings. It does not export a rendered video or replace the native multitrack engine. The native editor retains real application callbacks and all existing tools.

## Initial verification (v5)

- PASS: JavaScript syntax (`node --check web-preview/app.js`).
- PASS: DOM interaction checks with jsdom: five panels, selection state, dismissal, focus return, play state, keyboard clip opening.
- PASS: whitespace/diff checks (`git diff --check`).
- PASS: complete `app.slint` import tree compiles with the Python Slint 1.18.1b1 interpreter. This is UI compilation, not a build of the Rust application with its pinned toolchain.
- NOT VERIFIED: complete native build/APK, device editing/export, visual screenshots, responsive browser layout, 200% zoom, composed contrast and screen reader checks. This environment has no Rust toolchain or browser binary; the Chromium download returned invalid archives.
- N/A: account, database and payment checks; these systems are outside this visual change.

Before shipping an APK, run the repository's mobile build and inspect a 320px phone, a typical iPhone/Android size, landscape, both saved themes, real footage, all panel dismissals and export. Native materials do not provide live background blur; the web preview does.

## Revision v6 — unobstructed preview and distinct tools

- Removed the Canvas / Adjust / Fullscreen strip below the image.
- Replaced the generic selectable tile grid with independent Media, Text, Audio, Shapes and Effects renderers. Each has controls relevant to its category; edits update the stage directly.
- Panels now replace the timeline in normal flow. The preview, playback controls and category bar remain available. Escape/Done restores focus; categories can be switched without closing the panel. These are nonmodal regions, without a backdrop or focus trap.
- Native PhoneSheet is limited to the lanes region, keeping the monitor, transport and tool bar outside its bounds. Existing tool callbacks are retained.
- A single input frame can be 4:3, 16:9 or square; container sizing preserves its ratio in the available preview area.
- Import uses local object URLs, with replacement cleanup and page-cache-aware release. Text uses textContent. Unsupported media displays an error. Export is visibly unavailable in this web demonstration.

Verification for v6:

- PASS: real Chromium layout/panel checks at 320×700, 390×844, 430×932, 540×844, 768×1024, 1280×900, 390×650 and 844×390. No horizontal document overflow; open panels do not overlap the preview. Inspected the 390px screenshots with the text panel open/closed.
- PASS: DOM tests for separate categories, live text/shape/filter changes, literal text safety, undo/redo, Escape, focus return and media routing.
- PASS: real browser import/play/pause of a generated WebM; WAV import and simultaneous playback; original volume/mute; playback speed.
- PASS: JavaScript syntax and git diff checks; complete app.slint compilation with Python Slint 1.18.1b1 after the native sheet change.
- NOT VERIFIED: Safari/iPhone device behavior, final APK/Rust build and native export. Visual inspection is of the web preview, not a native application screenshot. Exact contrast measurement, 200% zoom and screen reader review remain unverified.

The Chromium download limitation in the initial checks was resolved for v6 with an npm-packaged local browser binary. No browser or test dependency is added to the app.
