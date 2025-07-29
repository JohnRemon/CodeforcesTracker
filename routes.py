from datetime import timedelta, datetime
from flask import render_template, request, redirect, url_for, session, current_app
from functools import wraps
from codeforces_api import *
from models import *
import openai
import jwt
from flask_mail import Message

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
def send_email(email, token):
    reset_link = url_for('reset_password_with_token', token=token, _external=True)
    msg = Message("Password Reset Request", recipients=[email],
                    body=f"Click the link to reset your password: {reset_link}")
    current_app.extensions['mail'].send(msg)
def setup_routes(app, db):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            handle = request.form.get('handle')
            if check_handle(handle) is False:
                return "Invalid Handle", 400
            return redirect(url_for('guest_dashboard', handle=handle))
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
                session['user_id'] = user.user_id
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
            elif not user.check_password(password):
                error_message = "Invalid Password."
            if error_message is None:
                session['user_id'] = user.user_id
                return redirect(url_for('dashboard', handle=user.handle))
            return render_template('login.html', error_message=error_message)
        else:
            return render_template('login.html')
        
    @app.route('/reset_password', methods=['GET', 'POST'])
    def reset_password():
        if request.method == 'POST':
            email = request.form.get('email')
            error_message = None
            user = db.session.query(User).filter_by(email=email).first()
            if not user:
                error_message = "Account Does Not Exit. Please Register"
            if error_message is None:
                success_message = "An email was sent. Link expires in 10 minutes."
                token = jwt.encode(
                    {
                        'email': email,
                        'exp': datetime.now() + timedelta(minutes=10)
                    },
                    'secret_key',
                    algorithm='HS256'
                )
                send_email(email, token)
                return render_template('reset_password.html', success_message=success_message)
            else:
                return render_template('reset_password.html', error_message=error_message)
            
        return render_template('reset_password.html')
    @app.route('/reset-password/<token>', methods=['GET', 'POST'])
    def reset_password_with_token(token):
        try:
            data = jwt.decode(token, 'secret_key', algorithms=['HS256'])
            email = data['email']
        except jwt.ExpiredSignatureError:
            return render_template('new_password.html', error_message="Token expired. Please request a new password reset.")
        except jwt.InvalidTokenError:
            return render_template('new_password.html', error_message="Invalid token. Please request a new password reset.")

        if request.method == 'POST':
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')

            if new_password != confirm_password:
                return render_template('new_password.html', error_message="Passwords do not match.")

            user = db.session.query(User).filter_by(email=email).first()
            if user:
                user.set_password(new_password) 
                db.session.commit()
                success_message = "Password reset successfully. You can now log in."
                return render_template('login.html', success_message=success_message)
            else:
                return render_template('new_password.html', error_message="User not found.")

        return render_template('new_password.html')

    @app.route('/logout')
    @login_required
    def logout():
        session.pop('user_id', None)
        return redirect(url_for('index'))

    def render_dashboard(handle, template, logged_in=False):
        data = get_problem_tags(handle)
        submissions = get_problem_info(handle)
        contests = get_user_contests(handle)
        contests.reverse()
        contest_problems = [get_contest_problems(contest['contestId']) for contest in contests]
        solved_problems = get_solved_contest_problems(handle)
        unsolved_problems = get_unsolved_contest_problems(handle)
        user_info = get_user_info(handle)
        user = db.session.query(User).filter_by(handle=handle).first()
        notes = {}
        if user:
            for sub in submissions:
                note = Note.query.filter_by(user_id=user.user_id, problem_name=sub['name']).first()
                notes[sub['name']] = note is not None


        return render_template(
            template,
            handle=handle,
            data=data,
            contests=contests,
            contest_problems=contest_problems,
            solved_problems=solved_problems,
            unsolved_problems=unsolved_problems,
            submissions=submissions,
            user_info=user_info,
            logged_in=logged_in,
            notes=notes,
        )

    @app.route('/dashboard/<handle>', methods=['GET', 'POST'])
    @login_required
    def dashboard(handle):
        return render_dashboard(handle, 'logged_in_dashboard.html', logged_in=True)

    @app.route('/guest_dashboard/<handle>', methods=['GET', 'POST'])
    def guest_dashboard(handle):
        return render_dashboard(handle, 'dashboard.html', logged_in=False)

    @app.route('/dashboard/<handle>/<int:contest_id>/<problem_index>/create_note', methods=['GET', 'POST'])
    @login_required
    def create_note(handle, contest_id, problem_index):
        problem = get_specific_problem_info(handle, contest_id, problem_index)
        user = db.session.query(User).filter_by(handle=handle).first()
        if request.method == 'POST':
            note = request.form.get('note')
            db.session.add(Note(user_id=user.user_id, contest_id=contest_id, problem_index=problem_index, problem_name=problem['name'], content=note, timestamp=datetime.now()))
            db.session.commit()
            return redirect(url_for('dashboard', handle=handle))
        else:
            return render_template('add_note.html', handle=handle, problem=problem)

    @app.route('/dashboard/<handle>/<int:contest_id>/<problem_index>/view_note', methods=['GET'])
    @login_required
    def view_note(handle, contest_id, problem_index):
        user = db.session.query(User).filter_by(handle=handle).first()
        if not user:
            return "User not found", 404
        problem = get_specific_problem_info(handle, contest_id, problem_index)
        notes = Note.query.filter_by(user_id=user.user_id,contest_id=contest_id,problem_index=problem_index).all()
        solution = Solution.query.filter_by(user_id=user.user_id, contest_id=contest_id, problem_index=problem_index).first()
        return render_template('view_note.html', handle=handle, problem=problem, notes=notes, solution=solution)

    @app.route('/dashboard/<handle>/<int:contest_id>/<problem_index>/add_solution', methods=['GET', 'POST'])
    @login_required
    def add_solution(handle, contest_id, problem_index):
        problem = get_specific_problem_info(handle, contest_id, problem_index)
        user = db.session.query(User).filter_by(handle=handle).first()
        if request.method == 'POST':
            code = request.form.get('solution')
            db.session.add(Solution(user_id=user.user_id, contest_id=contest_id, problem_index=problem_index, problem_name=problem['name'], code=code, timestamp=datetime.now()))
            db.session.commit()
            return redirect(url_for('dashboard', handle=handle))
        return render_template('add_solution.html', handle=handle, problem=problem)
    
    @app.route('/dashboard/<handle>/<int:contest_id>/<problem_index>/ai_review', methods=['GET'])
    @login_required
    def ai_review(handle, contest_id, problem_index):
        problem = get_specific_problem_info(handle, contest_id, problem_index)
        user_code = Solution.query.filter_by(user_id=session['user_id'], contest_id=contest_id, problem_index=problem_index).first()
        prompt = f"""
        Here is a codeforces problem:
        Problem Name: {problem['name']}
        Problem Index: {problem_index}
        Problem Statement: {problem['description']}
        Here is the user's solution:
        {user_code.code if user_code else "No solution submitted yet."}
        Please provide:
        1. An optimal Solution
        2. a comparison between the user's solution and the optimal solution
        3. a review of the user's solution
        4. suggestions for improvement
        """
        
        message = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        response = message['choices'][0]['message']['content']
        return render_template('ai_review.html', handle=handle, problem=problem, response=response)