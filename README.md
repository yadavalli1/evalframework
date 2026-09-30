# evalframework

Research and design notes for building an LLM evaluation framework.

| Deliverable | Path |
|---|---|
| Research paper (PDF) | [`paper/paper.pdf`](paper/paper.pdf) |
| Paper source (Markdown) | [`paper/paper.md`](paper/paper.md) |
| Narrated review video (MP4, 1080p) | [`video/paper_review.mp4`](video/paper_review.mp4) |
| Video subtitles | [`video/paper_review.srt`](video/paper_review.srt) |

**Paper:** *Building an LLM Evaluation Framework: Architecture, Statistics, and Practice.* It covers a
seven-component reference architecture, the statistics a framework should build in (CIs, paired tests,
clustered SEs, power analysis), calibrating LLM-as-judge, contamination, RAG and agent evals, and CI gating.
Every figure is analytic or a seeded simulation. No benchmark results for real models are reported.

## Rebuilding

```bash
pip install numpy matplotlib markdown playwright kokoro-onnx soundfile
python3 scripts/make_figures.py      # paper/figures/*.png
python3 scripts/build_paper.py       # paper/paper.html, paper/paper.pdf (headless Chromium)
# Kokoro voice files from https://github.com/thewh1teagle/kokoro-onnx/releases (model-files-v1.0):
#   kokoro-v1.0.int8.onnx, voices-v1.0.bin
KOKORO_DIR=/path/to/kokoro python3 scripts/build_video.py   # video/paper_review.mp4 (needs ffmpeg)
```

Video slide content and narration live in [`video/slides.py`](video/slides.py).
