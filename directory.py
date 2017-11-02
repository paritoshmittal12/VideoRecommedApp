#! /usr/bin/python
import json
import os
from pprint import pprint

BASEDIR = "/home/paritosh/Desktop/labAssignmnet/DatabaseAssignment/test/"
filesasList = os.listdir(BASEDIR)
writefile = open("trywords.txt","w")
for file in filesasList:
	file = BASEDIR+file
	openfile = open(file,"r")
	parsedJson = json.load(openfile)
	title = parsedJson['videoInfo']['snippet']['title']
	description = parsedJson['videoInfo']['snippet']['description']
	tags = parsedJson['videoInfo']['snippet'].get('tags',[])
	
	for title_word in title.split():
		writefile.write("%s\n" % title_word.encode("utf-8"))
	for tag in tags:
		for tags_word in tag.split():
			writefile.write("%s\n" % tags_word.encode("utf-8"))
	for description_word in description.split():
		writefile.write("%s\n" % description_word.encode("utf-8"))



writefile.close()
with open("trywords.txt",'r') as f:
	distinct_content=set(f.readlines())

to_file=""                                                                                                                                                                                                                                                                       
for element in distinct_content:                                                                                                                                                                                                                                                               
    to_file=to_file+element                                                                                                                                                                                                                                                           
with open('try_output.txt','w') as w:                                                                                                                                                                                                                                                  
    w.write(to_file)
print "file ends"