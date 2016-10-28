# rep.0
Research Experiment Testbed for conducting participant experiments

## Application Flow
- Log in with Google Sign in
- Grant SLM access to your Google Calendar
- Connect to Moves (you also need to download moves app on your phone for this to work)
- Enjoy!

## Privacy
This only stores oauth access tokens for providing developer access to user accounts.

## Frontend / Client
- HTML 5, Jinja2, CSS, Javascript

## Backend / Server
- Flask server for managing & hosting content
- Postgres database for storing records
- Celery for periodically exporting moves data to Google calendar
- Redis server for supporting celery

## Services
- Account Login using Google Oauth2 and Flask-Login
- Google Calendar Service for accessing user calendar
- [Moves API][Moves API]

## Environment
- Install virtualenv and activate a new environment. Virtualenv was used to set up the environment of this project. If you a little fancy, you can use virtualenvwrapper to manage your virtual environments. You can look at [this helpful virtual env & virtualenvwrapper guide][Virtualenv Guide]
- Install requirements: `pip install -r requirements.txt`

## Oauth2 Setup
- To [use Google Oauth2][Google Credentials], create a project so you have `client_id` and `client_secret`.  
*NB: Although countless ways/libraries exist for enabling Oauth2, I recommend [this nice tutorial][Google Flask Oauth Tutorial] for how to setup Google Oauth2 access on a flask server. It's simple and straight to the point.*
- To [access Moves API][Moves API], you also need to set up a developer account.

## Create postgres user
- Install postgres and launch session: `sudo -u postgres psql`
- create user: `CREATE USER slmadmin WITH password 'password';`
- you can alter user password later: `ALTER USER slmadmin WITH PASSWORD '<new password>' # password must be in quotes`
- create db: `CREATE DATABASE slmdb WITH OWNER slmadmin;`
- grant privileges: `grant all privileges on database slmdb to slmadmin;`
- change database owner: `ALTER DATABASE slmdb OWNER to slmadmin;`
- login: `psql -d slmdb -U slmadmin -W # -W prompts for a password`

## Additional postgres config
You may need to configure postgres file: `pg_hba.conf` if getting error:
`FATAL: Ident authentication failed for user`:
- For linux, login as postgres user: `sudo su - postgres` or open config file in `/var/lib/<pgsql_version>/data/`
- Add this line to pg_hba.conf file: `host slmdb slmadmin all md5`
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

## How to run
- Start redis server: `redis-server`
- Start postgresql server by launching `Postgres` application
- Create database: `db.create_all() # you can do this by importing db from models`.
- Commit changes: `db.session.commit()`. You can use Postico as a gui for your DB.
- Start celery in verbose mode: `run celery verbose: celery -A tasks.celery worker --loglevel=info --beat`
- Start flask server: `python run.py`
- Go to your server link: [http://localhost:5000](http://localhost:5000)


[Google Credentials]: [https://console.developers.google.com/apis/credentials?project=_]

[Google Flask Oauth Tutorial]: [https://developers.google.com/api-client-library/python/auth/web-app]

[Moves API]: [https://dev.moves-app.com/]

[Virtualenv Guide]: [http://docs.python-guide.org/en/latest/dev/virtualenvs/]
