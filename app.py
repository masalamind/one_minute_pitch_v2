from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
Bootstrap(app)
db = SQLAlchemy(app)

  

app.config['SECRET_KEY'] = 'my secret string' # place in config later
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'


class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(15), unique=True)
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(80))


class LoginForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
  remember = BooleanField('Remember me')

# You pass this class to the form in the template


class RegisterForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
  email = StringField('Email', validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
  

@app.route('/')
def index():
  return render_template('index.html')


@app.route('/login', methods=["GET", "POST"])
def login():
  # instantiate the form 
  form = LoginForm()  
  if form.validate_on_submit():
    user = User.query.filter_by(username=form.username.data).first()
    if user:
      if user.password == form.password.data:
        return redirect(url_for("pitches"))
    # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return '<h1>Invalid username or password</h1>'
  return render_template('login.html', form=form)

@app.route('/signup', methods=["GET", "POST"])
def signup():
  form = RegisterForm()
  if form.validate_on_submit():
    new_user=User(username=form.username.data, email=form.email.data, password=form.password.data ) 
    db.session.add(new_user)
    db.session.commit()
    return '<h1>New user has been added.</h1>'
    # return '<h1>' + form.username.data + ' ' + form.email.data + form.password.data + '</h1>'
  return render_template('signup.html', form=form)

@app.route('/pitches')
def pitches():
  return render_template('index.html')

@app.route('/profile')
def profile():
  return render_template('user_profile.html')



if __name__== '__main__':
  app.run(debug=True)