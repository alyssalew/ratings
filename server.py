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
    existing_user = User.query.filter(User.email == email).all()
    print existing_user

    if len(existing_user) == 0:
        print "New User"

        user = User(email=email, password=password)
        db.session.add(user)
        db.session.commit()
        flash("Thanks for registering!")
        return redirect('/')

    elif len(existing_user) == 1:
        print "Existing user"
        flash("You're already registered!")
        return redirect('/')

    else:
        print "MAJOR PROBLEM!"
        flash("You have a website loophole... Please try again later.")
        return redirect("/")


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
    existing_user = User.query.filter(User.email == login_email).all()

    # In DB?
    if len(existing_user) == 1:
        print "UN in DB"
        existing_password = existing_user[0].password

        # Correct password?
        if login_password == existing_password:
            #Add to session
            session['login'] = existing_user[0].user_id
            flash("Success, you are now logged in!")
            return redirect('/')
        else:
            flash("Incorrect password. Please try again.")
            return redirect('/login')

    # Not in DB
    elif len(existing_user) == 0:
        print "UN not in DB"
        flash("That email couldn't be found. Please try again.")
        return redirect('/login')

    else:
        print "MAJOR PROBLEM!"
        flash("You have found a website loophole... Please try again later.")
        return redirect("/")


@app.route('/logout')
def logout():
    """Logs user out """

    session.pop('login')

    flash("Goodbye, you are now logged out!")
    return redirect('/')


@app.route('/users/<user_id>')
def show_user_details(user_id):
    """ Display infomration about the user """

    requested_user = User.query.get(user_id)
    print requested_user

    age = requested_user.age
    zipcode = requested_user.zipcode
    movie_list = Rating.query.filter_by(user_id=user_id).all()



    return render_template('user_page.html',
                            user_id=user_id,
                            age=age,
                            zipcode=zipcode,
                            movies= movie_list)



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
