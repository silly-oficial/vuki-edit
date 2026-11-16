#!/usr/bin/env python3
"""Pending pt-BR localization pass, no IPA build.
Apply to upstream checkout after existing UI patches.
Never add captions to icon-only controls; translate only existing string keys.
"""
import json
from pathlib import Path

path = Path("AppleApp/Resources/Localization/Localizable.xcstrings")
data = json.loads(path.read_text(encoding="utf-8"))
translations = {
    "Add to Queue": "Adicionar à fila",
    "Play Next": "Reproduzir a seguir",
    "Start Radio": "Iniciar rádio",
    "Track Log": "Histórico da faixa",
    "Track Log…": "Histórico da faixa…",
    "Lyrics": "Letras",
    "Lyrics Offset": "Sincronização da letra",
    "Lyrics Offset…": "Sincronização da letra…",
    "Lyrics Sources": "Fontes de letras",
    "Lyrics options": "Opções de letras",
    "Show Lyrics": "Mostrar letra",
    "Change Lyrics Source": "Alterar fonte da letra",
    "Adjust Lyrics Timing": "Ajustar sincronização da letra",
    "Prefer Word-Synced Lyrics": "Preferir letras sincronizadas por palavra",
    "Lyrics off": "Letras desativadas",
    "Lyrics offset": "Ajuste de sincronização da letra",
    "Playing from YouTube": "Reproduzindo pelo YouTube",
    "No music video for this song": "Não há videoclipe disponível para esta música",
    "Loading music video": "Carregando videoclipe",
    "Open video theater": "Abrir vídeo em tela cheia",
    "Start Picture in Picture": "Abrir vídeo em janela flutuante",
    "Picture in Picture": "Vídeo em janela flutuante",
    "Open Video Theater": "Abrir vídeo em tela cheia",
    "Home": "Início",
    "Explore": "Explorar",
    "Library": "Biblioteca",
    "Search": "Pesquisar",
    "Artist": "Artista",
    "Artists": "Artistas",
    "Album": "Álbum",
    "Albums": "Álbuns",
    "Songs": "Músicas",
    "Play": "Reproduzir",
    "Pause": "Pausar",
    "Shuffle": "Aleatório",
    "Repeat": "Repetir",
    "Share": "Compartilhar",
    "Delete Download": "Excluir download",
    "Delete download": "Excluir download",
    "Sleep Timer": "Temporizador de sono",
    "Revert to Original": "Voltar ao original",
    "Not Playing": "Nada em reprodução",
    "Settings": "Ajustes",
    "Queue": "Fila de reprodução",
    "Downloads": "Downloads",
    "Now Playing": "Em reprodução",
}
changed = 0
for key, translated in translations.items():
    if key not in data["strings"]:
        continue
    item = data["strings"][key]
    item.setdefault("localizations", {})["pt-BR"] = {
        "stringUnit": {"state": "translated", "value": translated}
    }
    changed += 1
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Updated {changed} existing pt-BR string keys; no new UI labels created")
