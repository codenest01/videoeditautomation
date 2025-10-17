import os
import glob
import importlib.util
import cv2
import uuid

# Paths
output_dir = r"C:\Users\Mr_robot\Desktop\videoeditautomation\output"
effects_dir = r"C:\Users\Mr_robot\Desktop\videoeditautomation\Effect Bulk"

def load_effect_module(effect_path):
    module_name = os.path.splitext(os.path.basename(effect_path))[0]
    spec = importlib.util.spec_from_file_location(module_name, effect_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def apply_effects_to_video(video_path):
    """Apply all effects to a video safely using a temporary file."""
    print(f"\n🎬 Processing video: {os.path.basename(video_path)}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"❌ Could not open {video_path}")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    temp_output_path = os.path.join(output_dir, f"temp_{uuid.uuid4()}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(temp_output_path, fourcc, fps, (frame_width, frame_height))

    effect_files = glob.glob(os.path.join(effects_dir, "*.py"))
    effects = []
    for effect_file in effect_files:
        module = load_effect_module(effect_file)
        if hasattr(module, "apply_effect_frame"):
            effects.append(module.apply_effect_frame)
            print(f"✨ Loaded effect: {os.path.basename(effect_file)}")
        else:
            print(f"⚠️ Skipped {effect_file} (no apply_effect_frame function)")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        for effect_fn in effects:
            frame = effect_fn(frame)

        out.write(frame)

    cap.release()
    out.release()

    # Replace original video
    os.replace(temp_output_path, video_path)
    print(f"✅ Effects applied to {video_path}")

if __name__ == "__main__":
    videos = glob.glob(os.path.join(output_dir, "*.mp4"))
    if not videos:
        print("❌ No videos found in the output folder.")
    else:
        for video in videos:
            apply_effects_to_video(video)
        print("\n🎉 All effects applied to all videos!")
