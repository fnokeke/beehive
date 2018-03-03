# Beehive Web v2.0
A framework for conducting behavioral studies using mobile phones, digital nudges and contexts (such as location traces, phone usage habit, and electronic calendar schedules).

## Application Flow 
In its default state, the framework can be used to run research studies. Below is the application flow for conducting a study:
- Researcher logs in and creates a new experiment.
- Participant joins experiment via mobile app (android/iOS) and experiences study interventions (such as push notifications, phone vibrations, PAM).
- Researcher monitors experiment progress through dashboards and can download user data for extensive offline analysis.

## Quick Setup
- `mkvirtualenv bhenv` (virtualenv wrapper creates and activates virtualenv / if you don't have plugin, first create virtualenv then activate)
- `pip install -r requirements.txt`.
- If you encounter issues installing `psycopg2`, open `requirements.txt` and change `psycopg2==2.6.1` to `psycopg2` and rerun the install cmd.
- `mv rep/fake_secret_keys.py rep/secret_keys.py` (rename fake_secret_keys to secret_keys. This file contains empty variables that will be populated later. See example with Google Oauth2.0 below.)
- `python runserver.py` to start server on `http://localhost:5000/` as dev mode


***NB: You need to setup Google Oauth2.0 for Google Login to work.***

## Google Oauth2.0 Setup
- Create a new project on [Google Developer Console](https://console.developers.google.com/project/_/apiui/apis/library).
- In the console, add `http://localhost:5000` and your domain as Authorized redirect URIs as local and prod urls respectively.
- Locate your credentials on the developer console and copy your developer client ID and client secret into `secret_keys.py` as `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` variables respectively


## Frontend / Client
- HTML 5, Jinja2, CSS, Javascript

## Backend / Server
- Flask server for managing & hosting content.
- Local Postgres database for storing records.
- Celery for periodically exporting data from 3rd party services into another location e.g. exporting moves data as events on Google calendar.
- Redis server for supporting celery.

## Services
- Account Login using Google Oauth2 and Flask-Login.
- Google Calendar Service for accessing user calendar.
- [RescueTime API][RescueTime API].
- [Moves API][Moves API].
- More coming soon.

## Tips about setup
###### Virtual Environment
- Virtualenv was used to set up the environment of this project. If you a little fancy, you can use virtualenvwrapper to manage your virtual environments. You can look at [this helpful virtual env & virtualenvwrapper guide][Virtualenv Guide].
- Install requirements for development into python virtualenv environment using: `pip install -r requirements.txt`.

###### Postgres
- Install Postgres or Postgres app on your local development machine. Make sure postgres sql (or postgres sql app) is installed and the path to pg_config is included in the $PATH variable. For Mac/Linux users this involves adding appropriate path to the .bash_profile file.
- If on mac, it's much easier to setup your postgres local environment by installing [postgres app][postgres app link].
- On production environment, you need to install psycopg2: `pip install psycopg2`.
-For GUI database client on mac, I highly recommend the pro version of [Postico app](https://eggerapps.at/postico/).

###### Oauth2 Setup
- To [use Google Oauth2](Google Credentials), create a project so you have `client_id` and `client_secret`.  
- Although countless ways/libraries exist for enabling Oauth2, I recommend [this nice tutorial](Google Flask Oauth Tutorial) for how to setup Google Oauth2 access on a flask server. It's simple and straight to the point.

###### Other Datastreams
- To access google calendar data, follow the same logic as Google Oauth2.0 Signin but update the access scope to include calendar.
- To [access Moves API][Moves API], you also need to set up a developer account.
- To access RescueTime API using Oauth, you need to contact RescueTime (applicable July 2017).

## Postgres Installation
###### Create new postgres user
- Install postgres and launch command line tool.
- create user: `CREATE USER repadmin WITH password 'password';`.
- you can alter user password later: `ALTER USER repadmin WITH PASSWORD '<new password>' # password must be in quotes`.
- Create db: `CREATE DATABASE repdb WITH OWNER repadmin;`.
- Grant privileges: `grant all privileges on database repdb to repadmin;`.
- Change database owner: `ALTER DATABASE repdb OWNER to repadmin;`.
- Login: `psql -d repdb -U repadmin -W # -W prompts for a password`.

###### Additional postgres config
You may need to configure postgres file: `pg_hba.conf` if getting error:
`FATAL: Ident authentication failed for user`:
- For linux, login as postgres user: `sudo su - postgres` or open config file in `/var/lib/<pgsql_version>/data/`.
- Add this line to pg_hba.conf file: `host repdb repadmin all md5`.
- Save file and launch postgres session as shown above and reload config: `SELECT pg_reload_conf();`.

###### DB Migrations
```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
$ python manage.py db --help
```

###### Redis and Celery (optional)
Celery is a task queue. Celery requires a solution to send and receive messages; usually this comes in the form of a separate service called a message broker.
There are several choices available, including:  RabbitMQ, Redis, Amazon SQS etc. In this project we user Redis as the message broker.
Redis is an open source (BSD licensed), in-memory data structure store, used as a database, cache and message broker. 

You can follow these instructions if you plan to run periodic tasks. In this project, Celery is used for running cron jobs that dump results in the postresql database.
- Start redis server: `redis-server`.
- Start postgresql server by launching `Postgres` application.
- Create database: `db.create_all() # you can do this by importing db from models`.
- Commit changes: `db.session.commit()`. You can use Postico as a gui for your DB.
- Start celery in verbose mode: `run celery verbose: celery -A tasks.celery worker --loglevel=info --beat`.
- Start flask server: `python runserver.py`.
- Go to your local server: [http://localhost:5000/](http://localhost:5000/).

###### Production deployment with gunicorn, supervisor, wsgi
- `pip install gunicorn supervisor`.
(NB: supervisor is installed in virtualenv instead of performing system wide installation).
- Generate sample supervisor file with `echo_supervisord_conf > supervisord.conf`.
- Modify your supervisord.conf to add the program of interest (inside supervisord.conf, our program is titled: rep-webserver).
- Start supervisor: `supervisord -c supervisord.conf`.
- `./run_gunicorn.sh` starts server with multiple workers.
- Refresh your browser and you should be good to go!

## Beehive + ResearchStack
To create android apps that build on ResearchStack,[follow this guide.](https://github.com/fnokeke/NewBeehiveSurvey)

## Privacy
To maintain and preserve user privacy, this project will eventually access third party datastreams using [Immersive Core](https://github.com/cornelltech/immersive-core).


[Google Credentials]: [https://console.developers.google.com/apis/credentials?project=_]

[Google Flask Oauth Tutorial]: [https://developers.google.com/api-client-library/python/auth/web-app]

[Moves API]: [https://dev.moves-app.com/]

[RescueTime API]: [https://www.rescuetime.com/developers]

[Virtualenv Guide]: [http://docs.python-guide.org/en/latest/dev/virtualenvs/]

[postgres app link]: [http://postgresapp.com/]
