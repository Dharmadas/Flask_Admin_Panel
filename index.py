from waitress import serve
from flask import Flask, request, render_template, session, redirect, url_for, flash, current_app
from flask_dance.contrib.google import make_google_blueprint, google
from flask_login import LoginManager, logout_user, login_required
from userform import UserForm
from db import db
from models.User import UserModel
from controllers.login import LoginController
from controllers.user import UserController
from conf.settings import database, social, SECRET_KEY, admin_users
import os

# Google authentication requires https website, hence setting environment variables
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

app = Flask(__name__)
blueprint = make_google_blueprint(
    client_id=social['google']['client_id'],
    client_secret=social['google']['client_secret'],
    offline=True,
    reprompt_consent=True,
    # hosted_domain='gmail.com',
    scope=[
        "https://www.googleapis.com/auth/plus.me",
        "https://www.googleapis.com/auth/userinfo.email",
    ]
)
app.register_blueprint(blueprint, url_prefix="/login")
login_manager = LoginManager()
login_manager.init_app(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True

app.config['SECRET_KEY'] = SECRET_KEY
basedir = os.path.abspath(os.path.dirname(__file__))

db.init_app(app)
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/', methods=['GET','POST'])
def home():
    return add_update_user()

@app.route('/add_user', methods=['GET','POST'])
def add_user():
    return add_update_user()

@app.route('/update_user', methods=['GET','POST'])
def add_update_user():
    if not LoginController.athenticate_user():
        return redirect(url_for("google.login"))

    resp = google.get("/oauth2/v2/userinfo")
    email = resp.json()["email"]

    message = "User created/updated successfully."
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        dept_id = form.dept_id.data
        login_ip = form.login_ip.data
        
        user = UserModel.find_by_username(username)
        if user:
            user.dept_id = dept_id
            user.login_ip = login_ip
        else:
            user = UserModel(username, dept_id, login_ip)
        
        try:
            user.save()
        except:
            message = "Unable to save/update user"
            
        flash(message)
    return render_template('add_user.html', form=form, email=email)

@app.route('/list_all', methods=['GET','POST'])
def list_all():
    if not LoginController.athenticate_user():
        return redirect(url_for('logout'))

    resp = google.get("/oauth2/v2/userinfo")
    email = resp.json()["email"]

    # all_agents = UserModel.find_all()
    user = UserController()
    all_agents = user.get_all()
    return render_template('list_all.html', all_agents=all_agents, email=email)

@app.errorhandler(404)
def not_found_404(error):
    return render_template('error_404.html'), 404

@app.errorhandler(405)
def not_found_405(error):
    return render_template('error_404.html'), 405

# @app.errorhandler(Exception)
# def handle_500(error):
#     session.clear()
#     return redirect(url_for('home'))
    # return render_template('error_500.html'), 500

@login_manager.user_loader
@app.route("/logout")
def logout():
    token = current_app.blueprints["google"].token["access_token"]
    resp = google.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": token},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert resp.ok, resp.text
    logout_user()        # Delete Flask-Login's session cookie
    del blueprint.token  # Delete OAuth token from storage
    return redirect(url_for('home'))

if __name__ == "__main__":
    # db.init_app(app)
    # app.run(debug=False)
    serve(app)