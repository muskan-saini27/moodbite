# MoodBite — Mood-Based Food Recommendation System

MoodBite is a Django-based food recommendation web application that helps users discover food based on their mood, dietary preferences, budget, and food choices. It combines a food dataset, recommendation logic, and personalized features in one web platform.

## Features

- **Mood-Based Recommendations:** Discover food suggestions based on mood and preferences.
- **Personalized Food Discovery:** Filter recommendations using dietary requirements, cuisine, and budget.
- **Food Details:** Explore information about recommended dishes.
- **User Accounts:** Register, log in, and manage personal preferences.
- **Saved Foods:** Save and revisit favorite dishes.
- **Recommendation History:** Review previous recommendations.
- **Analytics Dashboard:** View food and recommendation insights.
- **Search:** Find foods from the available dataset.
- **Feedback:** Submit feedback on food recommendations.

## Technology Stack

- **Backend:** Python, Django
- **Database:** SQLite
- **Data Processing:** Pandas
- **Frontend:** HTML, CSS, JavaScript, Django Templates
- **Recommendation Engine:** Custom recommendation logic and similarity-based recommendations

## Project Structure

```text
MoodBite/
├── accounts/
├── analytics/
├── config/
├── core/
├── data/
├── foods/
├── recommendations/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd MoodBite
```

Replace `YOUR_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Running Tests

Run the full Django test suite:

```bash
python manage.py test
```

## Configuration and Security

The project uses environment-based settings for configuration. For production deployment:

- Set a strong, unique `DJANGO_SECRET_KEY`.
- Set `DJANGO_DEBUG=False`.
- Configure `DJANGO_ALLOWED_HOSTS` for your actual domain.
- Configure HTTPS and secure cookies.
- Use a production-ready email backend if email delivery is required.

Never commit production secrets, private credentials, or sensitive user data to version control.

## Current Status

The main application flows have been manually tested, and the existing Django test suite passes. Further production deployment, security hardening, and dataset quality checks should be completed before a public release.

## Future Improvements

- Improve food image coverage and consistency.
- Validate food prices and nutritional information.
- Expand automated tests for recommendation quality and user permissions.
- Improve production deployment and monitoring.

## Author

**Muskan Saini**

MoodBite — Discover food that matches your mood.
