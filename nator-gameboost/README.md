# Nator GameBoost 0.1.0

A conservative app process priority helper for iPhone 11, iOS 18.5, Dopamine 3 rootless, complementary to iOS 18 native Game Mode.

**It is experimental. Build success does not mean on-device performance has been validated.**

- Checks running user app processes using libproc and their Info.plist bundle identifiers.
- For a matching game, calls setpriority(PRIO_PROCESS) to try setting nice to -1, -3, or -5.
- Optional (disabled by default) setpriority nice +5 for other **user app processes**, not Apple system daemons.
- Restores original nice values when a configured game stops running or the daemon terminates.
- Recognizes Free Fire (com.dts.freefireth), COD Mobile (com.activision.callofduty.shooter), and PUBG Mobile (com.tencent.ig). Edit the comma-separated list in Settings > Nator GameBoost.
- Does **not** override iOS Game Mode, thermal protection, jetsam bands or memory limits. It does not clean RAM or guarantee FPS increases.
- A process being alive does not prove it is foreground. Native iOS Game Mode handles actual foreground scheduling.
- If the kernel rejects changes, it logs and leaves the process untouched.

## Install
Install the iphoneos-arm64 .deb with Sileo, then respring or reboot userspace.
If the launch daemon did not start, you may need to restart the jailbreak environment (the package does not force reboot).

## Verify (NewTerm/SSH)
```sh
/var/jb/usr/bin/natorgamerd status
/var/jb/usr/bin/natorgamerd list
```
Check nice values with your game open. If unchanged, priority changes may be blocked by iOS or the launch daemon may not have started.

## Reviewed sources (NOT copied or bundled)
- https://github.com/opa334/Dopamine
- https://github.com/opa334/Choicy
- https://github.com/Mathelord/infobar
- https://github.com/conradev/jetsamctl

The implementation is original code. We intentionally do not merge unrelated tweak binaries or disable iOS system services. Set Powercuff to Desativado for gaming.
