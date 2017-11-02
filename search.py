from flask import Flask,render_template,request,redirect,flash,Response
from flask_pymongo import PyMongo
from word_correct import *
from bson.objectid import ObjectId
from flask_mysqldb import MySQL
import MySQLdb

from flask_login import LoginManager, UserMixin,login_required, login_user, logout_user,current_user

from py2neo import Graph, Node, Relationship
import json



app=Flask(__name__)

app.config.update(
    DEBUG = True,
    SECRET_KEY = 'secret_124'
)


app.config['MONGO_DBNAME']='search'
mongo = PyMongo(app)

db = MySQLdb.connect(host="localhost", user="root", passwd="root", db="dbname")

cursor = db.cursor()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


graph = Graph("Neo4jServerIP")

class User(UserMixin):
	def __init__(self, data):
		self.id = data[0]
		self.name = data[1]

        # self.password = data[2]


def modify_weight(json):
	return json['score']+1*json['videoInfo']['statistics']['clicks']



@app.route('/',methods=['POST','GET'])
def index():
	trendingVideo=[]
	channelVideo=[]
	if current_user.is_authenticated==False:
		youtube = mongo.db.youtube
		trendingVideo = youtube.find().sort('videoInfo.statistics.clicks',-1).limit(10)
		cursor.execute("Select channelId,count(channelId) from UserSubscribe group by channelId order by count(channelId) DESC limit 0,4")
		data = cursor.fetchall()
		for each_data in data:
			trending_channel_video = youtube.find({'videoInfo.snippet.channelId':each_data[0]}).sort('videoInfo.statistics.clicks',-1).limit(4)
			channelVideo.append(trending_channel_video)
	else:
		youtube = mongo.db.youtube
		trendingVideo = youtube.find().sort('videoInfo.statistics.clicks',-1).limit(10)
		cursor.execute("Select channelId from UserSubscribe where userId=%s limit 0,4",[current_user.id])
		data = cursor.fetchall()
		for each_data in data:
			trending_channel_video = youtube.find({'videoInfo.snippet.channelId':each_data[0]}).sort('videoInfo.statistics.clicks',-1).limit(4)
			channelVideo.append(trending_channel_video)

	return render_template('home.html',trending=trendingVideo,channel=channelVideo)


def search(text):
	queryArray=[]
	corrected_text=""
	corrected_query=""
	textArray = text.split()
	temp =-1
	for i,text_word in enumerate(textArray):#text.split("( |\\\".*?\\\"|'.*?')"):
		if text_word != "AND" and text_word != "OR" and text_word != "NOT" and text_word != '"':
			if temp != i:
				corrected_text += " " + correct(text_word)
			corrected_query += " " + correct(text_word)
		elif text_word == '"':
			corrected_text += " " + text_word
			corrected_query += " " + text_word
		elif text_word == "AND":
			queryArray.append(corrected_text)
			corrected_query += " " + text_word
			corrected_text=""
		elif text_word == "NOT":
			corrected_text += " "+ '-' + correct(textArray[i+1])
			corrected_query += " " + text_word
			temp = i+1
	queryArray.append(corrected_text)
	youtube = mongo.db.youtube
	ArrayjsonArray = []
	for query in queryArray:
		result = youtube.find({'$text':{'$search':query}},{'score':{'$meta':'textScore'} })#.sort([('score',{'$meta':'textScore'})])
		jsonArray = []
		for each_result in result:
			jsonArray.append(each_result)
		ArrayjsonArray.append(jsonArray)
	finalResult=[]
	for Arraylist in ArrayjsonArray:
		for json in Arraylist:
			count=0
			for jsonList in ArrayjsonArray:
				for json2 in jsonList:
					if json["_id"]==json2["_id"]:
						if json2 not in finalResult:
							count = count + 1
						else:
							for json3 in finalResult:
								if json["_id"] == json3["_id"]:
									json3["score"] = (json2["score"] + json["score"])/2
			if count==len(ArrayjsonArray):
				finalResult.append(json)
	# print corrected_text
	# print text
	# print "yolo"
	finalResult.sort(key=modify_weight,reverse=True)
	return {'finalResult':finalResult,'corrected_text':corrected_text,'corrected_query':corrected_query}


