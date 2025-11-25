import os
from pathlib import Path
from dotenv import load_dotenv
from django.contrib.messages import constants as messages

# .env dosyasını yükle
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET KEY ve DEBUG ayarlarını .env dosyasından al
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-default-key-for-development')
DEBUG = os.getenv('DEBUG', 'True') == 'True' # Geliştirme ortamında True olması için varsayılanı değiştirdim

ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Kendi Uygulamalarımız (apps klasörü altındakiler)
    'apps.core.apps.CoreConfig',
    'apps.users.apps.UsersConfig',
    'apps.profiles.apps.ProfilesConfig',
    'apps.gamification.apps.GamificationConfig',
    'apps.diary.apps.DiaryConfig',
    'apps.plans.apps.PlansConfig', 
    'apps.nutrition.apps.NutritionConfig', 
    'apps.chatbot.apps.ChatbotConfig',
    'apps.appointments.apps.AppointmentsConfig',
    'apps.recipes.apps.RecipesConfig',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Proje genelindeki templates klasörü
        'DIRS': [BASE_DIR / 'templates'], 
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                
                # Eğer core uygulamasında bu dosya yoksa burayı yorum satırına almalısın!
                # 'apps.core.context_processors.dynamic_nav', 
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'tr'
TIME_ZONE = 'Europe/Istanbul'
USE_I18N = True
USE_TZ = True

# --- STATIC FILES (CSS, JS, Images) ---
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles' # collectstatic komutu için gerekli

# --- MEDIA FILES (Yemek Fotoğrafları İçin Kritik) ---
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- AUTHENTICATION SETTINGS ---
# CustomUser modelimizi işaret ediyoruz (users/models.py dosyasındaki sınıf adı)
AUTH_USER_MODEL = 'users.CustomUser'

# Yönlendirmeler
LOGIN_REDIRECT_URL = '/'       # Giriş yapınca ana sayfaya (dashboard) git
LOGOUT_REDIRECT_URL = '/'      # Çıkış yapınca ana sayfaya (login) git
LOGIN_URL = 'login'            # Giriş yapmamış kullanıcıyı buraya at

# --- BOOTSTRAP 5 MESAJ ENTEGRASYONU ---
# Django'nun 'error' mesajını Bootstrap'in 'danger' sınıfına eşliyoruz
MESSAGE_TAGS = {
    messages.ERROR: 'danger',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.INFO: 'info',
}

# --- GOOGLE GEMINI AI SETTINGS ---
# Not: API Anahtarını .env dosyasından çekmek en doğrusudur.
GEMINI_API_KEY = "Guvenliknedeniylesildim" 
GEMINI_MODEL_NAME = "gemini-2.0-flash"