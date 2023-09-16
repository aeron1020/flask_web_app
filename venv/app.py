import os
from werkzeug.utils import secure_filename
import pytz
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, jsonify
from flask_session import Session
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

# Configure application
app = Flask(__name__)

# Define the file upload directory
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app.jinja_env.filters['strftime'] = datetime.strftime
# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///web_app.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def time_format(str_timestamp):
    timezone = pytz.timezone('UTC')
    past_time = timezone.localize(
        datetime.strptime(str_timestamp, "%Y-%m-%d %H:%M:%S"))
    datetime_now = datetime.now(timezone)

    time_diff = datetime_now - past_time

    if time_diff < timedelta(seconds=60):
        return f"{time_diff.seconds} seconds ago"

    elif time_diff < timedelta(minutes=60):
        return f"{time_diff.seconds // 60} minutes ago"

    elif time_diff < timedelta(hours=24):
        return f"{time_diff.seconds // 3600} hours ago"

    elif time_diff < timedelta(weeks=1):
        return f"{time_diff.days} days ago"

    elif time_diff < timedelta(days=365):
        return f"{time_diff.days // 7} weeks ago"

    else:
        return f"{time_diff.days // 365} years ago"

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    """Home page"""
    # Retrieve the list of blog posts
    posts = db.execute("SELECT post.id, post.post_date, post.title, head_media.media_url, admin.adminname, content.content  FROM post LEFT JOIN head_media ON post.id = head_media.post_id LEFT JOIN admin ON post.author_id = admin.id LEFT JOIN content ON post.id = content.post_id ORDER BY post.post_date DESC LIMIT 1")

    # List to hold formatted posts
    formatted_posts = []

    # Iterate through each post
    for post in posts:
        # Convert the post_date string to a datetime object
        post_date = post["post_date"]

        # Format the post_date using your time_format function (assuming it's defined)
        formatted_date = time_format(post_date)

        formatted_post = {
            "id": post["id"],
            "title": post["title"],
            "media_url": post["media_url"],
            "adminname": post["adminname"],
            "content": post["content"],
            "formatted_date": formatted_date
        }

        # Add the formatted post to the list
        formatted_posts.append(formatted_post)

     # Retrieve the list of blog posts
    blogs = db.execute("SELECT post.id, post.post_date, post.title, head_media.media_url, admin.adminname  FROM post LEFT JOIN head_media ON post.id = head_media.post_id LEFT JOIN admin ON post.author_id = admin.id WHERE post.id NOT IN (SELECT id FROM post ORDER BY post_date DESC LIMIT 1) ORDER BY post.post_date DESC LIMIT 4")

    # List to hold formatted posts
    blog_posts = []

    # Iterate through each post
    for blog in blogs:
        # Convert the post_date string to a datetime object
        blog_date = blog["post_date"]

        # Format the post_date using your time_format function (assuming it's defined)
        formatted_blog_date = time_format(blog_date)

        formatted_blog = {
            "id": blog["id"],
            "title": blog["title"],
            "media_url": blog["media_url"],
            "adminname": blog["adminname"],
            "formatted_date": formatted_blog_date
        }

        # Add the formatted post to the list
        blog_posts.append(formatted_blog)

    return render_template("index.html", posts=formatted_posts, blogs=blog_posts)


@app.route("/adminregister", methods=["GET", "POST"])
def adminregister():
    """Register in the admin"""
    # If method is POST
    if request.method == "POST":
        # If no username input
        if not request.form.get("username"):
            flash("Please complete the registration form",  category="warning")
            return render_template("adminregister.html")

        # If no password input
        elif not request.form.get("password"):
            flash("Please complete the registration form",  category="warning")
            return render_template("adminregister.html")

        # Password must be 8 char long
        elif len(request.form.get("password")) < 8:
            flash("Password must be 8 char long",  category="warning")
            print(len(request.form.get("password")))
            return render_template("adminregister.html")

        # If form is completed
        else:
            username = request.form.get("username")
            password = request.form.get("password")
            password_confirmation = request.form.get("confirmation")
            password_hash = generate_password_hash(password)
            # Ensure username exists
            reg_username = db.execute("SELECT * FROM admin WHERE adminname = ?",
                                      request.form.get("username"))
            if password != password_confirmation:
                flash("Password does not match.",  category="warning")
                return render_template("adminregister.html")

            elif len(reg_username) == 1:
                flash("Sorry, this username is already taken.",
                      category="warning")
                return render_template("adminregister.html")

            # Uppercase
            elif not any(x.isupper() for x in request.form.get("password")):
                flash("Password must contain atleast one uppercase letter",
                      category="warning")
                return render_template("adminregister.html")
            # Lowercase
            elif not any(x.islower() for x in request.form.get("password")):
                flash("Password must contain atleast one lowercase letter",
                      category="warning")
                return render_template("adminregister.html")
            # Number
            elif not any(x.isdigit() for x in request.form.get("password")):
                flash("Password must contain atleast one number",
                      category="warning")
                return render_template("adminregister.html")

            # If all okay, add it to the database
            else:
                db.execute(
                    "INSERT INTO admin (adminname, hash) VALUES (?, ?)", username, password_hash)

                flash("You are registered!", category="success")
                return redirect("/adminlogin")

    # If method is GET
    return render_template("adminregister.html")


