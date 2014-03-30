from flask import Flask, g, jsonify, Response, request, json, render_template, redirect, current_app
import pymongo

app = Flask(__name__)
import lessonhub.routes
import lessonhub.api
# mongo
client = pymongo.MongoClient()
db = client['lessonhub']

if __name__ == '__main__':
    app.run(debug=True)