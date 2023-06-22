import os
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash


# Configure application 
app = Flask(__name__)
app.secret_key = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = generate_password_hash(password)

class Subscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.String(50), nullable=False) 
   

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    username = session.get("username")
    email = session.get("email")
    return render_template("dashboard.html", username=username, email=email)


# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")

        if not email:
            flash("Please enter your email")
            return redirect(url_for("login"))
        elif not password:
            flash("Please enter your password")
            return redirect(url_for("login"))
        
        user = User.query.filter_by(email=email).first()
        password_correct = check_password_hash(user.password, password)

        if not user:
            user = User.query.filter_by(username=username).first()
            flash("User not found, don't have an account? Sign up")
    
        if user and password_correct:
            session["user_id"] = user.id
            flash("You have been logged in successfully.")
            session["username"] = user.username
            session["email"] = user.email
            return redirect(url_for('dashboard'))
        
        else:
            flash("Invalid email or password.")
            return redirect(url_for('login'))
        
    else:
        return render_template("login.html")


# Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        # Ensure email, username, password, and confirmation are submitted
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not email:
            flash("You must provide an email")
            return redirect(url_for("register"))
        elif not username:
            flash("You must provide a username")
            return redirect(url_for("register"))
        elif not password:
            flash("You must provide a password")
            return redirect(url_for("register"))
        elif password != confirmation:
            flash("Passwords do not match")
            return redirect(url_for("register"))

        # Create a new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    else:
        return render_template("register.html")



@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/login")



@app.route("/subscribe", methods=["GET", "POST"])
def subscribe():
    if request.method == "GET":
        user_id = request.args.get("user_id")
        print(user_id)

        # Validate the username
        if not user_id:
            flash("Invalid subscription request")
            return redirect(url_for("subscribe"))

        # Retrieve the user details using the username
        user = User.query.filter_by(username=user_id).first()
        if not user:
            flash("Invalid user")
            return redirect(url_for("subscribe"))
        
        # Render the subscription page template for GET requests
        return render_template("subscription.html", user_id=user_id)
    
    elif request.method == "POST":
        email = request.form.get("email")
        user_id = request.form.get("user_id")

         # Validate the username
        if not email or not user_id:
            flash("Invalid subscription request")
            return redirect(url_for("subscribe"))

        # Retrieve the user details using the username
        user = User.query.filter_by(username=user_id).first()
        if not user:
            flash("Invalid user")
            return redirect(url_for("subscribe"))

        # Create a new instance of your Subscriber model and set the email field and any other relevant fields
        subscriber = Subscriber(email=email, user_id=user.id)
        # Store the subscriber in the database
        db.session.add(subscriber)
        db.session.commit()
        session["user_id"] = user_id
        return redirect(url_for("subscribed"))


@app.route("/subscribed")
def subscribed():
    user_id = session.get("user_id")  # Access user_id from the URL parameter
    return render_template("subscribed.html", user_id=user_id)




if __name__ == '__main__':
    app.run()
