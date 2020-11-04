from flask import Flask, Blueprint, render_template, request, redirect, session
import random
from pymongo import MongoClient
from argon2 import PasswordHasher
from datetime import date 
import datetime as dt 

app = Flask(__name__)
app.config["SECRET_KEY"] = "OCML3BRawWEUeaxcuKHLpw"

db = MongoClient()['pointage']
ph = PasswordHasher()


@app.route('/see', methods=['GET'])
def see():
    code = random.randint(1000, 9999)

    db['code_legit'].drop()

    db['code_legit'].insert_one({
        "code": str(code)
    })

    return render_template("see.htm", code=code)


@app.route('/login', methods=['GET'])
def login_page():
    return render_template("login.htm")


@app.route('/register', methods=['GET'])
def register_page():
    return render_template("register.htm")


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    users = db['users'].find_one({"email": email})

    if users:
        try:
            ph.verify(users['password'], password)

            session["firstname"] = users["firstname"]
            session["lastname"] = users["lastname"]
            session["role"] = "member"

            return redirect("/")
        except:
            return render_template("login.htm", error=True)
    else:
        return render_template("register.htm")


@app.route('/register', methods=['POST'])
def register():
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]
    email = request.form["email"]
    password = request.form["password"]

    hash = ph.hash(password)

    db['users'].insert_one({
        "firstname": firstname,
        "lastname": lastname,
        "email": email,
        "password": hash
    })

    return render_template("login.htm")


@app.route('/', methods=['GET'])
def index():
    try:
        if session["firstname"]:
            return render_template("index.htm")
    except:
        return redirect("/login")


@app.route('/validate', methods=['POST'])
def validate():
    code = request.form["code"]
    verified_code = db["code_legit"].find_one({"code": str(code)})

    if verified_code:
        db["vision"].insert_one({ 
            "firstname": session["firstname"],
            "lastname": session["lastname"],
            "date": date.today().strftime("%b-%d-%Y"),
            "hours": str(dt.datetime.now().hour) + ":" + str(dt.datetime.now().minute)
        })

        return render_template("index.htm", success=True)
    else:
        return render_template("index.htm", error=True)

@app.route('/vision', methods=["GET"])
def vision():
    today = db["vision"].find({ "date": date.today().strftime("%b-%d-%Y") })

    return render_template("vision.htm", today=today)

if __name__ == "__main__":
    app.run()
