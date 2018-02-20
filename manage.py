#!/usr/bin/env python

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from rep import app
from rep.models import db
from rep.tasks_apscheduler import schedule_rescuetime_task

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

# Initialize task-queue before and run flask app
if __name__ == '__main__':
    schedule_rescuetime_task()
    manager.run()



