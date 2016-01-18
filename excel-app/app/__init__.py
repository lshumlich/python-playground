#!/bin/env python3 

from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'secret'

from app import views
