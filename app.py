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


# Main inventory listing
@app.route('/')
@app.route('/dealerships')
def showDealers():
    return "Dealership Listing here"


# Inventory of a specific dealership
@app.route('/dealerships/<int:dealer_id>')
def displayInventory(dealer_id):
    return "Page for Dealer with ID# {}".format(dealer_id)


# Information for a specific car
@app.route('/dealerships/<int:dealer_id>/cars/<int:car_id>')
def displayCar(dealer_id, car_id):
    return "Page for Car # {} at Dealer # {}".format(car_id, dealer_id)


if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0', port = 5000)
