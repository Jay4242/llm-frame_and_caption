import json
import os
from dataclasses import dataclass, field


CONFIG_DIR = os.path.expanduser("~/.config/frame_and_caption")
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")


@dataclass
class APIConfig:
    base_url: str = "http://localhost:1234/v1"
    api_key: str = "not-needed"
    model: str = ""


@dataclass
class FrameConfig:
    color: str = "#1a1a2e"
    thickness: int = 80
    headline: str = ""
    font_size: int = 36
    caption_font_size: int = 32
    gradient_enabled: bool = False
    gradient_color2: str = "#e94560"
    gradient_direction: str = "horizontal"


@dataclass
class Config:
    api: APIConfig = field(default_factory=APIConfig)
    frame: FrameConfig = field(default_factory=FrameConfig)
    prompt: str = "You are a helpful assistant. Describe this image concisely in a brief, engaging caption."


def load_config() -> Config:
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                data = json.load(f)
            api_data = data.get("api", {})
            frame_data = data.get("frame", {})
            config = Config(
                api=APIConfig(
                    base_url=api_data.get("base_url", APIConfig.base_url),
                    api_key=api_data.get("api_key", APIConfig.api_key),
                    model=api_data.get("model", APIConfig.model),
                ),
                frame=FrameConfig(
                    color=frame_data.get("color", FrameConfig.color),
                    thickness=frame_data.get("thickness", FrameConfig.thickness),
                    headline=frame_data.get("headline", FrameConfig.headline),
                    font_size=frame_data.get("font_size", FrameConfig.font_size),
                    caption_font_size=frame_data.get("caption_font_size", FrameConfig.caption_font_size),
                    gradient_enabled=frame_data.get("gradient_enabled", FrameConfig.gradient_enabled),
                    gradient_color2=frame_data.get("gradient_color2", FrameConfig.gradient_color2),
                    gradient_direction=frame_data.get("gradient_direction", FrameConfig.gradient_direction),
                ),
                prompt=data.get("prompt", Config.prompt),
            )
            return config
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return Config()


def save_config(config: Config) -> None:
    os.makedirs(CONFIG_DIR, exist_ok=True)
    data = {
        "api": {
            "base_url": config.api.base_url,
            "api_key": config.api.api_key,
            "model": config.api.model,
        },
        "frame": {
            "color": config.frame.color,
            "thickness": config.frame.thickness,
            "headline": config.frame.headline,
            "font_size": config.frame.font_size,
            "caption_font_size": config.frame.caption_font_size,
            "gradient_enabled": config.frame.gradient_enabled,
            "gradient_color2": config.frame.gradient_color2,
            "gradient_direction": config.frame.gradient_direction,
        },
        "prompt": config.prompt,
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=2)
