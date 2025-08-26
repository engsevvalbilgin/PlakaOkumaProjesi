# **Vehicle Tracking and License Plate Recognition Project**

This project is a **real-time vehicle tracking and license plate recognition system** for monitoring vehicles entering and exiting a facility. The system uses **YOLOv8 deep learning model for license plate detection**, OCR for reading plates, and a **SQLite database** to store entry and exit records. The user interface is built with **Streamlit**.

---

## **Features**

* Real-time license plate detection using YOLOv8
* OCR-based license plate reading
* Vehicle entry and exit timestamp logging
* Viewing and filtering vehicles currently inside
* Download records as CSV
* Interactive web-based interface with Streamlit
* Supports live video input from a camera

---

## **Project Structure**

```
PlakaTakipProjesi/
├── data/
│   └── database.db              # SQLite database
├── scripts/
│   ├── create_database.py       # Creates database and adds sample data
│   ├── detect_plate.py          # Detects plates from camera or video
│   └── tracker.py               # Tracks vehicles and calculates entry/exit times
├── app/
│   └── streamlit_app.py         # User interface
├── models/
│   └── plate_detection/best.pt  # Trained YOLO license plate detection model
├── requirements.txt             # Required Python packages
└── README.md
```

---

## **Installation**

1. Clone the repository:

```bash
git clone <your_repo_link>
cd PlakaTakipProjesi
```

2. Create and activate a virtual environment (optional but recommended):

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Create the database:

```bash
python scripts/create_database.py
```

---

## **Usage**

* Run the Streamlit app:

```bash
streamlit run app/streamlit_app.py
```

* In the browser interface, you can:

  * View vehicles currently inside
  * Search by license plate
  * Filter by date ranges
  * Download data as CSV
* **Live camera input:** The system can read vehicles and their plates directly from a live camera feed using the YOLOv8 model and update the database in real-time.

---

## **Development and Integration**

* `scripts/detect_plate.py` → Detects license plates from camera or video.
* `scripts/tracker.py` → Tracks vehicles, calculates entry/exit durations, and updates `database.db`.
* `app/streamlit_app.py` → Visualizes the database in an interactive interface.

---

## **Notes**

* This project is a demo; for real-world deployment, camera calibration and OCR accuracy adjustments may be necessary.
* SQLite is suitable for single-user setups; for larger scale or multi-user applications, consider PostgreSQL or MySQL.
* dataset link:https://www.kaggle.com/datasets/smaildurcan/turkish-license-plate-dataset/data

---

If you want, I can also **add a “Live Camera Demo” section with screenshots and instructions on integrating your camera feed into the Streamlit app**, making the README GitHub-ready and visually appealing.

Do you want me to do that?
