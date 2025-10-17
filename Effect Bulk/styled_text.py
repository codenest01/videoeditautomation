import cv2
import random
import os
import json

# -----------------------------
# JSON persistence
# -----------------------------
USAGE_FILE = os.path.join(os.path.dirname(__file__), "style_usage.json")

def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"video_map": {}}
    return {"video_map": {}}

def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

USAGE_DATA = load_usage()

# -----------------------------
# Fonts & color utilities
# -----------------------------
FONT_CHOICES = [
    cv2.FONT_HERSHEY_SIMPLEX,
    cv2.FONT_HERSHEY_DUPLEX,
    cv2.FONT_HERSHEY_COMPLEX,
    cv2.FONT_HERSHEY_SCRIPT_COMPLEX
]

def get_random_color():
    """Generates a random bright BGR color."""
    return (
        random.randint(50, 255),
        random.randint(50, 255),
        random.randint(50, 255),
    )

# -----------------------------
# Core drawing function
# -----------------------------
def draw_styled_text(
    frame,
    text,
    font=cv2.FONT_HERSHEY_DUPLEX,
    scale=1.5,
    thickness=2,
    color=(255, 255, 255),
    outline_color=(0, 0, 0),
    x_offset=0,
    y_from_bottom=100,
):
    text_size, _ = cv2.getTextSize(text, font, scale, thickness)
    text_w, text_h = text_size
    H, W = frame.shape[:2]

    pos_y = H - y_from_bottom
    pos_x = W // 2 - text_w // 2 + x_offset
    pos = (pos_x, pos_y)

    # Shadow
    cv2.putText(
        frame,
        text,
        (pos[0] + 3, pos[1] + 3),
        font,
        scale,
        outline_color,
        thickness + 4,
        cv2.LINE_AA,
    )
    # Main text
    cv2.putText(
        frame,
        text,
        pos,
        font,
        scale,
        color,
        thickness,
        cv2.LINE_AA,
    )

    return frame

# -----------------------------
# Style picker with JSON memory
# -----------------------------
def pick_style_for_video(video_id):
    if video_id in USAGE_DATA["video_map"]:
        return USAGE_DATA["video_map"][video_id]

    chosen = {
        "font": random.choice(FONT_CHOICES),
        "color": get_random_color(),
        "scale": round(random.uniform(1.2, 1.8), 2),
        "thickness": random.randint(2, 3),
        "outline": (0, 0, 0),
    }

    USAGE_DATA["video_map"][video_id] = chosen
    save_usage(USAGE_DATA)
    return chosen

# -----------------------------
# Main effect function
# -----------------------------
def apply_effect_frame(frame, audio_name="Unknown", video_id="default", **kwargs):
    style = pick_style_for_video(video_id)
    frame = draw_styled_text(
        frame,
        audio_name.upper(),
        font=style["font"],
        scale=style["scale"],
        thickness=style["thickness"],
        color=tuple(style["color"]),
        outline_color=tuple(style["outline"]),
        y_from_bottom=80,
    )
    return frame
