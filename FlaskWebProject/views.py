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
    quota = request.form['quota']
    size = request.form['size']
    item_dir = {
        'username': username,
        'password': password,
        'quota' : quota,
        'size' : size
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
    global userID
    userID = username
    res = db.pzdb.find({'username': username , 'password': password}).count() > 0
    if res :
        return render_template('upload.html', user = userID)
    else:
        return 'retry with proper credentials'

    return render_template('upload.html', user = userID)

@app.route('/upload', methods=['POST'])
def upload():
    print "Inside upload photo"
    subject = request.form['subject']
    #input subject and split
    splitSubject = subject.split(' ')
    if len(splitSubject) > 1:
        return render_template("upload.html", user = userID, errormsg = "Please enter the single word subject" )
    #input filename and priority
    filename = request.form['filename']
    priority = request.form['priority']
    #calculate time to upload
    time_to_upload = datetime.now().strftime("%Y-%m-%d %H:%M") 
    #browse and select file from the local machine
    file = request.files['filecontents']
    #target stores and reads the file
    target = file.read()
    #length of file gets calculated
    length_of_file = len(target)
    #check the content type of file
    contentType = file.content_type
    print file.filename
    #define fs
    fs = gridfs.GridFS(db)
    print 'gridFS'
    
    #file saved with contents in target, filename, username and priority on the gridFS
    stored = fs.put(target, filename=filename, username=userID, priority = priority, content_type = contentType)
    print stored
    fs = gridfs.GridFS(db)
    print 'file length' + str(length_of_file)
    res = db.register.find({'username':userID})    
    #calculating the quota and size remaining with the user
    quota = ''
    size = ''
    for item in res:
        print item['size']
        filesize = item['size']
        quota = item['quota']
        break;
    
    count = 0
    total_length = 0
    for item in db.fs.files.find({"username":userID}):
        count = count+1
        length_of_file = length_of_file + item['length']
    
    if count >= quota:
        return 'User Quota to upload file is exceeded'
    
    if size < length_of_file:
        return 'User file size quota to upload file is exceeded the specified limit of : ' + size + 'bytes'
    
    #appending items with all the file contents
    fs = gridfs.GridFS(db)
    items = []

    for item in db.fs.files.find({"username":userID}):
        filename = item['filename']
        read_file = fs.find_one({"filename": filename}).read()
        #condition checking for text files
        if item['contentType'] != 'text/plain':
            data_received = "data:image/jpeg;base64," + base64.b64encode(read_file)
            contents = {}
            contents['filename'] = filename
            contents['url'] = data_received
            #adding the upload date in the contents
            contents['time'] = item['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time'] = timeSplit[0]
            contents['priority'] = item['priority']
            contents['content_type'] = item['contentType']
            items.append(contents)
        else:
            print 'Inside text content'
            print read_file
            contents = {}
            contents['filename'] = filename
            contents['content'] = read_file
            #adding upload date in the contents
            contents['time'] = item['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time'] = timeSplit[0]
            contents['priority'] = item['priority']
            contents['content_type'] = item['contentType']
            items.append(contents)
            print contents['content']                

    return render_template("displayPhotos.html",items=items, userID = userID, timeup = time_to_upload)
    """
    #only for images
    for item in db.fs.filedb.find({'username': username}):
        #com = None
        filename = item['filename']
        picture = fs.filedb.find_one({'filename':filename}).read()
        data_received = "data:image/jpeg;base64," + base64.b64.b64encode(picture)
        dir_var = {}

        dir_var['user'] = username
        dir_var['filename'] = filename
        dir_var['file'] = data_received

        item_dir.append(dir_var)
    print timeUpload
    return render_template('displayPhotos.html', items = item_dir, now = timeUpload)
"""
@app.route('/showAllFiles', methods=['GET','POST'])
def showAllFiles():
    fs = gridfs.GridFS(db)
    #the array will later on get appended with contents
    list_allFiles = []
    #time to show the entire table
    time_to_show = datetime.now().strftime("%Y-%m-%d %H:%M")
    for file in db.fs.files.find():
        filename = file['filename']
        read_file = fs.find_one({"filename": filename}).read()
        #checking file type here...first one checks for image and the second one checks for text and stores contents accordingly
        if file['contentType'] != 'text/plain':
            data_received="data:image/jpeg;base64," + base64.b64encode(read_file)
            contents = {}
            contents['filename']=filename
            contents['url']=data_received
            contents['time']=file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time']=timeSplit[0]
            contents['priority']=file['priority']
            contents['content_type']=file['contentType']
            list_allFiles.append(contents)
        else:
            contents = {}
            contents['filename'] = filename
            contents['content'] = read_file
            #adding upload date in the contents
            contents['time'] = file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time'] = timeSplit[0]
            contents['priority'] = file['priority']
            contents['content_type'] = file['contentType']
            list_allFiles.append(contents)
            print contents['content']

    return render_template("displayPhotos.html",items=list_allFiles, user = userID, timeup= time_to_show)
    
@app.route('/deleteFile', methods=['GET','POST'])
def delete():
    filename = request.form['filename']

    fs = gridfs.GridFS(db)
    
    #time to delete the file from the fs.file and fs.chunks
    time_to_delete = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    #fetching the username and filename and then remove the file and it's respective chunks from mlabs(backend)
    for file in db.fs.files.find({"username":userID, "filename" : filename}):
        #print file['_id']
        removechunk = db.fs.chunk.remove({"files_id": file['_id']})
        removefiles = db.fs.files.remove({"username":userID, "filename" : filename})
    
    list_allFiles = []
    for file in db.fs.files.find():
        filename = file['filename']
        read_file = fs.find_one({"filename": filename}).read()
        #checking if file type is image/jpeg (converting to base64 and uploading it then)
        if file['contentType'] != 'text/plain':
            data_received="data:image/jpeg;base64," + base64.b64encode(read_file)
            contents = {}
            contents['filename']=filename
            contents['url']=data_received
            contents['time']=file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time']=timeSplit[0]
            contents['priority']=file['priority']
            contents['content_type']=file['contentType']
            list_allFiles.append(contents)
        else:
            #checking if file type is text/plain
            contents = {}
            contents['filename'] = filename
            contents['content'] = read_file
            #adding upload date in the contents
            contents['time'] = file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time'] = timeSplit[0]
            contents['priority'] = file['priority']
            contents['content_type'] = file['contentType']
            list_allFiles.append(contents)

    return render_template("displayPhotos.html",items=list_allFiles, user = userID, timeup = time_to_delete)

@app.route('/searchFile', methods=['POST'])
def searchFile():

    global userID

    #taking the string input by the user on the form
    criteria = request.form['searchFile']
    #splitting the input on the basis of blank spaces
    
    #time to search
    time_to_search = datetime.now().strftime("%Y-%m-%d %H:%M")

    criteria = criteria.split(" ")
    print criteria
    #split into field
    field = criteria[0]
    #split into comparison operator
    comparison = criteria[1]
    #split into value
    value = criteria[2]
    print field
    print comparison
    print value

    #assigning the equivalent comparison operator 
    if comparison == '<':
        comparison = "$lt"
    elif comparison == '>':
        comparison = "$gt"
    else:
        comparison = "$eq"

    if field == "date":
        field = "time"
        value = str(datetime.strptime(str(value), '%Y-%m-%dT%H:%M:%SZ'))
        print type(value)
    elif field== "priority":
        value = int(value)
        print 'after priority field'
    
    fs = gridfs.GridFS(db)

    listAllFiles = []
    print field
    print comparison
    print value
    #v=str(value)
    searchAllFiles = {"username":userID, field:{comparison:str(value)}}
    print str(searchAllFiles)

    for file in db.fs.files.find(searchAllFiles):
        filename = file['filename']
        print filename
        read_file = fs.find_one({"filename": filename}).read()
        print read_file
        if file['contentType'] != 'text/plain':
            data_received="data:image/jpeg;base64," + base64.b64encode(read_file)
            contents = {}
            contents['filename']=filename
            contents['url']=data_received
            contents['time']=file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time']=timeSplit[0]
            contents['priority']=file['priority']
            contents['content_type']=file['contentType']
            listAllFiles.append(contents)
            print 'end of if condition 1'
        else:
            print 'inside second if condition of text'
            contents = {}
            contents['filename'] = filename
            contents['content'] = read_file
            #adding upload date in the contents
            contents['time'] = file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time'] = timeSplit[0]
            contents['priority'] = file['priority']
            contents['content_type'] = file['contentType']
            listAllFiles.append(contents)
            print 'end of if condition 2'
    print 'outside of loop'
    return render_template("displayPhotos.html", items=listAllFiles, user=userID)

@app.route('/updatePriority', methods=['POST','GET'])
def update():
    priority = request.form['priority']
    filename = request.form['filename']
    
    fs = gridfs.GridFS(db)

    db.fs.files.find_and_modify(query={'filename':filename},update={'$set':{'priority' : priority}})

    updateFiles = []
    for file in db.fs.files.find({"username":userID}):
        filename = file['filename']
        #print filename
        read_file = fs.find_one({"filename": filename}).read()
        #print read_file
        if file['contentType'] != 'text/plain':
            data_received="data:image/jpeg;base64," + base64.b64encode(read_file)
            contents = {}
            contents['filename']=filename
            contents['url']=data_received
            contents['time']=file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time']=timeSplit[0]
            contents['priority']=file['priority']
            contents['content_type']=file['contentType']
            updateFiles.append(contents)
            #print 'end of if condition 1'
        else:
            print 'inside second if condition of text'
            contents = {}
            contents['filename'] = filename
            contents['content'] = read_file
            #adding upload date in the contents
            contents['time'] = file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time'] = timeSplit[0]
            contents['priority'] = file['priority']
            contents['content_type'] = file['contentType']
            updateFiles.append(contents)
            #print 'end of if condition 2'
    #print 'outside of loop'
    return render_template("displayPhotos.html", items=updateFiles,user=userID)

@app.route('/sort', methods=['POST', 'GET'])
def sort():
    field = str(request.form['field'])
    order = int(request.form['order'])
    print order
    print field

    fs = gridfs.GridFS(db)

    sortFiles = []

    for file in db.fs.files.find().sort([(field , order)]):
        filename = file['filename']
        read_file = fs.find_one({"filename": filename}).read()
        if file['contentType'] != 'text/plain':
            data_received="data:image/jpeg;base64," + base64.b64encode(read_file)
            contents = {}
            contents['filename']=filename
            contents['url']=data_received
            contents['time']=file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time']=timeSplit[0]
            contents['priority']=file['priority']
            contents['content_type']=file['contentType']
            sortFiles.append(contents)
            #print 'end of if condition 1'
        else:
            print 'inside second if condition of text'
            contents = {}
            contents['filename'] = filename
            contents['content'] = read_file
            #adding upload date in the contents
            contents['time'] = file['uploadDate']
            timeSplit = str(contents['time']).split('.')
            contents['time'] = timeSplit[0]
            contents['priority'] = file['priority']
            contents['content_type'] = file['contentType']
            sortFiles.append(contents)

    return render_template("displayPhotos.html", items=sortFiles,user=userID)