@app.route("/adminlogin", methods=["GET", "POST"])
def adminlogin():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Must provide username", category="danger")
            return render_template("adminlogin.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Must provide password", category="danger")
            return render_template("adminlogin.html")

        else:
            # Query database for username
            rows = db.execute(
                "SELECT * FROM admin WHERE adminname = ?", request.form.get("username"))
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                flash("Invalid username and/or password", category="danger")
                return render_template("adminlogin.html")

            # Remember which user has logged in
            session["id"] = rows[0]["id"]

            # Redirect user to home page
            flash("You have been logged in!", category="success")
            return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    return render_template("adminlogin.html")


@ app.route("/create_blog", methods=["GET", "POST"])
@ login_required
def create_blog():
    """Writing blog"""
    # Check if the user is logged in
    if 'id' not in session:
        flash('Please log in to create a new post', category="danger")
        return render_template("adminlogin.html")

    # Upload extention
    image_extension = ['.jpeg', '.jpg', '.png', '.gif', '.bmp']
    movie_extension = ['.mp4', '.mov', '.MOV']

    if request.method == 'POST':
        # Handling the post
        title = request.form.get('title')
        author_id = session["id"]

        if title:

            # Insert post into the database
            db.execute(
                "INSERT INTO post (title, author_id) VALUES (?,?)", title, author_id)

            # Get the newly inserted post's ID
            id = db.execute("SELECT id FROM post WHERE title = ?", title)
            id = id[0]["id"]

            # Handling head_media
            headimage_file = request.files.get("headimage")

            if headimage_file:
                filename = secure_filename(
                    headimage_file.filename)
                file_path = (os.path.join(
                    app.config['UPLOAD_FOLDER'], filename))
                headimage_file.save(file_path)

                # Determine media type based on file extension
                media_type = "image" if any(extension in filename for extension in image_extension) else "video"

                # Insert head media into the database
                db.execute(
                    "INSERT INTO head_media (media_type, media_url, post_id) VALUES (?,?,?)", media_type, filename, id)

            # Handling the content
            num_content_fields = int(request.form.get('num_content_fields'))

            for i in range(num_content_fields + 1):
                content = request.form.get(f'contentcontentContainer_{i}')
                figure_file = request.files.get(f'figure{i}')

                if content:
                    if figure_file:
                        # Handle figure media and description
                        figure_description = request.form.get(
                            f'figureDescriptioncontentContainer_{i}')

                        figure_filename = secure_filename(
                            figure_file.filename)

                        file_path = (os.path.join(
                            app.config['UPLOAD_FOLDER'], figure_filename))
                        figure_file.save(file_path)

                        # Determine media type based on figure file extension
                        media_type = "video" if any(extension in figure_filename for extension in movie_extension) else "image"

                        # Insert content into the database
                        db.execute("INSERT INTO content (content, figure_media_type, figure_media_url, figure_description, post_id) VALUES(?,?,?,?,?)",
                                content, media_type, figure_filename, figure_description, id)

                    else:
                        # Insert content without figure
                        db.execute("INSERT INTO content (content, figure_media_type, figure_media_url, figure_description, post_id) VALUES(?,?,?,?,?)",
                                content, "none", "none", "none", id)

            flash("New post successfully created", category="success")
            return redirect("/")

        flash("Create a content title", category="danger")
        return redirect("/create_blog")

    return render_template("create_blog.html")


@ app.route("/logout")
@ login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@ app.route("/blogs")
def blogs():
    """Blog cards"""
    # Retrieve the list of blog posts
    posts = db.execute("SELECT post.id, post.post_date, post.title, head_media.media_url, admin.adminname FROM post LEFT JOIN head_media ON post.id = head_media.post_id LEFT JOIN admin ON post.author_id = admin.id ORDER BY post.post_date DESC")

    # List to hold formatted posts
    formatted_posts = []

    # Iterate through each post
    for post in posts:
        # Convert the post_date string to a datetime object
        post_date = post["post_date"]

        # Format the post_date using your time_format function (assuming it's defined)
        formatted_date = time_format(post_date)

        formatted_post = {
            "id": post["id"],
            "title": post["title"],
            "media_url": post["media_url"],
            "adminname": post["adminname"],
            "formatted_date": formatted_date
        }

        # Add the formatted post to the list
        formatted_posts.append(formatted_post)


    return render_template("blogs.html", posts=formatted_posts)


