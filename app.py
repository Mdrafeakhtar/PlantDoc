from flask import Flask, render_template, request, redirect, send_from_directory, session
import numpy as np
import json
import uuid
import tensorflow as tf
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import base64
from PIL import Image
import qrcode

app = Flask(__name__)
app.secret_key = os.environ.get("PLANTDOC_SECRET_KEY", "change-this-secret-key")

# LOAD MODEL
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "plant_disease_recog_model_pwp.keras")
model = tf.keras.models.load_model(MODEL_PATH)

# LOAD DISEASE JSON (LIST WITH name, cause, cure)
with open(os.path.join(BASE_DIR, "plant_disease.json"), "r") as file:
    plant_disease = json.load(file)

# REQUIRED FOLDERS
os.makedirs(os.path.join(BASE_DIR, "uploadimages"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "static", "qrcodes"), exist_ok=True)

# USER STORAGE
USERS_FILE = os.path.join(BASE_DIR, "users.json")
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

history_data = []
history_full = []
last_farmer_name = ""
last_image_path = ""

# IMAGE SERVING
@app.route('/uploadimages/<path:filename>')
def uploaded_images(filename):
    return send_from_directory(os.path.join(BASE_DIR, 'uploadimages'), filename)

# USER HELPERS
def get_users():
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["username"]
        pwd = request.form["password"]

        users = get_users()
        for u in users:
            if u["username"] == user and u["password"] == pwd:
                session["user"] = user
                return redirect("/")
        return redirect("/login?error=Invalid+username+or+password")

    return render_template("login.html")

# SIGNUP
@app.route("/signup", methods=["POST"])
def signup():
    username = request.form["username"]
    password = request.form["password"]

    users = get_users()
    for u in users:
        if u["username"] == username:
            return redirect("/login?error=That+username+is+already+registered")

    users.append({"username": username, "password": password})
    save_users(users)
    return redirect("/login")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# HOME
@app.route("/", methods=["GET"])
def home():
    if "user" not in session:
        return redirect("/login")
    return render_template("home.html")

# IMAGE PREPROCESSING
def extract_features(image):
    image = tf.keras.utils.load_img(image, target_size=(160,160))
    feature = tf.keras.utils.img_to_array(image)
    feature = np.array([feature])
    return feature

# MODEL PREDICTION (CAUSE + CURE METHOD)
# Below this confidence, we don't trust the model's guess enough to call it a leaf.
CONFIDENCE_THRESHOLD = 0.70

def model_predict(image):
    img = extract_features(image)
    prediction = model.predict(img)
    confidence = float(np.max(prediction))
    prediction_label = plant_disease[prediction.argmax()]
    return prediction_label, confidence

# UPLOAD + CAMERA + RESULT WITH NON-LEAF CHECK
@app.route('/upload/', methods=['POST','GET'])
def uploadimage():
    global last_farmer_name, last_image_path

    if request.method == "POST":
        last_farmer_name = request.form.get("farmer_name")

        camera_data = request.form.get("camera_image")

        if camera_data and camera_data.startswith("data:image"):
            header, encoded = camera_data.split(",", 1)
            image_data = base64.b64decode(encoded)

            temp_name = os.path.join(BASE_DIR, "uploadimages", f"temp_{uuid.uuid4().hex}.jpg")
            with open(temp_name, "wb") as f:
                f.write(image_data)

            final_path = f'/{temp_name}'

        else:
            image = request.files['img']
            temp_name = os.path.join(BASE_DIR, "uploadimages", f"temp_{uuid.uuid4().hex}")
            save_path = f'{temp_name}_{image.filename}'
            image.save(save_path)
            final_path = f'/{save_path}'

        last_image_path = final_path.lstrip("/")

        # PREDICT
        prediction, confidence = model_predict(f'.{final_path}')

        # NON-LEAF CHECK — either the model explicitly says "no leaf",
        # or it isn't confident enough in any leaf/disease class to trust the guess.
        if prediction["name"] == "Background_without_leaves" or confidence < CONFIDENCE_THRESHOLD:
            return render_template(
                'home.html',
                not_leaf=True,
                result=False,
                imagepath=final_path
            )

        # NORMAL LEAF FLOW
        history_data.append(prediction["name"])
        history_full.append(prediction)

        return render_template(
            'home.html',
            result=True,
            imagepath=final_path,
            prediction=prediction,
            history=history_data[-5:],
            not_leaf=False
        )

    else:
        return redirect('/')

# MULTI-PAGE PDF REPORT
@app.route("/download-report")
def download_report():
    file_path = os.path.join(BASE_DIR, "static", "report.pdf")
    c = canvas.Canvas(file_path, pagesize=letter)

    now = datetime.now().strftime("%d-%m-%Y   %I:%M %p")
    last_prediction = history_full[-1]

    # QR CODE
    qr_data = f"Farmer: {last_farmer_name}, Disease: {last_prediction['name']}, Date: {now}"
    qr_img = qrcode.make(qr_data)
    qr_path = os.path.join(BASE_DIR, "static", "qrcodes", "qr_latest.png")
    qr_img.save(qr_path)

    # PAGE 1
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 770, "Plant Disease Detection Report")

    c.setFont("Helvetica", 11)
    c.drawString(50, 740, f"Farmer Name: {last_farmer_name}")
    c.drawString(50, 720, f"Date & Time: {now}")
    c.drawString(50, 700, f"Disease Name: {last_prediction['name']}")

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 670, "Cause:")
    c.setFont("Helvetica", 11)
    c.drawString(50, 650, last_prediction["cause"])

    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, 620, "Cure:")
    c.setFont("Helvetica", 11)
    c.drawString(50, 600, last_prediction["cure"])

    if os.path.exists(last_image_path):
        c.drawImage(last_image_path, 350, 550, width=180, height=180)

    c.drawImage(qr_path, 350, 350, width=180, height=180)

    c.showPage()

    # HISTORY PAGES
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 770, "Prediction History")

    y = 740
    for item in history_full:
        c.setFont("Helvetica", 11)
        c.drawString(50, y, f"Disease: {item['name']}")
        y -= 15
        c.drawString(60, y, f"Cause: {item['cause']}")
        y -= 15
        c.drawString(60, y, f"Cure: {item['cure']}")
        y -= 30

        if y < 100:
            c.showPage()
            y = 770

    c.save()
    return send_from_directory(os.path.join(BASE_DIR, "static"), "report.pdf", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)

