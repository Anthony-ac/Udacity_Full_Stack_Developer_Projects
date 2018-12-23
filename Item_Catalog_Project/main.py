from flask import Flask, render_template, request, \
    redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from db_setup import Base, BodyPart, Workout, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Creates Flask instance


app = Flask(__name__)

"""sets CLIENT_ID equal to the web and client_id fields
from JSON file."""

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


APPLICATION_NAME = "Weightlifting Application"


# Connects to Weightlifting database and creates database session


engine = create_engine('sqlite:///weightlifting.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Creates anti-forgery state token


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # Passes state as STATE to login.html

    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validates state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtains authorization code

    code = request.data
    try:
        # Upgrades the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Checks that the access token is valid.

    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # Aborts if error in access token info.

    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verifies that the access token is used for the intended user.

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verifies that the access token is valid for the application

    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is \
                                             already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Stores the access token in the session for later use.

    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Gets user info

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Adds provider to login session

    login_session['provider'] = 'google'

    # See if user exists, if it doesn't make new one

    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: \
                150px;-webkit-border-radius: \
                150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output

# User retrieval functions

# Creates new user and returns new user's id via filter by email


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id

# Returns user's id via filter by user_id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user

# Returns user's id via filter by email


def getUserID(email):
    user = session.query(User).filter_by(email=email).one_or_none()
    if user is not None:
        return user.id
    return None


# Revokes a current user's token and resets their login_session

@app.route('/gdisconnect')
def gdisconnect():
    # If access token does not exist send 401 message
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    """If access token exists disconnect and send 200 message
       If access token exists but no 200 status code:
       don't disconnect and send 400 message"""
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to \
                                 revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs


# view listing of workouts


@app.route('/bodycategorieslifting/<int:body_part_id>/list/JSON')
def workoutsJSON(body_part_id):
    bodypart = session.query(BodyPart).filter_by(id=body_part_id).one()
    workouts = session.query(Workout).filter_by(
        body_part_id=body_part_id).all()
    return jsonify(Workouts=[w.serialize for w in workouts])

# view information for a workout


@app.route('/bodycategorieslifting/<int:body_part_id>/<int:workout_id>/JSON')
def workoutJSON(body_part_id, workout_id):
    workout = session.query(Workout).filter_by(id=workout_id).one()
    return jsonify(workout=workout.serialize)

# view listing of body categories


@app.route('/bodycategorieslifting/JSON')
def bodyCategoriesJSON():
    bodyparts = session.query(BodyPart).all()
    return jsonify(bodyparts=[b.serialize for b in bodyparts])

# Global variable to list any modifications to a body category


bodyCategoryChanges = []


# Shows body part categories for weightlifting


@app.route('/')
@app.route('/bodycategorieslifting/')
def bodyCategories():
    bodyparts = session.query(BodyPart).order_by(asc(BodyPart.name))
    if 'username' not in login_session:
        return render_template('bodyCategories.html', bodyparts=bodyparts,
                               bodyCategoryChanges=bodyCategoryChanges,
                               loggedIn=False)
    else:
        return render_template('bodyCategories.html', bodyparts=bodyparts,
                               bodyCategoryChanges=bodyCategoryChanges,
                               loggedIn=True)


# Creates a new body part


@app.route('/bodycategorieslifting/new/', methods=['GET', 'POST'])
def newBodyCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newBodyPart = BodyPart(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(newBodyPart)
        session.commit()
        bodyCategoryChanges.append(newBodyPart.name + " Body Category Added.")
        flash('New Body Category %s Successfully Created' % newBodyPart.name)
        return redirect(url_for('bodyCategories'))
    else:
        return render_template('newBodyCategory.html')

# Edits current body part


@app.route('/bodycategorieslifting/<int:body_part_id>/edit/',
           methods=['GET', 'POST'])
def editBodyCategory(body_part_id):
    editedBodyPart = session.query(
        BodyPart).filter_by(id=body_part_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedBodyPart.user_id != login_session['user_id']:
        return "<script>function myFunction() \
        {alert('Action Not Authorized!!!');}</script> \
        <body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedBodyPart.name = request.form['name']
            flash('Body Category Successfully Edited %s' % editedBodyPart.name)
            bodyCategoryChanges.append(editedBodyPart.name +
                                       " Body Category Edited.")
        return redirect(url_for('bodyCategories'))
    else:
        return render_template('editBodyCategory.html',
                               bodypart=editedBodyPart)


# Deletes a body category


@app.route('/bodycategorieslifting/<int:body_part_id>/delete/',
           methods=['GET', 'POST'])
def deleteBodyCategory(body_part_id):
    bodyPartToDelete = session.query(
        BodyPart).filter_by(id=body_part_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if bodyPartToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() \
        {alert('Action Not Authorized!!!');}</script> \
        <body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(bodyPartToDelete)
        session.commit()
        flash('%s Successfully Deleted' % bodyPartToDelete.name)
        bodyCategoryChanges.append(bodyPartToDelete.name +
                                   " Body Category Deleted.")
        return redirect(url_for('bodyCategories',
                                body_part_id=body_part_id))
    else:
        return render_template('deleteBodyCategory.html',
                               bodypart=bodyPartToDelete)


# Global variable to list any modifications for workouts


workoutChanges = []

# shows workouts for body category


@app.route('/bodycategorieslifting/<int:body_part_id>/')
@app.route('/bodycategorieslifting/<int:body_part_id>/list/')
def workouts(body_part_id):
    bodypart = session.query(BodyPart).filter_by(id=body_part_id).one()
    creator = getUserInfo(bodypart.user_id)
    workouts = session.query(Workout).filter_by(
        body_part_id=body_part_id).all()
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('workouts.html', workouts=workouts,
                               bodypart=bodypart,
                               creator=creator,
                               workoutChanges=workoutChanges,
                               loggedIn2=False)
    else:
        return render_template('workouts.html', workouts=workouts,
                               bodypart=bodypart,
                               creator=creator,
                               workoutChanges=workoutChanges,
                               loggedIn2=True)


# Creates a new workout


@app.route('/bodycategorieslifting/<int:body_part_id>/list/new/',
           methods=['GET', 'POST'])
def newWorkouts(body_part_id):
    if 'username' not in login_session:
        return redirect('/login')
    bodypart = session.query(BodyPart).filter_by(id=body_part_id).one()
    if login_session['user_id'] != bodypart.user_id:
        return "<script>function myFunction() \
        {alert('Action Not Authorized!!!');}</script> \
        <body onload='myFunction()'>"
    if request.method == 'POST':
            newWorkout = Workout(name=request.form['name'],
                                 description=request.form['description'],
                                 difficulty=request.form['difficulty'],
                                 body_part_id=body_part_id,
                                 user_id=bodypart.user_id)

            session.add(newWorkout)
            session.commit()
            flash('New Workout %s Created' % (newWorkout.name))
            workoutChanges.append(newWorkout.name + " Workout Added.")
            return redirect(url_for('workouts', body_part_id=body_part_id))
    else:
        return render_template('newWorkout.html', body_part_id=body_part_id)

# Edits a workout


@app.route('/bodycategorieslifting/<int:body_part_id> \
/list/<int:workout_id>/edit',
           methods=['GET', 'POST'])
def editWorkout(body_part_id, workout_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedWorkout = session.query(Workout).filter_by(id=workout_id).one()
    bodypart = session.query(BodyPart).filter_by(id=body_part_id).one()
    if login_session['user_id'] != bodypart.user_id:
        return "<script>function myFunction() \
        {alert('Action Not Authorized!!!');} \
        </script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedWorkout.name = request.form['name']
        if request.form['description']:
            editedWorkout.description = request.form['description']
        if request.form['difficulty']:
            editedWorkout.difficulty = request.form['difficulty']
        session.add(editedWorkout)
        session.commit()
        flash('Workout succesfully edited.')
        workoutChanges.append(editedWorkout.name + " Workout Edited.")
        return redirect(url_for('workouts', body_part_id=body_part_id))
    else:
        return render_template('editWorkout.html', body_part_id=body_part_id,
                               workout_id=workout_id,
                               editedWorkout=editedWorkout)


# Deletes a workout


@app.route('/bodycategorieslifting/<int:body_part_id> \
/list/<int:workout_id>/delete',
           methods=['GET', 'POST'])
def deleteWorkout(body_part_id, workout_id):
    if 'username' not in login_session:
        return redirect('/login')
    bodypart = session.query(BodyPart).filter_by(id=body_part_id).one()
    workoutToDelete = session.query(Workout).filter_by(id=workout_id).one()
    if login_session['user_id'] != bodypart.user_id:
        return "<script>function myFunction() \
        {alert('Action Not Authorized!!!');} \
        </script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(workoutToDelete)
        session.commit()
        flash('Workout Successfully Deleted')
        workoutChanges.append(workoutToDelete.name + " Workout Deleted.")
        return redirect(url_for('workouts', body_part_id=body_part_id))
    else:
        return render_template('deleteWorkout.html',
                               workoutToDelete=workoutToDelete)


"""Disconnects user if logged in via google
by calling gdisconnect and deleting session"""


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("     You have successfully been logged out.")
        return redirect(url_for('bodyCategories'))
    else:
        flash("     You were not logged in")
        return redirect(url_for('bodyCategories'))


# Interpreter will use this .py file as main code to run

if __name__ == '__main__':

    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000, threaded=False)
