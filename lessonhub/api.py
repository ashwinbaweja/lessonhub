from flask import Flask, g, session, jsonify, Response, request, json, render_template, redirect, current_app
from lessonhub import app, db
from werkzeug.security import generate_password_hash, check_password_hash
import json
import datetime

@app.route('/v1/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(db.users.find_one({'_id': user_id}))

@app.route('/v1/follow', methods='POST')
def follow_user(follower_id, followed_id):
    pass

@app.route('/v1/user/<int:user_id>/curricula', methods=["GET"])
def get_all_curricula(user_id):
    x = db.curricula.find({"author": user_id})
    curricula = []
    for curric in x:
        curricula.append(curric)
    print curricula
    return json.dumps(curricula)

@app.route('/v1/curriculum/<int:curriculum_id>', methods=["GET"])
def get_curriculum(curriculum_id):
    return jsonify(db.curricula.find_one({'_id': curriculum_id}))

@app.route('/v1/curriculum', methods="POST")
def create_curriculum():
    title = request.form['title']
    subject = request.form['subject']
    subtitle = request.form['subtitle']
    parent_id = request.form['parentId']
    author_id = session['user_id']
    date_created = datetime.utcnow()
    last_updated = datetime.utcnow()
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
    return curriculum_id

@app.route('/v1/lesson/<int:lesson_id>', methods=["GET"])
def get_lesson(lesson_id):
    jsonify(db.lessons.find_one({'_id': lesson_id}))

@app.route("/v1/lesson", methods="POST")
def create_lesson():
    name = request.data.get('name', '')
    subtitle = request.data.get('subtitle', '')
    expected_duration = request.data.get('expectedDuration', '')
    parent_id = request.data.get('parentId', '')
    children = []
    date_created = datetime.utcnow()
    last_updated = datetime.utcnow()
    content = request.data.get('content', '')
    curriculum_id = request.data.get('curriculumId', '')
    original_author_id = request.data.get('originalAuthor', '')
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
    return lesson_id

@app.route("/v1/lesson", methods=["PUT"])
def update_lesson():
    lesson_id = request.data.get('lessonId')
    name = request.data.get('name')
    subtitle = request.data.get('subtitle')
    expected_duration = request.data.get('expectedDuration')
    content = request.data.get('content')
    last_updated = datetime.datetime.utcnow()

    lesson = db.lessons.find_one({'_id': lesson_id})

    lesson.name = name
    lesson.subtitle = subtitle
    lesson.expected_duration = expected_duration
    lesson.content = content
    lesson.last_updated = last_updated

    db.lessons.save(lesson)

@app.route("/v1/curriculum", methods=["PUT"])
def update_curriculum():
    curriculum_id = request.data.get('curriculumId')
    title = request.data.get('title')
    subject = request.data.get('subject')
    subtitle = request.data.get('subtitle')
    last_updated = datetime.datetime.utcnow()

    curriculum = db.curricula.find_one({'_id': curriculum_id})
    curriculum.last_updated = last_updated
    curriculum.subtitle = subtitle
    curriculum.title = title
    curriculum.subject = subject
    db.curricula.save(curriculum)

def create_or_query(fields, regex):
    query = {'$or': []}
    for field in fields:
        query['$or'].append({field: regex})
    return query

def array_from_cursor(cursor, max_limit):
    return_arr = []
    for item in cursor:
        if len(return_arr) >= max_limit:
            break
        return_arr.append(item)
    return return_arr

@app.route('/v1/search/<search_query>', methods=['GET'])
def search(search_query):
    search_query_regex = { '$regex': search_query.replace(' ', '.*'), '$options': 'i'}

    users_search_query = create_or_query(['name', 'affiliation'], search_query_regex)
    users_search_results = db.users.find(users_search_query).limit(50)
    users = array_from_cursor(users_search_results)

    curricula_search_query = create_or_query(['title', 'subtitle', 'subject'], search_query_regex)
    curricula_search_results = db.curricula.find(curricula_search_query).limit(50)
    curricula = array_from_cursor(curricula_search_results)

    lessons_search_query = create_or_query(['name', 'subtitle', 'content'], search_query_regex)
    lessons_search_results = db.lessons.find(lessons_search_query).limit(50)
    lessons = array_from_cursor(lessons_search_results)

    return flask.jsonify({
        'users': users,
        'curricula': curricula,
        'lessons': lessons
    })