@ app.route("/myblogs")
@ login_required
def myblogs():
    """Display post"""
    author_id = session["id"]

    # Retrieve the list of blog posts
    posts = db.execute("SELECT post.id, post.post_date, post.title, head_media.media_url, admin.adminname FROM post LEFT JOIN head_media ON post.id = head_media.post_id LEFT JOIN admin ON post.author_id = admin.id WHERE post.author_id = ? ORDER BY post.post_date DESC", author_id)

    # List to hold formatted posts
    formatted_posts = []

    # Iterate through each post
    for post in posts:
        # Convert the post_date string to a datetime object
        post_date = post["post_date"]

        # Format the post_date using your time_format function (assuming it's defined)
        formatted_date = time_format(post_date)

        formatted_post = {
            "id": post["id"],
            "title": post["title"],
            "media_url": post["media_url"],
            "adminname": post["adminname"],
            "formatted_date": formatted_date
        }

        # Add the formatted post to the list
        formatted_posts.append(formatted_post)


    return render_template("myblogs.html", posts=formatted_posts)

@ app.route("/blog_art")
def blog_art():
    # Get the 'id' parameter from the query string
    post_id = request.args.get('id')

    # Retrieve the post's timestamp and format it
    timestamp_str = db.execute(
        'SELECT post_date FROM post WHERE id = ?', post_id)
    timestamp = datetime.strptime(
        timestamp_str[0]["post_date"], '%Y-%m-%d %H:%M:%S').strftime('%B %d, %Y')

    # Retrieve the details of the selected blog post
    posts = db.execute(
        "SELECT post.id, post.post_date, post.title, head_media.media_url FROM post LEFT JOIN head_media ON post.id = head_media.post_id WHERE post.id = ? ORDER BY post_date DESC", post_id)

    # Retrieve the content associated with the selected post
    contents = db.execute("SELECT * FROM content WHERE post_id = ?", post_id)

    # Render the 'blog_art.html' template with the retrieved data
    return render_template("blog_art.html", posts=posts, timestamp=timestamp, contents=contents)

