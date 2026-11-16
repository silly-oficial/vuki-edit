#!/usr/bin/env python3
"""Complete pt-BR string catalog for UI text, with validated translation coverage.

The existing translations are preserved. Curated terminology takes priority.
Remaining public, static UI strings are translated in the build runner, and the
build fails rather than shipping a partially translated interface.
"""
import concurrent.futures
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

CATALOG = Path("AppleApp/Resources/Localization/Localizable.xcstrings")
MANUAL = "Lyrics\tLetras\nTrack Log…\tHistórico da faixa…\nTrack Log\tHistórico da faixa\nUpgrade Quality\tMelhorar qualidade\nStart Radio\tIniciar rádio\nAdd to Queue\tAdicionar à fila\nPlay Next\tReproduzir a seguir\nConvert to Audio\tConverter em áudio\nOpen Artist\tAbrir artista\nOpen Album\tAbrir álbum\nRevert to Original\tVoltar à versão original\nAdd to Playlist…\tAdicionar à playlist…\nAdd to Playlist\tAdicionar à playlist\nShare\tCompartilhar\nSign In\tEntrar\nSign Out\tSair\nSign In to YouTube Music\tEntrar no YouTube Music\nSign in to YouTube Music\tEntrar no YouTube Music\nSign in for your library\tEntre para acessar sua biblioteca\nSign in for your playlists\tEntre para acessar suas playlists\nAccount\tConta\nAccount & Settings\tConta e ajustes\nAccount and Settings\tConta e ajustes\nAccount & Integrations\tConta e integrações\nAccount & Updates\tConta e atualizações\nSources\tFontes\nSound & Quality\tSom e qualidade\nPlayback\tReprodução\nDownloads & Storage\tDownloads e armazenamento\nAppearance\tAparência\nAdvanced Options\tOpções avançadas\nYour Data & Backup\tSeus dados e backup\nAbout & Updates\tSobre e atualizações\nAudio quality, playback, appearance\tQualidade do áudio, reprodução e aparência\nAccess your playlists, library, and personalized mixes.\tAcesse suas playlists, biblioteca e mixes personalizados.\nPersonalized recommendations and your library, on every device.\tRecomendações personalizadas e sua biblioteca em todos os dispositivos.\nAddons, source order, renewal and your libraries\tExtensões, prioridade das fontes, renovação e bibliotecas\nRequested quality, decoded format, effects and device output\tQualidade solicitada, formato decodificado, efeitos e saída de áudio\nQueue, transitions, speed and background playback\tFila, transições, velocidade e reprodução em segundo plano\nOffline quality, local folders and temporary storage\tQualidade offline, pastas locais e arquivos temporários\nPlayer, lyrics, language and visual preferences\tPlayer, letras, idioma e preferências visuais\nSign-in, sharing and connected services\tLogin, compartilhamento e serviços conectados\nModels, analysis, performance and version alignment\tModelos, análise, desempenho e compatibilidade de versões\nListening history, export and importing a backup\tHistórico de reprodução, exportação e importação de backup\nInstalled build, latest release and installation\tVersão instalada, atualização mais recente e instalação\nHome\tInício\nExplore\tExplorar\nLibrary\tBiblioteca\nSearch\tPesquisar\nSearch settings\tPesquisar ajustes\nListen Now\tOuvir agora\nCalm tunes\tMúsicas tranquilas\nToday's biggest hits\tOs maiores sucessos de hoje\nArtist\tArtista\nArtists\tArtistas\nAlbum\tÁlbum\nAlbums\tÁlbuns\nSongs\tMúsicas\nSong\tMúsica\nTrack\tFaixa\nPlay\tReproduzir\nPause\tPausar\nNext\tPróxima\nPrevious\tAnterior\nPlaylists\tPlaylists\nSettings\tAjustes\nDone\tConcluído\nCancel\tCancelar\nClose\tFechar\nBack\tVoltar\nOpen\tAbrir\nSave\tSalvar\nDelete\tExcluir\nRemove\tRemover\nRetry\tTentar novamente\nRefresh\tAtualizar\nLoading\tCarregando\nMore\tMais\nMore Options\tMais opções\nShow all\tVer tudo\nView\tVisualizar\nSort\tOrdenar\nSort By\tOrdenar por\nSort by\tOrdenar por\nFilter this library\tFiltrar esta biblioteca\nNo results\tNenhum resultado\nNothing here yet\tAinda não há nada aqui\nNothing playing.\tNada em reprodução.\nNothing playing\tNada em reprodução\nNow Playing\tEm reprodução\nNow playing\tEm reprodução\nUp next\tA seguir\nQueue\tFila de reprodução\nShuffle\tAleatório\nShuffle on\tModo aleatório ativado\nShuffle off\tModo aleatório desativado\nRepeat all\tRepetir todas\nRepeat one\tRepetir uma\nRepeat off\tRepetição desativada\nDownloads\tDownloads\nDownload\tBaixar\nDownload anyway\tBaixar mesmo assim\nDelete Download\tExcluir download\nCancel download\tCancelar download\nSleep timer\tTemporizador de sono\nSleep 15 min\tDesligar em 15 min\nSleep 30 min\tDesligar em 30 min\nSleep 45 min\tDesligar em 45 min\nSleep 60 min\tDesligar em 60 min\nStop after this track\tParar após esta música\nCancel timer\tCancelar temporizador\nLocal Music\tMúsicas locais\nAudio Quality\tQualidade do áudio\nAudio Output\tSaída de áudio\nAudio output\tSaída de áudio\nOutput\tSaída\nOutput Precision\tPrecisão de saída\nOutput Switcher\tSeletor de saída de áudio\nEqualizer\tEqualizador\nNormalization\tNormalização\nBalance\tBalanço\nVolume\tVolume\nVolume Up\tAumentar volume\nVolume Down\tDiminuir volume\nHeadphones\tFones de ouvido\nHeadphone\tFone de ouvido\nSpeaker\tAlto-falante\nBluetooth\tBluetooth\nAirPlay & Bluetooth\tAirPlay e Bluetooth\nWi-Fi recommended\tWi-Fi recomendado\nWaiting for Wi-Fi\tAguardando Wi-Fi\nOn Device\tNo dispositivo\nOn This Device\tNeste dispositivo\nOn device\tNo dispositivo\nOn disk\tNo armazenamento\nOffline\tOffline\nOn\tAtivado\nOff\tDesativado\nDark\tEscuro\nLight\tClaro\nSystem\tAutomático\nTransparent\tTransparente\nLanguage\tIdioma\nApp Language\tIdioma do aplicativo\nFollow the App Language\tSeguir o idioma do aplicativo\nTranslation Language\tIdioma da tradução\nChoose Language…\tEscolher idioma…\nChoose Output\tEscolher saída de áudio\nShow Lyrics\tMostrar letra\nNo lyrics\tNenhuma letra\nNo lyrics for this track\tNão há letra para esta música\nNo lyrics for this track.\tNão há letra para esta música.\nLyrics Sources\tFontes de letras\nLyrics options\tOpções de letras\nLyrics Offset\tSincronização da letra\nLyrics Offset…\tSincronização da letra…\nAdjust Lyrics Timing\tAjustar sincronização da letra\nChange Lyrics Source\tAlterar fonte da letra\nPrefer Word-Synced Lyrics\tPreferir letras sincronizadas por palavra\nPositive values show lyrics later\tValores positivos atrasam a exibição da letra\nLooking for lyrics\tBuscando letra\nLooking for lyrics…\tBuscando letra…\nShow Original\tMostrar original\nRecent\tRecentes\nRecents\tRecentes\nRecently Searched\tPesquisas recentes\nHistory\tHistórico\nListening History\tHistórico de reprodução\nActivity\tAtividade\nRecent activity\tAtividade recente\nLiked\tMarcadas como favoritas\nLike\tCurtir\nUnlike\tRemover curtida\nSave to Library\tSalvar na biblioteca\nPin to Library\tFixar na biblioteca\nUnpin from Library\tDesafixar da biblioteca\nPin\tFixar\nUnpin\tDesafixar\nPinned\tFixados\nNew Playlist\tNova playlist\nNew playlist\tNova playlist\nRename Playlist\tRenomear playlist\nRename Playlist…\tRenomear playlist…\nRemove from Playlist\tRemover da playlist\nRemove from Liked Music\tRemover das músicas curtidas\nImport Playlist File\tImportar arquivo de playlist\nPlaylist Import\tImportação de playlist\nPlaylist Update\tAtualização da playlist\nPlaylist Privacy…\tPrivacidade da playlist…\nPlaylist privacy\tPrivacidade da playlist\nPublic\tPública\nPrivate\tPrivada\nUnlisted\tNão listada\nYour Songs\tSuas músicas\nYour albums live here\tSeus álbuns aparecem aqui\nYour artists live here\tSeus artistas aparecem aqui\nYour songs live here\tSuas músicas aparecem aqui\nYour playlists\tSuas playlists\nYour libraries\tSuas bibliotecas\nYour Data\tSeus dados\nYour Replay\tSeu resumo musical\nYour Replay is growing\tSeu resumo musical está crescendo\nTop result\tPrimeiro resultado\nNo tracks\tNenhuma faixa\nNo downloads yet\tAinda não há downloads\nNo albums yet\tAinda não há álbuns\nNo artists yet\tAinda não há artistas\nNo playlists yet\tAinda não há playlists\nNo listening history yet\tAinda não há histórico de reprodução\nNo saved albums yet\tAinda não há álbuns salvos\nNo saved artists yet\tAinda não há artistas salvos\nNo log lines for this track\tNão há registros para esta faixa\nNo audio files here\tNão há arquivos de áudio aqui\nNo results\tNenhum resultado\nNo matches\tNenhuma correspondência\nSearch unavailable\tPesquisa indisponível\nManage Sources\tGerenciar fontes\nManage party\tGerenciar sessão em grupo\nListen Together\tOuvir juntos\nListen together\tOuvir juntos\nJoin a party\tEntrar em uma sessão\nCreate a party\tCriar sessão\nLeave the party\tSair da sessão\nParty code\tCódigo da sessão\nParty server\tServidor da sessão\nParty size\tParticipantes\nPeople listening\tPessoas ouvindo\nInvite\tConvidar\nShare invite\tCompartilhar convite\nUsername\tNome de usuário\nYour name\tSeu nome\nYour profile details couldn’t be loaded. You can still review and confirm them on the Google page.\tNão foi possível carregar os dados do perfil. Você ainda pode conferir e confirmar na página do Google.\nAccount & Settings\tConta e ajustes\nAccount and Settings\tConta e ajustes\nSound Mode\tModo de som\nSound & Quality\tSom e qualidade\nAudio Pipeline\tProcessamento de áudio\nPlayback Diagnostics\tDiagnóstico de reprodução\nDiagnostic Reports\tRelatórios de diagnóstico\nSave Diagnostic Report\tSalvar relatório de diagnóstico\nShare Diagnostic Report\tCompartilhar relatório de diagnóstico\nCheck for Updates\tVerificar atualizações\nCheck for updates automatically\tVerificar atualizações automaticamente\nAbout\tSobre\nDeveloper\tDesenvolvedor\nVersion\tVersão\nView Release Notes\tVer novidades da versão\nInstall\tInstalar\nInstalled\tInstalado\nDownload Models\tBaixar modelos\nModels\tModelos\nPerformance\tDesempenho\nRefresh Rate\tTaxa de atualização\nHigh Performance Mode\tModo de alto desempenho\nCore ML · Neural Engine\tCore ML · Neural Engine\nEqualizer\tEqualizador\nReduce Animation\tReduzir animações\nReduce Dynamic Blur\tReduzir desfoque dinâmico\nFull-Screen Cover Art\tCapa em tela cheia\nAnimated Cover Art\tCapa animada\nSpotify Canvas\tSpotify Canvas\nSpotify Canvas Setup\tConfigurar Spotify Canvas\nSwitch to grid view\tExibir em grade\nSwitch to list view\tExibir em lista\nList or grid\tLista ou grade\nTest Connection\tTestar conexão\nTest connection\tTestar conexão\nTesting…\tTestando…\nVerify\tVerificar\nVerifying checksum…\tVerificando integridade…\nWorking…\tProcessando…\nDone\tConcluído\nContinue in Background\tContinuar em segundo plano\nOpen BitChord\tAbrir BitChord\nOpen system output switcher\tAbrir seletor de saída do sistema\nOpen the release\tAbrir página da versão\nOpen the lyrics\tAbrir letra\nOpens the lyrics\tAbre a letra\nOpens Now Playing\tAbre a tela de reprodução\nPlay a song to see lyrics here.\tReproduza uma música para ver a letra aqui.\nYouTube Music\tYouTube Music\nEnglish\tInglês\nPortuguese\tPortuguês\nSpanish\tEspanhol\nFrench\tFrancês\nGerman\tAlemão\nItalian\tItaliano\nJapanese\tJaponês\nChinese\tChinês\nHindi\tHíndi\nKorean\tCoreano"
curated = dict(line.split("\t", 1) for line in MANUAL.splitlines() if "\t" in line)
data = json.loads(CATALOG.read_text(encoding="utf-8"))
strings = data["strings"]

