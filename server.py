from flask import Flask, request, jsonify, make_response, render_template, session
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os
from dotenv import load_dotenv

##################################
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY']=os.getenv("FLASK_SECRET_KEY")


def token_required(func):
    @wraps(func)
    def decorated(*args,**kwargs):
        token = request.args.get("token")
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'Alert!': 'Invalid Token!'}), 401
    return decorated






#########################

@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return 'Logged in Currently'
    

@app.route("/login", methods=['POST'])
def login():
    if request.form['username'] and request.form['password'] == '123456':
        session['logged_in']=True
        exp_time = datetime.utcnow() + timedelta(seconds=600)
        token = jwt.encode({
            'user': request.form['username'],
            'exp': exp_time.timestamp()
        },
        app.config['SECRET_KEY'])
        return jsonify({'token': token}), 200
    else:
        return make_response('Unable to veriy', 403, {'auth': 'Basic realm : "Auth Failed"'})

    
@app.route('/public')
def public():
    return 'For Public'

@app.route('/auth')
@token_required
def auth():
    return 'JWT is verified, Welcome to the APP'

if __name__ == '__main__':
    app.run(debug=True)