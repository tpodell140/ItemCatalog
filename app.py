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
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    inventory = session.query(Car).filter_by(dealer_id = dealer_id)
    return render_template('displayInventory.html', dealership = dealership, inventory = inventory)


# Add a car to inventory
@app.route('/dealership/<int:dealer_id>/cars/addCar', methods = ['GET', 'POST'])
def addCar(dealer_id):
    dealership = session.query(Dealership).filter_by(id = dealer_id).one()
    if request.method == 'POST':
        image = request.form['image']
        if not image:
            image = 'http://luxmimotorssirsa.com/wp-content/plugins/wp-car-manager/assets/images/placeholder-single.png'
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
    return "Page for Car # {} at Dealer # {}".format(car_id, dealer_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
