# Frame & Caption

A Python desktop app that frames images with decorative borders and AI-generated captions using any OpenAI-compatible LLM API (local or remote).

## Features

- Select images via file dialog or **drag-and-drop**
- Send images to any **OpenAI-compatible API** (LM Studio, llama.cpp server, Ollama, etc.) — images stay local
- LLM returns a JSON `{"Caption": "..."}` response that gets rendered on the image
- Renders a **colored border frame** around the image with configurable:
  - Frame color (color picker)
  - Border thickness
  - **Headline text** in the top frame band (e.g. "Class of 2026!")
  - Font size
- **Live preview** updates as you tweak settings
- Settings persisted to `~/.config/frame_and_caption/settings.json`

## Requirements

- Python 3.10+
- A vision-capable LLM served behind an OpenAI-compatible endpoint

## Setup

```bash
# Clone and set up
git clone https://github.com/Jay4242/llm-frame_and_caption.git
cd frame_and_caption

# Create venv and install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run
python -m frame_and_caption
```

## Usage

1. **Configure your API** in the left panel:
   - Base URL — e.g. `http://localhost:1234/v1` (LM Studio default)
   - API Key — `not-needed` for most local servers
   - Model — e.g. `llama-3.2-vision`, `minicpm-v`, `qwen2-vl`
   - Click **Test Connection** to verify

2. **Load an image** — drag-and-drop onto the dashed area or click **Browse**

3. **Set your frame** — pick a color, thickness, headline text, and font size

4. **Write or edit the system prompt** — the LLM **must** return JSON with a `Caption` field. Default:
   ```
   You are a helpful assistant. Describe this image concisely
   in a brief, engaging caption. Respond with a JSON object
   containing a single key 'Caption' with your caption text.
   ```

5. **Generate Caption** — sends the image to your LLM and renders the result in the frame preview

6. **Save Framed Image** — exports the finished image as PNG

## Dependencies

| Package | Purpose |
|---------|---------|
| [customtkinter](https://github.com/TomSchimansky/CustomTkinter) | Modern-looking UI |
| [Pillow](https://python-pillow.org/) | Image processing and frame compositing |
| [openai](https://github.com/openai/openai-python) | API client for any OpenAI-compatible endpoint |
| [tkinterdnd2](https://github.com/ElmGonalves/tkinterDnD) | Drag-and-drop file support |

## Project Structure

```
frame_and_caption/
├── frame_and_caption/
│   ├── __main__.py           # Entry point
│   ├── app.py                # Root window setup
│   ├── config.py             # Settings persistence
│   ├── api_client.py         # LLM API communication
│   ├── image_processor.py    # Frame + text compositing
│   └── ui/
│       ├── main_window.py    # Full app layout
│       ├── drop_zone.py      # Drag-and-drop / file browse
│       ├── api_panel.py      # API configuration inputs
│       ├── frame_panel.py    # Frame style controls
│       └── prompt_panel.py   # LLM prompt editor
├── requirements.txt
└── pyproject.toml
```

## License

MIT
