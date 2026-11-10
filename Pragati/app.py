import os
import sqlite3
import secrets
import smtplib
from email.message import EmailMessage
from datetime import date, datetime, timedelta
from functools import wraps

from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from crop_passport import init_passport_db, add_crop_passport_entry, get_crop_history
from weather_service import get_weather

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pragati.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-this-secret-key")
OTP_EXPIRY_MINUTES = 10


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_app_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                is_verified INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Upgrade an older starter database safely.
        columns = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "is_verified" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN is_verified INTEGER NOT NULL DEFAULT 0")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS otp_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                otp_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    init_passport_db(DB_PATH)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "warning")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def hash_otp(otp):
    # Hashing means the actual OTP is not stored in the database.
    import hashlib
    return hashlib.sha256(otp.encode("utf-8")).hexdigest()


def send_otp_email(email, otp):
    """Send email if SMTP is configured; otherwise print OTP for local development."""
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    sender = os.environ.get("SMTP_FROM", smtp_user or "")
    if smtp_host and smtp_user and smtp_password and sender:
        message = EmailMessage()
        message["Subject"] = "Your Pragati verification code"
        message["From"] = sender
        message["To"] = email
        message.set_content(
            f"Your Pragati verification code is {otp}.\n"
            f"It expires in {OTP_EXPIRY_MINUTES} minutes. If you did not request this, ignore this email."
        )
        with smtplib.SMTP(smtp_host, smtp_port, timeout=15) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(message)
        return "email"
    print(f"\n[Pragati development OTP] {email}: {otp}\n")
    return "terminal"


def create_and_send_otp(email):
    otp = f"{secrets.randbelow(1_000_000):06d}"
    expires_at = (datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)).isoformat(timespec="seconds")
    with get_db() as conn:
        conn.execute("DELETE FROM otp_requests WHERE email = ?", (email,))
        conn.execute(
            "INSERT INTO otp_requests (email, otp_hash, expires_at, attempts) VALUES (?, ?, ?, 0)",
            (email, hash_otp(otp), expires_at)
        )
    delivery = send_otp_email(email, otp)
    return delivery


SUPPORTED_LANGUAGES = {
    "en": "English", "hi": "हिन्दी", "pa": "ਪੰਜਾਬੀ", "bn": "বাংলা",
    "ta": "தமிழ்", "te": "తెలుగు", "mr": "मराठी", "gu": "ગુજરાતી",
    "ur": "اردو", "ar": "العربية", "fr": "Français", "es": "Español"
}


@app.context_processor
def inject_language_settings():
    return {"supported_languages": SUPPORTED_LANGUAGES, "current_language": session.get("language", "en")}


@app.route("/language", methods=["GET", "POST"])
def language():
    if request.method == "POST":
        selected = request.form.get("language", "en")
        if selected not in SUPPORTED_LANGUAGES:
            selected = "en"
        session["language"] = selected
        destination = request.form.get("next", "")
        if destination.startswith("/") and not destination.startswith("//"):
            return redirect(destination)
        return redirect(url_for("index"))
    return render_template("language_select.html")




ABOUT_PAGES = {
    "history": {
        "title": "History",
        "heading": "How Pragati started",
        "paragraphs": [
            "Pragati was designed as a student project to explore how digital tools can make everyday farming information easier to access.",
            "The project brings together a crop-care assistant concept, weather information, a Crop Health Passport for dated field observations, a symptom checker, and a multilingual assistant interface.",
            "The website is being developed iteratively. New crop-specific information and verified local resources can be added as the project grows."
        ],
        "bullets": ["Farmer-friendly homepage and language selector", "Crop Health Passport using a local SQLite database", "Weather lookup using the Open-Meteo service", "Educational crop symptom guidance and assistant interface"]
    },
    "structure": {
        "title": "Organizational Structure",
        "heading": "How the Pragati project is organized",
        "paragraphs": [
            "Pragati is a software prototype, not an agricultural department. Its modules are organized around common farmer tasks so users can find the relevant tool from the homepage.",
            "The web layer is built with Python and Flask. HTML templates and CSS provide the interface, while SQLite stores user accounts and crop passport records. Weather information is requested from an external weather API.",
            "AI disease identification is not represented as a trained diagnostic model unless a model is separately installed and integrated."
        ],
        "bullets": ["User interface: HTML, CSS and JavaScript", "Application routes: Python Flask", "Local records: SQLite", "Weather: Open-Meteo API", "Crop tools: Passport, symptom checker, disease scanner interface and farm assistant"]
    },
    "objective": {
        "title": "Objective",
        "heading": "The goal of Pragati",
        "paragraphs": [
            "The objective of Pragati is to bring useful crop-care tools into one simple, accessible website for farmers.",
            "The project aims to help users record crop growth and observations, check local weather, explore possible causes of crop symptoms, and access farming guidance in a comfortable language.",
            "Pragati is intended to support informed decisions, not replace agricultural experts, laboratory testing, or official government services."
        ],
        "bullets": ["Make common farming tools easier to discover", "Maintain dated crop-health observations", "Present weather information for planning field work", "Offer a simple multilingual interface", "Keep advice transparent and encourage expert verification"]
    }
}


