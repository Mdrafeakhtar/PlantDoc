# PlantDoc — AI Plant Disease Detection System

PlantDoc is a Flask-based web application that uses a TensorFlow/Keras image-classification model to identify plant leaf diseases from uploaded images or a camera capture.

## Features

- User login and registration
- Upload a plant-leaf image
- Capture a leaf image using the device camera
- AI-based plant disease classification
- Confidence-based rejection for uncertain/non-leaf images
- Disease cause and recommended cure information
- Recent scan history during the current session
- PDF diagnostic report generation
- QR code containing report information
- Responsive web interface

## Technology Stack

- Python
- Flask
- TensorFlow / Keras
- NumPy
- Pillow
- ReportLab
- QRCode
- HTML / CSS / JavaScript

## Project Structure

```text
PlantDoc/
├── app.py
├── plant_disease.json
├── requirements.txt
├── README.md
├── .gitignore
├── models/
│   └── README.md
├── templates/
│   ├── home.html
│   └── login.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── scanner.js
│   └── qrcodes/
│       └── .gitkeep
└── uploadimages/
```

## Run locally

### 1. Create a virtual environment

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Download the trained model

The trained model is approximately 203 MB, so it is not included in this GitHub source package.

Download it from:

https://drive.google.com/file/d/1Ond7UzrNOfdAXWedjlZr2sDXYU6MRBuj/view?usp=sharing

Place it at:

```text
models/plant_disease_recog_model_pwp.keras
```

### 4. Set the Flask secret key

macOS/Linux:

```bash
export PLANTDOC_SECRET_KEY="replace-with-a-long-random-secret"
```

Windows PowerShell:

```powershell
$env:PLANTDOC_SECRET_KEY="replace-with-a-long-random-secret"
```

### 5. Start the application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

On first run, PlantDoc creates a local `users.json` file. It is intentionally ignored by Git because it contains user credentials.

## GitHub upload

After creating an empty repository named `PlantDoc` on GitHub:

```bash
git init
git add .
git commit -m "Initial commit: PlantDoc AI plant disease detection"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/PlantDoc.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username.

## Important: trained model

The trained model is about 203 MB. GitHub's normal repository upload has a 100 MB per-file limit, so the model is excluded by `.gitignore`.

If you later want the model inside GitHub, use Git LFS or another large-file/model hosting service.

## Security

Do not commit:

- `users.json`
- `.env`
- passwords
- API keys
- private credentials
- private datasets

The original development `users.json` contained plaintext passwords. It has deliberately been excluded from this GitHub-ready package.

## Model details

The application expects:

```text
models/plant_disease_recog_model_pwp.keras
```

Input images are resized to `160 × 160` before prediction.

## Disclaimer

PlantDoc is an educational/research project. Model predictions and treatment information should be independently verified by an appropriate agricultural professional before making crop-management decisions.

## Author

**Md Rafe Akhtar**  
B.Tech — Electronics & Communication Engineering (Avionics)  
Central University of Jammu

### Suggested GitHub repository description

> AI-powered plant disease detection web application built with Flask and TensorFlow/Keras, featuring camera/image diagnosis, disease information, PDF reports, and QR-code generation.
