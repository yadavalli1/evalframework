"""Build video/paper_review.mp4: render slides with Chromium, narrate with Kokoro TTS, stitch with ffmpeg.

Requires: pip install playwright kokoro-onnx soundfile; ffmpeg; Kokoro model files
(kokoro-v1.0.int8.onnx, voices-v1.0.bin from github.com/thewh1teagle/kokoro-onnx releases) in $KOKORO_DIR.
"""
import os, re, subprocess, sys, soundfile as sf
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
VID = ROOT / "video"; BUILD = VID / "build"; BUILD.mkdir(exist_ok=True)
sys.path.insert(0, str(VID))
from slides import SLIDES

CSS = """
*{box-sizing:border-box} body{margin:0;width:1920px;height:1080px;background:#fcfcfb;color:#0b0b0b;
 font-family:'DejaVu Sans',sans-serif;padding:90px 130px 110px;position:relative;overflow:hidden}
body:before{content:"";position:absolute;left:0;top:0;width:100%;height:10px;background:linear-gradient(90deg,#2a78d6,#eb6834,#1baf7a)}
h1{font-size:64px;margin:0 0 44px;letter-spacing:-1px} h3{font-size:36px;margin:0 0 14px}
ul,ol{font-size:38px;line-height:1.45;margin:0;padding-left:50px} li{margin-bottom:16px}
b{color:#1f5fae} .good{color:#127a55} .warn{color:#b8471b}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:60px} .grid2 ul{font-size:34px}
.split{display:grid;grid-template-columns:1.1fr 1fr;gap:50px;align-items:center} .split ul{font-size:32px}
.fig{text-align:center} .fig img{max-width:100%;max-height:640px;border-radius:10px} .cap{font-size:22px;color:#52514e;margin:8px 0}
.stat{font-size:36px;text-align:center;margin-top:18px}
.note{font-size:30px;color:#52514e;margin-top:40px;border-left:6px solid #2a78d6;padding-left:22px}
.ladder li{padding-left:10px} .big{font-size:42px}
.svgwrap svg{width:100%;margin-top:40px}
.title{display:flex;flex-direction:column;justify-content:center;height:100%}
.title h1{font-size:92px;line-height:1.1;margin-bottom:24px} .title h2{font-size:52px;color:#52514e;font-weight:normal;margin:0 0 60px}
.kicker{font-size:30px;text-transform:uppercase;letter-spacing:6px;color:#eb6834;margin:0 0 24px;font-weight:bold}
.meta{font-size:30px;color:#52514e}
.foot{position:absolute;bottom:40px;left:130px;right:130px;display:flex;justify-content:space-between;font-size:22px;color:#8a8984}
code{font-family:'DejaVu Sans Mono',monospace;font-size:.9em}
"""
CHROME = str(next(Path("/opt/pw-browsers").glob("chromium-*/chrome-linux*/chrome"))) if Path("/opt/pw-browsers").exists() else None

def render_slides():
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME)
        pg = b.new_page(viewport={"width": 1920, "height": 1080})
        for i, (body, _) in enumerate(SLIDES, 1):
            foot = f'<div class="foot"><span>Review · Building an LLM Evaluation Framework</span><span>{i} / {len(SLIDES)}</span></div>'
            html = BUILD / f"s{i:02d}.html"
            html.write_text(f"<!doctype html><html><head><meta charset=utf-8><style>{CSS}</style></head><body>{body}{foot if i > 1 else ''}</body></html>")
            pg.goto(html.as_uri()); pg.wait_for_timeout(150)
            pg.screenshot(path=str(BUILD / f"s{i:02d}.png"))
        b.close()

def narrate():
    from kokoro_onnx import Kokoro
    kd = os.environ.get("KOKORO_DIR", ".")
    k = Kokoro(f"{kd}/kokoro-v1.0.int8.onnx", f"{kd}/voices-v1.0.bin")
    durs = []
    for i, (_, text) in enumerate(SLIDES, 1):
        out = BUILD / f"s{i:02d}.wav"
        if not out.exists():
            audio, sr = k.create(text, voice="am_michael", speed=1.0, lang="en-us")
            sf.write(out, audio, sr)
        durs.append(sf.info(out).duration)
    return durs

def srt(durs, lead=0.6, tail=0.9):
    def ts(t): h, r = divmod(t, 3600); m, s = divmod(r, 60); return f"{int(h):02d}:{int(m):02d}:{int(s):02d},{int((s%1)*1000):03d}"
    lines, t0, n = [], 0.0, 1
    for (_, text), d in zip(SLIDES, durs):
        sents = [s for s in re.split(r"(?<=[.!?])\s+", text.replace(" I Ds", " IDs").replace("L L M", "LLM").replace(" I D", " ID").replace("C I ", "CI ")) if s]
        tot = sum(len(s) for s in sents); t = t0 + lead
        for s in sents:
            dt = d * len(s) / tot
            lines.append(f"{n}\n{ts(t)} --> {ts(t+dt)}\n{s}\n"); n += 1; t += dt
        t0 += lead + d + tail
    (VID / "paper_review.srt").write_text("\n".join(lines))

def stitch(durs, lead=0.6, tail=0.9):
    parts = []
    for i, d in enumerate(durs, 1):
        seg = BUILD / f"seg{i:02d}.mp4"; T = lead + d + tail
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", str(BUILD / f"s{i:02d}.png"),
            "-i", str(BUILD / f"s{i:02d}.wav"), "-filter_complex",
            f"[0:v]fade=t=in:st=0:d=0.35,fade=t=out:st={T-0.35:.2f}:d=0.35,format=yuv420p[v];[1:a]adelay={int(lead*1000)}:all=1,apad,aresample=48000[a]",
            "-map", "[v]", "-map", "[a]", "-t", f"{T:.2f}", "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-tune", "stillimage", "-c:a", "aac", "-b:a", "160k", "-ac", "2", str(seg)], check=True)
        parts.append(seg)
    lst = BUILD / "list.txt"; lst.write_text("".join(f"file '{p}'\n" for p in parts))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(VID / "paper_review.mp4")], check=True)

if __name__ == "__main__":
    render_slides(); durs = narrate(); srt(durs); stitch(durs)
    print(f"wrote {VID/'paper_review.mp4'} ({sum(durs)+1.5*len(durs):.0f}s)")
