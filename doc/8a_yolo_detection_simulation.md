# Running yolo
```bash
cd ~/workspaces/movensys_ws/src/movensys-manpulator/movensys_manipulator_perception
mros ros2 launch movensys_manipulator_perception yolo_cube_detector.launch.py
```

```bash
cd ~/workspaces/movensys_ws/src/movensys-manpulator/movensys_manipulator_perception
mros ros2 launch movensys_manipulator_perception yolo_dice_detector.launch.py
```


```bash
ros2 run rqt_image_view rqt_image_view /yolo_dice_detector/debug_image

ros2 run rqt_image_view rqt_image_view /yolo_cube_detector/debug_image
```
