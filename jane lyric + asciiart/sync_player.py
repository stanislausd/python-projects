"""
Author link: https://github.com/stanislausd
"""

import os
import re
import sys
import time
import shutil
import subprocess
from dataclasses import dataclass
from typing import List, Optional, Tuple



@dataclass
class LyricLine:
    time_sec: float
    text: str


LRC_PATTERN = re.compile(r"\[(\d{2}):(\d{2}(?:\.\d{1,3})?)\](.*)")


def parse_lrc(path: str) -> List[LyricLine]:
    result: List[LyricLine] = []
    with open(path, encoding="utf-8") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line or raw_line.startswith("#"):
                continue
            match = LRC_PATTERN.match(raw_line)
            if not match:
                continue
            minutes, seconds, text = match.groups()
            total_seconds = int(minutes) * 60 + float(seconds)
            result.append(LyricLine(total_seconds, text.strip()))
    result.sort(key=lambda l: l.time_sec)
    return result


def load_art(path: str) -> List[str]:
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))  # type: ignore


def rgb_to_ansi(rgb: Tuple[int, int, int], bold: bool = False) -> str:
    r, g, b = rgb
    prefix = "1;" if bold else ""
    return f"\x1b[{prefix}38;2;{r};{g};{b}m"


def dim_rgb(rgb: Tuple[int, int, int], factor: float = 0.4) -> Tuple[int, int, int]:
    return tuple(max(0, int(c * factor)) for c in rgb)  # type: ignore



class SyncRenderer:
    LYRIC_COLOR_HEX = "#03fcf8"

    def __init__(self, art_lines: List[str], lyric_col: int, lyric_start_row: int,
                 context_size: int = 4):
        self.art_lines = art_lines
        self.lyric_col = lyric_col
        self.lyric_start_row = lyric_start_row
        self.context_size = context_size

        active_rgb = hex_to_rgb(self.LYRIC_COLOR_HEX)
        inactive_rgb = dim_rgb(active_rgb)
        self.style_active = rgb_to_ansi(active_rgb, bold=True)
        self.style_inactive = rgb_to_ansi(inactive_rgb, bold=False)
        self.style_reset = "\x1b[0m"

    def draw_static_art(self):
        os.system("cls" if os.name == "nt" else "clear")
        sys.stdout.write("\x1b[H")
        sys.stdout.write("\n".join(self.art_lines))
        sys.stdout.flush()

    def draw_lyrics(self, context: List[str], active_index: int):
        for i in range(self.context_size):
            row = self.lyric_start_row + i
            text = context[i] if i < len(context) else ""
            style = self.style_active if i == active_index else self.style_inactive
            padding = " " * 40
            sys.stdout.write(f"\x1b[{row};{self.lyric_col}H{style}{text}{padding}{self.style_reset}")
        sys.stdout.flush()

    def print_status(self, message: str):
        bottom_row = max(len(self.art_lines), self.lyric_start_row + self.context_size) + 2
        sys.stdout.write(f"\x1b[{bottom_row};1H\x1b[J")
        sys.stdout.write(message + "\n")
        sys.stdout.flush()



def start_audio(path: str):

    try:
        import pygame
        pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        return ("pygame", pygame.mixer)
    except Exception:
        pass
        
    ffplay_path = shutil.which("ffplay")
    if ffplay_path:
        proc = subprocess.Popen(
            [ffplay_path, "-nodisp", "-autoexit", "-loglevel", "quiet", path],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return ("ffplay", proc)

    print("[audio dilewati] tidak ada backend audio yang tersedia "
          "(install pygame-ce, atau ffmpeg untuk ffplay)", file=sys.stderr)
    return (None, None)


def audio_still_playing(handle) -> bool:
    backend, obj = handle
    if backend == "pygame":
        return obj.music.get_busy()
    if backend == "ffplay":
        return obj.poll() is None 
    return False



def run(lrc_path: str, art_path: str, audio_path: Optional[str] = None,
        lyric_col: int = 53, lyric_start_row: int = 8):

    audio_handle = start_audio(audio_path) if audio_path else (None, None)
    start = time.perf_counter()

    lyrics = parse_lrc(lrc_path)
    art = load_art(art_path)
    renderer = SyncRenderer(art, lyric_col, lyric_start_row)
    renderer.draw_static_art()

    shown_index = -1

    while True:
        elapsed = time.perf_counter() - start

        next_index = shown_index
        while next_index + 1 < len(lyrics) and lyrics[next_index + 1].time_sec <= elapsed:
            next_index += 1

        if next_index != shown_index:
            shown_index = next_index
            lo = max(0, shown_index - 1)
            hi = min(len(lyrics), lo + renderer.context_size)
            context = [lyrics[i].text for i in range(lo, hi)]
            renderer.draw_lyrics(context, active_index=shown_index - lo)

        lyrics_done = shown_index >= len(lyrics) - 1

        if audio_path:
            if lyrics_done and not audio_still_playing(audio_handle):
                break
        else:
            if lyrics_done:
                break

        time.sleep(0.01)

    renderer.print_status("[selesai]")


if __name__ == "__main__":
    # https://github.com/stanislausd
    run(
        lrc_path="lyrics.lrc",
        art_path="ascii.txt",
        audio_path="jane.mp3",
        lyric_col=53,
        lyric_start_row=8,
    )