# Catalog misses dynamic String labels, particularly SettingsLine and the side drawer.
# Register existing named controls only. Never create UI captions for icon-only actions.
ui = Path("AppleApp/Sources/UI")
patterns = [
    r'\b(?:Text|Button|Label|Tab|TabSection|Toggle|Picker|NavigationLink|option|actionLabel)\(\s*"([^"\n]{2,230})"',
    r'\b(?:title|subtitle|prompt|accessibilityLabel):\s*"([^"\n]{2,230})"',
    r'\.navigationTitle\(\s*"([^"\n]{2,230})"',
]
added = 0
for file in ui.rglob("*.swift"):
    source = file.read_text(encoding="utf-8")
    for pattern in patterns:
        for value in re.findall(pattern, source):
            if ("\\(" in value or "\\n" in value or "://" in value
                    or not re.search(r"[A-Za-z]{2}", value)):
                continue
            if value not in strings:
                strings[value] = {}
                added += 1

# Include the existing user-facing drawer strings from the custom Swift file.
for key in curated:
    if key not in strings:
        strings[key] = {}

protected = re.compile(r'%(?:\d+\$)?(?:lld|ld|d|@|s|f)|\{[A-Za-z_][A-Za-z_0-9]*\}|\*\*')
def mask(value):
    tokens = []
    def replace(match):
        index = len(tokens)
        tokens.append(match.group())
        return "ZXQHOLD" + str(index) + "QXZ"
    return protected.sub(replace, value), tokens