@ app.route("/blogs/update_post/<int:post_id>", methods=["GET", "POST"])
@ login_required
def update_post(post_id):
    """Update post"""
    # Get form data
    if request.method == "POST":
        headimage = request.files.get("headimage")
        title = request.form.get("title")

        # Updating Headimage
        if headimage:
            # Secure the filename
            filename = secure_filename(
                headimage.filename)
            file_path = (os.path.join(
                app.config['UPLOAD_FOLDER'], filename))
            headimage.save(file_path)

         # Determine media type based on the file extension
            media_type = "image" if any(extension in filename for extension in ['.jpeg', '.jpg', '.png', '.gif', '.bmp']) else "video"

            db.execute(
                "UPDATE head_media SET media_type = ?, media_url = ? WHERE post_id = ?", media_type, filename, post_id)

        # Updating title
        prev_title = db.execute("SELECT title FROM post WHERE id = ?", post_id)[0]["title"]
        if title != prev_title:
            db.execute(
                "UPDATE post SET  title = ? WHERE id = ?", title, post_id)

        # Updating contents and figures
        contents = db.execute("SELECT id, content, figure_description FROM content WHERE post_id = ?", post_id)
        for content in contents:
            content_id = content["id"]
            content_text = request.form.get(f"content{content_id}")
            figure = request.files.get(f"figure{content_id}")
            figure_description = request.form.get(f"figure_description{content_id}")

            # Update content text
            if content_text != content["content"]:
                db.execute("UPDATE content SET content = ? WHERE id = ?", content_text, content_id)

            # Update figure
            if figure:
                filename = secure_filename(figure.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                figure.save(file_path)

                media_type = "image" if any(extension in filename for extension in ['.jpeg', '.jpg', '.png', '.gif', '.bmp']) else "video"
                db.execute("UPDATE content SET figure_media_type = ?, figure_media_url = ? WHERE id = ?", media_type, filename, content_id)


            # Update figure description
            if figure_description != content["figure_description"]:
                db.execute("UPDATE content SET figure_description = ? WHERE id = ?", figure_description, content_id)


        flash(f"You have successfully updated this article!", category="success")
        return redirect("/blogs")

    posts = db.execute(
        "SELECT post.id, post.post_date, post.title, head_media.media_url FROM post LEFT JOIN head_media ON post.id = head_media.post_id WHERE post.id = ? ORDER BY post_date DESC", post_id)

    contents = db.execute("SELECT * FROM content WHERE post_id = ?", post_id)

    return render_template("update_post.html", posts=posts, contents=contents)


@ app.route("/blogs/delete_post/<int:post_id>", methods=["GET", "POST"])
@ login_required
def delete_post(post_id):
    """Delete post"""
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Enter username", category="danger")
            return render_template("delete_post.html", post_id=post_id)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Enter password", category="danger")
            return render_template("delete_post.html", post_id=post_id)

        else:
            # Query database for username
            rows = db.execute(
                "SELECT * FROM admin WHERE adminname = ?", request.form.get("username"))
            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                flash("Invalid username and/or password, deletion unsuccessful", category="danger")
                return redirect(url_for("blogs"))

            db.execute("DELETE FROM content WHERE post_id = ?", post_id)
            db.execute("DELETE FROM head_media WHERE post_id = ?", post_id)
            db.execute("DELETE FROM post WHERE id = ?", post_id)

            # Redirect user to home page
            flash("You have been successfully deleted the post", category="success")
            return redirect(url_for("blogs"))

    return render_template("delete_post.html", post_id=post_id)

@ app.route("/settings", methods=["GET", "POST"])
@ login_required
def settings():
    """Settings"""

    return render_template("settings.html")


@ app.route("/changepassword", methods=["GET", "POST"])
@ login_required
def changepassword():
    """Change Password"""

    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        if not old_password:
            flash("Provide your old password", category="warning")
            return render_template("changepassword.html")

        elif not new_password:
            flash("Provide your new password", category="warning")
            return render_template("changepassword.html")
        elif not confirmation:
            flash("Retype your new password", category="warning")
            return render_template("changepassword.html")
        else:
            if new_password != confirmation:
                flash("Your new password do not match", category="danger")
                return render_template("changepassword.html")

            db_old_pass = db.execute(
                "SELECT hash FROM admin WHERE id = ?",  (session['id']))[0]['hash']

            if check_password_hash(db_old_pass, old_password):

                db.execute("UPDATE admin SET hash = ? WHERE id = ?", generate_password_hash(
                    new_password), session['id'])

                flash("You've successfully changed your password",
                      category="success")
                return redirect("/")
            else:
                flash("Previous password do not match", category="danger")
                return redirect("/changepassword")

    return render_template("changepassword.html")

@ app.route("/about", methods=["GET", "POST"])
def about():
    """About page"""
    return render_template("about.html")

@ app.route("/changeadminname", methods=["GET", "POST"])
@ login_required
def changeadminname():
    """Change Adminname"""
    if request.method == "POST":
        old_adminname = request.form.get("old_adminname")
        new_adminname = request.form.get("new_adminname")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        check_adminname = db.execute("SELECT adminname FROM admin WHERE adminname = ?",  new_adminname)

        if not old_adminname:
            flash("Provide your adminname", category="warning")
            return render_template("changeadminname.html")

        elif not new_adminname:
            flash("Provide your new password", category="warning")
            return render_template("changeadminname.html")

        elif len(check_adminname) == 1:
            flash("Sorry, this name is already taken.",
                category="warning")
            return render_template("changeadminname.html")


        elif not password:
            flash("Enter your password", category="warning")
            return render_template("changeadminname.html")

        elif not confirmation:
            flash("Enter again your password to verify", category="warning")
            return render_template("changeadminname.html")

        else:
            if password != confirmation:
                flash("Password confirmation error", category="danger")
                return render_template("changeadminname.html")

            db_old_adminname = db.execute(
                "SELECT adminname FROM admin WHERE id = ?",  (session['id']))[0]['adminname']

            if old_adminname != db_old_adminname:
                flash("Please check your name", category="warning")
                return render_template("changeadminname.html")

            db_password = db.execute(
                "SELECT hash FROM admin WHERE id = ?",  (session['id']))[0]['hash']

            if check_password_hash(db_password, confirmation):
                # db.execute("UPDATE admin SET adminname = ? WHERE id = ?", new_adminname, session['id'])
                flash("Updating success!", category="success")
                return redirect("/")

            flash("That is not your password", category="warning")
            return render_template("changeadminname.html")

    return render_template("changeadminname.html")


if __name__ == "__main__":
    app.run(debug=True)

# delete from admin;
# delete from post;
# delete from content;
# delete from head_media;
# DELETE FROM sqlite_sequence WHERE name = 'admin';
# DELETE FROM sqlite_sequence WHERE name = 'post';
# DELETE FROM sqlite_sequence WHERE name = 'content';
# DELETE FROM sqlite_sequence WHERE name = 'head_media';
