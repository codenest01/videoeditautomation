import cv2
import numpy as np
import math
import random
import os
import json

# -----------------------
# Base effect templates
# -----------------------

def effect_wave(frame, frame_idx, amp, freq):
    rows, cols, _ = frame.shape
    shift = amp * math.sin(frame_idx * freq)
    M = np.float32([[1, 0, shift], [0, 1, 0]])
    return cv2.warpAffine(frame, M, (cols, rows))

def effect_zoom(frame, frame_idx, strength, speed):
    h, w, _ = frame.shape
    scale = 1 + strength * math.sin(frame_idx * speed)
    M = cv2.getRotationMatrix2D((w/2, h/2), 0, scale)
    return cv2.warpAffine(frame, M, (w, h))

def effect_fade(frame, frame_idx, min_alpha, max_alpha, speed):
    alpha = min_alpha + (max_alpha - min_alpha) * (0.5 + 0.5 * math.sin(frame_idx * speed))
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=0)

def effect_shake(frame, frame_idx, dx, dy, speed):
    rows, cols, _ = frame.shape
    x = int(dx * math.sin(frame_idx * speed))
    y = int(dy * math.cos(frame_idx * speed))
    M = np.float32([[1, 0, x], [0, 1, y]])
    return cv2.warpAffine(frame, M, (cols, rows))

def effect_blur_pulse(frame, frame_idx, max_k, speed):
    k = int(abs(max_k * math.sin(frame_idx * speed))) * 2 + 1
    return cv2.GaussianBlur(frame, (k, k), 0)

# -----------------------
# Persistent unique effects
# -----------------------

USED_EFFECTS_FILE = "used_effects.json"

# Load used effects if file exists
if os.path.exists(USED_EFFECTS_FILE):
    with open(USED_EFFECTS_FILE, "r") as f:
        used_effects = set(tuple(x) for x in json.load(f))
else:
    used_effects = set()

def save_used_effects():
    """Save used effects to disk after each video"""
    with open(USED_EFFECTS_FILE, "w") as f:
        json.dump([list(x) for x in used_effects], f)

def choose_unique_effect():
    while True:
        choice = random.choice(["wave", "zoom", "fade", "shake", "blur"])

        if choice == "wave":
            amp = round(random.uniform(3, 15), 3)
            freq = round(random.uniform(0.01, 0.1), 4)
            sig = ("wave", amp, freq)
            if sig not in used_effects:
                used_effects.add(sig)
                return lambda f, i: effect_wave(f, i, amp, freq)

        elif choice == "zoom":
            strength = round(random.uniform(0.002, 0.02), 4)
            speed = round(random.uniform(0.01, 0.1), 4)
            sig = ("zoom", strength, speed)
            if sig not in used_effects:
                used_effects.add(sig)
                return lambda f, i: effect_zoom(f, i, strength, speed)

        elif choice == "fade":
            min_alpha = round(random.uniform(0.6, 0.8), 3)
            max_alpha = round(random.uniform(1.0, 1.3), 3)
            speed = round(random.uniform(0.01, 0.05), 4)
            sig = ("fade", min_alpha, max_alpha, speed)
            if sig not in used_effects:
                used_effects.add(sig)
                return lambda f, i: effect_fade(f, i, min_alpha, max_alpha, speed)

        elif choice == "shake":
            dx = round(random.uniform(1, 5), 2)
            dy = round(random.uniform(1, 5), 2)
            speed = round(random.uniform(0.1, 0.5), 3)
            sig = ("shake", dx, dy, speed)
            if sig not in used_effects:
                used_effects.add(sig)
                return lambda f, i: effect_shake(f, i, dx, dy, speed)

        elif choice == "blur":
            max_k = random.randint(3, 7)
            speed = round(random.uniform(0.01, 0.1), 4)
            sig = ("blur", max_k, speed)
            if sig not in used_effects:
                used_effects.add(sig)
                return lambda f, i: effect_blur_pulse(f, i, max_k, speed)

# -----------------------
# Video processing
# -----------------------

def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    if not cap.isOpened():
        print(f"❌ Could not open {input_path}")
        return

    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 👉 unique effect for this video
    effect_fn = choose_unique_effect()

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        effected = effect_fn(frame, frame_idx)
        out.write(effected)
        frame_idx += 1

    cap.release()
    out.release()
    save_used_effects()  # ✅ save after finishing video
    print(f"✅ Processed {input_path} -> {output_path}")

# -----------------------
# Batch runner
# -----------------------

input_folder = "output"   # your folder with videos
output_folder = "output"  # save back into same folder

for file in os.listdir(input_folder):
    if file.endswith(".mp4") and not file.endswith("_effect.mp4"):
        in_path = os.path.join(input_folder, file)
        out_name = file.replace(".mp4", "_effect.mp4")
        out_path = os.path.join(output_folder, out_name)
        process_video(in_path, out_path)
