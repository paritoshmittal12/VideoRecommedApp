from py2neo import Graph, Node, Relationship
import json
import os


def splitWords(str):
	a=str.split()
	b=[]
	for i in a:
		b+=i.split(',')
	a=b
	b=[]
	for i in a:
		b+=i.split(':')
	a=b
	b=[]
	for i in a:
		b+=i.split('/')
	a=b
	b=[]
	for i in a:
		b+=i.split('.')

	a=b
	b=[]
	for i in a:
		b+=i.split('"')

	return b


def descriptionCompare(description1,description2):
	word_description1 = splitWords(description1)		#split the string and store it in a set
	word_description2 = splitWords(description2)#find the intersection of the two sets
	count = len(set(word_description2)&set(word_description1)) 
	return count

#count the no of common tags
def tagsCompare(tags1,tags2):
	return len(set(tags1)&set(tags2))




#create a graph
graph = Graph("server_address_Neo4j")




arrayjson = []
DIR_ADDR="Path_to_database"
filelist = os.listdir(DIR_ADDR)

#read the JSON files one by one
for i in range(len(filelist)):
	filelist[i]=DIR_ADDR+ "/" +filelist[i]
	# print(filelist[i])
	page = open(filelist[i],"r")
	parsed = json.loads(page.read())
	arrayjson.append(parsed)


tx=graph.begin()

for i in range(len(arrayjson)):
	arraystring = arrayjson[i]['videoInfo']['statistics']
	a = Node("Youtube",name=arrayjson[i]['videoInfo']['id'],commentCount=arraystring['commentCount'],viewCount=arraystring['viewCount'],favoriteCount=arraystring['favoriteCount'],dislikeCount=arraystring['dislikeCount'],likeCount=int(arraystring['likeCount']))
	tx.merge(a)
	print("yolo "+str(i))
	# print(arrayjson[i]['videoInfo']['id'])
tx.commit()
for i in range(len(arrayjson)):
	tx=graph.begin()
	element = arrayjson[i]
	a = graph.find_one("Youtube",property_key='name', property_value=element['videoInfo']['id'])
	for j in range(i-1,-1,-1):
		b = graph.find_one("Youtube",property_key='name', property_value=arrayjson[j]['videoInfo']['id'])
		if arrayjson[j]['videoInfo']['snippet']['channelId'] == element['videoInfo']['snippet']['channelId']:	
			channelRelation = Relationship(a,"Same_Channel",b)
			tx.merge(channelRelation)
		Count=descriptionCompare(arrayjson[i]['videoInfo']['snippet']['description'],arrayjson[j]['videoInfo']['snippet']['description'])
		if Count >10:
			DescriptionRelation = Relationship(a,"Similar_Desc",b,weightage=Count)
			tx.merge(DescriptionRelation)

		if 'tags' in arrayjson[i]['videoInfo']['snippet'] and 'tags' in arrayjson[j]['videoInfo']['snippet']:
			tagCount = tagsCompare(arrayjson[i]['videoInfo']['snippet']['tags'], arrayjson[j]['videoInfo']['snippet']['tags'])
			if tagCount !=0:
				TagRelation = Relationship(a,"Similar_Tags",b,weightage=tagCount)
				tx.merge(TagRelation)
 
	print("yolo "+str(i))
	tx.commit()
print("finish")
