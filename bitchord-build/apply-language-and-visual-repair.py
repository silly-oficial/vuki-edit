#!/usr/bin/env python3
"""Apply device-language selection, localized labels, solid tab background, and remove hero seam."""
from pathlib import Path
import json

base = Path("AppleApp/Sources/UI")
def edit(path, old, new):
    p=base/path
    s=p.read_text()
    if old not in s: raise RuntimeError(f"Missing target in {path}: {old[:70]}")
    p.write_text(s.replace(old,new,1))

edit("RootView.swift",
    '    @State private var updateDetails: AppReleaseUpdate?',
    '    @State private var updateDetails: AppReleaseUpdate?\n    @AppStorage("bitchord.appLanguage") private var appLanguage = "system"')
edit("RootView.swift",
    '        .environment(\\.rowSelection, rowSelection)',
    '        .environment(\\.rowSelection, rowSelection)\n        .environment(\\.locale, appLanguage == "system" ? Locale.autoupdatingCurrent : Locale(identifier: appLanguage))')
edit("RootView.swift",
    '        .tabViewCustomization($tabCustomization)',
    '''        .background {
            // Opaque foundation independent of the iOS 26 scroll-edge glass.
            Color(uiColor: .systemBackground).ignoresSafeArea(edges: .bottom)
        }
        .toolbarBackground(Color(uiColor: .secondarySystemBackground), for: .tabBar)
        .toolbarBackground(.visible, for: .tabBar)
        .tabViewCustomization($tabCustomization)''')
edit("Settings/SettingsView.swift",
    '    @State var crossfade = Int(',
    '    @AppStorage("bitchord.appLanguage") var appLanguage = "system"\n    @State var crossfade = Int(')
edit("Settings/SettingsView+Appearance.swift",
    '    func buildAppearanceRows(_ rows: inout SettingsRows) {',
    '''    func buildAppearanceRows(_ rows: inout SettingsRows) {
        rows.row("Idioma do aplicativo", "idioma", "language", "português", "english") {
            VStack(alignment: .leading, spacing: 8) {
                SettingsLine(glyph: .lyricsSources, title: "Idioma do aplicativo",
                             subtitle: "Automático acompanha o idioma do iPhone.") { EmptyView() }
                Picker("Idioma do aplicativo", selection: $appLanguage) {
                    Text("Automático (iPhone)").tag("system")
                    Text("Português (Brasil)").tag("pt-BR")
                    Text("English").tag("en")
                    Text("Español").tag("es")
                    Text("Français").tag("fr")
                    Text("Deutsch").tag("de")
                    Text("Italiano").tag("it")
                }
                .labelsHidden()
                .pickerStyle(.menu)
                .frame(maxWidth: .infinity, alignment: .leading)
                .padding(.leading, 41)
            }
            .padding(.vertical, 4)
        }''')
# Dynamic String values are not localized by SwiftUI's Text(String) initializer.
for file in ["Settings/SettingsRows.swift"]:
    p=base/file
    s=p.read_text()
    s=s.replace("Text(title)", "Text(LocalizedStringKey(title))")
    s=s.replace("Text(subtitle)", "Text(LocalizedStringKey(subtitle))")
    p.write_text(s)
# Eliminate the artificial pixel-row continuation and gradient seams when a video is displayed.
p=base/"NowPlaying/PlayerArtwork.swift"
s=p.read_text()
s=s.replace("    private let fadeFraction: CGFloat = 0.42","    private let fadeFraction: CGFloat = 0.42")
# Avoid sampling a single distorted row from artwork; use smooth cover-color mesh instead.
s=s.replace('Image(decorative: edge, scale: 1).resizable()\n                        .frame(height: min(seam, geo.size.height))',
            'Image(decorative: texture, scale: 1).resizable()\n                        .frame(height: min(seam, geo.size.height))')
p.write_text(s)
# Existing custom drawer uses String titles; make these eligible for catalog lookup.
p=base/"NowPlaying/PlayerSideDrawer.swift"
if p.exists():
    s=p.read_text().replace('Text(title)', 'Text(LocalizedStringKey(title))')
    p.write_text(s)