def translate(value):
    masked, tokens = mask(value)
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode({
        "client":"gtx", "sl":"en", "tl":"pt", "dt":"t", "q":masked
    })
    last = None
    for attempt in range(5):
        try:
            request = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0 BitChordLocalization/1.0"})
            with urllib.request.urlopen(request, timeout=20) as response:
                result = json.load(response)
            output = "".join(part[0] or "" for part in result[0])
            for i, token in enumerate(tokens):
                marker = "ZXQHOLD" + str(i) + "QXZ"
                # Google may introduce spaces into synthetic markers.
                pattern = r"ZXQ\s*HOLD\s*" + str(i) + r"\s*QXZ"
                output, count = re.subn(pattern, lambda _: token, output, flags=re.I)
                if count != 1:
                    raise ValueError("Placeholder was changed: " + repr(value))
            if not output.strip():
                raise ValueError("Empty translation: " + repr(value))
            return output.strip()
        except Exception as exc:
            last = exc
            time.sleep(min(16, 2 ** attempt))
    raise RuntimeError(f"Could not translate {value!r}: {last}")

def eligible(key):
    if not key.strip() or not re.search(r"[A-Za-z]{2}", key):
        return False
    if key.startswith(("https://", "http://")):
        return False
    if key in {"BITCHORD", "WebDAV", "YouTube Music", "AirPlay", "Bluetooth", "Spotify Canvas",
               "GitHub", "DAC", "HDMI", "USB Audio", "CarPlay", "Core ML · Neural Engine",
               "open-unmix umxhq", "sp_dc cookie"}:
        return False
    return True

