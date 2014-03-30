from flask import Flask, g, jsonify, Response, request, json, render_template, redirect, current_app
from lessonhub import app

@app.route('/user')
def home():
	return render_template("index.html", user_object)

@app.route('/user/curriculum/<int:curriculum_id>')
def other_user_curriculum():
	return render_template("index.html")

@app.route('/user/curriculum/<int:curriculum_id>')
def user_curriculum():
	return render_template("index.html")
