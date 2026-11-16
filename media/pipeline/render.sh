#!/usr/bin/env bash
# Usage: pipeline/render.sh <video-id> [<scene-file> <SceneClass>]
# Needs narrate.py output (audio/, timings.json, <id>.srt) and the scene's data in $VIDEO_DATA.
# Renders with Manim ($QUALITY, default 720p30), muxes the concatenated narration, and copies
# <id>.mp4 and <id>.srt to $VIDEOS_OUT. Scene file/class default from the id: v1-foo -> v1_foo.py, V1.
set -euo pipefail
source "$(dirname "$0")/env.sh"
id=$1
file=${2:-${id//-/_}.py}
[[ $id =~ ^v([0-9]+) ]] && dcls=V${BASH_REMATCH[1]} || dcls=
cls=${3:-$dcls}
out=$MEDIA_RENDERS/$id
case $QUALITY in l) res=480p15 ;; m) res=720p30 ;; h) res=1080p60 ;; p) res=1440p60 ;; k) res=2160p60 ;; *) echo "bad QUALITY=$QUALITY" >&2; exit 2 ;; esac
( cd "$MEDIA/scenes" && manim -q"$QUALITY" --media_dir "$out/manim" "$file" "$cls" )
vid=$out/manim/videos/${file%.py}/$res/$cls.mp4
: > "$out/audio/list.txt"
for f in $(ls "$out"/audio/s*.wav | sort -V); do echo "file '$(realpath "$f")'" >> "$out/audio/list.txt"; done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$out/audio/list.txt" -c:a pcm_s16le "$out/narration.wav"
# Re-encode (Manim's own encode is ~50% bigger): visually identical (SSIM > 0.999 on v0), and it keeps
# each file under GitLab's 5 MiB per-file limit without Git LFS.
ffmpeg -y -loglevel error -i "$vid" -i "$out/narration.wav" -map 0:v -map 1:a \
  -c:v libx264 -crf 23 -preset slow -tune animation -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 128k -shortest "$out/$id.mp4"
mkdir -p "$VIDEOS_OUT"
cp "$out/$id.mp4" "$out/$id.srt" "$VIDEOS_OUT/"
size=$(stat -c %s "$VIDEOS_OUT/$id.mp4")
echo "$VIDEOS_OUT/$id.mp4  $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VIDEOS_OUT/$id.mp4") s  $((size / 1024)) KiB"
if [ "$size" -gt $((4608 * 1024)) ]; then
  echo "WARNING: $id.mp4 is over 4.5 MiB; GitLab rejects files over 5 MiB. Raise -crf or shorten the video." >&2
fi
