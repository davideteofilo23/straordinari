from flask import Flask, render_template, request, redirect, session, jsonify
import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Inizializza Firebase da variabile ambiente FIREBASE_CONFIG (JSON string)
import json

firebase_json = json.loads(os.environ.get("FIREBASE_CONFIG"))
cred = credentials.Certificate(firebase_json)
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route("/")
def index():
    if "user" in session:
        return redirect("/home")
    return redirect("/login-page")

@app.route("/login-page")
def login_page():
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = auth.create_user(email=email, password=password)
            session["user"] = email
            return redirect("/home")
        except:
            return "Errore nella registrazione"
    return render_template("register.html")

@app.route("/session", methods=["POST"])
def set_session():
    data = request.get_json()
    session["user"] = data.get("email")
    return jsonify({"success": True})

@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")
    doc = db.collection("utenti").document(session["user"]).get()
    nome = doc.to_dict().get("nome") if doc.exists else session["user"]
    return render_template("home.html", nome=nome)

@app.route("/ore", methods=["GET", "POST"])
def inserisci_ore():
    if "user" not in session:
        return redirect("/")

    data_oggi = datetime.now().strftime("%Y-%m-%d")
    lista_ore = []

    if request.method == "POST":
        data = request.form.get("data")
        entry = {
            "data": data,
            "dalle": request.form.get("dalle"),
            "alle": request.form.get("alle"),
            "motivo": request.form.get("motivo"),
            "totale": request.form.get("totale")
        }
        db.collection("ore_straordinari").document(session["user"]).collection("maggio_2025").document(data).set(entry)

    docs = db.collection("ore_straordinari").document(session["user"]).collection("maggio_2025").stream()
    for doc in docs:
        lista_ore.append(doc.to_dict())

    lista_ore.sort(key=lambda x: x['data'])
    return render_template("ore.html", data_oggi=data_oggi, lista_ore=lista_ore)

@app.route("/impostazioni", methods=["GET", "POST"])
def impostazioni():
    if "user" not in session:
        return redirect("/")

    user_doc = db.collection("utenti").document(session["user"])
    salvato = False

    if request.method == "POST":
        dati = {
            "nome": request.form.get("nome"),
            "codice_operatore": request.form.get("codice_operatore"),
            "filiale": request.form.get("filiale"),
            "email_pdf": request.form.get("email_pdf")
        }
        user_doc.set(dati)
        salvato = True

    doc = user_doc.get()
    utente = doc.to_dict() if doc.exists else {
        "nome": "", "codice_operatore": "", "filiale": "", "email_pdf": ""
    }

    return render_template("impostazioni.html", utente=utente, salvato=salvato)

@app.route("/firma", methods=["GET", "POST"])
def firma():
    if "user" not in session:
        return redirect("/")

    salvato = False
    if request.method == "POST":
        firma_dati = request.form.get("firma_dati")
        db.collection("utenti").document(session["user"]).update({
            "firma": firma_dati
        })
        salvato = True

    return render_template("firma.html", salvato=salvato)

@app.route("/invia")
def invia_pdf():
    if "user" not in session:
        return redirect("/")
    doc = db.collection("utenti").document(session["user"]).get()
    email = doc.to_dict().get("email_pdf", "default@example.com") if doc.exists else "default@example.com"
    return render_template("invia.html", email=email)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
