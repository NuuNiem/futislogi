import db 

def add_matches(home_team, away_team, stadium, date, user_id):
    match_name = f"{home_team} - {away_team}"
    sql = "INSERT INTO matches (home_team, away_team, stadium, date, user_id, name) VALUES (?, ?, ?, ?, ?, ?)"
    db.execute(sql, [home_team, away_team, stadium, date, user_id, match_name])

def get_matches():
    sql = "SELECT id, name, home_team, away_team, stadium, date FROM matches ORDER BY date DESC"
    return db.query(sql)

def get_match(match_id):
    sql = """SELECT matches.name,
                    matches.id,
                    matches.stadium,
                    matches.date,
                    users.id user_id,
                    users.username
                FROM matches, users
                WHERE matches.user_id = users.id AND
                matches.id = ?"""
    return db.query(sql, [match_id])[0]


def update_match(match_id, home_team, away_team, stadium, date):
    match_name = f"{home_team} - {away_team}"
    sql = """UPDATE matches SET name = ?,
                                home_team = ?,
                                away_team = ?, 
                                stadium = ?, 
                                date = ?
                            WHERE id = ?"""
    db.execute(sql, [match_name, home_team, away_team, stadium, date, match_id])


def remove_match(match_id):
    sql = "DELETE FROM matches WHERE id = ?"
    db.execute(sql, [match_id])


def find_matches(query):
    query = query.strip()  
    sql = """SELECT id, name, stadium, date
             FROM matches
             WHERE name LIKE ? OR
                   stadium LIKE ? OR
                   date LIKE ?
             ORDER BY date DESC"""
    return db.query(sql, ("%" + query + "%", 
                          "%" + query + "%",
                          "%" + query + "%"))




