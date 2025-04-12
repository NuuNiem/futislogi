import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
import db
import config
import matches

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    all_matches = matches.get_matches()
    return render_template("index.html", matches=all_matches)

@app.route("/find_match")
def find_match():
    query = request.args.get("query")
    if query:
        results = matches.find_matches(query)
    else:
        query = ""
        results = []
    return render_template("find_match.html", query=query, matches=results)

@app.route("/match/<int:match_id>")
def show_match(match_id):
    match = matches.get_match(match_id)
    return render_template("show_match.html", match=match)

@app.route("/new_match")
def new_item():
    return render_template("new_match.html")

@app.route("/create_match", methods=["POST"])
def create_match():
    home_team = request.form["home_team"]
    away_team = request.form["away_team"]
    stadium = request.form["stadium"]
    date = request.form["date"]
    user_id = session["user_id"]

    matches.add_matches(home_team, away_team, stadium, date, user_id)

    return redirect("/")

@app.route("/edit_match/<int:match_id>")
def edit_match(match_id):
    match = matches.get_match(match_id)
    if match["user_id"] !=session["user_id"]:
        abort(403)
    return render_template("edit_match.html", match=match)

@app.route("/update_match", methods=["POST"])
def update_match():
    match_id = request.form["match_id"]
    home_team = request.form["home_team"]
    away_team = request.form["away_team"]
    stadium = request.form["stadium"]
    date = request.form["date"]

    match = matches.get_match(match_id)
    if match["user_id"] != session["user_id"]:
        abort(403)

    matches.update_match(match_id, home_team, away_team, stadium, date)

    return redirect("/match/" + str(match_id))

@app.route("/remove_match/<int:match_id>", methods=["GET", "POST"])
def remove_match(match_id):
    match = matches.get_match(match_id)
    if match["user_id"] != session["user_id"]:
            abort(403)
    if request.method == "GET":
        return render_template("remove_match.html", match=match)
    
    if request.method == "POST":
        if "remove" in request.form:
            matches.remove_match(match_id)
            return redirect("/")
        else:
            return redirect("/match/" + str(match_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"

    return "Tunnus luotu"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
    
        sql = "SELECT id, password_hash FROM users WHERE username = ?"
        result = db.query(sql, [username])[0]
        user_id = result["id"]
        password_hash = result["password_hash"]

        if check_password_hash(password_hash, password):
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    del session["user_id"]
    del session["username"]
    return redirect("/")
