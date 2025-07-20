from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from users import get_user, users, User
from flask import Flask, render_template, request
import os
from predict import predict_image
from users import get_user, users, User, add_user


app = Flask(__name__)
app.secret_key = 'your_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


# users functions for flask-login
@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    result = ''
    img_path = ''

    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save uploaded image
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # Run prediction
            result, cam_path = predict_image(filepath)
            img_path = cam_path or filepath

    return render_template('index.html', result=result, img_path=img_path)

#   Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    username = '' 

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = 'remember' in request.form

        if username in users and users[username]['password'] == password:
            user = get_user(username)
            login_user(user)
            login_user(user, remember=remember)
            return redirect(url_for('index'))

        error = 'Invalid credentials'

    return render_template('login.html', error=error, username=username)

# ----Register here new user with password

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in users:
            error = "Username already exists"
        else:
            add_user(username, password)
            return redirect(url_for('login'))

    return render_template('register.html', error=error)

#  logout route 
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
