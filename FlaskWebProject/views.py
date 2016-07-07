"""
Routes and views for the flask application.
"""
import datetime
from pymongo import MongoClient
from datetime import datetime
from flask import render_template, request, redirect
from FlaskWebProject import app
import gridfs
import base64

client = MongoClient()
client = MongoClient("mongodb://pratira:theperfect1@ds011735.mlab.com:11735/pzdb")
#testdb is the new database getting created
db = client.pzdb 
fdb = client.filedb

@app.route('/')
def welcome():
    items = db.pzdb.find()
    items = [item for item in items]
    return render_template('login.html')

@app.route('/new_user',methods=['GET','POST'])  
def new_user():
    username = request.form['new_user']
    password = request.form['new_pass']
    item_dir = {
        'username': username,
        'password': password,
    }
    print "New Values taken"
    
    result = db.pzdb.users.find({'password':password,'username':username}).count()>0
    
    if not result:
        print "inserts value in db"
        db.pzdb.users.insert(item_dir)
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
    global userID
    userID = username
    res = db.pzdb.users.find({'username': username , 'password': password}).count() > 0
    if res :
        return render_template('upload.html', user = userID)
    else:
        return 'retry with proper credentials'

    return render_template('upload.html', user = userID)


@app.route('/flight', methods=['POST'])
def flight():
    hub = request.form['hub']
    vacation = request.form['vacation']
    traveldate = request.form['date_of_travel']

    print hub
    print vacation
    print traveldate

    fs = gridfs.GridFS(db)
    print 'gridFS'
    
    #stored = fs.put(username=userID, hub=hub, vacation=vacation,date_of_travel=traveldate)
    #print stored
    fs = gridfs.GridFS(db)
    res = db.register.find({'username':userID})    
        
    
    fs = gridfs.GridFS(db)
    list_allFlights  = [] 
    for file in db.reservations.find():
        
        traveldate = file['date']
        print traveldate
        source = file['vacation']
        print source
        
        if file['date'] == traveldate:
            contents = {}
            contents['date']=file['date']
            contents['name']=file['name']
            contents['hub']=file['hub']
            contents['vacation']=file['vacation']
            list_allFlights.append(contents)
            print contents   

    #return 'here'
    return render_template("displayPhotos.html",items=list_allFlights, userID = userID)


@app.route('/enterdate', methods=['GET','POST'])
def showAllFlights():
    traveldate = request.form['enterdate']
    fs = gridfs.GridFS(db)
    #the array will later on get appended with contents
    list_allFlights = []
    #time to show the entire table
    #time_to_show = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    for file in db.reservations.find():
        #traveldate = file['date']
        #read_file = fs.find_one({"filename": filename}).read()
        #checking file type here...first one checks for image and the second one checks for text and stores contents accordingly
        if file['date'] == traveldate:
            contents = {}
            contents['date']=file['date']
            contents['name']=file['name']
            contents['hub']=file['hub']
            contents['vacation']=file['vacation']
            list_allFlights.append(contents)
            print contents

    return render_template("displayPhotos.html",items=list_allFlights, user = userID)
