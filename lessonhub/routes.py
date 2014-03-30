from flask import Flask, url_for, g, session, jsonify, Response, request, json, render_template, redirect, current_app
from lessonhub import app, db
from lessonhub import api
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json
from bson.objectid import ObjectId
from functools import wraps


def login_required(f):
    @wraps(f)
    def check_login(*args, **kwargs):
        if 'user_id' not in session or not session['user_id']:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return check_login

@app.route('/')
@login_required
def home():
    print session['user_id']
    user_info = db.users.find_one({'_id': ObjectId(session["user_id"])})
    user = {}
    user['name'] = session["name"]
    user['username'] = session["username"]
    user['userid'] = session["user_id"]
    user['followers_count'] = len(user_info['followers'])
    user['followees_count'] = len(user_info['following'])
    print user
    return render_template("curriculum.html", user=user)
	#user_id, firstname, last name
	#title, subject, date created, date updated


@app.route('/login', methods=['GET'])
def login_page():
	errors = {}
	return render_template("login.html", errors=errors)

@app.route('/check_login', methods=['POST'])
def check_login():
	username = request.form["username"]
	password = request.form["password"]
	user_object = db.users.find_one({"username": username})
	if(user_object):
		if (check_password_hash(user_object['password'], password)):
			session['username'] = username
			session['name'] = user_object['name']
			session['user_id'] = str(user_object['_id'])
			session['logged'] = True
			return redirect(url_for('home'))
		return render_template("login.html", errors = {"error": 1})
	return render_template("login.html", errors={"error": 2})

@app.route('/signup', methods=['GET'])
def signup_page():
	d = {}
	return render_template("signup.html", errors = d)

@app.route('/create_user', methods=['POST'])
def create_user():
    name = request.form['name']
    affiliation = request.form['affiliation']
    username = request.form['username']
    password = generate_password_hash(request.form['password'])
    user = {
        'name': name,
        'affiliation': affiliation,
        'username': username,
        'password': password,
        'followers' : [],
        'following' : []
    }
    user_id = db.users.insert(user)
    return render_template("login.html")

@app.route('/logout', methods=['GET'])
@login_required
def logout():
	session['username']= ""
	session['user_id'] = ""
	session['name'] = ""
	session['logged'] = False
	return render_template("login.html", errors = {})

#view profile of other user
@app.route('/user/<user_id>')
@login_required
def user(user_id):
    user = api.get_user_info(user_id)
    user['followers_count'] = len(user['followers'])
    user['followees_count'] = len(user['following'])
    user['userid'] = user['_id']
    return render_template("curriculum.html", user=user)

#view curriculum
@app.route('/curriculum/<curriculum_id>')
@login_required
def curriculum(curriculum_id):
	#//title, subject, author, created/updated
    curr_info = db.curricula.find_one({'_id': ObjectId(curriculum_id)})
    currics = {}
    currics["curr_id"] = curriculum_id
    currics['title'] = curr_info['title']
    currics['subtitle'] = curr_info['subtitle']
    currics['subject'] = curr_info['subtitle']
    return render_template("lessons.html", curr_info=currics)

@app.route('/lesson/<lesson_id>')
@login_required
def lesson(lesson_id):
	return render_template("lesson.html")

@app.route("/curriculum/add_curriculum", methods=['GET'])
@login_required
def add_curriculum():
	return render_template("create_curriculum.html")

@app.route("/curriculum/add_curriculum", methods=['POST'])
@login_required
def create_curriculum_post():
    title = request.form['title']
    subject = request.form['subject']
    subtitle = request.form['subtitle']
    parent_id = request.form['parentId']
    author_id = session['user_id']
    date_created = datetime.datetime.utcnow()
    last_updated = datetime.datetime.utcnow()
    lessons = []
    comments = []
    children = []
    curriculum = {
        'title': title,
        'subtitle': subtitle,
        'subject': subject,
        'parent_id': parent_id,
        'author_id': author_id,
        'date_created' : date_created,
        'last_updated' : last_updated,
        'comments' : comments,
        'lessons' : lessons,
        'children' : children
    }
    curriculum_id = db.curricula.insert(curriculum)
    return redirect(url_for('curriculum', curriculum_id=curriculum_id))

