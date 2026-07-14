# 8. RGB Recording & Video Conversion

- Recording `record_rgb` topic via rosbag command.
- Bag of commands for converting the rosbag results to mp4 or gif videos.

## Setup (once)

```bash
python3 -m venv ~/.venvs/rosbag2video
source ~/.venvs/rosbag2video/bin/activate
pip install rosbags opencv-python numpy static-ffmpeg
static_ffmpeg -version
git clone https://github.com/mlaiacker/rosbag2video ~/rosbag2video
cp ~/workspaces/movensys_ws/src/movensys-manipulator/tools/rosbag2video/rosbag2video.py ~/rosbag2video/rosbag2video.py
```

## Start Record

```bash
ros2 bag record -o /home/noah/recordings/run1 record_rgb
```

## Activate (each session)

```bash
source ~/.venvs/rosbag2video/bin/activate
```

## bag → mp4

```bash
python3 ~/rosbag2video/rosbag2video.py -t /record_rgb -r 15 -o run1.mp4 /home/noah/recordings/run1
```

## mp4 → gif

```bash
static_ffmpeg -i run1.mp4 -vf "fps=10,scale=480:-1:flags=lanczos,palettegen" palette.png
static_ffmpeg -i run1.mp4 -i palette.png -filter_complex "fps=10,scale=480:-1:flags=lanczos[x];[x][1:v]paletteuse" run1.gif
```

## Fallback: extract frames → encode

```bash
python3 ~/rosbag2video/rosbag2video.py -t /record_rgb --save_images /home/noah/recordings/run1
static_ffmpeg -framerate 15 -i frame%04d.png -pix_fmt yuv420p run1.mp4
static_ffmpeg -framerate 15 -i frame%04d.png -vf "fps=10,scale=480:-1:flags=lanczos" run1.gif
```
