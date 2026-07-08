<div align="center">

# 🌾 KrishiMitra — कृषि मित्र

### AI-Powered Smart Farming Platform for Indian Farmers 🇮🇳

*Empowering farmers with AI-driven crop recommendations, soil health analysis, and live weather intelligence.*

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web_App-black?style=for-the-badge&logo=flask)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-ML-orange?style=for-the-badge&logo=scikitlearn)
![XGBoost](https://img.shields.io/badge/XGBoost-AI-green?style=for-the-badge)
![SQLite](https://img.shields.io/badge/SQLite-Database-blue?style=for-the-badge&logo=sqlite)
![HTML](https://img.shields.io/badge/HTML-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-1572B6?style=for-the-badge&logo=css3)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

</div>

---

# 📖 Overview

**KrishiMitra** is a full-stack AI-powered farming platform designed to assist Indian farmers in making informed agricultural decisions.

The platform combines **Machine Learning**, **Soil Intelligence**, and **Live Weather Analytics** to recommend suitable crops, evaluate soil health, and provide weather-based farming insights through an easy-to-use web interface.

---

# ✨ Features

## 🌱 AI Crop Recommendation
- Predicts the most suitable crop
- Ensemble ML model:
  - Random Forest
  - Gradient Boosting
  - XGBoost
- Supports **22 crop classes**
- Returns ranked crop recommendations
- **95% Test Accuracy**

---

## 🌿 Soil Health Analysis

- Soil health score (0–100)
- Health classification
  - Healthy
  - Moderate
  - Poor
- Nutrient-wise analysis
- Micronutrient deficiency detection
- Fertilizer recommendations
- Lime recommendation
- Recovery timeline
- 5-step soil improvement plan

---

## 🌦 Live Weather Intelligence

- Current weather
- 7-day forecast
- City search
- Interactive map
- Temperature markers
- Weather alerts
  - Heat
  - Frost
  - Drought
  - Heavy Rain
- Monthly crop sowing calendar

---

## 🔐 Authentication

- User Registration
- Login
- Logout
- Password Hashing
- Session Management
- SQLite User Database

---

## 📰 Agriculture News

- Live Agriculture News
- GNews Integration
- Server-side API Proxy
- Sample News Fallback

---

# 🚀 Tech Stack

| Category | Technologies |
|----------|--------------|
| Backend | Flask |
| Machine Learning | Scikit-learn, XGBoost |
| Database | SQLite |
| Authentication | Flask-Login, Werkzeug |
| Frontend | HTML, CSS, JavaScript |
| Maps | Leaflet, OpenStreetMap |
| Weather API | Open-Meteo |
| Geocoding | Nominatim |
| News API | GNews |

---

# 🧠 Machine Learning

## Crop Recommendation

**Models**

- Random Forest
- Gradient Boosting
- XGBoost

**Technique**

Soft Voting Ensemble

**Output**

- Ranked Crop Predictions
- Confidence Scores

**Accuracy**

> **95% Test Accuracy**

---

## Soil Health Prediction

Model:

- MLPClassifier (Neural Network)

Outputs:

- Soil Health Class
- Soil Score
- Nutrient Report
- Improvement Suggestions

---

# 📂 Project Structure

```text
krishimitra/
│
├── app.py
├── config.py
├── requirements.txt
├── Procfile
│
├── data/
├── database/
├── models/
├── routes/
├── static/
└── templates/
```

---

# ⚙ Installation

Clone the repository

```bash
git clone https://github.com/your-username/krishimitra.git

cd krishimitra
```

Create virtual environment

```bash
python -m venv venv
```

Activate

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create environment file

```bash
cp .env.example .env
```

Run

```bash
python app.py
```

Open

```
http://localhost:5000
```

---

# 🔄 Retrain Models

```bash
python models/generate_crop_dataset.py

python models/generate_soil_dataset.py

python models/train_crop_model.py

python models/train_soil_model.py
```

---

# 🌍 APIs Used

| API | Purpose |
|------|----------|
| Open-Meteo | Live Weather |
| Nominatim | City Geocoding |
| Leaflet | Interactive Maps |
| OpenStreetMap | Map Tiles |
| GNews | Agriculture News |

---

# 📊 Database

SQLite stores

- Users
- Crop Queries
- Soil Analysis Reports

---

# 📸 Screenshots

> Add screenshots here

```
Landing Page

Dashboard

Crop Recommendation

Soil Analysis

Weather Dashboard
```

---

# 🌟 Highlights

- Full Stack Flask Application
- AI Powered Crop Recommendation
- Neural Network Soil Analysis
- Live Weather Dashboard
- Interactive Maps
- User Authentication
- Modern Responsive UI
- Free API Integrations
- SQLite Database
- Ready for Render Deployment

---

# 🚀 Deployment

Supports

- Render
- Railway
- Hugging Face Spaces

Start Command

```bash
gunicorn app:app
```

---

# 🔮 Future Improvements

- Multi-language Support
- Farmer Dashboard
- Crop Disease Detection
- Image-based Soil Analysis
- Government Scheme Integration
- SMS Notifications
- Voice Assistant
- Satellite Weather Analytics
- Market Price Prediction

---

# 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push the branch
5. Open a Pull Request

---

# 📄 License

This project is licensed under the MIT License.

---

<div align="center">

### 🌾 Empowering Indian Agriculture with Artificial Intelligence 🇮🇳

**Made with ❤️ using Flask, Machine Learning & Open Source Technologies**

</div>
