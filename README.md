🚁 SKY GUARDIAN
AI-Powered Real-Time Surveillance & Anomaly Detection System

📌 Overview
Sky Guardian is an intelligent surveillance system that uses computer vision and machine learning (YOLOv8) to detect objects and anomalies in real-time from IP camera or drone feeds.It provides a live dashboard with map tracking, helping in faster decision-making for security and disaster management.

🎯 Objectives-
~Enable real-time object detection using AI
~Reduce manual monitoring
~Provide location-based tracking using maps
~Store detection data for analysis

🚀 Features
~Live IP camera / drone video feed
~Real-time object detection using YOLOv8
~Interactive map with live coordinates (Leaflet.js)
~Data visualization using charts
~Automatic CSV data logging
~Web-based dashboard

🏗️ System Architecture
IP Camera / Drone
↓
Frame Capture (OpenCV)
↓
YOLOv8 Model (Detection)
↓
Backend API (Flask)
↓
CSV Storage
↓
Frontend Dashboard (Map + Charts)

🛠️ Tech Stack
Frontend:
HTML
CSS
JavaScript
Leaflet.js

Backend:
Python
Flask

Machine Learning:
YOLOv8 (Ultralytics)
OpenCV

🧠 Machine Learning Model
Model: YOLOv8 (Pre-trained)
Variant: YOLOv8n (Nano)


📂 Project Structure
Sky-Guardian/
│
├── backend/
│ ├── app.py
│ └── data.csv
│
├── ml/
│ ├── detection.py
│ └── model files
│
├── frontend/
│ └── index.html
│
└── README.md

⚙️ Installation & Setup
Clone the repository
git clone https://github.com/your-username/sky-guardian.git
cd sky-guardian
Install dependencies
pip install -r requirements.txt
Run backend
cd backend
python app.py
Run ML model
cd ml
python detection.py
Open frontend
Open index.html in your browser


👥 Team
Alok Kumar Sharma – Hardware (Drone)
Saikrishna Pal – Hardware (Drone)
Sanvi Shan – Software (Frontend, Backend, ML Integration)
Sakshi – Research and Development

