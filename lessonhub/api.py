from flask import Flask, g, session, jsonify, Response, request, json, render_template, redirect, current_app
from lessonhub import app, db
import json

@app.route('/v1/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify(db.users.find_one({'_id': user_id}))

@app.route("/v1/test", methods=["GET"])
def test_other_app():
    return jsonify({"string": "string"})

@app.route('/v1/follow', methods='POST')
def follow_user(follower_id, followed_id):
    pass

# returns: user_id of newly created user
@app.route('/v1/user', methods=['POST'])
def create_user():
    name = request.data.get('name')
    affiliation = request.data.get('affiliation', '')
    user = { 'name': name,
        'affiliation': affiliation }
    user_id = db.users.insert(user)
    return user_id

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
    title = request.data.get('title', '')
    subject = request.data.get('subject', '')
    parent_id = request.data.get('parentId', '')
    author_id = request.data.get('authorId', '')
    curriculum = {
        'title': title,
        'subject': subject,
        'parent_id': parent_id,
        'author_id': author_id
    }
    curriculum_id = db.curricula.insert(curriculum)
    return curriculum_id

@app.route('/v1/lesson', methods=["GET"])
def get_lesson(lesson_id):
    jsonify(db.lessons.find_one({'_id': lesson_id}))

@app.route("/v1/lesson", methods="POST")
def create_lesson():
    name = request.data.get('name', '')
    subtitle = request.data.get('subtitle', '')
    expected_duration = request.data.get('expectedDuration', '')
    parent_id = request.data.get('parentId', '')
    content = request.data.get('content', '')
    curriculum_id = request.data.get('curriculumId', '')
    original_author = request.data.get('originalAuthor', '')
    lesson = {
        'name': name,
        'subtitle': subtitle,
        'expected_duration': expected_duration,
        'parent_id': parent_id,
        'content': content,
        'curriculum_id': curriculum_id,
        'original_author': original_author
    }
    lesson_id = db.lessons.insert(lesson)
    return lesson_id

@app.route("/v1/lesson", methods=["PUT"])
def update_lesson(lesson_id):
    pass

@app.route("/v1/curriculum", methods=["PUT"])
def update_curriculum(curriculum_id):
    pass

def create_or_query(fields, regex):
    query = {'$or': []}
    for field in fields:
        query['$or'].append({field: regex})
    return query

@app.route('/v1/search/<search_query>', methods=['GET'])
def search(search_query):
    search_query_regex = { '$regex': search_query.replace(' ', '.*'), '$options': 'i'}

    users_search_query = create_or_query(['name', 'affiliation'], search_query_regex)
    users_search_results = db.users.find(users_search_query).limit(50)
    users = []
    for u in users_search_results:
        users.append(u)

    curricula_search_query = create_or_query(['title', 'subtitle', 'subject'], search_query_regex)
    curricula_search_results = db.curricula.find(curricula_search_query).limit(50)
    curricula = []
    for u in curricula_search_results:
        curricula.append(u)

    lessons_search_query = create_or_query(['name', 'subtitle', 'content'], search_query_regex)
    lessons_search_results = db.lessons.find(lessons_search_query).limit(50)
    lessons = []
    for u in lessons_search_results:
        lessons.append(u)

    return flask.jsonify({
        'users': users,
        'curricula': curricula,
        'lessons': lessons
    })



