"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')





@app.route('/users')
def user_list():
    """ Show a list of all of our users """

    users = User.query.all()

    return render_template("user_list.html", users=users)


@app.route('/register')
def registration():
    """ Show the registration form """

    return render_template('register.html')

@app.route('/verify-registration', methods=["POST"])
def verify_reg():
    """Verify the email and password entered"""

    email = request.form.get("email")
    password = request.form.get("password")

    # Look for the email in the DB
    existing_user = User.query.filter(User.email == email).first()
    print existing_user

    if existing_user is None:
        print "New User"

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect('/')

    else:
        print "Existing user"
        return redirect('/')


    # users = User.query.all()
    # emails = []

    # for inx in range(len(users)):
    #     an_email = users[inx].email
    #     emails.append(an_email)

    # print emails

    #if email == an_email:


@app.route('/login')
def login():
    """Show login form"""
    return render_template('login.html')



@app.route('/verify-login', methods=["POST"])
def verify_login():
    """ Verify user and add to session """

    login_email = request.form.get("email")
    login_password = request.form.get("password")

    # Get user obbject
    existing_user = User.query.filter(User.email == login_email).first()

    # In DB?
    if existing_user is not None:
        print "UN in DB"
        existing_password = existing_user.password

        # Correct password?
        if login_password == existing_password:
            #Add to session
            session['login'] = existing_user.user_id
            return redirect('/')
        else:
            return redirect('/login')

    # Not in DB
    else:
        print "UN not in DB"
        return redirect('/login')




if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
