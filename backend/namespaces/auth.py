from flask_restx import Api, Resource, Namespace, fields
from models import User
import boto3
from flask import jsonify, request, current_app, make_response, session
from flask_cognito import CognitoAuth, cognito_auth_required, current_cognito_jwt
from exts import db

from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)


auth_ns = Namespace('auth', description='User Authentication APIs namespace')


# Function to get a Cognito client
def get_cognito_client():
    return boto3.client('cognito-idp', region_name=current_app.config['COGNITO_REGION'])

# Reusable error handling
def handle_cognito_error(error):
    if error.response['Error']['Code'] == 'UserNotFoundException':
        return {'message': 'User does not exist'}, 404
    elif error.response['Error']['Code'] == 'NotAuthorizedException':
        return {'message': 'Username or password is incorrect'}, 401
    else:
        return {'message': str(error)}, 400

########################## MODELS #############
login_model = auth_ns.model('Login', {
    'email': fields.String(required=True, description='The user email'),
    'password': fields.String(description='The user password'),
})

signup_confirmation_model= auth_ns.model('Singup_Confirmation', {
    'email': fields.String(required=True, description='The user email'),
    'verification_code': fields.String(description='The verification string'),
})


auth_model = auth_ns.model('Auth', {
    'username': fields.String(required=True, description='The user username'),
    'email': fields.String(required=True, description='The user email'),
    'password': fields.String(description='The user password'),
    'verification_code': fields.String(description='The verification string'),
})

reset_password_request_model = auth_ns.model('ResetPasswordRequest', {
    'email': fields.String(required=True, description='The user email')
})

reset_password_confirmation_model = auth_ns.model('ResetPasswordConfirmation', {
    'email': fields.String(required=True, description='The user email'),
    'password': fields.String(required=True, description='New password'),
    'verification_code': fields.String(required=True, description='Verification code sent to email')
})

logout_model = auth_ns.model('Logout', {
    'access_token': fields.String(required=True, description='User access code'),
})

######################### APIs #############################



@auth_ns.route('/signup')
class SignUp(Resource):

    @auth_ns.marshal_with(login_model) # adds swagger documentation ability
    @auth_ns.expect(login_model)
    def post(self):
        data = request.get_json()
        # app.logger.debug("Received data: %s", data)
        print("Received data:", data)  # Log the received data
        if not data:
            return jsonify({"error": "No data provided"}), 400
        password = str(data.get('password'))
        email = str(data.get('email'))

        client = get_cognito_client()
        try:
            response = client.sign_up(
                ClientId=current_app.config['COGNITO_CLIENT_ID'],
                Username=email,  # Using email as the username
                Password=password,
                UserAttributes=[
                    {'Name': 'email', 'Value': email},
                    # {'Name': 'short_username', 'Value': username}  # Verify the email by default
                ],
            )
            print("Signup Response: ", response)

            return response, 200
        except client.exceptions.ClientError as error:
            return handle_cognito_error(error)

@auth_ns.route('/signup_resend_code')
class SignupResendCode(Resource):
    @auth_ns.marshal_with(reset_password_request_model) # adds swagger documentation ability
    @auth_ns.expect(reset_password_request_model)
    def post(self):
        data = request.get_json()
        # app.logger.debug("Received data: %s", data)
        print("Received data:", data)  # Log the received data
        if not data:
            return jsonify({"error": "No data provided"}), 400
        email = str(data.get('email'))
        client = get_cognito_client()
        try:
            response = client.resend_confirmation_code(
                    ClientId=current_app.config['COGNITO_CLIENT_ID'],
                    Username=email,
                    )
            print("Response: ", response)
            return response, 200
        except client.exceptions.ClientError as error:
            return handle_cognito_error(error)
    
        

@auth_ns.route('/signup_confirmation')
class SignupConfirmation(Resource):
    @auth_ns.marshal_with(signup_confirmation_model) # adds swagger documentation ability
    @auth_ns.expect(signup_confirmation_model)
    def post(self):
        data = request.get_json()
        # app.logger.debug("Received data: %s", data)
        print("Received data:", data)  # Log the received data
        if not data:
            return jsonify({"error": "No data provided"}), 400
        email = str(data.get('email'))
        verification_code = str(data.get('verification_code'))
        client = get_cognito_client()
        try:
            # Confirm the user's signup in Cognito
            client.confirm_sign_up(
                ClientId=current_app.config['COGNITO_CLIENT_ID'],
                Username=email,
                ConfirmationCode=verification_code,
            )
            # Save the user to the database after successful confirmation
            user = User(email=email)
            user.save()
            return {'message': 'Email confirmed and user saved.'}, 200
        except client.exceptions.ClientError as error:
            return handle_cognito_error(error)
        

