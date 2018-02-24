#!~/.virtualenvs/rep-aws-env/bin/python

from rep import app

# Initialize task-queue before and run flask app
if __name__ == "__main__":
    # Call task scheduler here when using WSGI
    app.run(debug=True)

