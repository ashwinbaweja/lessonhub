from flask import Flask, g, session, jsonify, Response, request, json, render_template, redirect, current_app
from lessonhub import app, db
from werkzeug.security import generate_password_hash, check_password_hash
import json
import datetime
from bson.objectid import ObjectId

def get_serializable_user(user):
    return {
        '_id': str(user.get('_id', '')),
        'username': user.get('username', ''),
        'name': user.get('name', ''),
        'affiliation': user.get('affiliation', ''),
        'followers': user.get('followers'),
        'following': user.get('following')
    }

def get_serializable_curriculum(curriculum):
    lesson_ids = []
    for i in curriculum.get('lessons', []):
        lesson_ids.append(str(i))
    return {
        '_id': str(curriculum.get('_id', '')),
        'last_updated': str(curriculum.get('last_updated', '')),
        'date_created': str(curriculum.get('date_created', '')),
        'title': curriculum.get('title', ''),
        'subtitle': curriculum.get('subtitle', ''),
        'subject': curriculum.get('subject', ''),
        'lessons': lesson_ids,
        'parent_id': str(curriculum.get('parent_id', '')),
        'children': curriculum.get('children', ''),
        'comments': curriculum.get('comments', ''),
        'author_id': str(curriculum.get('author_id', ''))
    }

def get_seriazliable_lesson(lesson):
    children = []
    for i in lesson.get('children', []):
        children.append(str(i))
    return {
        '_id': str(lesson.get('_id', '')),
        'name': lesson.get('name', ''),
        'subtitle': lesson.get('subtitle', ''),
        'expected_duration': lesson.get('expected_duration', ''),
        'parent_id': str(lesson.get('parent_id', '')),
        'children': children,
        'date_created': str(lesson.get('date_created', '')),
        'last_updated': str(lesson.get('last_updated', '')),
        'comments': lesson.get('comments', ''),
        'num_forks': lesson.get('num_forks', ''),
        'content': lesson.get('content', ''),
        'curriculum_id': str(lesson.get('curriculum_id', '')),
        'original_author_id': str(lesson.get('original_author_id', ''))
    }

def get_user_info(user_id):
    return get_serializable_user(db.users.find_one({'_id': ObjectId(user_id)}))

@app.route('/v1/user/<user_id>', methods=['GET'])
def get_user(user_id):
    user = get_user_info(user_id)
    return jsonify(user)

@app.route('/v1/follow', methods='POST')
def follow_user(follower_id, followed_id):
    pass

@app.route('/v1/user/<user_id>/curricula', methods=["GET"])
def get_all_curricula(user_id):
    x = db.curricula.find({"author_id": user_id})
    curricula = []
    for curric in x:
        curricula.append(get_serializable_curriculum(curric))
    return json.dumps(curricula)

@app.route('/v1/curriculum/<curriculum_id>', methods=["GET"])
def get_curriculum(curriculum_id):
    curric = db.curricula.find_one({'_id': ObjectId(curriculum_id)})
    return jsonify(get_serializable_curriculum(curric))

@app.route('/v1/curriculum/<curriculum_id>/lessons', methods=["GET"])
def get_lessons_from_curriculum(curriculum_id):
    curriculum = db.curricula.find_one({'_id': ObjectId(curriculum_id)})
    lessons = []
    for lesson_id in curriculum['lessons']:
        lessons.append(get_seriazliable_lesson(db.lessons.find_one({'_id': ObjectId(lesson_id)})))
    print lessons
    return json.dumps(lessons)

@app.route('/v1/curriculum', methods=["POST"])
def create_curriculum():
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
    return curriculum_id

@app.route('/v1/lesson/<lesson_id>', methods=["GET"])
def get_lesson(lesson_id):
    l = db.lessons.find_one({'_id': ObjectId(lesson_id)})
    return jsonify(get_serializable_lesson(l))

@app.route("/v1/lesson", methods="POST")
def create_lesson():
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

    lesson_index = int(request.form.get('lessonIndex', ''))
    curriculum = db.curricula.find_one({'_id': ObjectId(curriculum_id)})
    curriculum['lessons'].insert(lesson_index, lesson_id)
    db.curricula.save(curriculum)

    return lesson_id

@app.route("/v1/lesson", methods=["PUT"])
def update_lesson():
    lesson_id = request.form.get('lessonId')
    lesson = db.lessons.find_one({'_id': ObjectId(lesson_id)})

    name = request.form.get('name', lesson.get("name"))
    subtitle = request.form.get('subtitle', lesson.get("subtitle"))
    expected_duration = request.form.get('expectedDuration', lesson.get("expected_duration"))
    content = request.form.get('content', lesson.get("content"))
    last_updated = datetime.datetime.utcnow()

    lesson['name'] = name
    lesson['subtitle'] = subtitle
    lesson['expected_duration'] = expected_duration
    lesson['content'] = content
    lesson['last_updated'] = last_updated

    db.lessons.save(lesson)


# @app.route("/v1/curriculum", methods=["PUT"])
# def update_curriculum():
#     curriculum_id = request.data.get('curriculumId')
#     title = request.data.get('title')
#     subject = request.data.get('subject')
#     subtitle = request.data.get('subtitle')
#     last_updated = datetime.datetime.utcnow()

#     curriculum = db.curricula.find_one({'_id': ObjectId(curriculum_id)})
#     curriculum.last_updated = last_updated
#     curriculum.subtitle = subtitle
#     curriculum.title = title
#     curriculum.subject = subject
#     db.curricula.save(curriculum)

def create_or_query(fields, regex):
    query = {'$or': []}
    for field in fields:
        query['$or'].append({field: regex})
    return query

def array_from_cursor(cursor, max_limit, type):
    return_arr = []
    for item in cursor:
        if len(return_arr) >= max_limit:
            break

        if type == 'user':
            return_arr.append(get_serializable_user(item))
        elif type == 'curriculum':
            return_arr.append(get_serializable_curriculum(item))
        elif type == 'lesson':
            return_arr.append(get_seriazliable_lesson(item))
        else:
            return_arr.append(item)
    return return_arr

def search_with_query(search_query):
    search_query_regex = { '$regex': search_query.replace(' ', '.*'), '$options': 'i'}

    users_search_query = create_or_query(['name', 'affiliation'], search_query_regex)
    users_search_results = db.users.find(users_search_query).limit(50)
    users = array_from_cursor(users_search_results, 50, 'user')

    curricula_search_query = create_or_query(['title', 'subtitle', 'subject'], search_query_regex)
    curricula_search_results = db.curricula.find(curricula_search_query).limit(50)
    curricula = array_from_cursor(curricula_search_results, 50, 'curriculum')

    lessons_search_query = create_or_query(['name', 'subtitle', 'content'], search_query_regex)
    lessons_search_results = db.lessons.find(lessons_search_query).limit(50)
    lessons = array_from_cursor(lessons_search_results, '50', 'lesson')

    return {
        'users': users,
        'curricula': curricula,
        'lessons': lessons
    }

@app.route('/v1/search/<search_query>', methods=['GET'])
def search(search_query):
    return jsonify(search_with_query(search_query))



