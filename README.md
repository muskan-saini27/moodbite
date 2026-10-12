# MoodBite — Mood-Based Food Recommendation System

MoodBite is a Django-based food recommendation web application that helps users discover food based on their mood, dietary preferences, cuisine, and budget.

## Features

- **Mood-Based Recommendations:** Discover food suggestions based on mood and hunger level.
- **Personalized Food Discovery:** Filter recommendations by dietary preferences, cuisine, and budget.
- **Food Details:** Explore information about recommended dishes.
- **User Accounts:** Register, log in, and manage personal preferences.
- **Saved Foods:** Save and revisit favorite dishes.
- **Recommendation History:** Review previous recommendations.
- **User Feedback:** Submit feedback on recommendations.
- **Analytics Dashboard:** View food and recommendation analytics.

## Technology Stack

- **Backend:** Python, Django
- **Data Analysis:** Pandas, NumPy
- **Machine Learning:** scikit-learn, Joblib
- **Image Processing:** Pillow
- **Database:** SQLite for local development
- **Frontend:** HTML, CSS, JavaScript

## Project Structure

```text
MoodBite/
├── accounts/
├── analytics/
├── config/
├── core/
├── data/
├── data_pipeline/
├── foods/
├── recommendations/
├── static/
├── templates/
├── manage.py
└── requirements.txt
```

## Installation

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd MoodBite
```

Replace `YOUR_REPOSITORY_URL` with your GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Import food data

If the repository includes the food dataset and the project's import command, run:

```bash
python manage.py import_foods
```

### 6. Start the development server

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in your browser.

## Testing

Run the automated tests with:

```bash
python manage.py test accounts analytics recommendations foods
```

The current test suite contains seven tests and passes in the development environment.

## Security Notes

- Keep secret keys and environment-specific settings out of version control.
- Do not commit local databases, virtual environments, or private credentials.
- Configure HTTPS and production security settings before deployment.

## Future Improvements

- Improve food image coverage.
- Add production deployment configuration.
- Continue improving recommendation quality and personalization.

## License

Choose and add a license before distributing this project for reuse.
