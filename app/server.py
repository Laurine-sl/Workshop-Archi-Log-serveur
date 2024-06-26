import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from flask_cors import CORS

load_dotenv()

API_URL = os.getenv('API_URL')
print(API_URL)

app = Flask(__name__)
CORS(app)

@app.route('/')
def get_users():
    try:
        response = requests.get(API_URL + "user")
        response.raise_for_status()
        users = response.json()
    except requests.exceptions.RequestException as e:
        print({"error": str(e)}), 500
        users = []
    return render_template("accueil.html", users=users)
    
# @app.route('/users', methods=['GET'])
# def get_users():
    
@app.route('/user/<user_id>', methods=['GET'])
def get_user(user_id):
    try:
        response = requests.get(API_URL + "user/" + user_id)
        response.raise_for_status()
        users = response.json()
        return jsonify(users)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/users/update/<user_id>', methods=['PUT'])
def update_user(user_id) :
    try:
        response = requests.get(API_URL + "user/" + user_id)
        response.raise_for_status()
        users = response.json()
        return jsonify(users)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/exercises/<session_id>', methods=['GET'])
def getExercisesFromSession(session_id) :
    return "Exercises Session"

@app.route('/exercises/<session_id>/<exercise_id>', methods=['GET'])
def getExerciseFromSessionByIds(session_id, exercise_id) :
    return "Exercise id Session Detail"

@app.route('/exercises', methods=['GET'])
def getExercises() :
    return "Exercises Available"

@app.route('/exercice/<exercise_id>', methods=['GET'])
def getExerciseById(exercise_id) :
    return "Exercise Detail"