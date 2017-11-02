# <p align="center"> WebApp to log and recommed videos. <p>

This interesting project uses three databases **MySQL**, **Neo4j** and **MongoDB** to create a youtube like application. 

The dataset is JSON files containing video data from youtube itself including the file name, tags, description and likes, comments, views etc.

## Databases

#### MongoDB
It contains all the JSON files as Documents. A python code is written to insert all files into an instance of database. Since data inside a JSON file is not properly structured and two files may have entirely different structure, content and size it makes more sense to use a Document based NoSQL database to store such details.

```
$ python insert_mongo.py
```
#### Neo4j
The graph based database is used to store relationship between two videos. Each video is a node in the graph and edges are created based on properties like:
* Two videos belonging to same channel.
* Two videos having similar tags. 
* Two videos having similar description.

A python file to create nodes and relationships is present in repo.
```
$ python insert_neo.py
```

#### MySQL
Activity of each user is logged in tables present in MySQL. What the user watches, or likes and the channel to which s/he subscribes helps in predicting the taste of user and well tailored suggestions are made. User Login table also helps is saving user activity, and seperating anonymous users to logged in users.

---
### Feature

Backend of application is made in python using Flask. It has the following features:
* **Login**: Flask login module is for user authentication.
* **Trending Videos**: Video Clicks make it popular and more likely to appear as suggestion. More users watch it, higher it gets in the application. 
* **Word Correction**: A dictionary is created of unique words from database, and some common english words. A Fuzzy logic based word correction algo is used to correct mis-spelled words in the application.
* **Channel Subscription**: Logged in Users can subscribe to a channel. It will be shown in user's start page and any new video by the channel will be highlighted.
* **User Landing Page**: Each User has a landing page where all its liked videos and subscribed channels are kept for further watching.
*  **Channel PIage**: Each channel has its own page where user can visit and see all videos. 
*  **Boolean Search Box**: An advanced search box with And, Or and not operations in search bar to ensure effective search.  
* **Javascript based interactive interface**: The interactive web application makes the entire process smooth and user friendly.

### Pre-requisites
Install flask
```
$ pip install flask
```
Install flask_pymongo for MongoDB in flask
```
$ pip install flask_pymongo
```
Install flask_mysqldb for MySQL in flask
```
$ pip install flask_mysqldb
```
Install flask_login for Client Login 
```
$ pip install flask_login
```
Install py2neo for Neo4j
```
$ pip install py2neo
```
#### Run the application
Create a directory of words using: 
```
python directory.py
```
Create flask server to host the application using:
```
python search.py
```