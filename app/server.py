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
        return jsonify({'message': 'Failed to delete user'}), response.status_code
    
@app.route('/myexercises', methods=['GET'])
def getExercisesFromSession() :
    jwt_token = request.cookies.get('jwt_token')

    if not jwt_token:
        return redirect('/login')
    
    user_info = verify_jwt(jwt_token)
    userSession = getSessionId(user_info)
    response = requests.get(API_URL + "session/exercise/" + str(userSession.get("session_id")))
    
    if response.status_code == 200 or response.status_code == 201:
        response.raise_for_status()
        exercises = response.json()
    else :
        exercises=[]
    allExercises = getAllExercises()
    return render_template("exos_realises.html", allExercises=allExercises, exercises=exercises)


@app.route('/exercises', methods=['GET'])
def getExercises() :
    allExercises = getAllExercises()
    print(allExercises)
    return render_template("banque_exos.html", exercises=allExercises)

@app.route('/myexercises/add', methods=['GET', 'POST'])
def addExercise() :
    jwt_token = request.cookies.get('jwt_token')
    
    if not jwt_token:
        return redirect("/")
    user_info = verify_jwt(jwt_token)

    title = request.form.get("title")
    tempo = request.form.get("tempo")
    
    exercise_id = getExerciseIdByTitle(title).get("exercice_id")
    
    data={
        'exercise_id' : exercise_id,
        'tempo' : tempo
    }
    
    if not title or not tempo:
        return jsonify({'message': "Tous les champs n'ont pas été remplis"}), 400
    
    userSession = getSessionId(user_info)
    response = requests.post(API_URL + "session/exercise/" + str(userSession.get("session_id")), json=data)
    if response.status_code == 201 or response.status_code == 200:
        return redirect("/myexercises")
    else:
        print("You already have this exercise : modify your tempo instead"), response.status_code
    
@app.route('/myexercises/update/<exercise_id>', methods=['POST'])
def update_exercise(exercise_id) :
    
    jwt_token = request.cookies.get('jwt_token')
    
    if not jwt_token:
        return redirect("/")

    user_info = verify_jwt(jwt_token)
    title = request.form.get("title")
    tempo = request.form.get("tempo")
    
    exercise_id = getExerciseIdByTitle(title).get("exercice_id")
    
    data={
        'tempo' : tempo
    }
    
    if not title or not tempo:
        return jsonify({'message': "Tous les champs n'ont pas été remplis"}), 400
    
    userSession = getSessionId(user_info)
    response = requests.put(API_URL + "session/exercise/" + str(userSession.get("session_id")) + "/" + str(exercise_id), json=data)
    if response.status_code == 201 or response.status_code == 200:
        return redirect("/myexercises")
    else:
        return jsonify({'message': 'Failed to update exercise'}), response.status_code
    
@app.route('/myexercises/delete/<exercise_id>', methods=['GET'])
def delete_exercise(exercise_id) :
    jwt_token = request.cookies.get('jwt_token')
    
    if not jwt_token:
        return redirect("/")
    user_info = verify_jwt(jwt_token)
    userSession = getSessionId(user_info)
    response = requests.delete(API_URL + "session/exercise/" + str(userSession.get("session_id")) + "/" + exercise_id)
    print(API_URL + "session/exercise/" + str(userSession.get("session_id")) + "/" + exercise_id)
    if response.status_code == 201 or response.status_code == 200:
        return redirect("/myexercises")
    else:
        return jsonify({'message': 'Failed to delete exercise'}), response.status_code
        
def getAllExercises():
    response = requests.get(API_URL + "exercise")
    response.raise_for_status()
    allExercises = response.json()
    return allExercises
    
def getSessionId(user_info):
    userId = user_info.get("id")
    responseSession = requests.get(API_URL + "session/user/" + str(userId))
    responseSession.raise_for_status()
    return responseSession.json()

def getInstrumentById(exercise_id):
    response = requests.get(API_URL + "exercise/instrument/" + exercise_id)
    response.raise_for_status()
    return response.json()

def getExerciseIdByTitle(title):
    response = requests.get(API_URL + "exercise/id/" + title)
    response.raise_for_status()
    return response.json()