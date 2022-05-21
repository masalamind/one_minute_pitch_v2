from email import contentmanager
from sre_constants import CATEGORY_UNI_DIGIT
from unicodedata import category
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, RadioField, TextAreaField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

  

app.config['SECRET_KEY'] = 'my secret string' # place in config later
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.pitchy'

 
class User(UserMixin, db.Model):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(15), unique=True)
  email = db.Column(db.String(50), unique=True)
  password = db.Column(db.String(80))
  pitches = db.relationship('Pitch', backref="user")
  comments = db.relationship('Comment', backref="user")
  
  
class Category(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  category_id = db.Column(db.Integer)
  category_name = db.Column(db.String(20))
  pitches = db.relationship('Pitch', backref="category")
class Pitch (db.Model):
  pitch_id = db.Column(db.Integer, primary_key=True)
  publish_date = db.Column(db.DateTime)
  content = db.Column(db.Text)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))  
  category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
  comments= db.relationship('Comment', backref="pitch")
class Comment(db.Model):
  comment_id = db.Column(db.Integer, primary_key=True)
  content = db.Column(db.String(144))
  publish_date = db.Column(db.DateTime)
  pitch_id = db.Column(db.Integer, db.ForeignKey('pitch.pitch_id'))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
  return User.query.get(int(user_id))


# Wtf Forms classes 
class LoginForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
  remember = BooleanField('Remember me')

# You pass this class to the form in the template
class RegisterForm(FlaskForm):
  username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
  email = StringField('Email', validators=[InputRequired(), Email(message="Invalid email"), Length(max=50)])
  password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
  


class NewPitch(FlaskForm):
  category = RadioField('Category',tags=['product','elevator','interview','promotion','icebreakers','pickuplines'],validators=[InputRequired()])
  pitch_content = TextAreaField(u'pitch goes here' validators=[InputRequired(), Length(max=200)])
  
  
  
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
      if check_password_hash(user.password, form.password.data):
        login_user(user,remember=form.remember.data)# you have to include this line to login the user otherwise they won't be logged in, this is from login manager dependencies
        return redirect(url_for("pitches"))
    # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'
    return '<h1>Invalid username or password</h1>'
  return render_template('login.html', form=form)

@app.route('/signup', methods=["GET", "POST"])
def signup():
  form = RegisterForm()
  if form.validate_on_submit():
    hashed_password = generate_password_hash(form.password.data, method="sha256")
    new_user=User(username=form.username.data, email=form.email.data, password=hashed_password) 
    db.session.add(new_user)
    db.session.commit()
    return '<h1>New user has been added.</h1>'
    # return '<h1>' + form.username.data + ' ' + form.email.data + form.password.data + '</h1>'
  return render_template('signup.html', form=form)

@app.route('/pitch', methods=["GET", "POST"])
def new_pitch():
  form = NewPitch()
  if form.validate_on_submit():
    my_pitch = Pitch(content=form.pitch_content.data, user_id='1', category_id=form.category.data)
    db.session.add(my_pitch)
    db.session.commit()
    return '<h1>New pitch has been submitted</h1>'
  return render_template('new_pitch.html')

@app.route('/pitches')
@login_required
def pitches():
  if request.method == "POST":
    pitch_category = request.form['pitch-tag']
    pitch_content = request.form['pitch-content']
    
  # create the new pitch 
  # change the userid to come from current users id not hardcoded 
  mypitch = Pitch(content=pitch_content, user_id='1', category_id=pitch_category)
  db.session.add(mypitch)
  db.session.commit()    

  return render_template('index.html')

@app.route('/profile')
def profile():
  return render_template('user_profile.html')

@app.route('/logout')
@login_required
def logout():
  logout_user()
  return redirect(url_for('index'))



if __name__== '__main__':
  app.run(debug=True)