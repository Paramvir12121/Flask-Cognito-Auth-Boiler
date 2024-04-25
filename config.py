from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# General Flask configuration
SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'you_should_change_this')

# AWS Cognito Configuration
COGNITO_REGION = os.getenv('COGNITO_REGION')
COGNITO_USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
COGNITO_APP_CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
COGNITO_DOMAIN = os.getenv('COGNITO_DOMAIN')

# AWS Cognito Optional Configurations
# Depending on your setup, you might also need the following:
COGNITO_CLIENT_SECRET = os.environ.get('COGNITO_CLIENT_SECRET', None)  # Only if your client requires a secret
COGNITO_REDIRECT_URI = os.environ.get('COGNITO_REDIRECT_URI', 'http://localhost:5000/aws_cognito_redirect')

# JWT Configuration for the app
JWT_TOKEN_LOCATION = ['cookies']  # Tokens are transported via HTTPOnly Cookies
JWT_COOKIE_SECURE = False  # True in production (HTTPS), false in development (HTTP)
JWT_COOKIE_CSRF_PROTECT = True  # Enable CSRF protection
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'another_secret_key')  # Secret key for encoding JWTs

# Database configuration (if needed)
# DATABASE_URI = os.environ.get('DATABASE_URI', 'sqlite:///your_database.db')
