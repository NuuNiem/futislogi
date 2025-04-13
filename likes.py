import db
from datetime import datetime

def add_like(match_id, user_id):
    sql = "INSERT INTO likes (match_id, user_id, created_at) VALUES (?, ?, ?)"
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        db.execute(sql, [match_id, user_id, now])
        return True
    except:
        return False

def remove_like(match_id, user_id):
    sql = "DELETE FROM likes WHERE match_id=? AND user_id=?"
    db.execute(sql, [match_id, user_id])

def has_liked(match_id, user_id):
    sql = "SELECT 1 FROM likes WHERE match_id=? AND user_id=?"
    result = db.query(sql, [match_id, user_id])
    return len(result) > 0

def count_likes(match_id):
    sql = "SELECT COUNT(*) AS count FROM likes WHERE match_id=?"
    result = db.query(sql, [match_id])
    return result[0]["count"] if result else 0