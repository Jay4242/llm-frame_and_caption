import base64
import io
import json
import re
import sys
from typing import Callable, Optional

from openai import OpenAI
from PIL import Image

from .config import APIConfig, FaceEntry

StreamCallback = Callable[[str, str], None]


def _encode_pil(img: Image.Image) -> str:
    if img.mode not in ("RGB", "RGBA"):
        img = img.convert("RGB")
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _encode_image(image_data: bytes) -> str:
    img = Image.open(io.BytesIO(image_data))
    return _encode_pil(img)


def _extract_caption(content: str) -> str:
    try:
        parsed = json.loads(content)
        if isinstance(parsed, dict) and "Caption" in parsed:
            return parsed["Caption"]
        return content
    except (json.JSONDecodeError, TypeError):
        pass

    match = re.search(r'"Caption"\s*:\s*"([^"]*)"', content)
    if match:
        return match.group(1)

    return content.strip()


def generate_caption(
    image_path: str,
    prompt: str,
    api_config: APIConfig,
    on_stream: Optional[StreamCallback] = None,
    faces: Optional[list[FaceEntry]] = None,
) -> str:
    with open(image_path, "rb") as f:
        image_data = f.read()

    b64_image = _encode_image(image_data)
    data_uri = f"data:image/jpeg;base64,{b64_image}"

    messages: list[dict] = [{"role": "system", "content": prompt}]

    if faces:
        source_img = Image.open(io.BytesIO(image_data))
        for face in faces:
            crop = source_img.crop((face.x1, face.y1, face.x2, face.y2))
            face_b64 = _encode_pil(crop)
            face_data_uri = f"data:image/jpeg;base64,{face_b64}"
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": f"The following person is {face.name}:"},
                    {"type": "image_url", "image_url": {"url": face_data_uri}},
                ],
            })

    messages.append({
        "role": "user",
        "content": [
            {"type": "text", "text": "The following is the image to caption:"},
            {"type": "image_url", "image_url": {"url": data_uri}},
        ],
    })

    client = OpenAI(base_url=api_config.base_url, api_key=api_config.api_key, timeout=2400)

    kwargs = dict(
        model=api_config.model,
        stream=True,
        stream_options={"include_usage": True},
        messages=messages,
    )

    try:
        kwargs["response_format"] = {"type": "json_object"}
        stream = client.chat.completions.create(**kwargs)
    except Exception:
        del kwargs["response_format"]
        stream = client.chat.completions.create(**kwargs)

    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    finish_reason = None

    for chunk in stream:
        if not chunk.choices:
            if hasattr(chunk, "usage"):
                print(f"[DEBUG] LLM usage: {chunk.usage}", file=sys.stderr)
            continue

        delta = chunk.choices[0].delta
        finish_reason = chunk.choices[0].finish_reason or finish_reason

        reasoning = getattr(delta, "reasoning_content", None)
        if reasoning:
            reasoning_parts.append(reasoning)
            print(reasoning, end="", flush=True)
            if on_stream:
                on_stream("reasoning", reasoning)

        content_token = delta.content
        if content_token:
            content_parts.append(content_token)
            print(content_token, end="", flush=True)
            if on_stream:
                on_stream("content", content_token)

    print()

    content = "".join(content_parts)
    reasoning = "".join(reasoning_parts)

    print(f"\n[DEBUG] LLM finish_reason: {finish_reason}", file=sys.stderr)
    if reasoning:
        print(f"[DEBUG] LLM reasoning_content: {reasoning[:200]}...", file=sys.stderr)
    print(f"[DEBUG] LLM content: {content}", file=sys.stderr)
    if not content and reasoning:
        content = reasoning
        print("[DEBUG] Falling back to reasoning_content as content was empty", file=sys.stderr)
    caption = _extract_caption(content)
    print(f"[DEBUG] Extracted caption: {caption}", file=sys.stderr)
    return caption
