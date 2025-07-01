from flask import render_template, request, jsonify, redirect, url_for
from codeforces_api import *

def setup_routes(app, db):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            #get the handle
            handle = request.form.get('handle')
            if not handle:
                return "No Handle Provided", 400
            #redirect to the dashboard
            return redirect(url_for('dashboard', handle=handle))
        else:
            return render_template('index.html')
    @app.route('/dashboard/<handle>', methods=['GET', 'POST'])
    def dashboard(handle):
        #get user info and display it
        data = get_problem_tags(handle)
        return render_template('dashboard.html', handle=handle, data=data)