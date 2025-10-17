from PIL import Image, ImageDraw, ImageFont
import os

# --- UTILITIES ---

def draw_heavy_shadow_text(draw, position, text, font, fill_color, shadow_color, shadow_radius=10):
    """Draws text with a thick shadow/stroke effect for strong visibility."""
    x, y = position
    for dx in range(-shadow_radius, shadow_radius + 1, 4):
        for dy in range(-shadow_radius, shadow_radius + 1, 4):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=shadow_color)
    draw.text(position, text, font=font, fill=fill_color)

def get_text_size(draw, text, font):
    """Use textbbox for accurate measurement."""
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

def load_font_safely(font_path, size):
    """Try multiple fonts with fallback."""
    try:
        return ImageFont.truetype(font_path, size)
    except OSError:
        try:
            return ImageFont.truetype("impact.ttf", size)
        except OSError:
            try:
                return ImageFont.truetype("arialbd.ttf", size)
            except OSError:
                return ImageFont.load_default()

def auto_fit_font(draw, text, font_path, max_width, start_size, min_size=20):
    """Reduce font size until text fits within max_width."""
    font_size = start_size
    while font_size > min_size:
        font = load_font_safely(font_path, font_size)
        text_w, _ = get_text_size(draw, text, font)
        if text_w <= max_width:
            return font
        font_size -= 2  # step down gradually
    return load_font_safely(font_path, min_size)

# --- CONFIGURATION ---

image_path = r"C:\Users\Mr_robot\Desktop\videoeditautomation\images\background.jpg"

if not os.path.exists(image_path):
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), color='rgb(200, 100, 50)')
    draw = ImageDraw.Draw(img, "RGBA")
else:
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img, "RGBA")

width, height = img.size

# === SONG INFO ===
song_title = "JOURNEY OF LOVE you too"
artist_name = "Mr. Robot"

# Font paths and scale
CUSTOM_FONT_PATH = r"C:\Users\Mr_robot\Desktop\videoeditautomation\images\thumbnail fonts\Caramel and Vanilla.ttf"
REFERENCE_WIDTH = 1280
BASE_TITLE_SIZE = 120
BASE_ARTIST_SIZE = 50
scale_factor = width / REFERENCE_WIDTH

# --- AUTO FONT FITTING ---
max_text_width = int(width * 0.9)  # 90% of image width
font_title = auto_fit_font(draw, song_title, CUSTOM_FONT_PATH, max_text_width, int(BASE_TITLE_SIZE * scale_factor))
font_artist = auto_fit_font(draw, artist_name, CUSTOM_FONT_PATH, max_text_width, int(BASE_ARTIST_SIZE * scale_factor))

# --- TEXT MEASUREMENTS ---
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

# === COLORS ===
TITLE_FILL = (255, 255, 255)
TITLE_SHADOW = (0, 0, 0)
ARTIST_FILL = (255, 255, 255)
ARTIST_SHADOW = (0, 0, 0)

# === DRAW TEXT ===
draw_heavy_shadow_text(draw, (title_x, title_y), song_title, font_title, TITLE_FILL, TITLE_SHADOW, shadow_radius=int(12 * scale_factor))
draw_heavy_shadow_text(draw, (artist_x, artist_y), artist_name, font_artist, ARTIST_FILL, ARTIST_SHADOW, shadow_radius=int(6 * scale_factor))

# --- SAVE OUTPUT ---
output_path = os.path.join(os.path.dirname(image_path), "song_thumbnail_auto_fit.jpg")
img.save(output_path)
img.show()

print(f"✅ Auto-fit thumbnail saved at:\n{output_path}")