@app.route("/about/<section>")
def about_page(section):
    page = ABOUT_PAGES.get(section)
    if page is None:
        return redirect(url_for("index"))
    return render_template("about_page.html", page=page)


@app.route("/")
def index():
    # Always open the Pragati homepage first; language selection is optional in the navbar.
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name, a valid email, and a password of at least 8 characters.", "danger")
            return render_template("register.html")
        with get_db() as conn:
            existing = conn.execute("SELECT id, is_verified FROM users WHERE email = ?", (email,)).fetchone()
            if existing and existing["is_verified"]:
                flash("An account with that email is already verified. Please log in.", "warning")
                return redirect(url_for("login"))
            if existing:
                conn.execute(
                    "UPDATE users SET name = ?, password_hash = ? WHERE email = ?",
                    (name, generate_password_hash(password), email)
                )
            else:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash, is_verified) VALUES (?, ?, ?, 0)",
                    (name, email, generate_password_hash(password))
                )
        try:
            delivery = create_and_send_otp(email)
        except Exception:
            app.logger.exception("Could not send OTP email")
            flash("Could not send email. Check SMTP settings, or use development mode and check the VS Code terminal.", "danger")
            return render_template("register.html")
        session["pending_email"] = email
        if delivery == "terminal":
            flash("Development mode: OTP was printed in the VS Code terminal. Enter it on the verification page.", "info")
        else:
            flash("A verification code was sent to your email address.", "success")
        return redirect(url_for("verify_otp"))
    return render_template("register.html")


