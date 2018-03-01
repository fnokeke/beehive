from rep import app
from rep.tasks_apscheduler import schedule_rescuetime_task

if __name__ == '__main__':
    schedule_rescuetime_task()
    app.run(threaded=True, debug=True, host='localhost', port=5000)
