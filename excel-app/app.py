#!/bin/env python3

from flask import Flask, render_template
import database
import calcroyalties

app = Flask(__name__)

@app.route("/")
def mainpage():
	return render_template("index.html")

if __name__ == "__main__":
	app.run(debug=True)