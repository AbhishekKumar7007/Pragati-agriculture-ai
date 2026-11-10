# Pragati — Flask Starter Project

A student project starter for an agriculture assistant. It includes a working Flask/SQLite account flow, Crop Health Passport, weather lookup via Open-Meteo, a rule-based symptom checker, and UI placeholders for disease scanning and multilingual assistant features.

## Included features

- Registration and login using hashed passwords.
- Six-digit email OTP verification (10-minute expiry, five-attempt limit, resend option).
- SQLite database initialised automatically when `app.py` starts.
- Crop Health Passport: add, search, and view crop records.
- Weather-aware support: current conditions and a 3-day forecast (internet required).
- Rule-based symptom checker that gives cautious next steps, not a confirmed diagnosis.
- Disease Scanner and Assistant pages clearly marked as prototypes.
- Responsive HTML/CSS, a first-visit language selection screen (12 languages), and browser speech features for the assistant demo.

## Requirements

- Python 3.10+ recommended.
- Internet connection for installing packages and fetching weather.
- VS Code (optional but recommended).

## Run on Windows (PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use Command Prompt:
```bat
.venv\\Scripts\\activate.bat
```
Then run `pip install -r requirements.txt` and `python app.py`.

Open `http://127.0.0.1:5000`.

## Email OTP verification

For local testing, if SMTP environment variables are not configured, the OTP is printed in the VS Code terminal. This is a development fallback only; do not use it in production.

To send real email OTPs, set these environment variables before running Flask:
- `SMTP_HOST` (for example, your email provider's SMTP server)
- `SMTP_PORT` (usually `587`)
- `SMTP_USER`
- `SMTP_PASSWORD` (use an app password where required; do not hard-code it)
- `SMTP_FROM`
- `SECRET_KEY` (set a long random value)

The OTP expires after 10 minutes and is limited to five verification attempts. A verified account is required to log in.

## Language selection

On first visit, Pragati opens a language-selection page with English, Hindi, Punjabi, Bengali, Tamil, Telugu, Marathi, Gujarati, Urdu, Arabic, French, and Spanish. The selected language is stored in the Flask session and can be changed using the language link in the navigation. This version adds the language picker and language preference; not every page's content is fully translated yet.

## Demo flow

1. Register with a name, email, and password (8+ characters).
2. Log in.
3. Open Dashboard.
4. Add a Crop Health Passport entry and search records.
5. Open Weather and enter a city.
6. Try the symptom checker.

## Important limitations

- The disease scanner is a UI prototype. No trained machine-learning model is included, so it does not actually classify plant images.
- The multilingual assistant is a browser-based demo with a small rule-based response set, not a connected large language model. Speech features depend on browser and operating system support.
- Symptom checker results are general possibilities, not medical-grade or agronomic diagnoses. Confirm issues with a local agricultural extension service before applying pesticides or fertilizer.
- This starter uses basic session authentication and is intended for local learning/demo use. Before production, add CSRF protection, rate limiting, email verification, password reset, secure deployment settings, and user-scoped data access throughout.
- Weather API requires internet access. Open-Meteo values and weather codes are shown without guarantees for agricultural decisions.


Homepage updates: replaced the hero background with the user-provided farmer/advisor image; removed the right-side Farmer Services panel, Farmer Services nav link, and helpline/utility strip; moved language selection to an inline dropdown in the main navigation. Language selection posts to the Flask session and does not open a separate selection page.


## Visual update
- Added user-provided images to Weather Support, Dashboard, Crop Health Passport, Symptom Checker, Disease Scanner, and Farm Assistant pages.
- Added the supplied video as a muted, looping Registration page background with a seedling-image poster fallback.
- Helpdesk now displays only 7505257763.
- Images are decorative design assets. Weather values still depend on the live weather API; crop diagnosis remains a prototype until a trained model is integrated.
