import os
import subprocess

# Paths
base_dir = r"C:\\Users\\Mr_robot\\Desktop\\videoeditautomation"
output_dir = os.path.join(base_dir, "output")

os.makedirs(output_dir, exist_ok=True)

def apply_pro_slow_reverb(video_path, output_path):
    """
    Apply a professional-grade slow + reverb effect to the audio of a video file.
    Uses only filters that are widely supported in FFmpeg.
    """
    # Compatible pro chain: slowdown + multi-tap echo + long reverb tail + loudnorm
    audio_filters = (
        "atempo=0.8,"                              # Slow audio ~20%
        "aecho=0.8:0.88:60:0.4,"                   # Short echo (adds depth)
        "aecho=0.6:0.7:300:0.25,"                  # Mid echo
        "aecho=0.5:0.6:1000:0.3,"                  # Long tail echo
        "loudnorm"                                 # Normalize volume
    )

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-filter_complex", f"[0:a]{audio_filters}[a]",
        "-map", "0:v", "-map", "[a]",
        "-c:v", "copy",    # keep original video stream
        "-c:a", "aac",     # re-encode audio
        "-b:a", "256k",    # good audio quality
        output_path
    ]

    print(f"🔄 Applying pro slow + reverb → {video_path}")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Done: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error:\n{e.stderr}")
    except FileNotFoundError:
        print("❌ FFmpeg not found. Please install or add to PATH.")

if __name__ == "__main__":
    videos = [f for f in os.listdir(output_dir) if f.lower().endswith(".mp4")]
    if not videos:
        print("⚠️ No .mp4 videos found in output folder.")
    for video_file in videos:
        input_path = os.path.join(output_dir, video_file)
        name, ext = os.path.splitext(video_file)
        output_path = os.path.join(output_dir, f"{name}_pro_slowreverb_fixed{ext}")
        apply_pro_slow_reverb(input_path, output_path)
