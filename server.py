"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash, session)
from flask_debugtoolbar import DebugToolbarExtension

# For counting:
    # from SQLAlchemy import func

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

@app.route('/movies')
def movie_list():
    """ Show a list all of our movies """

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)

@app.route('/register')
def registration():
    """ Show the registration form """

    return render_template('register.html')


@app.route('/verify-registration', methods=["POST"])
def verify_reg():
    """Verify the email and password entered"""

    email = request.form.get("email")
    password = request.form.get("password")
    age = request.form.get("age")
    zipcode = request.form.get("zipcode")

    # Look for the email in the DB
    existing_user = User.query.filter(User.email == email).all()
    print existing_user

    if len(existing_user) == 0:
        print "New User"

        user = User(email=email, password=password, age=age, zipcode=zipcode)
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
        flash("You have found a website loophole... Please try again later.")
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

    # Get user object
    existing_user = User.query.filter(User.email == login_email).all()

    # In DB?
    if len(existing_user) == 1:
        print "UN in DB"
        existing_password = existing_user[0].password

        # Correct password?
        if login_password == existing_password:
            if 'login' in session:
                flash("You are already logged in!")
                return redirect('/')
            else:
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

    if 'login' in session:
        session.pop('login')
        flash("Goodbye, you are now logged out!")
        return redirect('/')
    else:
        flash("You were never logged in :(")
        return redirect ('/')


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

@app.route('/movies/<movie_id>', methods=['GET'])
def show_movie_details(movie_id):
    """ Display infomration about a movie """

    requested_movie = Movie.query.get(movie_id)
    # print requested_movie


    # Trying to get count of num times movies was rated each score:
        # ratings_list = Rating.query(Rating.score, func.count(Rating.score))filter_by(movie_id=movie_id).group_by(Rating.score).all()
    ratings_list = Rating.query.filter_by(movie_id=movie_id).all()
    # print ratings_list
    return render_template('movie_page.html',
                            movie_id=movie_id,
                            movie=requested_movie,
                            ratings=ratings_list)

@app.route('/movies/<movie_id>', methods=['POST'])
def show_updated_movie_details(movie_id):
    """ Display infomration about a movie, updated with user's rating"""

    user_rating = request.form.get("user_rating")

    if 'login' in session:
        user_id = session['login']

        # Look to see if they have existing rating for movie
        existing_rating = Rating.query.filter(Rating.user_id == user_id, Rating.movie_id == movie_id).all()

        if len(existing_rating) == 1:
            print "Existing User Rating"

            their_rating = existing_rating[0]
            their_rating.score = user_rating
            db.session.commit()

            flash("You have updated your rating to {}!".format(user_rating))

        if len(existing_rating) == 0:
            print "New User Rating!"
            new_rating = Rating(movie_id=movie_id, user_id=user_id, score=user_rating)
            print new_rating
            db.session.add(new_rating)
            db.session.commit()

            flash("You have added your new rating of {}!".format(user_rating))

        requested_movie = Movie.query.get(movie_id)
        ratings_list = Rating.query.filter_by(movie_id=movie_id).all()
        # print ratings_list
        return render_template('movie_page.html',
                                movie_id=movie_id,
                                movie=requested_movie,
                                ratings=ratings_list)

    else:
        flash ('You must be logged in to rate a movie. Please log in!')
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
