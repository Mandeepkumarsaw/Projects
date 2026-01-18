import tkinter as tk
from tkinter import filedialog
import cv2
from PIL import Image, ImageTk
from ultralytics import YOLO
import cvzone
import math
import threading
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Load model
model = YOLO("../yolo-weights/yolov8n.pt")
ClassNames = [
    "person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat", "dog",
    "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
    "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
    "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
    "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli", "carrot",
    "hot dog", "pizza", "donut", "cake", "chair", "sofa", "potted plant", "bed", "dining table", "toilet",
    "tv monitor", "laptop", "mouse", "remote", "keyboard", "cell phone", "microwave", "oven", "toaster",
    "sink", "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier", "toothbrush",
    "earphone"
]

class TrafficLight:
    def __init__(self):
        self.state = "RED"  # Start with RED light
        self.timer = 15     # Initial countdown time
        self.time_left = self.timer
        self.running = False
        self.timer_thread = None
        self.min_green_time = 10  
        self.max_green_time = 30 
        self.min_red_time = 5    
        self.max_red_time = 20    
    
    def start(self):
        self.running = True
        self.time_left = self.timer
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
    
    def stop(self):
        self.running = False
        
    def run_timer(self):
        while self.running:
            if self.time_left > 0:
                self.time_left -= 1
                time.sleep(1)
            else:
                # Cycle through traffic light states
                if self.state == "RED":
                    self.state = "GREEN"
                    self.time_left = self.timer
                elif self.state == "GREEN":
                    self.state = "YELLOW"
                    self.timer = 3   # Yellow is always 3 seconds
                    self.time_left = self.timer
                elif self.state == "YELLOW":
                    self.state = "RED"
                    self.time_left = self.timer
    
    def update_timer_based_on_traffic(self, vehicle_count):
        # Dynamically adjust timer based on actual vehicle count
        if self.state == "RED":
            # For red light: less traffic = shorter red light
            # Scale red light time inversely with traffic volume
            if vehicle_count <= 5:
                self.timer = self.min_red_time  # Minimum red time for very low traffic
            elif vehicle_count >= 20:
                self.timer = self.max_red_time  # Maximum red time for very high traffic
            else:
                # Linear scaling between min and max for intermediate traffic
                # As traffic increases, red light time increases
                traffic_factor = (vehicle_count - 5) / 15  # Normalized between 0 and 1
                self.timer = self.min_red_time + traffic_factor * (self.max_red_time - self.min_red_time)
                self.timer = int(self.timer)  # Convert to integer
                
        elif self.state == "GREEN":
            # For green light: more traffic = longer green light
            # Scale green light time directly with traffic volume
            if vehicle_count <= 5:
                self.timer = self.min_green_time  # Minimum green time for very low traffic
            elif vehicle_count >= 20:
                self.timer = self.max_green_time  # Maximum green time for very high traffic
            else:
                # Linear scaling between min and max for intermediate traffic
                # As traffic increases, green light time increases
                traffic_factor = (vehicle_count - 5) / 15  # Normalized between 0 and 1
                self.timer = self.min_green_time + traffic_factor * (self.max_green_time - self.min_green_time)
                self.timer = int(self.timer)  # Convert to integer

class TrafficGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic Moniter")
        self.root.geometry("1280x800")
        self.running = False
        self.last_source = None
        self.traffic_light = TrafficLight()

        # Layout frame
        self.container = tk.Frame(self.root)
        self.container.pack(padx=10, pady=10)

        # Display and button side (left)
        self.left_frame = tk.Frame(self.container)
        self.left_frame.grid(row=0, column=0, sticky="n")

        self.display_frame = tk.LabelFrame(self.left_frame, text="Display", font=("Arial", 12, "bold"), width=960, height=540)
        self.display_frame.grid(row=0, column=0, padx=5, pady=5)
        self.display_frame.pack_propagate(False)
        self.panel = tk.Label(self.display_frame)
        self.panel.pack(fill="both", expand=True)

        self.button_frame = tk.Frame(self.left_frame)
        self.button_frame.grid(row=1, column=0, pady=10)

        btn_cfg = {"font": ("Arial", 12), "width": 12, "padx": 10, "pady": 8}
        self.upload_button = tk.Button(self.button_frame, text="Upload Video", command=self.load_video, **btn_cfg)
        self.upload_button.grid(row=0, column=0, padx=5)
        self.camera_button = tk.Button(self.button_frame, text="Camera", command=self.start_camera, **btn_cfg)
        self.camera_button.grid(row=0, column=1, padx=5)
        self.resume_button = tk.Button(self.button_frame, text="Resume", command=self.resume_video, **btn_cfg)
        self.resume_button.grid(row=0, column=2, padx=5)
        self.stop_button = tk.Button(self.button_frame, text="Stop", command=self.stop_video, **btn_cfg)
        self.stop_button.grid(row=0, column=3, padx=5)

        # Right frame (analysis + log)
        self.right_frame = tk.Frame(self.container)
        self.right_frame.grid(row=0, column=1, padx=10, sticky="n")

        # Analysis panel
        tk.Label(self.right_frame, text="Live Analysis", font=("Arial", 16, "bold")).pack(pady=10)
        self.vehicle_label = tk.Label(self.right_frame, text="Vehicles: 0", font=("Arial", 14))
        self.vehicle_label.pack(pady=5)
        self.congestion_label = tk.Label(self.right_frame, text="Congestion: -", font=("Arial", 14))
        self.congestion_label.pack(pady=5)
        self.signal_label = tk.Label(self.right_frame, text="Signal Time: -", font=("Arial", 14))
        self.signal_label.pack(pady=5)

        # Traffic Light Display
        self.traffic_light_frame = tk.Frame(self.right_frame, bg="black", width=100, height=250, bd=2, relief=tk.RAISED)
        self.traffic_light_frame.pack(pady=10)
        
        # Create the three lights
        self.red_light = tk.Canvas(self.traffic_light_frame, width=60, height=60, bg="black", highlightthickness=0)
        self.red_light.pack(pady=5)
        self.red_circle = self.red_light.create_oval(5, 5, 55, 55, fill="darkred", outline="gray", width=2)
        
        self.yellow_light = tk.Canvas(self.traffic_light_frame, width=60, height=60, bg="black", highlightthickness=0)
        self.yellow_light.pack(pady=5)
        self.yellow_circle = self.yellow_light.create_oval(5, 5, 55, 55, fill="darkgoldenrod", outline="gray", width=2)
        
        self.green_light = tk.Canvas(self.traffic_light_frame, width=60, height=60, bg="black", highlightthickness=0)
        self.green_light.pack(pady=5)
        self.green_circle = self.green_light.create_oval(5, 5, 55, 55, fill="darkgreen", outline="gray", width=2)
        
        # Timer display
        self.timer_label = tk.Label(self.right_frame, text="Countdown: 15", font=("Arial", 16, "bold"))
        self.timer_label.pack(pady=5)
        
        # Next cycle time display
        self.next_cycle_label = tk.Label(self.right_frame, text="Next Cycle: 15s", font=("Arial", 14))
        self.next_cycle_label.pack(pady=5)

        # Chart
        fig = Figure(figsize=(3, 2), dpi=100)
        self.ax = fig.add_subplot(111)
        self.ax.set_title("Vehicle Count History")
        self.ax.set_ylabel("Count")
        self.ax.set_xlabel("Frames")
        self.chart_data = []
        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.right_frame)
        self.chart_canvas.get_tk_widget().pack(pady=10)

        # Log below chart
        tk.Label(self.right_frame, text="System Log", font=("Arial", 12, "bold")).pack(pady=(5, 2))
        self.vehicle_log = tk.Listbox(self.right_frame, height=6)
        self.vehicle_log.pack(fill="x", pady=5)
        
        # Start updating the traffic light display
        self.update_traffic_light()

    def update_traffic_light(self):
        # Update the traffic light display based on current state
        if self.traffic_light.state == "RED":
            self.red_light.itemconfig(self.red_circle, fill="red")
            self.yellow_light.itemconfig(self.yellow_circle, fill="darkgoldenrod")
            self.green_light.itemconfig(self.green_circle, fill="darkgreen")
        elif self.traffic_light.state == "YELLOW":
            self.red_light.itemconfig(self.red_circle, fill="darkred")
            self.yellow_light.itemconfig(self.yellow_circle, fill="yellow")
            self.green_light.itemconfig(self.green_circle, fill="darkgreen")
        elif self.traffic_light.state == "GREEN":
            self.red_light.itemconfig(self.red_circle, fill="darkred")
            self.yellow_light.itemconfig(self.yellow_circle, fill="darkgoldenrod")
            self.green_light.itemconfig(self.green_circle, fill="lime")
            
        # Update the timer display
        self.timer_label.config(text=f"Countdown: {self.traffic_light.time_left}")
        self.next_cycle_label.config(text=f"Next Cycle: {self.traffic_light.timer}s")
        
        # Schedule the next update
        self.root.after(100, self.update_traffic_light)

    def log_event(self, message):
        self.vehicle_log.insert(tk.END, message)
        if self.vehicle_log.size() > 10:
            self.vehicle_log.delete(0)

    def load_video(self):
        path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
        if path:
            self.log_event("Uploading")
            self.last_source = path
            self.start_detection(path)

    def start_camera(self):
        self.log_event("Camera Started")
        self.last_source = 0
        self.start_detection(0)

    def stop_video(self):
        self.running = False
        self.traffic_light.stop()
        self.log_event("Stopped")

    def resume_video(self):
        if not self.running and self.last_source is not None:
            self.log_event("Resumed")
            self.start_detection(self.last_source, resume=True)

    def start_detection(self, source, resume=False):
        if not resume:
            self.chart_data.clear()
            self.vehicle_log.delete(0, tk.END)
        self.running = True
        self.traffic_light.start()
        self.log_event("Running")
        threading.Thread(target=self.run_detection, args=(source,), daemon=True).start()

    def run_detection(self, source):
        cap = cv2.VideoCapture(source)
        while cap.isOpened() and self.running:
            success, img = cap.read()
            if not success:
                break
            img = cv2.resize(img, (960, 540))
            results = model(img, stream=True)
            vehicle_count = 0
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cls_id = int(box.cls[0])
                    name = ClassNames[cls_id]
                    if name in ["car", "truck", "bus", "motorbike"]:
                        vehicle_count += 1
                    w, h = x2 - x1, y2 - y1
                    cvzone.cornerRect(img, (x1, y1, w, h))
                    conf = math.ceil(box.conf[0] * 100) / 100
                    cvzone.putTextRect(img, f'{name} {conf}', (x1, max(35, y1)), scale=1, thickness=1)

            self.chart_data.append(vehicle_count)
            if len(self.chart_data) > 50:
                self.chart_data.pop(0)
            self.ax.clear()
            self.ax.plot(self.chart_data)
            self.ax.set_title("Vehicle Count History")
            self.ax.set_ylabel("Count")
            self.ax.set_xlabel("Frames")
            self.chart_canvas.draw()

            congestion = "High" if vehicle_count > 10 else "Low"
            
            # Update traffic light timer based on actual vehicle count
            self.traffic_light.update_timer_based_on_traffic(vehicle_count)
            
            self.vehicle_label.config(text=f"Vehicles: {vehicle_count}")
            self.congestion_label.config(text=f"Congestion: {congestion}")
            self.signal_label.config(text=f"Signal State: {self.traffic_light.state}")
            
            # Log significant changes in traffic
            if len(self.chart_data) > 1 and abs(self.chart_data[-1] - self.chart_data[-2]) > 3:
                if self.chart_data[-1] > self.chart_data[-2]:
                    self.log_event(f"Traffic increasing: {self.chart_data[-2]} → {self.chart_data[-1]}")
                else:
                    self.log_event(f"Traffic decreasing: {self.chart_data[-2]} → {self.chart_data[-1]}")

            # Draw traffic light state on the video
            light_color = (0, 0, 255) if self.traffic_light.state == "RED" else \
                         (0, 255, 255) if self.traffic_light.state == "YELLOW" else \
                         (0, 255, 0)  # GREEN
            cv2.circle(img, (50, 50), 30, light_color, -1)
            cv2.putText(img, f"{self.traffic_light.time_left}", (40, 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            # Add traffic count and next cycle time to the video
            cv2.putText(img, f"Vehicles: {vehicle_count}", (50, 100), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, f"Next cycle: {self.traffic_light.timer}s", (50, 130), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img_pil = ImageTk.PhotoImage(Image.fromarray(img_rgb))
            self.panel.config(image=img_pil)
            self.panel.image = img_pil

        cap.release()
        self.log_event("Stopped")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.iconbitmap("img/Traffic.ico")  # .ico format icon
    except:
        pass  # Skip if icon not found
    app = TrafficGUI(root)
    root.mainloop()
    