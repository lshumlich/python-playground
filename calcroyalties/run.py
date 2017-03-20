#!/bin/env python3
import logging, sys

root = logging.getLogger()
root.setLevel(logging.INFO)

if __name__ == '__main__':
    from src.app import app
    app.run('0.0.0.0', debug=True)
