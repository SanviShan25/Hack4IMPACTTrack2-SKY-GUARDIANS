# ==========================================
# SKY GUARDIAN - FINAL STABLE ML SYSTEM
# ==========================================

import cv2
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
import requests

# ------------------------------
# API FUNCTION
# ------------------------------
def send_data(data):
    try:
        requests.post("http://127.0.0.1:5001/update", json=data)
    except:
        pass

# ------------------------------
# ESP32 CAMERA (CAPTURE MODE)
# ------------------------------
STREAM_URL = "http://10.226.71.216/capture"

def get_frame():
    try:
        response = requests.get(STREAM_URL, timeout=2)
        img_array = np.frombuffer(response.content, dtype=np.uint8)
        frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        return frame
    except:
        return None

print("📡 ESP32 Camera Ready")

# ------------------------------
# LOAD MODEL
# ------------------------------
model = YOLO("yolov8n.pt")

# ------------------------------
# MEDIAPIPE SAFE INIT
# ------------------------------
pose = None
print("⚠️ Mediapipe disabled")

# ------------------------------
# VARIABLES
# ------------------------------
prev_positions = {}
movement_threshold = 15
prev_gray = None

# ==========================================
# FRAME GENERATOR (FOR FLASK)
# ==========================================
def generate_frames():
    global prev_positions, prev_gray

    while True:
        frame = get_frame()

        if frame is None:
            continue

        frame = cv2.resize(frame, (640, 480))

        results = model(frame)
        current_positions = {}

        for r in results:
            for i, box in enumerate(r.boxes):

                cls = int(box.cls[0])
                conf = float(box.conf[0])

                if conf > 0.5:
                    label = model.names[cls]

                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    current_positions[i] = (cx, cy)

                    status = "NORMAL"
                    priority = "LOW"

                    # ---------------- HUMAN ----------------
                    if label == "person":

                        posture = "UNKNOWN"
                        person_img = frame[y1:y2, x1:x2]

                        if person_img.size > 0 and pose is not None:
                            rgb = cv2.cvtColor(person_img, cv2.COLOR_BGR2RGB)
                            result_pose = pose.process(rgb)

                            if result_pose.pose_landmarks:
                                landmarks = result_pose.pose_landmarks.landmark

                                ls = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                                lh = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

                                if abs(ls.y - lh.y) < 0.05:
                                    posture = "LYING ⚠️"
                                else:
                                    posture = "UPRIGHT"

                        if posture == "LYING ⚠️":
                            status = "INJURED 🚨"
                            priority = "HIGH"

                        elif i in prev_positions:
                            px, py = prev_positions[i]
                            dist = ((cx - px)**2 + (cy - py)**2)**0.5

                            if dist < movement_threshold:
                                status = "NOT MOVING ⚠️"
                                priority = "MEDIUM"

                    # ---------------- OTHER OBJECTS ----------------
                    else:
                        status = f"{label.upper()} DETECTED"

                    # ---------------- SEND DATA ----------------
                    data = {
                        "latitude": 20.2961,
                        "longitude": 85.8245,
                        "object": label,
                        "status": status,
                        "priority": priority,
                        "coordinates": [cx, cy]
                    }

                    send_data(data)

                    # ---------------- DRAW ----------------
                    color = (0, 255, 0)
                    if priority == "HIGH":
                        color = (0, 0, 255)
                    elif priority == "MEDIUM":
                        color = (0, 165, 255)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    cv2.putText(frame, label, (x1, y1 - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                    cv2.putText(frame, status, (x1, y2 + 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # ---------------- FLOW DETECTION ----------------
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None,
                0.5, 3, 15, 3, 5, 1.2, 0
            )

            mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            avg_motion = np.mean(mag)

            if avg_motion > 2:
                cv2.putText(frame, "WATER FLOW 🌊", (20, 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

            if avg_motion > 5:
                cv2.putText(frame, "STRONG WIND 💨", (20, 80),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        prev_gray = gray
        prev_positions = current_positions.copy()

        # ---------------- STREAM TO FLASK ----------------
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
