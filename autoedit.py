import os
import cv2
import glob
import subprocess
import importlib.util
import inspect
import random
import uuid

# Directories
base_dir = r"C:\Users\Mr_robot\Desktop\videoeditautomation"
audio_dir = os.path.join(base_dir, 'audio')
image_dir = os.path.join(base_dir, 'images')
output_dir = os.path.join(base_dir, 'output')
effects_dir = os.path.join(base_dir, 'Effect Bulk')

os.makedirs(output_dir, exist_ok=True)

# -----------------------
# Load effect modules dynamically
# -----------------------
def load_effect_modules():
    modules = []
    for effect_file in glob.glob(os.path.join(effects_dir, "*.py")):
        name = os.path.splitext(os.path.basename(effect_file))[0]
        spec = importlib.util.spec_from_file_location(name, effect_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "apply_effect_frame"):
            modules.append(module.apply_effect_frame)
        else:
            print(f"⚠️ Skipping {effect_file} (no apply_effect_frame function)")
    return modules

effects_list = load_effect_modules()

# -----------------------
# Unique random video name
# -----------------------
def get_random_video_name(output_dir, prefix="video_", ext=".mp4"):
    unique_id = uuid.uuid4().hex[:8]  # 8-char random ID
    return os.path.join(output_dir, f"{prefix}{unique_id}{ext}")

# -----------------------
# Main video creation function (direct streaming to FFmpeg)
# -----------------------
def create_video(image_path, audio_path, output_path, fps=10):
    print(f"\n🎬 Starting video creation for: {os.path.basename(audio_path)}")

    # 1. Image and Dimensions
    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Error: Image not found or could not be loaded: {image_path}")
        return

    h, w, _ = img.shape

    # ✅ Ensure FFmpeg-compatible even dimensions
    if w % 2 != 0:
        w -= 1
    if h % 2 != 0:
        h -= 1
    img = cv2.resize(img, (w, h))

    # 2. Get Audio Duration and Frame Count
    try:
        cmd_duration = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', audio_path
        ]
        result = subprocess.run(cmd_duration, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        duration = float(result.stdout.strip())
        total_frames = int(duration * fps)
        print(f"✅ Audio duration: {duration:.2f}s, Total frames to process: {total_frames}")
        if total_frames <= 0:
            print("⚠️ Warning: Audio duration is too short. Skipping video creation.")
            return
    except (subprocess.CalledProcessError, ValueError) as e:
        print(f"❌ Error getting audio duration with ffprobe: {e}")
        return

    # 3. Start FFmpeg Subprocess
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-pix_fmt', 'bgr24',
        '-s', f'{w}x{h}',
        '-r', str(fps),
        '-i', 'pipe:0',
        '-i', audio_path,
        '-c:v', 'libx264',
        '-preset', 'ultrafast',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-shortest',
        output_path
    ]
    process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

    # 4. Process and Write Frames
    font = cv2.FONT_HERSHEY_SIMPLEX
    audio_name_text = os.path.splitext(os.path.basename(audio_path))[0]


    print(f"✨ Applying {len(effects_list)} effects sequentially for {os.path.basename(output_path)}")

    for frame_idx in range(total_frames):
        frame = img.copy()

        # ✅ Apply ALL effects in sequence
        for effect in effects_list:
            try:
                sig = inspect.signature(effect)
                params = sig.parameters

                kwargs = {}
                if "frame_idx" in params:
                    kwargs["frame_idx"] = frame_idx
                if "fps" in params:
                    kwargs["fps"] = fps
                if "video_id" in params:
                    kwargs["video_id"] = os.path.basename(output_path)
                if "audio_name" in params:
                    kwargs["audio_name"] = os.path.splitext(os.path.basename(audio_path))[0]

                frame = effect(frame, **kwargs)

            except Exception as e:
                print(f"❌ Error applying effect {effect.__name__}: {e}")

        # Write frame to FFmpeg stdin
        process.stdin.write(frame.tobytes())

        if frame_idx % fps == 0:
            print(f"Processing frame {frame_idx+1}/{total_frames}", end="\r")

    # 5. Cleanup FFmpeg Process
    try:
        process.stdin.close()
        process.wait(timeout=10)
        print(f"\n🎉 Video created with {len(effects_list)} effects: {output_path}")
    except (IOError, subprocess.TimeoutExpired) as e:
        print(f"❌ Error during FFmpeg cleanup: {e}")
        process.kill()

# -----------------------
# Process all images + audio
# -----------------------
if __name__ == "__main__":
    images = sorted([os.path.join(image_dir, f) for f in os.listdir(image_dir) if f.lower().endswith(('.png','.jpg','.jpeg'))])
    audios = sorted([os.path.join(audio_dir, f) for f in os.listdir(audio_dir) if f.lower().endswith(('.mp3','.wav','.aac'))])

    total_videos = min(len(images), len(audios))
    for i in range(total_videos):
        img = images[i]
        aud = audios[i]

        # ✅ Generate a random filename for each output
        out_file = get_random_video_name(output_dir, prefix="video_", ext=".mp4")

        create_video(img, aud, out_file)
