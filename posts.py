import db

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def add_post(title, description, user_id, classes):
    sql = """INSERT INTO posts (title, description, user_id)
            VALUES (?, ?, ?)"""
    db.execute(sql, [title, description, user_id])

    post_id = db.last_insert_id()

    sql = "INSERT INTO post_classes (post_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [post_id, title, value])

def get_classes(post_id):
    sql = "SELECT title, value FROM post_classes WHERE post_id = ?"
    return db.query(sql, [post_id])

def get_posts():
    sql = "SELECT id, title FROM posts ORDER BY id DESC"

    return db.query(sql)

def get_post(post_id):
    sql = """SELECT posts.title,
                    posts.description,
                    users.username,
                    users.id user_id,
                    posts.id
               FROM posts, users
              WHERE posts.user_id = users.id AND
                    posts.id = ?"""
    result = db.query(sql, [post_id])
    return result[0] if result else None

def update_post(post_id, title, description, classes):
    sql = """UPDATE posts SET title = ?,
                              description = ?
                          WHERE id = ?"""
    db.execute(sql, [title, description, post_id])

    sql = "DELETE FROM post_classes WHERE post_id = ?"
    db.execute(sql, [post_id])

    sql = "INSERT INTO post_classes (post_id, title, value) VALUES (?, ?, ?)"
    for title, value in classes:
        db.execute(sql, [post_id, title, value])

def remove_post(post_id):
    sql = "DELETE FROM post_classes WHERE post_id = ?"
    db.execute(sql, [post_id])
    sql = "DELETE FROM posts WHERE id = ?"
    db.execute(sql, [post_id])

def find_posts(query):
    sql = """SELECT id, title
             FROM posts
             WHERE title LIKE ? OR description LIKE ?
             ORDER BY id DESC"""
    like = "%" + query + "%"
    return db.query(sql, [like, like])