pending = []
for key, item in strings.items():
    if not eligible(key):
        continue
    existing = item.get("localizations", {}).get("pt-BR", {}).get("stringUnit", {}).get("value")
    if key in curated:
        value = curated[key]
    elif existing and existing != key:
        value = existing
    else:
        pending.append(key)
        continue
    item.setdefault("localizations", {})["pt-BR"] = {"stringUnit":{"state":"translated","value":value}}

print(f"Curated {len(curated)} entries; discovered {added} additional named UI keys; auto-translating {len(pending)} strings", flush=True)
failed = []
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    futures = {pool.submit(translate, key): key for key in pending}
    for index, future in enumerate(concurrent.futures.as_completed(futures), 1):
        key = futures[future]
        try:
            value = future.result()
            strings[key].setdefault("localizations", {})["pt-BR"] = {
                "stringUnit":{"state":"translated","value":value}
            }
        except Exception as exc:
            failed.append((key, str(exc)))
        if index % 100 == 0:
            print(f"Translation progress: {index}/{len(pending)}", flush=True)

if failed:
    for key, error in failed[:15]:
        print("TRANSLATION FAILED:", repr(key), error)
    raise SystemExit(f"Refusing incomplete pt-BR build: {len(failed)} missing translations")

missing = [key for key in strings if eligible(key) and
           not strings[key].get("localizations", {}).get("pt-BR", {}).get("stringUnit", {}).get("value")]
if missing:
    raise SystemExit(f"Missing {len(missing)} UI strings: {missing[:15]}")
CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"SUCCESS: {len(strings)} catalog keys; {len(strings)-len(missing)} pt-BR entries; 0 eligible untranslated", flush=True)
