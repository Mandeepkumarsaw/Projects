# 🚦 Adaptive Traffic Management System

An intelligent traffic control system that leverages real-time object detection to dynamically manage traffic lights using computer vision and smart logic. Built with Python, OpenCV, and YOLOv8.

---

## 🔍 Core Technologies & Libraries

- **Tkinter** – GUI interface (video display, buttons, stats, charts)
- **OpenCV (`cv2`)** – Video capture and frame processing
- **Pillow (`PIL`)** – Converts OpenCV images for Tkinter compatibility
- **Ultralytics YOLO (`ultralytics.YOLO`)** – YOLOv8-based object detection
- **Cvzone** – Enhanced bounding boxes (cornerRect, putTextRect)
- **Math** – Bounding box calculations and confidence levels
- **Threading** – Non-blocking detection and light updates
- **Time** – Signal simulation and countdown logic
- **Matplotlib** – Vehicle count chart integration via `FigureCanvasTkAgg`

---

## 📦 YOLOv8 Model Usage

- **Model**: `yolov8n.pt` (YOLOv8 nano)
- **Pretrained on**: 80+ COCO classes
- **Extended to detect**: Custom objects like `"ambulance"`, `"fire truck"`

---

## 🚦 Adaptive Traffic Light Control

The traffic lights dynamically adjust based on detected vehicle volume:

- **Red & Green timing** adapt between `min_green_time = 10s` and `max_green_time = 30s`
- **Yellow** is fixed at `3s`
- **Red timing** adapts between `min_red_time = 5s` and `max_red_time = 20s`
- Signal state is visualized:
  - On live video feed (colored circle + countdown)
  - On Tkinter panel (LED-style lights and timers)

### 🧠 Adaptive Logic Formula

```python
traffic_factor = (vehicle_count - 5) / 15
self.timer = min_time + traffic_factor * (max_time - min_time)