@app.route("/curriculum/<curriculum_id>/add_lesson", methods=['GET'])
@login_required
def add_lesson(curriculum_id):
    return render_template("add_lesson.html")

@app.route("/curriculum/<curriculum_id>/add_lesson", methods=['POST'])
@login_required
def add_lesson_post(curriculum_id):
    name = request.form.get('name', '')
    subtitle = request.form.get('subtitle', '')
    expected_duration = request.form.get('expectedDuration', '')
    parent_id = request.form.get('parentId', '')
    children = []
    date_created = datetime.datetime.utcnow()
    last_updated = datetime.datetime.utcnow()
    content = request.form.get('content', '')
    curriculum_id = request.form.get('curriculumId', '')
    original_author_id = request.form.get('originalAuthorId', '')
    num_forks = 0
    comments = []

    lesson = {
        'name': name,
        'subtitle': subtitle,
        'expected_duration': expected_duration,
        'parent_id': parent_id,
        'children' : children,
        'date_created' : date_created,
        'last_updated' : last_updated,
        'comments' : comments,
        'num_forks' : num_forks,
        'content': content,
        'curriculum_id': curriculum_id,
        'original_author_id': original_author_id
    }
    lesson_id = db.lessons.insert(lesson)

    lesson_index = int(request.form.get('lessonIndex', 0))
    curriculum = db.curricula.find_one({'_id': ObjectId(curriculum_id)})
    curriculum['lessons'].insert(lesson_index, lesson_id)
    db.curricula.save(curriculum)

    return redirect(url_for('curriculum', curriculum_id=curriculum_id))

def fork_lesson(lesson_id, curriculum_id):
    lesson = db.lessons.find_one({'_id': ObjectId(lesson_id)})
    new_lesson = {
    	'name': lesson.get('name'),
    	'subtitle': lesson.get('subtitle'),
    	'expected_duration': lesson.get('expected_duration'),
    	'parent_id': lesson.get('lesson_id'),
    	'children': [],
    	'content': lesson.get('content'),
    	'curriculum_id': str(curriculum_id),
    	'date_created': datetime.datetime.utcnow(),
    	'last_updated': datetime.datetime.utcnow(),
    	'num_forks': 0,
    	'original_author_id': lesson.get('original_author'),
    	'comments': []
    }

    new_lesson_id = db.lessons.insert(new_lesson)
    lesson['children'].append(new_lesson_id)
    db.lessons.save(lesson)
    return new_lesson_id

@app.route("/fork/curriculum/<curriculum_id>", methods=["POST"])
@login_required
def fork_curriculum(curriculum_id):
    old_curriculum = db.curricula.find_one({'_id': ObjectId(curriculum_id)})

    new_curriculum = {
    	"title": old_curriculum.get('title'),
    	"subtitle": old_curriculum.get('subtitle'),
    	"subject": old_curriculum.get('subject'),
    	"lessons": [],
    	"parent_id":  old_curriculum.get('_id', ''),
    	"children": [],
    	"date_created": datetime.datetime.utcnow(),
    	"last_updated": datetime.datetime.utcnow(),
    	"author_id": session.get('user_id', ''),
    	"comments": []
    }

    new_curriculum_id = db.curricula.insert(new_curriculum)

    new_lessons = []
    for lesson_id in old_curriculum.get('lessons'):
    	new_lesson_id = fork_lesson(lesson_id, new_curriculum_id)
    	new_lessons.append(new_lesson_id)


    new_curriculum = db.curricula.find_one({"_id": ObjectId(new_curriculum_id)})
    new_curriculum['lessons'] = new_lessons
    db.curricula.save(old_curriculum)
    db.curricula.save(new_curriculum)

    print new_lessons
    print new_curriculum

    return redirect(url_for('curriculum', curriculum_id=new_curriculum_id))

@app.route('/search', methods=['GET'])
def search_results():
    query = request.args.get('q', '')
    if query == '':
        results = None
    else:
        results = api.search_with_query(query)
    return render_template('search.html', results=results)

