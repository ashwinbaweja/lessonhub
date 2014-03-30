from flask import Flask, g, jsonify, Response, request, json, render_template, redirect, current_app
import pymongo
app = Flask(__name__)

# mongo
client = pymongo.MongoClient()
db = client['lessonhub']

@app.route('/v1/user', methods=['GET'])
def get_user(user_id):
	return db.users.find_one({'_id': user_id})

@app.route('/v1/follow', methods='POST') 
def follow_user(follower_id, followed_id):
	pass

# returns: user_id of newly created user
@app.route('/v1/user', methods= [ 'POST' ] )
def create_user():
	first_name = request.data.get('firstName', '')
	last_name = request.data.get('lastName', '')
	affiliation = request.data.get('affiliation', '')
	user = { 'first_name': first_name,
		'last_name': last_name,
		'affiliation': affiliation }
	user_id = db.users.insert(user)
	return user_id


@app.route('/v1/curriculum', methods="GET")
def get_curriculum(curriculum_id):
	db.curricula.find_one({'_id': curriculum_id})

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

@app.route('/v1/lesson', methods="GET")
def get_lesson(lesson_id):
	db.lessons.find_one({'_id': lesson_id})

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

@app.route("/v1/lesson", methods="PUT")
def update_lesson(lesson_id):
	

@app.route("/v1/curriculum", methods="PUT")
def update_curriculum(curriculum_id):
	pass


if __name__ == '__main__':
    app.run(debug=True)