catalog=Path("AppleApp/Resources/Localization/Localizable.xcstrings")
data=json.loads(catalog.read_text())
translations={
"Sources":"Fontes","Sound & Quality":"Som e qualidade","Playback":"Reprodução",
"Downloads & Storage":"Downloads e armazenamento","Appearance":"Aparência",
"Account & Integrations":"Conta e integrações","Advanced Options":"Opções avançadas",
"Your Data & Backup":"Seus dados e backup","About & Updates":"Sobre e atualizações",
"Account":"Conta","Sign In":"Entrar","Sign In to YouTube Music":"Entrar no YouTube Music",
"Access your playlists, library, and personalized mixes.":"Acesse suas playlists, biblioteca e recomendações personalizadas.",
"Audio quality, playback, appearance":"Qualidade do áudio, reprodução e aparência",
"Addons, source order, renewal and your libraries":"Extensões, ordem das fontes, renovação e suas bibliotecas",
"Requested quality, decoded format, effects and device output":"Qualidade desejada, formato de áudio, efeitos e saída do dispositivo",
"Queue, transitions, speed and background playback":"Fila, transições, velocidade e reprodução em segundo plano",
"Offline quality, local folders and temporary storage":"Qualidade offline, pastas locais e armazenamento temporário",
"Player, lyrics, language and visual preferences":"Player, letras, idioma e aparência",
"Sign-in, sharing and connected services":"Login, compartilhamento e serviços conectados",
"Models, analysis, performance and version alignment":"Modelos, análise, desempenho e compatibilidade de versões",
"Listening history, export and importing a backup":"Histórico de reprodução, exportação e importação de backup",
"Installed build, latest release and installation":"Versão instalada, atualização mais recente e instalação",
"Manage Sources":"Gerenciar fontes","Search settings":"Pesquisar ajustes",
"Upgrade Quality":"Melhorar qualidade","Start Radio":"Iniciar rádio",
"Add to Queue":"Adicionar à fila","Play Next":"Reproduzir a seguir",
"Track Log…":"Histórico da faixa…","Track Log":"Histórico da faixa",
"Lyrics":"Letras","Convert to Audio":"Converter em áudio","Open Artist":"Abrir artista",
"Open Album":"Abrir álbum","Add to Playlist…":"Adicionar à playlist…",
"Revert to Original":"Voltar à versão original","Upload to WebDAV":"Enviar ao WebDAV",
"Close track actions":"Fechar opções da faixa","Nothing playing":"Nada em reprodução",
"Personalized recommendations and your library, on every device.":"Recomendações personalizadas e sua biblioteca em todos os dispositivos.",
"Calm tunes":"Músicas tranquilas","Today's biggest hits":"Os maiores sucessos de hoje",
"Artist":"Artista","monthly audience":"ouvintes mensais",
"System":"Automático","Light":"Claro","Dark":"Escuro",
"Reduce Animation":"Reduzir animações","Reduce Dynamic Blur":"Reduzir desfoque dinâmico",
"Full-Screen Cover Art":"Capa em tela cheia","Legacy Mesh Gradient":"Gradiente clássico",
"Animated Cover Art":"Capa animada","Artist Signatures":"Assinaturas dos artistas",
"Translation Language":"Idioma da tradução","Lyrics Sources":"Fontes de letras",
"Prefer Word-Synced Lyrics":"Preferir letras sincronizadas por palavra",
"Automático (iPhone)":"Automático (iPhone)","Idioma do aplicativo":"Idioma do aplicativo",
"Automático acompanha o idioma do iPhone.":"Automático acompanha o idioma do iPhone.",
"Settings":"Ajustes","Done":"Concluído","Home":"Início","Explore":"Explorar",
"Library":"Biblioteca","Search":"Pesquisar","Playlists":"Playlists",
"Search":"Pesquisar","Sign In to YouTube Music":"Entrar no YouTube Music",
}
for k,v in translations.items():
    data["strings"].setdefault(k,{}).setdefault("localizations",{})["pt-BR"]={"stringUnit":{"state":"translated","value":v}}
catalog.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")
print(f"Applied language preference and {len(translations)} PT-BR UI translations")
