import cv2
import os
import imageio
import random
import json

# -----------------------------
# CONFIG
# -----------------------------
GIF_FOLDER = r"C:\Users\Mr_robot\Desktop\videoeditautomation\SubscribeEmoji"
USAGE_FILE = os.path.join(GIF_FOLDER, "gif_usage.json")
VIDEO_WIDTH = 1280
TARGET_RATIO = 0.25

# -----------------------------
# Load & preprocess GIFs
# -----------------------------
def load_gifs(folder, video_width, ratio=0.25):
    gifs = {}
    if not os.path.exists(folder):
        print(f"⚠️ GIF folder not found: {folder}")
        return gifs

    for file in os.listdir(folder):
        if not file.lower().endswith(".gif"):
            continue

        path = os.path.join(folder, file)
        try:
            gif_reader = imageio.get_reader(path)
            frames_raw = [frame for frame in gif_reader]

            target_width = int(video_width * ratio)
            frames = []
            for frame in frames_raw:
                frame_rgba = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGRA)
                scale = target_width / frame_rgba.shape[1]
                target_height = int(frame_rgba.shape[0] * scale)
                resized = cv2.resize(frame_rgba, (target_width, target_height), interpolation=cv2.INTER_LANCZOS4)
                frames.append(resized)

            gifs[file] = frames
        except Exception as e:
            print(f"❌ Failed to load {file}: {e}")

    return gifs

ALL_GIFS = load_gifs(GIF_FOLDER, VIDEO_WIDTH, TARGET_RATIO)

# -----------------------------
# JSON usage persistence
# -----------------------------
def load_usage():
    if os.path.exists(USAGE_FILE):
        try:
            with open(USAGE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"used": [], "video_map": {}}
    return {"used": [], "video_map": {}}

def save_usage(data):
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)

USAGE_DATA = load_usage()

# -----------------------------
# Pick GIF fairly
# -----------------------------
def pick_gif_for_video(video_id):
    # If video already has an assigned GIF, return it
    if video_id in USAGE_DATA["video_map"]:
        gif_name = USAGE_DATA["video_map"][video_id]
        return ALL_GIFS.get(gif_name, random.choice(list(ALL_GIFS.values())))

    all_names = list(ALL_GIFS.keys())
    used_names = set(USAGE_DATA["used"])

    # Reset if all used
    if len(used_names) >= len(all_names):
        USAGE_DATA["used"] = []
        used_names = set()

    # Available choices
    available = [g for g in all_names if g not in used_names]
    if not available:
        available = all_names  # fallback

    chosen_name = random.choice(available)
    USAGE_DATA["used"].append(chosen_name)
    USAGE_DATA["video_map"][video_id] = chosen_name
    save_usage(USAGE_DATA)

    return ALL_GIFS[chosen_name]

# -----------------------------
# Overlay helper
# -----------------------------
def overlay_frame(background, overlay, x, y):
    h, w = overlay.shape[:2]
    if y + h > background.shape[0] or x + w > background.shape[1]:
        return
    alpha_s = overlay[:, :, 3] / 255.0
    alpha_l = 1.0 - alpha_s
    for c in range(3):
        background[y:y+h, x:x+w, c] = (
            alpha_s * overlay[:, :, c] +
            alpha_l * background[y:y+h, x:x+w, c]
        )

# -----------------------------
# Main effect
# -----------------------------
def apply_effect_frame(frame, frame_idx, fps=30, video_id="default"):
    if not ALL_GIFS:
        return frame

    gif_frames = pick_gif_for_video(video_id)
    total_frames = len(gif_frames)

    # Show GIF between 1s → 5s
    start_time = 1.0
    duration = 5.0
    elapsed = frame_idx / fps

    if elapsed < start_time:
        return frame

    gif_elapsed = elapsed - start_time
    gif_idx = int((gif_elapsed / duration) * total_frames)
    if gif_idx >= total_frames:
        return frame

    gif_frame = gif_frames[gif_idx]

    # Bottom-right with padding
    x = frame.shape[1] - gif_frame.shape[1] - 12
    y = frame.shape[0] - gif_frame.shape[0] - 12
    overlay_frame(frame, gif_frame, x, y)

    return frame
