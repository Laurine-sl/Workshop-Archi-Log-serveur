import os

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv()

API_URL = os.getenv('API_URL')
print(API_URL)

app = Flask(__name__)
CORS(app)
    
# @app.route("/") 
# def connection() :
    



if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
