import os
import random
from PIL import Image, ImageDraw, ImageFont

# --- CONFIGURATION ---

IMAGES_DIR = r"C:\Users\Mr_robot\Desktop\videoeditautomation\images\images"
FONTS_DIR = r"C:\Users\Mr_robot\Desktop\videoeditautomation\images\thumbnail fonts"
TEXT_FILE = r"C:\Users\Mr_robot\Desktop\videoeditautomation\images\thumbnail_texts.txt"
OUTPUT_DIR = r"C:\Users\Mr_robot\Desktop\videoeditautomation\images\output_thumbnails"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- UTILITIES ---

def draw_heavy_shadow_text(draw, position, text, font, fill_color, shadow_color, shadow_radius=10):
    """Draw text with thick shadow/stroke effect."""
    x, y = position
    for dx in range(-shadow_radius, shadow_radius + 1, 4):
        for dy in range(-shadow_radius, shadow_radius + 1, 4):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    draw.text(position, text, font=font, fill=fill_color)

def get_text_size(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def load_font_safely(font_path, size):
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except OSError:
            return ImageFont.load_default()

def auto_fit_font(draw, text, font_path, max_width, start_size, min_size=20):
    font_size = start_size
    while font_size > min_size:
        font = load_font_safely(font_path, font_size)
        text_w, _ = get_text_size(draw, text, font)
        if text_w <= max_width:
            return font
        font_size -= 2
    return load_font_safely(font_path, min_size)

# --- LOAD FILES ---

font_files = [os.path.join(FONTS_DIR, f) for f in os.listdir(FONTS_DIR) if f.lower().endswith((".ttf", ".otf"))]
if not font_files:
    raise FileNotFoundError("⚠️ No fonts found in thumbnail fonts directory!")

image_files = [os.path.join(IMAGES_DIR, f) for f in os.listdir(IMAGES_DIR) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
if not image_files:
    raise FileNotFoundError("⚠️ No images found in images directory!")

if not os.path.exists(TEXT_FILE):
    raise FileNotFoundError(f"⚠️ Text file not found: {TEXT_FILE}")

with open(TEXT_FILE, "r", encoding="utf-8") as f:
    lines = [line.strip() for line in f.readlines() if line.strip()]

if not lines:
    raise ValueError("⚠️ No valid text entries found in the text file.")

# --- VALIDATION ---
if len(lines) < len(image_files):
    print(f"⚠️ Only {len(lines)} text entries found, {len(image_files)} images exist. Extra images will be skipped.")
elif len(lines) > len(image_files):
    print(f"⚠️ Only {len(image_files)} images found, extra text entries will be ignored.")

# --- CONSTANTS ---
REFERENCE_WIDTH = 1280
BASE_TITLE_SIZE = 120
BASE_ARTIST_SIZE = 50

# --- MAIN LOOP ---

for idx, (image_path, text_line) in enumerate(zip(image_files, lines), 1):
    print(f"🖼️ Processing {idx}/{len(image_files)}: {os.path.basename(image_path)}")

    # Split title | artist
    parts = [p.strip() for p in text_line.split("|")]
    song_title = parts[0] if len(parts) >= 1 else "Untitled"
    artist_name = parts[1] if len(parts) >= 2 else "Unknown Artist"

    # Load image
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")
    width, height = img.size

    # Font selection
    font_path = random.choice(font_files)
    scale_factor = width / REFERENCE_WIDTH
    max_text_width = int(width * 0.9)

    # Auto-fit font size
    font_title = auto_fit_font(draw, song_title, font_path, max_text_width, int(BASE_TITLE_SIZE * scale_factor))
    font_artist = auto_fit_font(draw, artist_name, font_path, max_text_width, int(BASE_ARTIST_SIZE * scale_factor))

    # Text positioning
    title_w, title_h = get_text_size(draw, song_title, font_title)
    artist_w, artist_h = get_text_size(draw, artist_name, font_artist)
    center_x, center_y = width // 2, height // 2
    spacing_between = int(20 * scale_factor)
    total_text_height = title_h + spacing_between + artist_h
    start_y = center_y - total_text_height // 2
    title_x = center_x - title_w // 2
    title_y = start_y
    artist_x = center_x - artist_w // 2
    artist_y = title_y + title_h + spacing_between

    # Text colors (unchanged style)
    TITLE_FILL = (255, 255, 255)
    TITLE_SHADOW = (0, 0, 0)
    ARTIST_FILL = (255, 255, 255)
    ARTIST_SHADOW = (0, 0, 0)

    # Draw text (same style as before)
    draw_heavy_shadow_text(draw, (title_x, title_y), song_title, font_title, TITLE_FILL, TITLE_SHADOW, shadow_radius=int(12 * scale_factor))
    draw_heavy_shadow_text(draw, (artist_x, artist_y), artist_name, font_artist, ARTIST_FILL, ARTIST_SHADOW, shadow_radius=int(6 * scale_factor))

    # Save thumbnail
    base_name = os.path.splitext(os.path.basename(image_path))[0]
    output_filename = f"{base_name}_thumbnail.jpg"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    img.save(output_path, quality=95)

    print(f"✅ Saved: {output_path}")

print("\n🎉 All thumbnails generated successfully!")
