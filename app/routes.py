from app import app
from flask import render_template, request, redirect, url_for, session, g, flash, render_template_string
from werkzeug.urls import url_parse
from app.forms import LoginForm, RegistrationForm, QuestionForm
from app.models import User, Questions
from app import db
from app import mail
from random import randint
from flask_session import Session
import numpy as np
import pickle
from werkzeug.security import generate_password_hash, check_password_hash


import os
import math
import random
import smtplib


import sqlite3

from email.mime.text import MIMEText
from pymongo import MongoClient


SECRET_KEY = "changeme"
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
# Session(app)
# session.modified = True
client = MongoClient('mongodb+srv://fenil_20:Gnu123456@fenil.ze63otk.mongodb.net/careerrecommd?retryWrites=true&w=majority')
db__ = client.careerrecommd

@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        g.user = user

digits="0123456789"
OTP=""
for i in range(6):
    OTP+=digits[math.floor(random.random()*10)]
otp = OTP + " is your OTP"
msg= otp
s = smtplib.SMTP('smtp.gmail.com', 587)
s.starttls()
s.login("devanshi2828@gmail.com", "xyonyzblwiswemvy")

# otp = randint(000000,999999)  

# @app.before_request
# def before_request():
#     g.user = None

#     if 'user_id' in session:
#         user = User.query.filter_by(id=session['user_id']).first()
#         g.user = user

@app.route('/')
def home():
    # return render_template_string("""
    #     {% if session['user_id'] %}
    #         <h1>Welcome {{ session['user_id'] }}!</h1>
    #         {% endif %}
    #         """)
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            return redirect(url_for('login'))
        session['user_id'] = user.id
        session['marks'] = 0
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home')
        return redirect(next_page)
        return redirect(url_for('home'))
    if g.user:
        return redirect(url_for('home'))
    return render_template('login.html', form=form, title='Login')

@app.route('/verify/<email>',methods=['GET', 'POST'])
def verify(email):
    # session['user_id'] = request.form.get('use')
    if 'user_id' in session:
        s.sendmail('&&&&&&&&&&&',email,msg) 
    return render_template('verify.html')  

    return render_template_string("""
            {% if session['user_id'] %}
                <h1>Welcome {{ session['user_id'] }}!</h1>
                {% endif %}
                """)

@app.route('/validate',methods=['POST'])
def validate():
    user_otp = request.form['otp']  
    if int(OTP) == int(user_otp):  
        return redirect(url_for('home'))
    return redirect(url_for('register'))  

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        session['marks'] = 0
        
        return redirect(url_for('verify',email=form.email.data))
    if g.user:
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)


@app.route('/hometest',methods=['POST','GET'])
def hometest():
    if not g.user:
        return redirect(url_for('login'))
    return render_template("hometest.html")


@app.route('/predict',methods = ['POST', 'GET'])
def predict():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == 'POST' or request.method == 'GET':
        result = request.form
        i = 0
        print(result)
        res = result.to_dict(flat=True)
        print("res:",res)
        arr1 = res.values()
        arr = ([value for value in arr1])

        data = np.array(arr, dtype=float)

        data = data.reshape(1,-1)
        print(data)

        loaded_model = pickle.load(open("career.pkl", 'rb'))
        predictions = loaded_model.predict(data)
        #return render_template('testafter.html',a=predictions)
      
        print(predictions)
        pred = loaded_model.predict_proba(data)
        print(pred)
        #acc=accuracy_score(pred,)
        pred = pred > 0.05
        #print(predictions)
        i = 0
        j = 0
        index = 0
        res = {}
        final_res = {}
        while j < 17:
            if pred[i, j]:
                res[index] = j
                index += 1
            j += 1
        # print(j)
        #print(res)
        index = 0
        for key, values in res.items():
            if values != predictions[0]:
                final_res[index] = values
                print('final_res[index]:',final_res[index])
                index += 1
        #print(final_res)
        jobs_dict = {0:'AI ML Specialist',
                    1:'API Integration Specialist',
                    2:'Application Support Engineer',
                    3:'Business Analyst',
                    4:'Customer Service Executive',
                    5:'Cyber Security Specialist',
                    6:'Data Scientist',
                    7:'Database Administrator',
                    8:'Graphics Designer',
                    9:'Hardware Engineer',
                    10:'Helpdesk Engineer',
                    11:'Information Security Specialist',
                    12:'Networking Engineer',
                    13:'Project Manager',
                    14:'Software Developer',
                    15:'Software Tester',
                    16:'Technical Writer'}
                
        #print(jobs_dict[predictions[0]])
        job = {}
        #job[0] = jobs_dict[predictions[0]]
        index = 1
        data1=predictions[0]
        
        jobs_desc = {}

        for i in jobs_dict.values():
            jobs_desc[i]= ''.join(i.split())
        
        print(jobs_desc)


        print(data1)
        return render_template("testafter.html",final_res=final_res,job_dict=jobs_dict,job0=data1,job_desc=jobs_desc)
    return None


