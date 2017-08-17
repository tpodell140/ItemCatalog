#!/usr/bin/env python3

from flask import Flask, render_template, request, redirect, jsonify, url_for
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base, Dealership, Car

from flask import session as login_session
import random, string

# oAuth import statements
import httplib2
from flask import make_response
import requests


# Connect to database and create session
engine = create_engine('sqlite:///dealerinventory.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession()


# Main inventory listing
@app.route('/')
@app.route('/dealerships')
def showDealers():
    dealerships = session.query(Dealership).all()
    return render_template('dealerships.html', dealerships = dealerships)


# Add a dealership
@app.route('/dealerships/new', methods = ['GET', 'POST'])
def addDealer():
    if request.method == 'POST':
        logo = request.form['logo']
        if not logo:
            logo = 'http://luxmimotorssirsa.com/wp-content/plugins/wp-car-manager/assets/images/placeholder-single.png'
        dealership = Dealership(name = request.form['name'], location = request.form['location'], make = request.form['make'], logo= logo)
        session.add(dealership)
        session.commit()
        return redirect(url_for('showDealers'))
    if request.method == 'GET':
        return render_template('newDealership.html')



# Inventory of a specific dealership
@app.route('/dealerships/<int:dealer_id>/cars')
def displayInventory(dealer_id):
    return "Page for Dealer with ID# {}".format(dealer_id)


# Information for a specific car
@app.route('/dealerships/<int:dealer_id>/cars/<int:car_id>')
def displayCar(dealer_id, car_id):
    return "Page for Car # {} at Dealer # {}".format(car_id, dealer_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
