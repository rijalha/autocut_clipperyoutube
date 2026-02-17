import os
import subprocess

# ================= PATH OTOMATIS SESUAI LOKASI FILE PYTHON =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BAHAN_FOLDER = os.path.join(BASE_DIR, "bahan")
SELESAI_FOLDER = os.path.join(BASE_DIR, "selesai")


def get_video_duration(filepath):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            filepath
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    return float(result.stdout.strip())


def format_time(seconds):
    jam = int(seconds // 3600)
    menit = int((seconds % 3600) // 60)
    detik = int(seconds % 60)
    return f"{jam:02}-{menit:02}-{detik:02}"


def parse_time(t):
    if ":" in t:
        parts = list(map(int, t.split(":")))
        if len(parts) == 3:
            return parts[0]*3600 + parts[1]*60 + parts[2]
        elif len(parts) == 2:
            return parts[0]*60 + parts[1]
    return int(t)


# ================= MODE LANDSCAPE =================
def cut_landscape(input_path, start_sec, end_sec):
    duration = end_sec - start_sec
    output_name = f"{format_time(start_sec)}_to_{format_time(end_sec)}.mp4"
    output_path = os.path.join(SELESAI_FOLDER, output_name)

    print(f"✂️ Landscape ({start_sec}s - {end_sec}s)")

    cmd = [
        "ffmpeg",
        "-ss", str(start_sec),
        "-i", input_path,
        "-t", str(duration),
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        "-fflags", "+genpts",
        output_path,
        "-y"
    ]
    subprocess.run(cmd)
    print(f"✅ Selesai: {output_name}")


# ================= MODE PORTRAIT =================
def cut_portrait(input_path, start_sec, end_sec):
    duration = end_sec - start_sec
    output_name = f"{format_time(start_sec)}_to_{format_time(end_sec)}.mp4"
    output_path = os.path.join(SELESAI_FOLDER, output_name)

    print(f"📱 Portrait Blur ({start_sec}s - {end_sec}s)")

    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=20:10[bg];"
        "[0:v]scale=1080:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    cmd = [
        "ffmpeg",
        "-ss", str(start_sec),
        "-i", input_path,
        "-t", str(duration),
        "-filter_complex", filter_complex,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path,
        "-y"
    ]
    subprocess.run(cmd)
    print(f"✅ Selesai: {output_name}")


# ================= MODE SHORTS STYLE =================
def cut_shorts_style(input_path, start_sec, end_sec):
    duration = end_sec - start_sec
    output_name = f"{format_time(start_sec)}_to_{format_time(end_sec)}.mp4"
    output_path = os.path.join(SELESAI_FOLDER, output_name)

    print(f"🎬 Shorts Style ({start_sec}s - {end_sec}s)")

    filter_complex = (
        "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,boxblur=25:15,eq=brightness=-0.05:saturation=1.2[bg];"
        "[0:v]scale=900:-2[fg];"
        "[bg][fg]overlay=(W-w)/2:(H-h)/2"
    )

    cmd = [
        "ffmpeg",
        "-ss", str(start_sec),
        "-i", input_path,
        "-t", str(duration),
        "-filter_complex", filter_complex,
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path,
        "-y"
    ]
    subprocess.run(cmd)
    print(f"✅ Selesai: {output_name}")


# ================= MAIN PROGRAM =================
def main():
    if not os.path.exists(BAHAN_FOLDER):
        print("❌ Folder 'bahan' tidak ditemukan!")
        return

    if not os.path.exists(SELESAI_FOLDER):
        os.makedirs(SELESAI_FOLDER)

    videos = [f for f in os.listdir(BAHAN_FOLDER) if f.lower().endswith((".mp4", ".mkv", ".mov"))]

    if not videos:
        print("❌ Tidak ada video di folder 'bahan'")
        return

    print("\n📂 Daftar video di folder 'bahan':")
    for i, vid in enumerate(videos, start=1):
        print(f"{i}. {vid}")

    try:
        choice = int(input("\n👉 Pilih nomor video: "))
        video_file = videos[choice - 1]
    except (ValueError, IndexError):
        print("❌ Pilihan tidak valid")
        return

    video_path = os.path.join(BAHAN_FOLDER, video_file)

    print(f"\n🎬 Video dipilih: {video_file}")
    duration = get_video_duration(video_path)
    print(f"⏱ Durasi video: {format_time(duration).replace('-', ':')}")

    print("\nPilih mode output:")
    print("1 = Landscape (kualitas asli)")
    print("2 = Portrait 9:16 (Shorts/TikTok)")
    print("3 = Shorts Style 🔥")
    mode = input("👉 Pilih mode (1/2/3): ")

    print("\nMasukkan durasi potong (contoh: 90-150 atau 00:01:30-00:02:30)")
    print("Bisa banyak, pisahkan koma\n")
    user_input = input("👉 Masukkan durasi potong: ")
    ranges = [r.strip() for r in user_input.split(",") if r.strip()]

    print("\n🚀 Proses dimulai...\n")
    for r in ranges:
        if "-" not in r:
            print(f"❌ Format range salah: {r}")
            continue
        try:
            start_raw, end_raw = r.split("-")
            start_sec = parse_time(start_raw.strip())
            end_sec = parse_time(end_raw.strip())
        except Exception as e:
            print(f"❌ Error memproses range: {r} ({e})")
            continue

        if start_sec >= end_sec:
            print(f"❌ Range tidak valid: {r}")
            continue

        if mode == "1":
            cut_landscape(video_path, start_sec, end_sec)
        elif mode == "2":
            cut_portrait(video_path, start_sec, end_sec)
        elif mode == "3":
            cut_shorts_style(video_path, start_sec, end_sec)
        else:
            print("❌ Mode tidak dikenal")

    print("\n🎉 Semua proses selesai! Cek folder 'selesai'")


if __name__ == "__main__":
    main()
