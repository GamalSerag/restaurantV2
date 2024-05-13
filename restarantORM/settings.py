from datetime import timedelta
import os
from dotenv import load_dotenv
from pathlib import Path
import firebase_admin
from firebase_admin import credentials

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-=#wwua!#l0$($r1gqe5s9p(8%#*4fylglkca00a(64)o)kmy(h'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TIME_ZONE = os.getenv('TIME_ZONE')


ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'django_jsonform',

    'dj_rest_auth',
    
    # allauth
    'django.contrib.sites',  # make sure sites is included
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.facebook',
    # other
    'multiselectfield',
    'drf_spectacular',
    'corsheaders',
    # 'channels',

    ####### apps
    'auth_app',
    'customer_app',
    'restaurant_app',
    'order_app',
    'employee_app',
    'review_app',
    'offers_app',
    'delivery_app',
    'payment_app',
    'location_app',
    'cart_app',
    'admin_app',
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # Place CSRF middleware here
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # After CSRF middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "allauth.account.middleware.AccountMiddleware",  # Add Allauth middleware
]

ROOT_URLCONF = 'restarantORM.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'restarantORM.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = os.getenv('TIME_ZONE')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'


CORS_ALLOWED_ORIGINS = [
    "http://192.168.1.30:8200",  # Add the URL of your React frontend
    "http://localhost:8200",
    "http://127.0.0.1:8200",

]

# Optional: Allow credentials (cookies, authentication headers, etc.)
CORS_ORIGIN_ALLOW_ALL = True



AUTH_USER_MODEL = 'auth_app.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.TokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',  # Optional if using sessions
        # 'dj_rest_auth.authentication.JWTAuthentication',  # Use JWT authentication
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


REST_AUTH = {
    
    'USE_JWT': True,
    'JWT_AUTH_HTTPONLY':False,
    'JWT_AUTH_COOKIE': 'access',
    'JWT_AUTH_REFRESH_COOKIE': 'refresh',
}

# REST_AUTH_REGISTER_SERIALIZERS  = {
#     'REGISTER_SERIALIZER ': 'auth_app.serializers.CustomSocialLoginSerializer',
# }

# SOCIALACCOUNT_ADAPTER = 'auth_app.custom_adapter.CustomSocialAccountAdapter'

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=0.3),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME': timedelta(days=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME_LATE_USER': timedelta(days=1),
    'SLIDING_TOKEN_LIFETIME_LATE_USER': timedelta(days=30),
}


AUTHENTICATION_BACKENDS = [
    'auth_app.auth_backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
    'rest_framework.authentication.TokenAuthentication',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# SECURE_SSL_REDIRECT = True


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

SITE_ID = 1
ACCOUNT_EMAIL_VERIFICATION = "none"


# SOCIALACCOUNT_PROVIDERS = {
    
#     'google': {
#         'APP': {
#             'client_id': '711863326926-v943grouifn58ksna3q1v3oir91dlafg.apps.googleusercontent.com',
#             'secret': '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',
#         },
#         'SCOPE': [
#             'profile',
#             'email',
#         ],
#         'AUTH_PARAMS': {
#             'access_type': 'offline',
#         }
#     }
# }

# Stripe API keys
STRIPE_TEST_PUBLIC_KEY = os.getenv('STRIPE_TEST_PUBLIC_KEY')
STRIPE_TEST_SECRET_KEY = os.getenv('STRIPE_TEST_SECRET_KEY')
# STRIPE_LIVE_PUBLIC_KEY = 'your_live_public_key'
# STRIPE_LIVE_SECRET_KEY = 'your_live_secret_key'

# DJSTRIPE_FOREIGN_KEY_TO_FIELD = "id"

# CSRF_TRUSTED_ORIGINS = ["http://192.168.1.37:8200", "http://localhost:8000", "http://localhost:8200"]

# CSRF_COOKIE_NAME = 'csrftoken'  # Default CSRF cookie name
CSRF_COOKIE_SECURE = True
# # CSRF_COOKIE_HTTPONLY = True  # Recommended to prevent client-side JavaScript access

SESSION_COOKIE_SECURE = True
# SESSION_COOKIE_SAMESITE = 'None'
# CSRF_COOKIE_SAMESITE = 'None'
# SESSION_COOKIE_DOMAIN = "http://192.168.1.37:8200"
CORS_ALLOW_CREDENTIALS = True

# SECURE_CROSS_ORIGIN_OPENER_POLICY = None




# Firebase Configuration
cred = credentials.Certificate(os.getenv('FIREBASE_CREDENTIALS_PATH'))
firebase_app = firebase_admin.initialize_app(cred, {
    'storageBucket': 'res-admin-app.appspot.com'
})
