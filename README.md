# Friendbook

## Functions

* User can create a profile and login
* User can add, edit and delete your own posts
* You can also add pictures on your post
* User can see user's own or other users' posts added to the application
* User can search posts by searching for the name of the person the post is about
* You can mark a friend as a friend, close friend or a best friend and also random categories
* You can also comment on posts

## Installing the application
Make sure you have Python installed and the repository cloned on your computer!

Create a virtual environment:
```
$ python3 -m venv venv
$ source venv/bin/activate
```

Install Flask:
```
$ pip install flask
```

Create the tables in the database and add the initial data:
```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Run the application:
```
$ flask run
```
Enjoy using the application :)