@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():
    email = session.get("pending_email")
    if not email:
        flash("Please register first to request a verification code.", "warning")
        return redirect(url_for("register"))
    if request.method == "POST":
        otp = request.form.get("otp", "").strip()
        if not (otp.isdigit() and len(otp) == 6):
            flash("Enter the six-digit code.", "danger")
            return render_template("verify_otp.html", email=email)
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM otp_requests WHERE email = ? ORDER BY id DESC LIMIT 1",
                (email,)
            ).fetchone()
            if not row:
                flash("No active code found. Request a new one.", "danger")
                return render_template("verify_otp.html", email=email)
            if row["attempts"] >= 5:
                conn.execute("DELETE FROM otp_requests WHERE email = ?", (email,))
                flash("Too many attempts. Please register again to get a new code.", "danger")
                return redirect(url_for("register"))
            expires_at = datetime.fromisoformat(row["expires_at"])
            if datetime.utcnow() > expires_at:
                conn.execute("DELETE FROM otp_requests WHERE email = ?", (email,))
                flash("The code has expired. Please register again to request a new code.", "danger")
                return render_template("verify_otp.html", email=email)
            if hash_otp(otp) != row["otp_hash"]:
                conn.execute("UPDATE otp_requests SET attempts = attempts + 1 WHERE id = ?", (row["id"],))
                flash("Incorrect code. Please try again.", "danger")
                return render_template("verify_otp.html", email=email)
            conn.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (email,))
            conn.execute("DELETE FROM otp_requests WHERE email = ?", (email,))
        session.pop("pending_email", None)
        flash("Email verified successfully. You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("verify_otp.html", email=email)


@app.route("/resend-otp", methods=["POST"])
def resend_otp():
    email = session.get("pending_email")
    if not email:
        flash("Please register first.", "warning")
        return redirect(url_for("register"))
    try:
        delivery = create_and_send_otp(email)
        if delivery == "terminal":
            flash("Development OTP printed in the VS Code terminal.", "info")
        else:
            flash("A new verification code was emailed to you.", "success")
    except Exception:
        app.logger.exception("Could not resend OTP")
        flash("Could not send a new code. Check your SMTP settings.", "danger")
    return redirect(url_for("verify_otp"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            if not user["is_verified"]:
                session["pending_email"] = email
                flash("Please verify your email with the OTP before logging in.", "warning")
                return redirect(url_for("verify_otp"))
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            flash("Welcome back!", "success")
            return redirect(url_for("dashboard"))
        flash("Incorrect email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name=session.get("user_name", "Farmer"))


@app.route("/weather", methods=["GET", "POST"])
@login_required
def weather():
    result = None
    city = ""
    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if city:
            try:
                result = get_weather(city)
            except Exception:
                result = {"error": "Weather service is unavailable. Check your internet connection and try again."}
    return render_template("weather.html", result=result, city=city)


@app.route("/passport", methods=["GET", "POST"])
@login_required
def passport():
    if request.method == "POST":
        crop_name = request.form.get("crop_name", "").strip()
        growth_stage = request.form.get("growth_stage", "").strip()
        observation = request.form.get("observation", "").strip()
        log_date = request.form.get("log_date", "").strip() or date.today().isoformat()
        try:
            entry_id = add_crop_passport_entry(
                crop_name, growth_stage, observation, log_date,
                db_path=DB_PATH, user_id=session["user_id"]
            )
            flash(f"Crop health record #{entry_id} saved.", "success")
            return redirect(url_for("passport"))
        except (ValueError, sqlite3.Error) as exc:
            flash(str(exc) or "Could not save record.", "danger")
    search = request.args.get("q", "").strip()
    records = get_crop_history(search or None, db_path=DB_PATH, user_id=session["user_id"])
    return render_template(
        "passport.html", records=records, search=search, today=date.today().isoformat()
    )


@app.route("/symptom-checker", methods=["GET", "POST"])
@login_required
def symptom_checker():
    result = None
    if request.method == "POST":
        leaf = request.form.get("leaf", "")
        soil = request.form.get("soil", "")
        spots = request.form.get("spots", "")
        pests = request.form.get("pests", "")
        if leaf == "yellow":
            result = {"title": "Possible nutrient issue or watering stress",
                      "detail": "Yellowing can be linked to nutrient deficiency, excess water, poor drainage, or natural leaf aging. Check soil moisture and compare older and newer leaves.",
                      "actions": ["Check soil moisture before watering again.", "Inspect several plants for the same pattern.", "Ask a local agricultural extension officer before applying fertilizer."]}
        elif spots == "yes":
            result = {"title": "Possible leaf spot or other leaf disease",
                      "detail": "Spots may have fungal, bacterial, pest-related, or environmental causes. This form cannot confirm a diagnosis.",
                      "actions": ["Photograph both sides of affected leaves.", "Avoid wetting foliage when watering.", "Seek local expert advice if symptoms spread."]}
        elif pests == "yes":
            result = {"title": "Possible pest damage",
                      "detail": "Look for insects, eggs, webbing, or feeding marks on leaves and young shoots.",
                      "actions": ["Inspect several plants.", "Use an integrated pest management approach.", "Confirm the pest before choosing a treatment."]}
        elif soil == "dry":
            result = {"title": "Possible water stress",
                      "detail": "Dry soil may contribute to wilting, leaf curling, or slow growth.",
                      "actions": ["Check moisture below the surface.", "Water according to crop needs and local conditions.", "Avoid waterlogging."]}
        else:
            result = {"title": "More observation is needed",
                      "detail": "These answers do not point to one clear cause. Multiple problems can look alike.",
                      "actions": ["Record when symptoms began.", "Take clear photos of the plant and affected leaves.", "Consult a local agriculture specialist if symptoms spread."]}
    return render_template("symptom_checker.html", result=result)


@app.route("/disease-scanner")
@login_required
def disease_scanner():
    return render_template("disease_scanner.html")


@app.route("/assistant")
@login_required
def assistant():
    return render_template("assistant.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", code=404, message="Page not found."), 404


if __name__ == "__main__":
    init_app_db()
    app.run(debug=True)
