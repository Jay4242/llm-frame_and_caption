# AGENTS.md

## Project

Frame & Caption — Python GUI app that sends an image to an OpenAI-compatible LLM for a caption, then renders a decorative border frame with headline text and the caption around the image.

## Run

```bash
source .venv/bin/activate
python -m frame_and_caption
```

## Architecture

Single-package (`frame_and_caption/`), no monorepo:

| File | Role |
|---|---|
| `__main__.py` | Entry point, delegates to `app.main()` |
| `app.py` | Creates root window (`TkinterDnD.Tk`, **not** `tkinter.Tk`) |
| `config.py` | Settings persistence + dataclasses |
| `api_client.py` | LLM chat completions + caption extraction |
| `image_processor.py` | Frame composite + text rendering |
| `ui/main_window.py` | Main layout wiring |
| `ui/api_panel.py` | API config fields + Test Connection |
| `ui/frame_panel.py` | Frame color/thickness/headline/font-size controls |
| `ui/drop_zone.py` | Drag-and-drop / file browse |
| `ui/prompt_panel.py` | System prompt editor |

## Gotchas

- Root widget must be `TkinterDnD.Tk()` (from `tkinterdnd2`), not plain `tkinter.Tk`, or drag-and-drop breaks.
- The API client first tries `response_format={"type": "json_object"}`; if the endpoint rejects it, it silently retries without that param. Many local LLM servers don't support it.
- Images are resized to max 1024px before base64 encoding for the API call.
- The LLM response is parsed for a `Caption` key — first as JSON, then via regex fallback.
- Settings live at `~/.config/frame_and_caption/settings.json`.

## Fonts

A hardcoded fallback chain is tried in order (Linux → macOS → Windows). If none are found, Pillow's default bitmap font is used. The chain lives in `image_processor.py:_FONT_CANDIDATES`.

## Dependencies

customtkinter, Pillow, openai, tkinterdnd2 — see `pyproject.toml` or `requirements.txt`.

## Git

- Commit after each meaningful chunk of progress.
- Write concise, descriptive commit messages.
