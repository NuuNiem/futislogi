import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session, abort
import db
import config
import matches
import re
import users
import likes

app = Flask(__name__)
app.secret_key = config.secret_key


def require_login():
    if "user_id" not in session:
        abort(403)

@app.route("/")
def index():
    all_matches = matches.get_matches()
    return render_template("index.html", matches=all_matches)

@app.route("/like/<int:match_id>", methods=["POST"])
def like_match(match_id):
    require_login()
    user_id = session["user_id"]
    match = matches.get_match(match_id)
    if not match:
        abort(404)

    if match["user_id"] == user_id:
        return "Et voi tykätä omasta ottelustasi"
    
    likes.add_like(match_id, user_id)
    return redirect("/match/" + str(match_id))

@app.route("/unlike/<int:match_id>", methods=["POST"])
def unlike_match(match_id):
    require_login()
    user_id = session["user_id"]
    match = matches.get_match(match_id)
    if not match:
        abort(404)
    
    likes.remove_like(match_id, user_id)
    return redirect("/match/" + str(match_id))

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    matches = users.get_matches(user_id)
    return render_template("show_user.html", user=user, matches=matches)

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
    if not match:
        abort(404)
    
    like_count = likes.count_likes(match_id)
    has_liked = False
    
    if "user_id" in session:
        has_liked = likes.has_liked(match_id, session["user_id"])
    
    return render_template("show_match.html", match=match, like_count=like_count, has_liked=has_liked)

@app.route("/new_match")
def new_item():
    require_login()
    return render_template("new_match.html")

@app.route("/create_match", methods=["POST"])
def create_match():
    require_login()
    home_team = request.form["home_team"]
    if len(home_team) > 20:
        abort(403)
    if not re.search(r"^[A-Za-z0-9\s\-\.&]{1,20}$", home_team):
        abort(403)
    away_team = request.form["away_team"]
    if len(away_team) > 20:
        abort(403)
    if not re.search(r"^[A-Za-z0-9\s\-\.&]{1,20}$", away_team):
        abort(403)
    stadium = request.form["stadium"]
    if len(stadium) > 30:
        abort(403)
    if not re.search(r"^[A-Za-z0-9\s\-\.&]{1,30}$", stadium):
        abort(403)
    
    date = request.form["date"]
    if not re.search(r"^\d{4}-\d{2}-\d{2}$", date):
        abort(403)
    user_id = session["user_id"]
    
    atmosphere_rating = request.form.get("atmosphere_rating")
    notes = request.form.get("notes")

    matches.add_matches(home_team, away_team, stadium, date, user_id, atmosphere_rating, notes)

    return redirect("/")

@app.route("/edit_match/<int:match_id>")
def edit_match(match_id):
    match = matches.get_match(match_id)
    if not match:
        abort(404)
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
    
    atmosphere_rating = request.form.get("atmosphere_rating")
    notes = request.form.get("notes")

    match = matches.get_match(match_id)
    if not match:
        abort(404)
    if match["user_id"] != session["user_id"]:
        abort(403)

    matches.update_match(match_id, home_team, away_team, stadium, date, atmosphere_rating, notes)

    return redirect("/match/" + str(match_id))

@app.route("/remove_match/<int:match_id>", methods=["GET", "POST"])
def remove_match(match_id):
    match = matches.get_match(match_id)
    if not match:
        abort(404)
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
    
    try:
        users.create_user(username, password1)
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
        
        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
    return redirect("/")