@app.route('/search',methods=['POST','GET'])
def final_search_is():
	if request.method=='POST':
		text = request.form['search']
		Result = search(text)
		finalResult = Result['finalResult']
		corrected_query = Result['corrected_query']
		return render_template('search_new.html',text=corrected_query,result=finalResult)
	return render_template('search_new.html')

@app.route('/subscribed')
def subscribed_channel():
	if current_user.is_authenticated:
		youtube = mongo.db.youtube
		cursor.execute("Select channelId from UserSubscribe where userId=%s ",[current_user.id])
		data = cursor.fetchall()
		channelVideo = []
		for each_data in data:
			trending_channel_video = youtube.find({'videoInfo.snippet.channelId':each_data[0]}).sort('videoInfo.statistics.clicks',-1)#.limit(4)
			channelVideo.append(trending_channel_video)
		return render_template("user_subscribed.html",channel=channelVideo)
	return render_template("user_subscribed.html")

@app.route('/liked')
def liked():
	if current_user.is_authenticated:
		youtube = mongo.db.youtube
		cursor.execute("Select * From UserLog where userId=%s and liked=1",[current_user.id])
		data = cursor.fetchall()
		liked_result=[]
		for each_data in data:
			liked_videos = youtube.find({'_id':ObjectId(each_data[1])})
			for video in liked_videos:
				liked_result.append(video)
		return render_template("user_likes.html",result=liked_result)
	return render_template("user_likes.html")

@app.route('/channel/<channelId>')
def channel_view(channelId):
	youtube = mongo.db.youtube
	channel_video = youtube.find({'videoInfo.snippet.channelId':channelId}).sort('videoInfo.statistics.likeCount',-1)
	boolSubscribe=0
	if current_user.is_authenticated:
		cursor.execute("Select * from UserSubscribe where userId= %s and channelId= %s",(current_user.id,channelId))
		subscribeData = cursor.fetchone()
		if subscribeData is not None:
			boolSubscribe=1
	return render_template("channelHome.html",result=channel_video,subscribed=boolSubscribe)


@app.route('/single/<id>/')
def single(id):
	youtube = mongo.db.youtube
	result=youtube.find({'_id':ObjectId(id)})
	#fetch neo4j data here

	vid_id=result[0]['videoInfo']['id']
	arr=[]
	for record in graph.data('match (n1)-[r:Same_Channel]-(n2) where n1.name="'+ vid_id +'" return n2.name as name limit 5'):
		print record['name']
		res=youtube.find({'videoInfo.id':record['name']})
		for obj in res:
			arr.append(obj)
	for record in graph.data('match (n1)-[r:Similar_Tags]-(n2) where n1.name="'+ vid_id +'" return n2.name as name order by r.weightage desc limit 5'):
		print record['name']
		res=youtube.find({'videoInfo.id':record['name']})
		for obj in res:
			arr.append(obj)
	for record in graph.data('match (n1)-[r:Similar_Desc]-(n2) where n1.name="'+ vid_id +'" return n2.name as name order by r.weightage desc limit 5'):
		print record['name']
		res=youtube.find({'videoInfo.id':record['name']})
		for obj in res:
			arr.append(obj)

	unique = { each['videoInfo']['id'] : each for each in arr }.values()

	boolLiked=0
	boolSubscribe=0
	if current_user.is_authenticated:
		cursor.execute("Select * From UserLog where userId=%s and videoId=%s and liked=1",(current_user.id,id))
		likedData = cursor.fetchone()
		
		if likedData is not None:
			boolLiked=1
		cursor.execute("Select * from UserSubscribe where userId= %s and channelId= %s",(current_user.id,result[0]['videoInfo']['snippet']['channelId']))
		subscribeData = cursor.fetchone()
		
		if subscribeData is not None:
			boolSubscribe=1
	return render_template('result_new.html',result=result,arr=unique,liked=boolLiked,subscribed=boolSubscribe)



