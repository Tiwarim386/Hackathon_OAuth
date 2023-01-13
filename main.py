# The user details get print in the console.
# so you can do whatever you want to do instead
# of printing it

from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user
from authlib.integrations.flask_client import OAuth
import os

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=template_dir)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://localhost/hackathon'
app.secret_key = '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!/xd5\xa2\xa0\x9fR\xa1\xa8'

# '''
# 	Set SERVER_NAME to localhost as twitter callback
# 	url does not accept 127.0.0.1
# 	Tip : set callback origin(site) for facebook and twitter
# 	as http://domain.com (or use your domain name) as this provider
# 	don't accept 127.0.0.1 / localhost
# '''

app.config['SERVER_NAME'] = 'localhost:5100'
oauth = OAuth(app)
db = SQLAlchemy(app)
login = LoginManager(app)


@login.user_loader
def load_user(email):
    return Users.query.filter(email=email)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255))


class MyModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login'))


admin = Admin(app)
admin.add_view(MyModelView(Users, db.session))


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login/')
def google():

    # Google Oauth Config
    # Get client_id and client_secret from environment variables
    # For development purpose you can directly put it
    # here inside double quotes
    GOOGLE_CLIENT_ID = "195012123006-ak23f86aftom8uvt2sj0jg6bf3jod29j.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = "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"

    CONF_URL = 'https://accounts.google.com/.well-known/openid-configuration'
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url=CONF_URL,
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

    # Redirect to google_auth function
    redirect_uri = url_for('google_auth', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/google/auth/')
def google_auth():
    token = oauth.google.authorize_access_token()
    user = oauth.google.parse_id_token(token, nonce=None)
    print(" Google User ", user)
    return redirect('/admin')


if __name__ == "__main__":
    app.run(debug=True)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
