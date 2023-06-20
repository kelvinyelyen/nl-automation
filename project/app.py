from flask import Flask, render_template

#configure application 
app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

#login
@app.route("/login")
def login():
    return render_template("login.html")

#register
@app.route("/register")
def register():
    return render_template("register.html")


if __name__ == '__main__':
    app.run()
