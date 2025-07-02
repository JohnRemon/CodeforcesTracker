from flask import render_template, request, redirect, url_for
from codeforces_api import *
from models import *

def setup_routes(app, db):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            handle = request.form.get('handle')
            if check_handle(handle) is False:
                return "Invalid Handle", 400
            return redirect(url_for('dashboard', handle=handle))
        else:
            return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            handle = request.form.get('handle')
            email = request.form.get('email')
            password = request.form.get('password')
            error_message = None

            if check_handle(handle) is False:
                error_message = "Invalid Handle."

            existing_user = db.session.query(User).filter_by(email=email).first()
            if existing_user:
                error_message = "Account already exists. Please log in."
            if error_message is None:
                user = User(handle=handle, email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                return redirect(url_for('dashboard', handle=handle))
            return render_template('register.html', error_message=error_message)
        else:
            return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            error_message = None

            user = db.session.query(User).filter_by(email=email).first()
            if user is None:
                error_message = "Account does not exist. Please register."
            if not user.check_password(password):
                error_message = "Invalid Password."
            if error_message is None:
                return redirect(url_for('dashboard', handle=user.handle))
            return render_template('login.html', error_message=error_message)
        else:
            return render_template('login.html')

    @app.route('/dashboard/<handle>', methods=['GET', 'POST'])
    def dashboard(handle):
        data = get_problem_tags(handle)
        submissions = get_problem_info(handle)[:5]
        contests = get_user_contests(handle)[:5]
        contests.reverse()
        contest_problems = []
        for contest in contests:
            contest_problems.append(get_contest_problems(contest['contestId']))
        solved_problems = get_solved_contest_problems(handle)
        unsolved_problems = get_unsolved_contest_problems(handle)
        user_info = get_user_info(handle)
        return render_template(
            'dashboard.html',
            handle=handle,
            data=data,
            contests=contests,
            contest_problems=contest_problems,
            solved_problems=solved_problems,
            unsolved_problems=unsolved_problems,
            submissions=submissions,
            user_info=user_info
        )