@app.route('/login',methods=['POST','GET'])
def login():
	if request.method=='POST':
		userName=request.form['username']
		password=request.form['password']

		cursor.execute("Select * FROM User where userName= %s and password= %s",(userName,password))

		db.commit()
		data = cursor.fetchone()
		print data
		if data is not None:
			user = User(data)
			login_user(user)
			return redirect('/')
		else:
			print ("Error Login")

		return render_template('sign-in.html',data=data)

	else:
		return render_template('sign-in.html')


@app.route('/register',methods=['POST','GET'])
def register():
	if request.method=='POST':
		userName2=request.form['username']
		password1=request.form['password1']
		password2=request.form['password2']
		if password1 == password2:
		# login_user(user)
			cursor.execute("Select * FROM User where userName= %s",[userName2])
			db.commit()
			data = cursor.fetchone()
			if data is None:
				cursor.execute("Insert into User(userName,password) values ( %s , %s)" ,(userName2,password1))
				db.commit()
				cursor.execute("Select * FROM User where userName= %s and password= %s",(userName2,password1))
				newData = cursor.fetchone()
				print newData
				user = User(newData)
				login_user(user)
				return redirect('/')
			else:
				print "UserName taken"
				return redirect('/register')
	else:
		return render_template('sign-up.html')



@app.route('/like/<videoId>',methods=['POST','GET'])
def like_a_video(videoId):
	if current_user.is_authenticated:
		print current_user.id
		youtube = mongo.db.youtube
		print videoId
		cursor.execute("Select * from UserLog where userId= %s and videoId= %s",(current_user.id,videoId))
		data = cursor.fetchone()
		if data[2] == 0:
			cursor.execute("Update UserLog set liked =1 where userId= %s and videoId= %s",(current_user.id,videoId))
			youtube.update_one({'_id':ObjectId(videoId)},{'$inc':{'videoInfo.statistics.likeCount':1}})
		elif data[2]== 1:
			cursor.execute("Update UserLog set liked =0 where userId= %s and videoId= %s",(current_user.id,videoId))
			youtube.update_one({'_id':ObjectId(videoId)},{'$inc':{'videoInfo.statistics.likeCount':-1}})
		db.commit()

		#to update the like count in MongoDB


		return redirect('/single/'+str(videoId)+'/')
	return Response("Yolo")

@app.route('/subscribe/<videoId>/<channelId>/<channelName>')
def subscribe_a_video(videoId,channelId,channelName):
	if current_user.is_authenticated:
		cursor.execute("Select * from UserSubscribe where userId= %s and channelId= %s",(current_user.id,channelId))
		data = cursor.fetchone()
		print data
		if data is None:
			cursor.execute("Insert into UserSubscribe (userId,channelId,channelName) values (%s, %s , %s)",(current_user.id,channelId,channelName))
			db.commit()
		else:
			cursor.execute("Delete From UserSubscribe where userId= %s and channelId= %s and channelName= %s",(current_user.id,channelId,channelName))
			db.commit()
		return redirect('/single/'+str(videoId)+'/')
@app.route('/try')
def try_template():
	return render_template('index.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/login')


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):

	cursor.execute("Select * FROM User where userId=%s",[userid])
	data = cursor.fetchone()
	return User(data)

@app.route('/result/<id>')
def search_result(id):
	if current_user.is_authenticated:
		click_increment(current_user.id,id)
	else:
		click_increment(0,id)
	return redirect('/single/'+str(id)+'/')

def click_increment(userId,videoId):
	youtube = mongo.db.youtube
	youtube.update_one({'_id':ObjectId(videoId)},{'$inc':{'videoInfo.statistics.clicks':1}})
	if userId !=0:
		try:
			cursor.execute("Insert into UserLog(userId,videoId) values (%s, %s)",(userId,videoId))
		except:
			cursor.execute("Update UserLog set clickCount = clickCount+1 where userId=%s and videoId=%s",(userId,videoId))
		db.commit()


@app.context_processor
def inject():
	cursor.execute("Select channelId,channelName,count(channelId) from UserSubscribe group by channelId,channelName order by count(channelId) DESC limit 0,4")
	data = cursor.fetchall()
	context={'ChannelsAre':data}
	return context

if __name__ == '__main__':
	app.run(host='0.0.0.0',port=6050,debug=True)