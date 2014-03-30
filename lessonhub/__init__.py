from flask import Flask, session, jsonify, Response, request, json, render_template, redirect, current_app
import pymongo

app = Flask(__name__)
# mongo
client = pymongo.MongoClient()
db = client['lessonhub']
import lessonhub.api
import lessonhub.routes


if __name__ == '__main__':
    app.run(debug=True)