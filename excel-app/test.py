#!/bin/env python3

from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask.ext import excel
import pyexcel.ext.xlsx

app=Flask(__name__)
app.secret_key = "verysecretkey"

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        session["records"] = request.get_array(field_name="file")
        return redirect(url_for("show_file"))

    return '''
    <!doctype html>
    <title>Upload an Excel file</title>
    <h1>Upload an Excel file</h1>
    <form action="" method=post enctype=multipart/form-data><p>
    <input type=file name=file><input type=submit value="Upload">
    </form>
    '''

@app.route("/table")
def show_file():
    records = session["records"]
    return render_template("table.html", records=records)

if __name__ == "__main__":
    app.run(debug=True)

