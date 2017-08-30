# Beehive Web 1.5
A platform for researchers to conduct behavioral studies using mobile phones and user contexts

## Application Flow
- Researcher logs in to create experiment in `/researcher` and activates experiment datastreams
- Participant joins experiment via mobile app (android/iOS);
- Participant can also log in via web to see account details through `/participant`
- Participant grants access to researcher experiment through mobile app or web view
- Depending on activated experiment datastreams, participant may need to grant access to datastreams such as Google Calendar, Moves, RescueTime, Photographic Affect Meter (PAM).
- Enjoy!

## Privacy
todo

## Frontend / Client
- HTML 5, Jinja2, CSS, Javascript

## Production Backend / Server
- Flask server for managing & hosting content
- Postgres database for storing records
- Celery for periodically tasks
- Redis server for supporting celery

## Development Backend / Local Server
- Flask server for managing & hosting content
- Local Postgres database for storing records
- Celery for periodically exporting moves data to Google calendar
- Redis server for supporting celery

## Services
- Account Login using Google Oauth2 and Flask-Login
- Google Calendar Service for accessing user calendar
- [Moves API][Moves API]
- [RescueTime API][RescueTime API]

## Environment
- Install virtualenv and activate a new environment. Virtualenv was used to set up the environment of this project. If you're a little fancy, you can use virtualenvwrapper to manage your virtual environments. You can look at [this helpful virtual env & virtualenvwrapper guide][Virtualenv Guide]
=======
## Development Environment
- Install virtualenv and activate a new environment. Virtualenv was used to set up the environment of this project. If you a little fancy, you can use virtualenvwrapper to manage your virtual environments. You can look at [this helpful virtual env & virtualenvwrapper guide][Virtualenv Guide]
- Install Postgres or Postgres app on your local development machine. Make sure postgres sql (or postgres sql app) is installed and the path to pg_config is included in the $PATH variable. For Mac/Linux users this involves adding appropriate path to the .bash_profile file.
- Install requirements: `pip install -r requirements.txt`

## Oauth2 Setup
- To [use Google Oauth2][Google Credentials], create a project so you have `client_id` and `client_secret`.  
*NB: Although countless ways/libraries exist for enabling Oauth2, I recommend [this nice tutorial][Google Flask Oauth Tutorial] for how to setup Google Oauth2 access on a flask server. It's simple and straight to the point.*
- To [access Moves API][Moves API], you also need to set up a developer account.
- To access RescueTime API using Oauth, you need to contact RescueTime (applicable July 2017)

## Postgres installation
- If on mac, best to setup your postgres local environment by installing [postgres app][postgres app link].
- On linux, use `pip install psycopg2` (psycopg2 is not in requirements.txt because it breaks setup on mac).

## Create postgres user
- Install postgres and launch command line tool.
- create user: `CREATE USER repadmin WITH password 'password';`
- you can alter user password later: `ALTER USER repadmin WITH PASSWORD '<new password>' # password must be in quotes`
- create db: `CREATE DATABASE repdb WITH OWNER slmadmin;`
- grant privileges: `grant all privileges on database repdb to repadmin;`
- change database owner: `ALTER DATABASE repdb OWNER to repadmin;`
- login: `psql -d repdb -U repadmin -W # -W prompts for a password`

## Additional postgres config
You may need to configure postgres file: `pg_hba.conf` if getting error:
`FATAL: Ident authentication failed for user`:
- For linux, login as postgres user: `sudo su - postgres` or open config file in `/var/lib/<pgsql_version>/data/`
- Add this line to pg_hba.conf file: `host repdb repadmin all md5`
- Save file and launch postgres session as shown above and reload config: `SELECT pg_reload_conf();`

## PAM
- Install PAM application from android/iOS store

## DB Migrations
```
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py db upgrade
$ python manage.py db --help
```

## Run Server
- `pip install -r requirements.txt`
- Change directory to one directory lower so you see `runserver.py` file
- Rename `fake_secret_keys.py` to `secret_keys.py`
- Move `secret_keys.py` so it is in the same directory as `runserver.py`
- `python runserver.py` to start server on `localhost:5000`

## How to run
- Start redis server: `redis-server`
- Start postgresql server by launching `Postgres` application
- Create database: `db.create_all() # you can do this by importing db from models`.
- Commit changes: `db.session.commit()`. You can use Postico as a gui for your DB.
- Start celery in verbose mode: `run celery verbose: celery -A tasks.celery worker --loglevel=info --beat`
- Start flask server: `python run.py`
- Go to your server link: [http://localhost:5000](http://localhost:5000)

## Production deployment with gunicorn, supervisor, wsgi
- `pip install gunicorn supervisor` (NB: supervisor is installed in virtualenv
		instead of system wide installation)
- generate sample supervisor file with `echo_supervisord_conf > supervisord.conf`
- modify your supervisord.conf to add the program of interest (inside
		supervisord.conf, our program is titled: rep-webserver)
- start supervisor: `supervisord -c supervisord.conf`
- Refresh your browser and good to go!


[Google Credentials]: [https://console.developers.google.com/apis/credentials?project=_]

[Google Flask Oauth Tutorial]: [https://developers.google.com/api-client-library/python/auth/web-app]

[Moves API]: [https://dev.moves-app.com/]

[RescueTime API]: [https://www.rescuetime.com/developers]

[Virtualenv Guide]: [http://docs.python-guide.org/en/latest/dev/virtualenvs/]

[postgres app link]: [http://postgresapp.com/]
