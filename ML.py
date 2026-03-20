# ==========================================
# SKY GUARDIAN - FINAL ML SYSTEM (FIXED)
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
        requests.post("http://127.0.0.1:5000/update", json=data)
        print("📡 Sent:", data)
    except Exception as e:
        print("❌ API Error:", e)

# ------------------------------
# MODE SELECTION
# ------------------------------
print("===================================")
print("🚀 SKY GUARDIAN SYSTEM")
print("===================================")
print("1 - Live Camera")
print("2 - Video File")
print("===================================")

choice = input("Enter choice (1/2): ")

if choice == "1":
    cap = cv2.VideoCapture(0)
    print("📷 Using Live Camera...")
elif choice == "2":
    video_path = input("📂 Enter video file path: ")
    cap = cv2.VideoCapture(video_path)
    print(f"🎥 Processing video: {video_path}")
else:
    print("❌ Invalid choice")
    exit()

if not cap.isOpened():
    print("❌ Error opening video source")
    exit()

# ------------------------------
# SAVE OUTPUT VIDEO
# ------------------------------
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

# ------------------------------
# LOAD MODEL
# ------------------------------
model = YOLO("yolov8n.pt")

# ------------------------------
# MEDIAPIPE SETUP
# ------------------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# ------------------------------
# VARIABLES
# ------------------------------
prev_positions = {}
movement_threshold = 15
prev_gray = None

frame_count = 0
anomaly_count = 0

print("🚀 SYSTEM STARTED")

# ==========================================
# MAIN LOOP
# ==========================================
while True:
    ret, frame = cap.read()

    if not ret:
        print("✅ Processing complete")
        break

    frame = cv2.resize(frame, (640, 480))
    frame_count += 1

    results = model(frame)
    current_positions = {}

    for r in results:
        for i, box in enumerate(r.boxes):

            cls = int(box.cls[0])
            conf = float(box.conf[0])

            if conf > 0.5:

                label = model.names[cls]

                # --------------------------
                # BOUNDING BOX
                # --------------------------
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx = (x1 + x2) // 2
                cy = (y1 + y2) // 2

                current_positions[i] = (cx, cy)

                # --------------------------
                # DEFAULT STATUS
                # --------------------------
                status = "NORMAL"
                priority = "LOW"

                # --------------------------
                # HUMAN LOGIC
                # --------------------------
                if label == "person":

                    posture = "UNKNOWN"
                    person_img = frame[y1:y2, x1:x2]

                    if person_img.size > 0:
                        rgb = cv2.cvtColor(person_img, cv2.COLOR_BGR2RGB)
                        result_pose = pose.process(rgb)

                        if result_pose.pose_landmarks:
                            landmarks = result_pose.pose_landmarks.landmark

                            left_shoulder = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
                            left_hip = landmarks[mp_pose.PoseLandmark.LEFT_HIP.value]

                            if abs(left_shoulder.y - left_hip.y) < 0.05:
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

                # --------------------------
                # NON-HUMAN OBJECTS
                # --------------------------
                else:
                    status = f"{label.upper()} DETECTED"
                    priority = "LOW"

                # --------------------------
                # COUNT ANOMALY
                # --------------------------
                if priority == "HIGH":
                    anomaly_count += 1

                # --------------------------
                # SEND DATA TO BACKEND
                # --------------------------
                data = {
                    "latitude": 20.2961,
                    "longitude": 85.8245,
                    "object": label,
                    "status": status,
                    "priority": priority,
                    "coordinates": [cx, cy]
                }

                send_data(data)   # ✅ FIXED

                # --------------------------
                # DRAW
                # --------------------------
                color = (0, 255, 0)
                if priority == "HIGH":
                    color = (0, 0, 255)
                elif priority == "MEDIUM":
                    color = (0, 165, 255)

                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                cv2.putText(frame, f"{label}", (x1, y1 - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                cv2.putText(frame, status, (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                cv2.putText(frame, f"Priority: {priority}", (x1, y2 + 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

                cv2.putText(frame, f"({cx},{cy})", (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)

                if priority == "HIGH":
                    print("🚨 CRITICAL ALERT DETECTED!")

    # --------------------------
    # WATER + WIND DETECTION
    # --------------------------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    if prev_gray is not None:
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, gray,
            None, 0.5, 3, 15, 3, 5, 1.2, 0
        )

        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        avg_motion = np.mean(magnitude)

        if avg_motion > 2:
            cv2.putText(frame, "WATER FLOW 🌊", (20,40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)

        if avg_motion > 5:
            cv2.putText(frame, "STRONG WIND 💨", (20,80),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)

    prev_gray = gray
    prev_positions = current_positions.copy()

    out.write(frame)

    cv2.imshow("🚁 SKY GUARDIAN AI SYSTEM", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

# ------------------------------
# REPORT
# ------------------------------
print("\n📊 ANALYSIS REPORT")
print(f"Total Frames: {frame_count}")
print(f"Critical Anomalies: {anomaly_count}")

if anomaly_count > 0:
    print("🚨 ALERT: Anomalies detected")
else:
    print("✅ No anomalies detected")

# ------------------------------
# CLEANUP
# ------------------------------
cap.release()
out.release()
cv2.destroyAllWindows()