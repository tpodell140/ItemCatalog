# Dealership Manager App
---
## About

Dealership Manager is a tool to manage inventory of cars at multiple dealerships. The main page is a list of all dealerships contained within the database, and clicking on each dealership will show a listing of cars for sale at those dealerships.

Authenticated users have the ability to add/edit/delete cars from inventory; unauthenticated users may only view dealerships and inventory.

Dealership Manager is written in Python 3.

## Getting Started

The repository contains a demo database that already contains sample dealerships and cars in inventory. To start from scratch, simply delete or rename the `dealerinventory.db` file before running the program.

The program can be started by running the `app.py` file in a terminal. Note that this is a Python 3 program, so the command to start the program will be

```
python3 app.py
```

The server will start and be accessible from `http://localhost:5000`.

Note that you must authenticate before being able to modify or add to the database. This is especially important to remember for users starting with an empty database as no functionality will be accessible without logging in. See "Authentication" below for more details.

## Authentication
Authentication is done using Google Accounts. Users who are not logged in will see a "Sign in with Google" button at the top of every page. Links to manage inventory are not accessible without a successful log-in.

Users who have successfully logged in will see log out buttons at the top of every page.

## Inventory Management

Once authenticated, users may create dealerships on the main page. Once created, the user can edit and delete the dealership from the main page as well.

Clicking on a dealership will show the inventory at that dealership. Clicking on any car shown in inventory will bring up a page showing the details of that car as well as a larger image. Cars in inventory may also be edited and deleted by authenticated users.

For both dealerships and cars, a generic placeholder image will be used if the user does not provide an image at the time of creation.

## JSON endpoints
Information contained in the database may be accessed in a convenient JSON format by using the following endpoints:

### Listing of all Dealerships in the Database:
`/dealerships/JSON` will return the following for each dealership:

```
id
location
logo
make
model
```
Note that id is the id of the dealership.
### Inventory for a Specific Dealer:
The ID of the dealer must be known.

`/dealerships/#/JSON` where # is the ID of the dealership.
Will return:
```
  color
  dealer_id
  id
  image
  make
  mileage
  model
  price
  status
  year
```
for each car in inventory or "No result found" if the id is not in the database.
id is the id of the car, dealer_id is the id of the dealership.
### Information for a specific car:
The id of the car must be known.

`/cars/#/JSON` where # is the ID of the car.
Will return:
```
  color
  dealer_id
  id
  image
  make
  mileage
  model
  price
  status
  year
```
for the requested car or "No result found" if the id is not in the database.
