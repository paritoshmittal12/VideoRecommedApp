#! /usr/bin/python
from pymongo import MongoClient
import json
import os
from pprint import pprint

BASEDIR = "Path_to_database"
client = MongoClient()
database = client.search
collection = database.youtube
filesasList = os.listdir(BASEDIR)



for file in filesasList:
	file = BASEDIR+file
	openfile = open(file,"r")
	parsedJson = json.load(openfile)
	#change the likeCount to int
	parsedJson['videoInfo']['statistics']['likeCount']=int( parsedJson['videoInfo']['statistics']['likeCount'])
	collection.insert(parsedJson)
print "file ends"