@auth_ns.route('/login')
class Login(Resource):
    
    @auth_ns.marshal_with(login_model)
    @auth_ns.expect(login_model)
    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        client = get_cognito_client()
        try:
            # Making the call to AWS Cognito
            response = client.initiate_auth(
                ClientId=current_app.config['COGNITO_CLIENT_ID'],
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
            print(response["ChallengeParameters"])
            # If the login is successful, Cognito responds with tokens
            if "AuthenticationResult" in response:
                access_token = response['AuthenticationResult']['AccessToken']
                refresh_token = response['AuthenticationResult']['RefreshToken']
                # Fetch or create user in the database
                user = User.query.filter_by(email=email).first()
                if not user:
                    user = User(email=email)
                    db.session.add(user)
                # Update access and refresh tokens
                user.update_access(access_token, refresh_token)
                session['user_email'] = email
                session['logged_in'] = True
                print("Session: ", session)
                return {"message": "Login Successful"}, 200
                
        except client.exceptions.ClientError as error:
            return handle_cognito_error(error)


@auth_ns.route('/reset_forgotten_password_request')
class ResetForgottenPasswordRequest(Resource):

    @auth_ns.marshal_with(reset_password_request_model)
    @auth_ns.expect(reset_password_request_model)
    def post(self):
        data = request.get_json()
        email = data.get('email')
        client = get_cognito_client()
        try:
            response = client.forgot_password(
            ClientId=current_app.config['COGNITO_CLIENT_ID'],
            Username=email,
            )
            return response, 201
        except client.exceptions.ClientError as error:
            return handle_cognito_error(error)

@auth_ns.route('/reset_forgotten_password_Conformation')
class ResetForgottenPasswordConfirmation(Resource):

    @auth_ns.marshal_with(reset_password_confirmation_model)
    @auth_ns.expect(reset_password_confirmation_model)
    def post(self):
        data = request.get_json()
        email= data.get('email')
        password = data.get('password')
        verification_code = str(data.get('verification_code'))
        client = get_cognito_client()
        try:
            response = client.confirm_forgot_password(
                ClientId=current_app.config['COGNITO_CLIENT_ID'],
                Username=email,
                ConfirmationCode=verification_code,
                Password=password,
            )
            return response, 201
        except client.exceptions.CodeMismatchException:
            return {'message': 'Invalid verification code provided'}, 400
        except client.exceptions.InvalidPasswordException as e:
            return {'message': str(e)}, 400
        except client.exceptions.UserNotFoundException:
            return {'message': 'User not found'}, 404
        except client.exceptions.ClientError as e:
            return {'message': f'Unexpected error occurred: {e.response["Error"]["Message"]}'}, 500
        
@auth_ns.route('/refresh')
class RefreshResource(Resource):
    @cognito_auth_required
    def post(self):
        # current_user = 
        # new_access_token = 
        pass

        

@auth_ns.route('/logout')
class Logout(Resource):
    def post(self):
        if 'user_email' in session:
            email = session['user_email']
            user = User.query.filter_by(email=email).first()
            if user:
                access_token = user.access_token  # Retrieve the access token from the user record
                print("access_token: ", access_token)
                user.update_access(None, None)  # Clear tokens in the database
                session.clear()  # Clear the session
                client = get_cognito_client()
                try:
                    if access_token:
                        client.global_sign_out(AccessToken=access_token)
                        return jsonify({'message': 'Successfully logged out'}), 200
                    else:
                        return jsonify({'message': 'No access token found, manual logout required'}), 400
                except client.exceptions.ClientError as error:
                    return handle_cognito_error(error)
            else:
                session.clear()  # Clear the session even if no user record is found
                return jsonify({'message': 'User not found or already logged out'}), 404
        else:
            return jsonify({'message': 'No active session found'}), 401



        
@auth_ns.route('/protected')
class Protected(Resource):

    @jwt_required()
    def post(self):
        print("Authorized!!!")
        response = {"authorized": "Authorized"}
        print(f"Response to be returned: {response}")
        return make_response(jsonify(response), 201)
