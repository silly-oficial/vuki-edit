import SwiftUI
import BitChordShared

#if os(iOS)
/// A right-hand track action drawer. It leaves PlaybackController and every
/// playback surface mounted, and only responds to the same actions used by
/// SongActionButtons in the native menu.
struct PlayerSideDrawer: View {
    @Binding var isPresented: Bool
    let onLyricsOffset: () -> Void

    @Environment(PlaybackController.self) private var controller
    @Environment(AuthController.self) private var auth
    @Environment(AppModel.self) private var appModel
    @Environment(ToastCenter.self) private var toast
    @Environment(\.accessibilityReduceTransparency) private var reduceTransparency
    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    @GestureState private var dragDistance: CGFloat = 0
    @State private var sleepOptionsExpanded = false

    private var current: QueueEntry? { controller.current }

    // Use the same sampled-artwork palette as the player, never a fixed hue.
    private var artworkTint: ArtworkPalette.PageTint {
        ArtworkPalette.pageTint(
            from: current?.artworkData,
            seed: current?.id.hashValue ?? 0
        )
    }

    private var animation: Animation {
        reduceMotion ? .linear(duration: 0.01) : .easeInOut(duration: 0.30)
    }

    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .trailing) {
                if isPresented {
                    Color.black.opacity(0.43)
                        .ignoresSafeArea()
                        .contentShape(Rectangle())
                        .onTapGesture(perform: dismissDrawer)
                        .transition(.opacity)
                        .accessibilityLabel("Close track actions")

                    drawer(width: geometry.size.width * 0.75, height: geometry.size.height)
                        .offset(x: dragDistance)
                        .transition(.move(edge: .trailing))
                        .zIndex(1)
                        // A horizontal gesture is simultaneous with the vertical
                        // ScrollView; swiping through the actions still scrolls.
                        .simultaneousGesture(
                            DragGesture(minimumDistance: 16)
                                .updating($dragDistance) { value, state, _ in
                                    guard value.translation.width > 0,
                                          abs(value.translation.width) > abs(value.translation.height)
                                    else { return }
                                    state = value.translation.width
                                }
                                .onEnded { value in
                                    guard value.translation.width > 85 ||
                                          (value.predictedEndTranslation.width > 150 &&
                                           abs(value.translation.width) > abs(value.translation.height))
                                    else { return }
                                    dismissDrawer()
                                }
                        )
                }
            }
            .frame(width: geometry.size.width, height: geometry.size.height)
        }
        .ignoresSafeArea(edges: .bottom)
        .allowsHitTesting(isPresented)
        .animation(animation, value: isPresented)
        .animation(reduceMotion ? nil : .easeInOut(duration: 0.55), value: current?.id)
        .onChange(of: isPresented) { _, visible in
            if visible { sleepOptionsExpanded = false }
        }
        // Also handles an iPhone VoiceOver "scrub" / Escape back gesture.
        .accessibilityAction(.escape) { dismissDrawer() }
    }

    private func dismissDrawer() {
        withAnimation(animation) { isPresented = false }
    }

    private func perform(_ action: () -> Void) {
        action()
        dismissDrawer()
    }

    private func drawer(width: CGFloat, height: CGFloat) -> some View {
        let tint = artworkTint
        return ScrollView(.vertical) {
            VStack(alignment: .leading, spacing: 11) {
                Capsule()
                    .fill(.primary.opacity(0.26))
                    .frame(width: 42, height: 5)
                    .frame(maxWidth: .infinity)
                    .padding(.top, 14)
                    .padding(.bottom, 10)

                header
                    .padding(.bottom, 11)

                if let entry = current {
                    options(for: entry)
                } else {
                    Label("Nothing playing", systemImage: "music.note")
                        .foregroundStyle(.secondary)
                        .padding(.vertical, 24)
                }

                Spacer(minLength: 22)
            }
            .padding(.horizontal, 13)
            .frame(maxWidth: .infinity, alignment: .topLeading)
        }
        .scrollIndicators(.hidden)
        .frame(width: width, height: height)
        .background {
            ZStack {
                // Preserve the dynamic blur/mesh that responds to album changes.
                MeshBackdrop(seed: current?.id.hashValue ?? 0, artwork: current?.artworkData)
                Rectangle()
                    .fill(reduceTransparency ? tint.wash : tint.wash.opacity(0.43))
                Rectangle()
                    .fill(.ultraThinMaterial)
                    .opacity(reduceTransparency ? 0 : 0.72)
            }
            .clipShape(
                UnevenRoundedRectangle(
                    topLeadingRadius: 32, bottomLeadingRadius: 32,
                    bottomTrailingRadius: 0, topTrailingRadius: 0
                )
            )
        }
        .overlay(alignment: .leading) {
            UnevenRoundedRectangle(
                topLeadingRadius: 32, bottomLeadingRadius: 32,
                bottomTrailingRadius: 0, topTrailingRadius: 0
            )
            .strokeBorder(tint.accent.opacity(0.20), lineWidth: 1)
            .allowsHitTesting(false)
        }
        .shadow(color: tint.wash.opacity(0.48), radius: 25, x: -9)
        .accessibilityIdentifier("player.trackActionDrawer")
    }

    private var header: some View {
        HStack(spacing: 11) {
            if let entry = current {
                ArtworkView(entry: entry, side: 59)
                    .frame(width: 59, height: 59)
                    .clipShape(RoundedRectangle(cornerRadius: 13, style: .continuous))
                    .accessibilityHidden(true)
            } else {
                Image(systemName: "music.note")
                    .frame(width: 59, height: 59)
                    .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 13))
            }

            VStack(alignment: .leading, spacing: 5) {
                Text(current?.title ?? "Nothing playing")
                    .font(.system(size: 16, weight: .semibold))
                    .lineLimit(2)
                    .foregroundStyle(.primary)
                Text(current?.artist ?? "")
                    .font(.system(size: 14))
                    .lineLimit(2)
                    .foregroundStyle(.secondary)
            }
            .frame(maxWidth: .infinity, alignment: .leading)

            Button(action: dismissDrawer) {
                Image(systemName: "xmark")
                    .font(.system(size: 12, weight: .bold))
                    .frame(width: 30, height: 30)
                    .background(.thinMaterial, in: Circle())
            }
            .buttonStyle(.plain)
            .accessibilityLabel("Close track actions")
        }
        .accessibilityElement(children: .contain)
        .accessibilityIdentifier("player.trackActionDrawerHeader")
    }

    @ViewBuilder
    private func options(for entry: QueueEntry) -> some View {
        // This menu deliberately preserves the same gating and action calls as
        // SongActionButtons(entry:showSleepTimer:showDebugLog:).
        let _ = LikeStore.shared.epoch

        option("Lyrics Offset…", icon: "music.note.list",
               enabled: !controller.displayedLyrics.isEmpty) {
            onLyricsOffset()
        }
        option("Track Log…", icon: "doc.text") {
            toast.showTrackLog(entry)
        }

        Button {
            withAnimation(animation) { sleepOptionsExpanded.toggle() }
        } label: {
            actionLabel(
                controller.sleepTimerStatus.map { "Temporizador de sono · " + $0 }
                    ?? "Temporizador de sono",
                icon: "moon.zzz", chevron: sleepOptionsExpanded ? "chevron.up" : "chevron.right"
            )
        }
        .buttonStyle(.plain)

        if sleepOptionsExpanded {
            VStack(spacing: 7) {
                option("15 minutos", icon: "timer") { controller.startSleep(minutes: 15) }
                option("30 minutos", icon: "timer") { controller.startSleep(minutes: 30) }
                option("45 minutos", icon: "timer") { controller.startSleep(minutes: 45) }
                option("60 minutos", icon: "timer") { controller.startSleep(minutes: 60) }
                option("Após esta música", icon: "moon.stars") { controller.startSleepAfterTrack() }
                if controller.sleepTimerStatus != nil {
                    option("Cancelar temporizador", icon: "xmark.circle", destructive: true) {
                        controller.cancelSleep()
                    }
                }
            }
            .padding(.leading, 12)
            .transition(.opacity.combined(with: .move(edge: .top)))
        }

        ShareLink(item: shareURL(for: entry)) {
            actionLabel("Compartilhar", icon: "square.and.arrow.up")
        }
        .buttonStyle(.plain)

        if !entry.isLocal {
            downloadOption(for: entry)
        }

        if entry.id == controller.current?.id, controller.canUpgradeQuality {
            option("Upgrade Quality", icon: "sparkles") {
                controller.upgradeQuality()
            }
        }

        groupDivider

        option("Start Radio", icon: "dot.radiowaves.left.and.right") {
            controller.playRadio(entry)
        }
        option("Add to Queue", icon: "text.badge.plus") {
            controller.addToQueue(entry)
            toast.queueNotice("Added to queue: \(entry.title)")
        }
        option("Play Next", icon: "text.line.first.and.arrowtriangle.forward") {
            controller.playNext(entry)
            toast.queueNotice("Playing next: \(entry.title)")
        }
        option("Tocar", icon: "play.fill") {
            controller.play([entry], at: 0)
        }

        // These conditional options were also present in the original menu;
        // don't drop them when the music is liked or from a saved playlist.
        if auth.signedIn, let vid = entry.videoId {
            groupDivider
            option(SongRatingActions.likeTitle(vid), icon: "hand.thumbsup") {
                Task {
                    await SongRatingActions.toggleLike(
                        videoId: vid, controller: controller, toast: toast
                    )
                }
            }
            option(SongRatingActions.dislikeTitle(vid), icon: "hand.thumbsdown") {
                Task {
                    await SongRatingActions.toggleDislike(
                        videoId: vid, controller: controller, toast: toast
                    )
                }
            }
            option("Add to Playlist…", icon: "music.note.list") {
                appModel.playlistPicker = PlaylistPickerRequest(
                    videoId: vid, title: entry.title
                )
            }
        }

        if entry.id == controller.current?.id {
            if controller.songVersions[entry.id] != nil {
                option("Convert to Audio", icon: "music.note") {
                    controller.playSongVersion()
                }
            }
            if controller.canRevertToOriginal {
                option("Revert to Original", icon: "arrow.uturn.backward") {
                    controller.revertToOriginal()
                }
            }
        }

        if WebDavStore.shared.canUpload(path: entry.source, id: entry.id) {
            option("Upload to WebDAV", icon: "arrow.up.doc") {
                toast.show("Uploading \(entry.title)…", kind: .info)
                Task {
                    do {
                        let fileName = try await WebDavStore.shared.upload(
                            path: entry.source, title: entry.title, artist: entry.artist
                        )
                        toast.show("Uploaded \(fileName)", kind: .success)
                    } catch {
                        toast.show(error.localizedDescription, kind: .failure)
                    }
                }
            }
        }
        if let albumId = entry.albumId {
            option("Open Album", icon: "square.stack") {
                appModel.pendingDetail = .detail(
                    browseId: albumId, title: entry.albumName ?? "Album"
                )
            }
        }
        if let artistId = entry.artistId {
            option("Open Artist", icon: "person.crop.square") {
                appModel.pendingDetail = .detail(
                    browseId: artistId, title: entry.artist
                )
            }
        }
    }

    @ViewBuilder
    private func downloadOption(for entry: QueueEntry) -> some View {
        let store = DownloadStore.shared
        let asset = store.asset(for: entry)
        let activeJob = store.jobs.first {
            $0.entry.source == entry.source && $0.entry.id == entry.id &&
            ($0.status == .queued || $0.status == .running)
        }
        let failedJob = store.jobs.first {
            $0.entry.source == entry.source && $0.entry.id == entry.id &&
            $0.status == .failed
        }

        if let activeJob {
            option("Cancelar download", icon: "xmark.circle", destructive: true) {
                store.cancel(activeJob.id)
                toast.show("Cancelled \(entry.title)")
            }
        } else if let failedJob {
            option("Repetir download", icon: "arrow.clockwise") {
                switch store.download(entry) {
                case .started:
                    toast.show("Retrying \(entry.title)")
                case .blockedByWifiOnly:
                    toast.show("Downloads are limited to Wi-Fi. Turn that off in Settings to use mobile data.", kind: .failure)
                case .alreadyExists:
                    toast.show("\(entry.title) is already downloading or downloaded", kind: .info)
                case .ignoredLocalTrack:
                    break
                }
            }
        } else if let asset {
            option("Excluir download", icon: "trash", destructive: true) {
                let title = entry.title
                toast.requestConfirmation(ConfirmationRequest(
                    title: "Delete the download?",
                    message: "“\(title)” will be removed from this device. It will download again when played.",
                    confirm: "Delete Download"
                ) {
                    DownloadStore.shared.delete(asset.path)
                    toast.show("Deleted \(title)")
                })
            }
        } else {
            option("Baixar", icon: "arrow.down.to.line") {
                SongRatingActions.startDownload(entry, toast: toast)
            }
        }
    }

    private var groupDivider: some View {
        Rectangle()
            .fill(artworkTint.accent.opacity(0.19))
            .frame(height: 1)
            .padding(.vertical, 8)
            .padding(.horizontal, 12)
            .accessibilityHidden(true)
    }

    private func shareURL(for entry: QueueEntry) -> URL {
        if let videoId = entry.videoId {
            return URL(string: "https://music.youtube.com/watch?v=\(videoId)")!
        }
        return URL(string: "https://music.youtube.com")!
    }

    private func option(
        _ title: String, icon: String,
        destructive: Bool = false,
        enabled: Bool = true,
        action: @escaping () -> Void
    ) -> some View {
        Button {
            perform(action)
        } label: {
            actionLabel(title, icon: icon, destructive: destructive)
        }
        .buttonStyle(.plain)
        .disabled(!enabled)
        .opacity(enabled ? 1 : 0.45)
    }

    private func actionLabel(
        _ title: String,
        icon: String,
        destructive: Bool = false,
        chevron: String? = nil
    ) -> some View {
        let tint = artworkTint
        return HStack(spacing: 11) {
            Image(systemName: icon)
                .font(.system(size: 18, weight: .medium))
                .foregroundStyle(destructive ? Color.red : tint.accent)
                .frame(width: 25)
                .accessibilityHidden(true)
            Text(title)
                .font(.system(size: 15, weight: .medium))
                .foregroundStyle(.primary)
                .multilineTextAlignment(.leading)
                .fixedSize(horizontal: false, vertical: true)
            Spacer(minLength: 2)
            if let chevron {
                Image(systemName: chevron)
                    .font(.system(size: 12, weight: .semibold))
                    .foregroundStyle(.secondary)
                    .accessibilityHidden(true)
            }
        }
        .padding(.horizontal, 13)
        .frame(minHeight: 50)
        .padding(.vertical, 2)
        .background {
            RoundedRectangle(cornerRadius: 15, style: .continuous)
                .fill(.ultraThinMaterial)
                .overlay {
                    RoundedRectangle(cornerRadius: 15, style: .continuous)
                        .fill(tint.elevated.opacity(0.35))
                }
        }
        .overlay {
            RoundedRectangle(cornerRadius: 15, style: .continuous)
                .strokeBorder(tint.accent.opacity(0.13), lineWidth: 1)
        }
        .contentShape(RoundedRectangle(cornerRadius: 15))
        .accessibilityElement(children: .combine)
    }
}
#endif
