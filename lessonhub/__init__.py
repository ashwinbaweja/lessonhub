from flask import Flask, g, jsonify, Response, request, json, render_template, redirect, current_app
import flask
import pymongo

# mongo
client = pymongo.MongoClient()
db = client['lessonhub']

app = Flask(__name__)
import lessonhub.routes
import lessonhub.api

if __name__ == '__main__':
    app.run(debug=True)