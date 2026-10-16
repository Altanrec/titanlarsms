import os, re, time, secrets
from collections import defaultdict, deque
from threading import Lock
from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-before-deploying")
WINDOW_SECONDS, MAX_PER_WINDOW = 60, 5
_recent = defaultdict(deque)
_lock = Lock()

def normalize_phone(value):
    digits = re.sub(r"\\D", "", value or "")
    if digits.startswith("90") and len(digits) == 12: digits = digits[2:]
    elif digits.startswith("0") and len(digits) == 11: digits = digits[1:]
    return digits if len(digits) == 10 and digits.startswith("5") else ""

def rate_allowed(phone):
    now = time.time()
    with _lock:
        q = _recent[phone]
        while q and now - q[0] > WINDOW_SECONDS: q.popleft()
        if len(q) >= MAX_PER_WINDOW: return False
        q.append(now)
        return True

def send_verification_sms(phone, code):
    # Demo only: intentionally does not send a real SMS.
    app.logger.info("DEMO SMS to +90%s: code %s", phone, code)
    return True

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/send-code")
def send_code():
    phone = normalize_phone(request.form.get("phone", ""))
    if not phone:
        flash("Geçerli bir Türkiye cep telefonu gir. Örn: 5XXXXXXXXX", "error")
        return redirect(url_for("index"))
    if not rate_allowed(phone):
        flash("Bu numara için çok fazla deneme yapıldı. Bir dakika sonra tekrar dene.", "error")
        return redirect(url_for("index"))
    code = f"{secrets.randbelow(1_000_000):06d}"
    session["demo_phone"], session["demo_code"] = phone, code
    session["demo_expires"] = int(time.time()) + 300
    send_verification_sms(phone, code)
    flash("Demo kodu oluşturuldu. Gerçek SMS gönderilmedi; kod sunucu loglarında görünür.", "success")
    return redirect(url_for("verify"))

@app.get("/verify")
def verify():
    if not session.get("demo_phone"): return redirect(url_for("index"))
    return render_template("verify.html", phone=session["demo_phone"])

@app.post("/verify")
def verify_post():
    submitted, expected = (request.form.get("code") or "").strip(), session.get("demo_code")
    if not expected or int(time.time()) > int(session.get("demo_expires", 0)):
        session.clear()
        flash("Kodun süresi doldu. Yeniden başlayabilirsin.", "error")
        return redirect(url_for("index"))
    if not re.fullmatch(r"\\d{6}", submitted) or submitted != expected:
        flash("Kod hatalı. Tekrar dene.", "error")
        return redirect(url_for("verify"))
    session["verified"] = True
    session.pop("demo_code", None)
    session.pop("demo_expires", None)
    flash("Demo doğrulama başarılı. Gerçek SMS gönderilmedi.", "success")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
