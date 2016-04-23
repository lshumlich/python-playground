from functools import wraps
from flask import session, redirect, url_for, abort

class PermissionHandler():
    ''' Checks for permissions. Works both as a decorator (easy to apply to endpoints)
        and as a context manager (for more fine-grained control).
        Checks to see if a user is logged in, then if the user has the necessary permission'''
    def __init__(self, perm):
        self.perm = perm

    def __call__(self, f):
        # decorator implementation
        @wraps(f)
        def wrapper(*args, **kwds):
            if 'login' not in session: return redirect(url_for('login'))
            if self.perm not in session['permissions']:
                abort(403)
            else:
                return f(*args, **kwds)
        return wrapper

    def __enter__(self):
        # context manager implementation
        if 'login' not in session: return redirect(url_for('login'))
        if not self.perm in session['permissions']:
            abort(403)

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False