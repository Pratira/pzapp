"""
Routes and views for the flask application.
"""

from pymongo import MongoClient
from datetime import datetime
from flask import render_template, request, redirect
from FlaskWebProject import app

client = MongoClient()
client = MongoClient("mongodb://pratira:theperfect1@ds011735.mlab.com:11735/pzdb")
#testdb is the new database getting created
db = client.pzdb 

@app.route('/')
def welcome():
    items = db.pzdb.find()
    items = [item for item in items]
    return render_template('login.html')

@app.route('/new_user',methods=['GET','POST'])  
def register():
    username = request.form['new_user']
    password = request.form['new_pass']
    item_dir = {
        'username': username,
        'password': password,
    }
    print "New Values taken"
    
    result = db.pzdb.find({'password':password,'username':username}).count()>0
    
    if not result:
        print "inserts value in db"
        db.pzdb.insert(item_dir)
    else:
        return 'User Already Exists!'
    
    return render_template('login.html') 
    #print ("Successfully logged in!")

@app.route('/user_login',methods=['GET','POST'])
def login():
    username = request.form['user']
    password = request.form['passwd']
    item_values = {
    'username': username,
    'password': password
    }

    res = db.pzdb.find({'username': username , 'password': password}).count() > 0
    if res :
        return render_template('upload.html', user = username)
    else:
        return 'retry with proper credentials'

    return render_template('upload.html', user = username)
"""
@app.route('/contact')
def contact():
    #Renders the contact page.
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    #Renders the about page.
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )
"""