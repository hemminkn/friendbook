import secrets
import sqlite3

from flask import Flask
from flask import abort, redirect, make_response, render_template, request, session, flash
import markupsafe

import config
import posts
import users


app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.route("/")
def index():
    all_posts = posts.get_posts()
    return render_template("index.html", posts=all_posts)

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)
    user_posts = users.get_posts(user_id)
    return render_template("show_user.html", user=user, posts=user_posts)

@app.route("/find_post")
def find_post():
    query = request.args.get("query")
    if query:
        results = posts.find_posts(query)
    else:
        query = ""
        results = []
    return render_template("find_post.html", query=query, results=results)

@app.route("/post/<int:post_id>")
def show_post(post_id):
    post = posts.get_post(post_id)
    if not post:
        abort(404)
    cl = posts.get_classes(post_id)
    co = posts.get_comments(post_id)
    im = posts.get_images(post_id)
    return render_template("show_post.html", post=post, classes=cl, comments=co, images=im)

@app.route("/image/<int:image_id>")
def show_image(image_id):
    image = posts.get_image(image_id)
    if not image:
        abort(404)

    response = make_response(bytes(image))
    response.headers.set("Content-Type", "image/png")
    return response

@app.route("/new_post")
def new_post():
    require_login()
    classes = posts.get_all_classes()
    return render_template("new_post.html", classes=classes)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/create_post", methods=["POST"])
def create_post():
    require_login()
    check_csrf()

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 3000:
        abort(403)
    user_id = session["user_id"]

    all_classes = posts.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    posts.add_post(title, description, user_id, classes)

    return redirect("/")

@app.route("/create_comment", methods=["POST"])
def create_comment():
    require_login()
    check_csrf()

    comment = request.form["comment"]
    if not comment or len(comment) > 200:
        abort(403)
    post_id = request.form["post_id"]
    post = posts.get_post(post_id)
    if not post:
        abort(403)
    user_id = session["user_id"]

    posts.add_comment(post_id, user_id, comment)

    return redirect("/post/" + str(post_id))

@app.route("/edit_post/<int:post_id>")
def edit_post(post_id):
    require_login()
    post = posts.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    all_classes = posts.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in posts.get_classes(post_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_post.html", post=post, classes=classes, all_classes=all_classes)

@app.route("/images/<int:post_id>")
def edit_images(post_id):
    require_login()
    post = posts.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    images = posts.get_images(post_id)

    return render_template("images.html", post=post, images=images)

@app.route("/add_image", methods=["POST"])
def add_image():
    require_login()
    check_csrf()

    post_id = request.form["post_id"]
    post = posts.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    file = request.files["image"]
    if request.method == "POST":
        file = request.files["image"]
        if not file.filename.endswith(".png"):
            flash("ERROR: wrong format")
            return redirect("/images/" + str(post_id))

        image = file.read()
        if len(image) > 100 * 1024:
            flash("ERROR: image is too large")
            return redirect("/images/" + str(post_id))

        posts.add_image(post_id, image)
        return redirect("/images/" + str(post_id))

@app.route("/remove_images", methods=["POST"])
def remove_images():
    require_login()
    check_csrf()

    post_id = request.form["post_id"]
    post = posts.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    for image_id in request.form.getlist("image_id"):
        posts.remove_image(post_id, image_id)

    return redirect("/images/" + str(post_id))

@app.route("/update_post", methods=["POST"])
def update_post():
    require_login()
    check_csrf()

    post_id = request.form["post_id"]
    post = posts.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 50:
        abort(403)
    description = request.form["description"]
    if not description or len(description) > 3000:
        abort(403)

    all_classes = posts.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    posts.update_post(post_id, title, description, classes)

    return redirect("/post/" + str(post_id))

@app.route("/remove_post/<int:post_id>", methods=["GET", "POST"])
def remove_post(post_id):
    require_login()

    post = posts.get_post(post_id)
    if not post:
        abort(404)
    if post["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_post.html", post=post)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            posts.remove_post(post_id)
            return redirect("/")
        return redirect("/post/" + str(post_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("ERROR: passwords don't match")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("ERROR: username is taken")
        return redirect("/register")

    return "User created"

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
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")

        flash("ERROR: wrong user or password")
        return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        session.clear()
    return redirect("/")

@app.route("/page1")
def page1():
    session["test"] = "aybabtu"
    return "Session set"

@app.route("/page2")
def page2():
    return "Information about the session: " + session["test"]
