#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Dealership, Car, User

from flask import session as login_session
import random, string

from oauth2client import client, crypt
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
# Connect to database and create session
engine = create_engine('sqlite:///dealerinventory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()


# Create a state token to prevent request forgery.
# Store it in the session for later validation.
@app.route('/login/')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.
        digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['POST'])
def gconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json',scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    #Verify that the access token is used for the intended user:
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Verify that the access token is valid for this app:
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps("Token's client ID doesn't match given client ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    #Check to see if user is already logged in:
    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps("Current user is already connected"), 200)
        response.headers['Content-Type'] = 'application/json'

    #Store the access tokens in the session for later use:
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    #Get user info:
    userinfo_url = "https://www.googleapis.com/userinfo/v2/me"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = json.loads(answer.text)

    login_session['username'] = data["name"]
    login_session['picture'] = data["picture"]
    print(data)
    login_session['email'] = data["email"]
    login_session['provider'] = 'google'


    # See if user exists, if not create new user
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id


    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 75px; height: 75px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output



@app.route('/gdisconnect/')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print ('Access Token is None')
        response = make_response(json.dumps('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)
    if result['status'] == '200':
        # del login_session['username']
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have successfullly been logged out.")
        return redirect(url_for('showDealers'))
    else:
        response = make_response(json.dumps('Failed to revoke token for given user'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


# Main inventory listing
@app.route('/')
@app.route('/dealerships')
def showDealers():
    state = checkState()
    dealerships = session.query(Dealership).all()
    return render_template('dealerships.html', dealerships = dealerships, STATE=state)


# Add a dealership
@app.route('/dealerships/new', methods = ['GET', 'POST'])
def addDealer():
    if request.method == 'POST':
        logo = request.form['logo']
        if not logo:
            logo = 'https://oncarrot.com/app/themes/oncarrot/images/property_placeholder.jpg'
        dealership = Dealership(name = request.form['name'], location = request.form['location'], make = request.form['make'], logo= logo)
        session.add(dealership)
        session.commit()
        return redirect(url_for('showDealers'))
    if request.method == 'GET':
        return render_template('newDealership.html')


# Edit Dealership Information
@app.route('/dealerships/<int:dealer_id>/edit', methods = ['GET', 'POST'])
def editDealer(dealer_id):
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    if request.method == 'POST':
        dealership.name = request.form['name']
        dealership.location = request.form['location']
        dealership.make = request.form['make']
        dealership.logo = request.form['logo']
        session.add(dealership)
        session.commit()
        return redirect(url_for('showDealers'))
    if request.method == 'GET':
        return render_template('editDealership.html', dealership = dealership)


# Delete a Dealership
@app.route('/dealerships/<int:dealer_id>/delete', methods = ['GET', 'POST'])
def deleteDealer(dealer_id):
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    if request.method == 'POST':
        session.delete(dealership)
        session.commit()
        return redirect(url_for('showDealers'))
    if request.method == 'GET':
        return render_template('deleteDealership.html', dealership = dealership)


# Inventory of a specific dealership
@app.route('/dealerships/<int:dealer_id>/cars')
def displayInventory(dealer_id):
    state = checkState()
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    inventory = session.query(Car).filter_by(dealer_id = dealer_id)
    return render_template('displayInventory.html', dealership = dealership, inventory = inventory, STATE=state)


# Add a car to inventory
@app.route('/dealerships/<int:dealer_id>/cars/addCar', methods = ['GET', 'POST'])
def addCar(dealer_id):
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    if request.method == 'POST':
        image = request.form['image']
        if not image:
            image = 'http://myclassicgarage.com/assets/image_placeholder_low_res.png'
        newCar = Car(
                    status = request.form['status'],
                    make = request.form['make'],
                    model = request.form['model'],
                    year = request.form['year'],
                    price = request.form['price'],
                    image = image,
                    mileage = request.form['mileage'],
                    color = request.form['color'],
                    dealer_id = dealership.id
                    )
        session.add(newCar)
        session.commit()
        return redirect(url_for('displayInventory', dealer_id = dealership.id))
    if request.method == 'GET':
        return render_template('addCar.html', dealership = dealership)


# Information for a specific car
@app.route('/dealerships/<int:dealer_id>/cars/<int:car_id>')
def displayCar(dealer_id, car_id):
    state = checkState()
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    car = session.query(Car).filter_by(id = car_id).one()
    return render_template('displayCar.html', dealership = dealership, car = car, STATE=state)


# Edit Information for a specific car
@app.route('/dealerships/<int:dealer_id>/cars/<int:car_id>/edit', methods = ['GET', 'POST'])
def editCar(dealer_id, car_id):
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    car = session.query(Car).filter_by(id = car_id).one()
    if request.method == 'POST':
        car.make = request.form['make']
        car.model = request.form['model']
        car.year = request.form['year']
        car.price = request.form['price']
        car.image = request.form['image']
        car.mileage = request.form['mileage']
        car.color = request.form['color']
        session.commit()
        return redirect(url_for('displayInventory', dealer_id = dealership.id))
    if request.method == 'GET':
        return render_template('editCar.html', dealership = dealership, car = car)


# Delete a car from inventory
@app.route('/dealerships/<int:dealer_id>/cars/<int:car_id>/delete', methods = ['GET', 'POST'])
def deleteCar(dealer_id, car_id):
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    car = session.query(Car).filter_by(id = car_id).one()
    if request.method == 'POST':
        session.delete(car)
        session.commit()
        return redirect(url_for('displayInventory', dealer_id = dealership.id))
    if request.method == 'GET':
        return render_template('deleteCar.html', dealership = dealership, car = car)


# JSON endpoints
@app.route('/dealerships/JSON')
def dealershipJSON():
    dealerships = session.query(Dealership).all()
    return jsonify(dealerships = [dealer.serialize for dealer in dealerships])


@app.route('/dealerships/<int:dealer_id>/cars/JSON')
def dealerInventoryJSON(dealer_id):
    cars = session.query(Car).filter_by(dealer_id = dealer_id).all()
    return jsonify(cars = [car.serialize for car in cars])


@app.route('/dealerships/<int:dealer_id>/cars/<int:car_id>/JSON')
def carJSON(dealer_id, car_id):
    car = session.query(Car).filter_by(id = car_id).one()
    return jsonify(car = car.serialize)


def checkState():
    # Get state if user is already logged in, otherwise create state
    if 'username' in login_session:
        state = login_session['state']
    else:
        state = ''.join(random.choice(string.ascii_uppercase + string.
            digits) for x in range(32))
        login_session['state'] = state
    return state


def getUserID(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None


def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user



def createUser(login_session):
    newUser  = User(name =login_session['username'],
        email = login_session['email'], picture = login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    return user.id



if __name__ == '__main__':
    app.secret_key = "Super_secret_key"
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