@app.route('/score')
def score():
    if not g.user:
        return redirect(url_for('login'))
    g.user.marks = session['marks']
    # db.session.commit()
    return render_template('score.html', title='Final Score')
    # return redirect('/course')
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/logout')
def logout():
    if not g.user:
        return redirect(url_for('login'))
    session.pop('user_id', None)
    session.pop('marks', None)
    return redirect(url_for('home'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/submit-comment', methods=['GET', 'POST'])
def submit_comment():
    
    name = request.form['name']
    emai_l = request.form['emai_l']
    comment = request.form['comment']

    # comment_doc = {
    #     'name': name,
    #     'email': email,
    #     'comment': comment
    # }

    db__.comments.insert_one({'name': name,'emai_l': emai_l,'comment': comment})

    flash('Your comment has been submitted!')
    return redirect('/contact')

@app.route('/description/<role>')
def description(role):
    
    if role =="ApplicationSupportEngineer":
        return render_template('ApplicationSupportEngineer.html')
    elif role == "DatabaseAdministrator":
        return render_template('DatabaseAdministrator.html')
    elif role == "CyberSecuritySpecialist":
        return render_template('CyberSecuritySpecialist.html')
    elif role == "HardwareEngineer":
        return render_template('HardwareEngineer.html')
    elif role == "AIMLSpecialist":
        return render_template('AIMLSpecialist.html')
    elif role == "APIIntegrationSpecialist":
        return render_template('APIIntegrationSpecialistr.html')
    elif role == "BusinessAnalyst":
        return render_template('BusinessAnalyst.html')
    elif role == "CustomerServiceExecutive":
        return render_template('CustomerServiceExecutive.html')
    elif role == "DataScientist":
        return render_template('DataScientist.html')
    elif role == "GraphicsDesigner":
        return render_template('GraphicsDesigner.html')
    elif role == "HelpdeskEngineer":
        return render_template('HelpdeskEngineer.html')
    elif role == "InformationSecuritySpecialist":
        return render_template('InformationSecuritySpecialist.html')
    elif role == "NetworkingEngineer":
        return render_template('NetworkingEngineer.html')
    elif role == "ProjectManager":
        return render_template('ProjectManager.html')
    elif role == "SoftwareDeveloper":
        return render_template('SoftwareDeveloper.html')
    elif role == "SoftwareTester":
        return render_template('SoftwareTester.html')
    elif role == "TechnicalWriter":
        return render_template('TechnicalWriter.html')




@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('app.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user WHERE email=?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user:
            # generate and send OTP to user's email address
            otp = str(randint(100000, 999999))
            session['otp'] = otp
            session['email'] = email
            send_otp(email, otp)
            flash('An OTP has been sent to your email address.')
            return render_template('reset_password.html')
        else:
            flash('Invalid email address. Please try again.')
    return render_template('forgot_password.html')


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        otp = request.form['otp']
        if otp == session.get('otp'):
            email = session.get('email')
            new_password = request.form['new_password']
            password_h = generate_password_hash(new_password)

            conn = sqlite3.connect('app.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE user SET password_hash=? WHERE email=?", (password_h, email))
            conn.commit()
            conn.close()
            flash('Your password has been reset successfully.')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')
    return render_template('forgot_password.html')

def send_otp(email, otp):
    msg = MIMEText(f"Your OTP is: {otp}")
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = 'fenilapatel19@gnu.ac.in'
    msg['To'] = email
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login('fenilapatel19@gnu.ac.in', 'Gnu@123456')
    server.sendmail('fenilapatel19@gnu.ac.in', [email], msg.as_string())
    server.quit()

@app.route('/course')
def course():
    if not g.user:
        return redirect(url_for('login'))
    return render_template('course.html')


@app.route('/viz')
def viz():
    return render_template('viz.html')
# ---------------------------------------------------------------------------------------

# from app import app
# from flask import render_template, request, redirect, url_for, session, g, flash
# from werkzeug.urls import url_parse
# from app.forms import LoginForm, RegistrationForm, QuestionForm
# from app.models import User, Questions
# from app import db


# @app.before_request
# def before_request():
#     g.user = None

#     if 'user_id' in session:
#         user = User.query.filter_by(id=session['user_id']).first()
#         g.user = user

# @app.route('/')
# def home():
#     return render_template('index.html', title='Home')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.username.data).first()
#         if user is None or not user.check_password(form.password.data):
#             return redirect(url_for('login'))
#         session['user_id'] = user.id
#         session['marks'] = 0
#         next_page = request.args.get('next')
#         if not next_page or url_parse(next_page).netloc != '':
#             next_page = url_for('home')
#         return redirect(next_page)
#         return redirect(url_for('home'))
#     if g.user:
#         return redirect(url_for('home'))
#     return render_template('login.html', form=form, title='Login')

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.password.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         session['user_id'] = user.id
#         session['marks'] = 0
#         return redirect(url_for('home'))
#     if g.user:
#         return redirect(url_for('home'))
#     return render_template('register.html', title='Register', form=form)



# @app.route('/question/<int:id>', methods=['GET', 'POST'])
# def question(id):
#     form = QuestionForm()
#     q = Questions.query.filter_by(q_id=id).first()
#     if not q:
#         return redirect(url_for('score'))
#     if not g.user:
#         return redirect(url_for('login'))
#     if request.method == 'POST':
#         option = request.form['options']
#         if option == q.ans:
#             session['marks'] += 10
#         return redirect(url_for('question', id=(id+1)))
#     form.options.choices = [(q.a, q.a), (q.b, q.b), (q.c, q.c), (q.d, q.d)]
#     return render_template('question.html', form=form, q=q, title='Question {}'.format(id))


# @app.route('/score')
# def score():
#     if not g.user:
#         return redirect(url_for('login'))
#     g.user.marks = session['marks']
#     # db.session.commit()
#     return render_template('score.html', title='Final Score')

# @app.route('/logout')
# def logout():
#     if not g.user:
#         return redirect(url_for('login'))
#     session.pop('user_id', None)
#     session.pop('marks', None)
#     return redirect(url_for('home'))