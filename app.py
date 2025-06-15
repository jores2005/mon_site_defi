from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response
import os
import datetime
import smtplib
from email.message import EmailMessage
from functools import wraps

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = "submissions"
EVAL_FOLDER = "evaluations"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EVAL_FOLDER, exist_ok=True)

# Configuration email
EMAIL_ADDRESS = "saakamtajores@gmail.com"
EMAIL_PASSWORD = "saa.kamta.2005"

# Configuration admin login
ADMIN_USERNAME = "jores"
ADMIN_PASSWORD = "saa.kamta.2005"

def check_auth(username, password):
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD

def authenticate():
    return Response(
        'Accès refusé. Veuillez vous authentifier.',
        401,
        {'WWW-Authenticate': 'Basic realm="Admin Area"'}
    )

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    email = request.form.get("email")
    challenge = request.form.get("challenge")
    code = request.form.get("code")

    if not email or not challenge or not code:
        return "Formulaire incomplet", 400

    now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{challenge}_{now}.py"
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# Email: {email}\n")
        f.write(f"# Challenge: {challenge}\n")
        f.write("\n")
        f.write(code)

    send_confirmation_email(email, challenge)

    return redirect(url_for("thank_you"))

@app.route("/merci")
def thank_you():
    return "<h2>Merci pour ta soumission ! Tu recevras une réponse par email sous peu.</h2>"

@app.route("/admin")
@requires_auth
def admin_panel():
    only_pending = request.args.get("pending") == "1"
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    evaluations = {}
    for file in files:
        eval_file = os.path.join(EVAL_FOLDER, f"{file}.txt")
        if os.path.exists(eval_file):
            with open(eval_file, "r", encoding="utf-8") as f:
                evaluations[file] = f.read().strip()
        else:
            evaluations[file] = None

    if only_pending:
        files = [f for f in files if evaluations[f] is None]

    return render_template("admin.html", files=files, evaluations=evaluations, only_pending=only_pending)

@app.route("/submissions/<filename>")
@requires_auth
def download_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

@app.route("/evaluate/<filename>", methods=["GET", "POST"])
@requires_auth
def evaluate_file(filename):
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    if request.method == "POST":
        comment = request.form.get("comment")
        eval_path = os.path.join(EVAL_FOLDER, f"{filename}.txt")
        with open(eval_path, "w", encoding="utf-8") as f:
            f.write(comment)

        with open(filepath, "r", encoding="utf-8") as f:
            first_line = f.readline()
            email_line = first_line.strip()
            if email_line.startswith("# Email:"):
                user_email = email_line.replace("# Email:", "").strip()
                send_evaluation_email(user_email, filename, comment)

        return redirect(url_for("admin_panel"))

    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return render_template("evaluate.html", filename=filename, content=content)

@app.route("/delete-evaluation/<filename>", methods=["POST"])
@requires_auth
def delete_evaluation(filename):
    eval_path = os.path.join(EVAL_FOLDER, f"{filename}.txt")
    if os.path.exists(eval_path):
        os.remove(eval_path)
    return redirect(url_for("admin_panel"))

def send_confirmation_email(to_email, challenge):
    msg = EmailMessage()
    msg["Subject"] = f"Confirmation - Défi soumis : {challenge}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(f"Bonjour !\n\nNous avons bien reçu ta soumission pour le défi '{challenge}'.\n\nMerci pour ta participation, tu recevras une évaluation sous peu.\n\n- L'équipe DevGame Challenge")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("Erreur envoi email:", e)

def send_evaluation_email(to_email, filename, comment):
    msg = EmailMessage()
    msg["Subject"] = f"Évaluation de ta soumission : {filename}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg.set_content(f"Bonjour !\n\nVoici notre retour sur ta soumission '{filename}' :\n\n{comment}\n\nMerci pour ta participation et continue à coder !\n\n- L'équipe DevGame Challenge")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
    except Exception as e:
        print("Erreur envoi évaluation:", e)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)