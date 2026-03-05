# Medical Vision Suite

Medical Vision Suite is a full-stack AI-assisted screening platform for:
- Chest X-ray classification
- Brain MRI tumor classification
- Skin lesion classification

It includes:
- React frontend for authentication, scan upload, and result/history pages
- Flask backend API for prediction and user/history management
- TensorFlow-based model inference and training scripts
- MySQL persistence for users, login events, and prediction history

## Features

- Role-based registration/login (`doctor`, `technician`)
- Profile update and password change
- Unified prediction endpoint for multiple scan types
- Prediction history with filtering/sorting
- Stored image uploads and image URL support
- Optional LAN access for frontend/backend

## Tech Stack

- Frontend: React, React Router, Axios
- Backend: Flask, Flask-CORS
- ML: TensorFlow/Keras, OpenCV, NumPy
- Database: MySQL (`mysql-connector-python`)
- Analysis/plots: scikit-learn, Matplotlib, Seaborn

## Project Structure

```text
medical_cnn_project/
  backend/
    app.py
    ml.py
    db.py
    config.py
    utils.py
    *.h5
    uploads/
  frontend/
    src/
    public/
    package.json
  train_*.py
  evaluate_*.py
  predict_*.py
  requirements.txt
```

## Prerequisites

- Python 3.10+ recommended
- Node.js 18+ and npm
- MySQL 8+

## Backend Setup (Flask)

1. Create and activate virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure MySQL connection via environment variables (PowerShell example):
```powershell
$env:MYSQL_HOST="127.0.0.1"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="Root@123"
$env:MYSQL_DATABASE="medical_cnn"
```

4. Start backend:
```bash
cd backend
python app.py
```

Default backend runs on:
- `http://127.0.0.1:5000`
- If configured with `host="0.0.0.0"`, it is accessible on LAN as `http://<your-ip>:5000`

## Frontend Setup (React)

1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Start frontend:
```bash
npm start
```

Frontend default:
- `http://localhost:3000`

API base URL behavior:
- Uses `REACT_APP_API_BASE_URL` if provided
- Otherwise uses `http://<browser-hostname>:5000`

Example override:
```powershell
$env:REACT_APP_API_BASE_URL="http://192.168.1.20:5000"
npm start
```

## Available API Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/profile`
- `PUT /auth/profile`
- `POST /auth/change-password`
- `GET /history`
- `POST /predict`
- `GET /uploads/<filename>`

## Database Initialization

On backend startup, `init_db()` ensures required tables exist:
- `users`
- `login_events`
- `predictions`

It also applies additive schema updates for missing columns when needed.

## Model Files Used by Backend

The backend loads these models from `backend/`:
- `medical_xray_finetuned.h5`
- `brain_tumor_mobilenet.h5`
- `skin_model_mobilenet_v2.h5`

## Training and Evaluation Scripts

Training scripts:
- `train_cnn.py`
- `train_transfer.py`
- `train_brain_mobilenet.py`
- `train_skin.py`
- `train_skin_mobilenet.py`
- `train_skin_mobilenet_v2.py`
- `fine_tune.py`

Evaluation scripts:
- `evaluate_medical_xray.py`
- `evaluate_brain.py`
- `evaluate_skin_mobilenet.py`

Prediction utilities:
- `predict.py`
- `predict_brain.py`
- `predict_skin.py`
- `predict_skin_mobilenet.py`

## Troubleshooting

- `Can't connect to MySQL`: verify MySQL service and env vars.
- `ModuleNotFoundError`: confirm virtual environment is active and requirements are installed.
- `CORS/network issue from phone/LAN`: run backend on `0.0.0.0` and open firewall port `5000`.
- `Model load error`: ensure required `.h5` files are present in `backend/`.
## Project Snippets
![iamge alt](https://github.com/ArfanZaid2004/Medical-Vision-Suite/blob/54d6f33e2c568575dbe37c9b296d8992daac1e11/Screenshot%202026-03-05%20103436.png)
## Notes

- Do not commit large datasets and trained artifacts unless intentionally versioning them.
- Keep secrets (`.env`, DB passwords, API keys) out of source control.
