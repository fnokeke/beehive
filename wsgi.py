#!~/.virtualenvs/rep-aws-env/bin/python

from rep import app
from rep.tasks_apscheduler import schedule_rescuetime_task

# Initialize task-queue before and run flask app
if __name__ == "__main__":
    print "WSGI.py"
    schedule_rescuetime_task()
    app.run(debug=True)

