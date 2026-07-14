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
static_ffmpeg -i run1.mp4 -vf "fps=15,scale=1280:-1:flags=lanczos,split[a][b];[a]palettegen[p];[b][p]paletteuse" run1.gif
```

## Speed up / slow down (x times)

`X > 1` = faster, `X < 1` = slower. Set `X` once and reuse it.
`setpts=PTS/X` divides each frame's timestamp, so `X=2` plays twice as fast and `X=0.5` plays at half speed.

### mp4 → mp4

```bash
X=1
static_ffmpeg -i run1.mp4 -filter:v "setpts=PTS/$X" -an run1_x${X}.mp4
```

### gif → gif

```bash
X=1
static_ffmpeg -i run1.gif -filter:v "setpts=PTS/$X,split[a][b];[a]palettegen[p];[b][p]paletteuse" run1_x${X}.gif
```

## Fallback: extract frames → encode

Frames are written to `frames/%07d.png` (7-digit index) in the current directory.

```bash
python3 ~/rosbag2video/rosbag2video.py -t /record_rgb --save_images /home/noah/recordings/run1
static_ffmpeg -framerate 15 -i frames/%07d.png -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" -pix_fmt yuv420p run1.mp4
static_ffmpeg -framerate 15 -i frames/%07d.png -vf "fps=15,scale=1280:-1:flags=lanczos" run1.gif
```
