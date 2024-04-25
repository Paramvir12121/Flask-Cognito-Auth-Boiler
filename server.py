from flask import Flask, request, redirect, url_for,render_template
from jose import jwt
import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)


app.config['AWS_DEFAULT_REGION'] = os.getenv('COGNITO_REGION')
app.config['AWS_COGNITO_USER_POOL_ID'] = os.getenv('COGNITO_USER_POOL_ID')
app.config['AWS_COGNITO_USER_POOL_CLIENT_ID'] = os.getenv('COGNITO_CLIENT_ID')
app.config['AWS_COGNITO_DOMAIN'] = os.getenv('COGNITO_DOMAIN')
app.config['AWS_COGNITO_USER_POOL_CLIENT_SECRET'] = os.getenv('COGNITO_SECRET', None)
app.config['AWS_COGNITO_REDIRECT_URL'] = 'http://localhost:5000/aws_cognito_redirect'



cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION, aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)














#################### ROUTES #################################


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)