import os

import jwt
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
)
from flask_cors import CORS

load_dotenv()

API_URL = os.getenv('API_URL')
SECRET_TOKEN = os.getenv('SECRET_TOKEN')

app = Flask(__name__)
CORS(app)

def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_TOKEN, algorithms=['HS256'])
        print(decoded)
        return decoded
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError as e:
        print({"msg": f"Erreur de JWT: {str(e)}"})

@app.route('/')
def home():
    jwt_token = request.cookies.get('jwt_token')
    
    if not jwt_token:
        return redirect('/login')
    
    user_info = verify_jwt(jwt_token)
    if user_info.get('admin'):
        try:
            response = requests.get(API_URL + "user")
            response.raise_for_status()
            users = response.json()
        except requests.exceptions.RequestException as e:
            print({"error": str(e)}), 500
            users = []
        return render_template("accueilAdmin.html", users=users)
    return render_template("profil.html", user=user_info)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        mail = request.form['mail']
        password = request.form['password']
        
        response = requests.post(API_URL + "user/signin", json={'mail': mail, 'password': password})
        
        if response.status_code == 200:
            token = response.json().get('token')
            if token:
                resp = make_response(redirect('/'))
                resp.set_cookie('jwt_token', token, httponly=True, max_age=100000)
                return resp
            else:
                flash('Erreur lors de la récupération du token', 'error')
                return redirect('/login')
        else:
            flash('Email ou mot de passe incorrect', 'error')
            return redirect('/login')
    
    return render_template('connexion.html')

@app.route('/logout')
def logout() :
    resp = redirect('/login')
    resp.set_cookie('jwt_token', '', expires=0)
    return resp
    
@app.route('/signup', methods=['GET', 'POST'])
def signUp() :
    jwt_token = request.cookies.get('jwt_token')
    
    if not jwt_token:
        if request.method == 'POST':
            mail = request.form.get("mail")
            password = request.form.get("password")
            name = request.form.get("name")
            firstname = request.form.get("firstname")
            age = request.form.get("age")

            data={
                'mail' : mail,
                'password' : password,
                'name' : name,
                'firstname' : firstname,
                'age' : age
            }
            
            if not name or not password or not firstname or not age or not mail:
                return jsonify({'message': "Tous les champs n'ont pas été remplis"}), 400
            
            response = requests.post(API_URL + "user/signup", json=data)
            if response.status_code == 201 or response.status_code == 200:
                return redirect("/login")
            else:
                return jsonify({'message': 'Failed to add user'}), response.status_code
        return render_template("inscription.html")
    
    
@app.route('/profil', methods=['GET'])
def get_user():
    jwt_token = request.cookies.get('jwt_token')
    
    if not jwt_token:
        return redirect('/login')
    
    user_info = verify_jwt(jwt_token)
    
    return render_template("profil.html", user=user_info)
    
@app.route('/user/add', methods=['POST'])
def add_user() :
    mail = request.form.get("mail")
    password = request.form.get("password")
    name = request.form.get("name")
    firstname = request.form.get("firstname")
    age = request.form.get("age")

    data={
        'mail' : mail,
        'password' : password,
        'name' : name,
        'firstname' : firstname,
        'age' : age
    }
    
    if not name or not password or not firstname or not age or not mail:
        return jsonify({'message': "Tous les champs n'ont pas été remplis"}), 400
    
    response = requests.post(API_URL + "user/signup", json=data)
    if response.status_code == 201 or response.status_code == 200:
        return redirect("/")
    else:
        return jsonify({'message': 'Failed to add user'}), response.status_code
    
@app.route('/user/update/<user_id>', methods=['POST'])
def update_user(user_id) :
    mail = request.form.get("mail")
    password = request.form.get("password")
    name = request.form.get("name")
    firstname = request.form.get("firstname")
    age = request.form.get("age")

    data={
        'mail' : mail,
        'password' : password,
        'name' : name,
        'firstname' : firstname,
        'age' : age
    }
    
    if not name or not password or not firstname or not age or not mail:
        return jsonify({'message': "Tous les champs n'ont pas été remplis"}), 400
    
    response = requests.put(API_URL + "user/" + user_id, json=data)
    if response.status_code == 201 or response.status_code == 200:
        return redirect("/")
    else:
        return jsonify({'message': 'Failed to add user'}), response.status_code
    
@app.route('/user/delete/<user_id>', methods=['GET'])
def delete_user(user_id) :
    response = requests.delete(API_URL + "user/" + user_id)
    if response.status_code == 201 or response.status_code == 200:
        return redirect("/")
    else:
        return jsonify({'message': 'Failed to add user'}), response.status_code
    
@app.route('/myexercises', methods=['GET'])
def getExercisesFromSession() :
    jwt_token = request.cookies.get('jwt_token')
    
    if not jwt_token:
        return redirect('/login')
    
    user_info = verify_jwt(jwt_token)
    try:
        userSession = requests.get(API_URL + "session/user/" + user_info.get("user_id"))
        response = requests.get(API_URL + "exercise/" + userSession)
        response.raise_for_status()
        exercises = response.json()
        return render_template('exos_realises.html', exercises=exercises)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/exercises/<session_id>/<exercise_id>', methods=['GET'])
def getExerciseFromSessionByIds(session_id, exercise_id) :
    return "Exercise id Session Detail"

@app.route('/exercises', methods=['GET'])
def getExercises() :
    return "Exercises Available"

@app.route('/exercice/<exercise_id>', methods=['GET'])
def getExerciseById(exercise_id) :
    return "Exercise Detail"


