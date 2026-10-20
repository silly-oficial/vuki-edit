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

The web page remains a labelled interface demonstration. Its tool tiles demonstrate selection, not video processing. The native editor retains the real application callbacks and all existing tools.

## Verification

- PASS: JavaScript syntax (`node --check web-preview/app.js`).
- PASS: DOM interaction checks with jsdom: five panels, selection state, dismissal, focus return, play state, keyboard clip opening.
- PASS: whitespace/diff checks (`git diff --check`).
- PASS: complete `app.slint` import tree compiles with the Python Slint 1.18.1b1 interpreter. This is UI compilation, not a build of the Rust application with its pinned toolchain.
- NOT VERIFIED: complete native build/APK, device editing/export, visual screenshots, responsive browser layout, 200% zoom, composed contrast and screen reader checks. This environment has no Rust toolchain or browser binary; the Chromium download returned invalid archives.
- N/A: account, database and payment checks; these systems are outside this visual change.

Before shipping an APK, run the repository's mobile build and inspect a 320px phone, a typical iPhone/Android size, landscape, both saved themes, real footage, all panel dismissals and export. Native materials do not provide live background blur; the web preview does.
