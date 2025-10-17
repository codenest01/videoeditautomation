import cv2
import numpy as np
import os
import json
import random

# -----------------------------
# CONFIGURATION
# -----------------------------
PARTICLE_USAGE_FILE = r"C:\Users\Mr_robot\Desktop\videoeditautomation\particle_usage.json"

ALPHA = 0.6  # blending opacity

# 10 unique particle presets
PARTICLE_PRESETS = {
    "blue_wave":    {"num_particles": 100, "speed": 1.0, "size": 2, "color": (100, 150, 255)},
    "red_flare":    {"num_particles": 80,  "speed": 1.5, "size": 3, "color": (255, 80, 80)},
    "green_spark":  {"num_particles": 120, "speed": 0.8, "size": 2, "color": (80, 255, 100)},
    "purple_glow":  {"num_particles": 90,  "speed": 1.2, "size": 3, "color": (180, 80, 255)},
    "gold_trail":   {"num_particles": 70,  "speed": 1.0, "size": 4, "color": (255, 215, 0)},
    "cyan_ripple":  {"num_particles": 110, "speed": 0.9, "size": 2, "color": (0, 255, 255)},
    "pink_drift":   {"num_particles": 85,  "speed": 1.3, "size": 3, "color": (255, 100, 255)},
    "orange_burst": {"num_particles": 95,  "speed": 1.1, "size": 3, "color": (255, 165, 0)},
    "white_flash":  {"num_particles": 105, "speed": 1.0, "size": 2, "color": (255, 255, 255)},
    "teal_wave":    {"num_particles": 100, "speed": 1.2, "size": 2, "color": (0, 128, 128)},
}

# -----------------------------
# JSON USAGE FUNCTIONS
# -----------------------------
def load_particle_usage():
    default_data = {"video_map": {}, "video_counter": 0}
    if os.path.exists(PARTICLE_USAGE_FILE):
        try:
            with open(PARTICLE_USAGE_FILE, "r") as f:
                data = json.load(f)
                if "video_counter" not in data:
                    data["video_counter"] = 0
                return data
        except Exception:
            return default_data
    return default_data

def save_particle_usage(data):
    try:
        with open(PARTICLE_USAGE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"❌ Error saving particle usage JSON: {e}")

USAGE_DATA = load_particle_usage()

# -----------------------------
# Global State
# -----------------------------
particles = None
WIDTH = None
HEIGHT = None
current_config = None

# -----------------------------
# Preset assignment per video
# -----------------------------
def get_video_particle_config(video_id):
    global USAGE_DATA

    # Already assigned
    if video_id in USAGE_DATA["video_map"]:
        preset_name = USAGE_DATA["video_map"][video_id]
        return PARTICLE_PRESETS[preset_name]

    # Reset after 10 videos
    if USAGE_DATA["video_counter"] >= 10:
        USAGE_DATA["video_map"] = {}
        USAGE_DATA["video_counter"] = 0

    all_presets = list(PARTICLE_PRESETS.keys())
    usage_counts = {p: 0 for p in all_presets}
    for p in USAGE_DATA["video_map"].values():
        if p in usage_counts:
            usage_counts[p] += 1

    available = [p for p, count in usage_counts.items() if count < 1]  # unique per cycle
    chosen_name = random.choice(available)

    USAGE_DATA["video_map"][video_id] = chosen_name
    USAGE_DATA["video_counter"] += 1
    save_particle_usage(USAGE_DATA)

    return PARTICLE_PRESETS[chosen_name]

# -----------------------------
# Particle Initialization
# -----------------------------
def init_particles(width, height, config, seed=42):
    global particles, WIDTH, HEIGHT, current_config
    WIDTH, HEIGHT = width, height
    current_config = config

    num_particles = config["num_particles"]
    max_speed = config["speed"]

    np.random.seed(seed)
    particles = np.zeros(num_particles, dtype=[('x', float), 
                                               ('y', float), 
                                               ('size', float), 
                                               ('speed', float),
                                               ('vx', float),
                                               ('vy', float)])
    particles['x'] = np.random.uniform(0, WIDTH, num_particles)
    particles['y'] = np.random.uniform(0, HEIGHT, num_particles)
    particles['size'] = np.random.uniform(1, config['size'], num_particles)
    particles['speed'] = np.random.uniform(0.5, max_speed, num_particles)
    angle = np.random.uniform(0, 2*np.pi, num_particles)
    particles['vx'] = np.cos(angle) * particles['speed']
    particles['vy'] = np.sin(angle) * particles['speed']

# -----------------------------
# Frame Effect
# -----------------------------
def apply_effect_frame(frame, frame_idx=0, fps=30, video_id="default"):
    global particles, WIDTH, HEIGHT, current_config

    h, w = frame.shape[:2]

    config = get_video_particle_config(video_id)
    if particles is None or config != current_config:
        seed_value = int(video_id.replace('-', ''), 16) if video_id.replace('-', '').isalnum() else 42
        init_particles(w, h, config, seed=seed_value)

    layer = np.zeros_like(frame, dtype=np.float32)

    # Convert color to integer tuple for OpenCV
    color_tuple = tuple(int(c) for c in config['color'])

    # Draw particles
    xs = particles['x'].astype(np.int32)
    ys = particles['y'].astype(np.int32)
    sizes = np.maximum(1, np.round(particles['size']).astype(np.int32))

    for x, y, s in zip(xs, ys, sizes):
        if 0 <= x < WIDTH and 0 <= y < HEIGHT:
            cv2.circle(layer, (x, y), s, color_tuple, -1)

    # Update particle positions
    particles['x'] += particles['vx']
    particles['y'] += particles['vy']

    # Bounce off edges
    mask_x = (particles['x'] < 0) | (particles['x'] >= WIDTH)
    mask_y = (particles['y'] < 0) | (particles['y'] >= HEIGHT)
    particles['vx'][mask_x] *= -1
    particles['vy'][mask_y] *= -1

    # Blend
    layer_uint8 = np.clip(layer, 0, 255).astype(np.uint8)
    final = cv2.addWeighted(frame, 1.0, layer_uint8, ALPHA, 0)
    return final
