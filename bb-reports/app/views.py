from app import app
from flask import render_template
from bb_timing import timing_report
from bb_status import status_report


@app.route("/")
@app.route("/index")
def index():
    return "Hello World! (views.py)"

@app.route('/bb-timing-report')
def bb_timing_report():
    run_data = timing_report()
    return render_template('timing_report.html',
                           title='Timing Report',
                           run_data=run_data)

@app.route('/bb-status')
def bb_status():
    status_data = status_report()
    return render_template('status.html',
                           title='Buildbot Status',
                           status_data=status_data)

