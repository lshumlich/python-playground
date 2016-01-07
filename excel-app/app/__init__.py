#!/bin/env python3 

from flask import Flask, render_template

app = Flask(__name__)

from app import views
import database

@app.errorhandler(404)
def not_found(error):
    return "Sorry mate, page not found"
