# Noctua OSINT

This is a web application for OSINT for internet-connected devices. Search by IP and host to discover internet-facing devices, perform passive banner grabbing and discover vulnerable systems.

## Requirements

-Django 4.1.5
-django-environ 0.9.0
-django-leaflet 0.28.3
-GDAL 3.4.1
-python 3.10.6
-ZoomEye account with an API key

## Installation
**1. Clone the Repository**

    $ git clone https://github.com/spetrone/noctua-osint.git

**2. Create and activate a virtual environment**

    $ python3 -m venv <env_name>
    $ source <env_name>/bin/activate
**3. Install requirements**

    $ pip install -r requirements.txt
    
 **4. Install GDAL**

*This is required to use Django-Leaflet used for displaying maps*

Installation of the GDAL library is platform-specific. Follow instructions from mothergeo (GDAL's creator) for your system:
https://mothergeo-py.readthedocs.io/en/latest/development/how-to/gdal-ubuntu-pkg.html 

Downloads can be found here: 
https://gdal.org/download.html 
  
  ## Configure & Run
**1. Create environment variables**
*This will hide secret information. We will add variables later on.*

In settings.py write these lines 

    import environ
    env = environ.Env()
    environ.Env.read_env() 

**2. Create a PostgreSQL database**
*(install pgAdmin and postgres if not already installed)*

    $ psql postgres
    $ CREATE DATABASE database_name
    $ \connect database_name

Using credentials for pgAdmin, set the attributes for the DATABASES section in settings.py

    DATABASES = {
    ‘default’: {‘ENGINE’:
    ‘django.db.backends.postgresql_psycopg2’,
    ‘NAME’: env(‘DATABASE_NAME’),
    ‘USER’: env(‘DATABASE_USER’),
    ‘PASSWORD’: env(‘DATABASE_PASS’),}
     }
   In the `.env` file, add the credentials from pgAdmin as the database credentials:

    DATABASE_NAME=database_name
    DATABASE_USER=db_user
    DATABASE_PASS=db_secret_password

**3. Set up the database**

Make migrations

    $ python3 manage.py makemigrations
    $ python3 manage.py migrate 

Create a superuser

    python3 manage.py createsuperuser

**4. Generate a new secret key for the Django app**
1.  Access the Python Interactive Shell

2.  Import  `get_random_secret_key()`  from`django.core.management.utils`.

3.  Generate the key using  `>>> get_random_secret_key()`  

4.  Copy and paste the key into the  `SECRET_KEY`  variable in the  `.env` file
	`SECRET_KEY='xxxxxxxxxxxxxxxxxxxxxxxxxx'`  (it is a string)

**5. Configure ZoomEye API Key**
In the `.env` file add your ZoomEye API key:

    ZOOMEYE_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx

**6. Run**

    python3 manage.py runserver
