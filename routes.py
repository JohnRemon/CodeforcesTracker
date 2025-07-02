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
        submissions = get_problem_info(handle)[:8]
        contests = get_user_contests(handle)[:5]
        contests.reverse()
        contest_problems = []
        for contest in contests:
            contest_problems.append(get_contest_problems(contest['contestId']))
        solved_problems = get_solved_contest_problems(handle)
        unsolved_problems = get_unsolved_contest_problems(handle)
        return render_template(
            'dashboard.html',
            handle=handle,
            data=data,
            contests=contests,
            contest_problems=contest_problems,
            solved_problems=solved_problems,
            unsolved_problems=unsolved_problems,
            submissions=submissions
        )