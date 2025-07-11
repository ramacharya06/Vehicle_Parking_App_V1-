import os
from math import ceil 
from flask import Flask, render_template, redirect, url_for, request
from models.database import db
from models import user_model, parking_model 
from models.user_model import *
from models.parking_model import *
from datetime import datetime 
from flask import current_app as app

@app.route('/',methods=["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        logged = User.query.filter_by(email = email).first()
        if logged != None:
            if logged.password == password:
                return redirect(url_for("userdashboard",user_id = logged.id))
            else:
                return render_template("login.html", wrongpass = True)
        else:
            return render_template("login.html",not_reg_user = True)   
    else:
        return render_template("error.html")

@app.route('/register',methods=["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        address = request.form.get("address")
        pincode = request.form.get("pincode")
        
        if not User.query.filter_by(email = email).first():
            new_entry = User(fullname = name, email=email, password = password, address = address, pincode = pincode)
        
            db.session.add(new_entry)
            db.session.commit()
            return redirect(url_for("login"))
        else:
            return render_template("userexists.html")
    else:
        return render_template("error.html")
        
@app.route("/userdashboard/<user_id>",methods = ["GET","POST"])
def userdashboard(user_id):
    recents = db.session.query(ReserveSpot, ParkingSpot, ParkingLot)\
    .join(ParkingSpot, ReserveSpot.spot_id == ParkingSpot.id)\
    .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)\
    .filter(ReserveSpot.user_id == user_id)\
    .order_by(ReserveSpot.id.desc()).all()
    pincode = User.query.filter_by(id = user_id).first().pincode
    recents = recents[:6]
    if request.method == "POST":
        query = request.form.get("query")
        searches = ParkingLot.query.filter_by(pincode = query).all()
        return render_template("userDashboard.html",user_id = user_id,recents= recents,searches = searches, pincode = query)
    elif request.method == "GET":
        searches = ParkingLot.query.filter_by(pincode = pincode).all()
        return render_template("userDashboard.html",user_id = user_id,recents= recents,pincode = pincode,searches = searches)
    else:
        return render_template("error.html")

@app.route("/userdashboard/<user_id>/<lot_id>",methods = ["GET","POST"])
def bookspot(user_id,lot_id):
    if request.method == "GET":
        spot_id = ParkingSpot.query.filter_by(lot_id = lot_id).filter_by(status = True).first().id
        return render_template('bookparkingspotuser.html',user_id = user_id, lot_id = lot_id, spot_id = spot_id)
    elif request.method == "POST":
        spot_id = request.form.get("spot_id")
        vehicle_no = request.form.get("vehicle_no")
        
        spot_entry = ParkingSpot.query.filter_by(id = int(spot_id)).first()
        spot_entry.status = False
        spot_reserve = ReserveSpot(spot_id=spot_id,user_id=user_id,vehicle_no = vehicle_no)
        db.session.add(spot_reserve)
        db.session.commit()
        return redirect(url_for('userdashboard',user_id=user_id))
    else:
        return render_template("error.html")
    
@app.route("/userdashboard/<id>/release",methods = ["GET","POST"])
def releasespot(id):
    releasedspot = ReserveSpot.query.filter_by(id = id).first()
    spot_id = releasedspot.spot_id
    lot_id = ParkingSpot.query.filter_by(id = spot_id).first().lot_id
    cost_perhr = ParkingLot.query.filter_by(id = lot_id).first().price
    current_time = datetime.now()
    total_time_parked = ceil((current_time - releasedspot.parking_timestamp).seconds/3600)
    if request.method == "GET":
        return render_template('releaseparkingspotuser.html',releasedspot = releasedspot,current_time = current_time,cost = cost_perhr*total_time_parked)
    elif request.method == "POST":
        releasedspot.leaving_timestamp = datetime.strptime(request.form.get("release_time"),'%Y-%m-%d %H:%M:%S.%f')
        ParkingSpot.query.filter_by(id = spot_id).first().status = True
        releasedspot.cost = request.form.get("cost")
        db.session.commit()
        return redirect(url_for('userdashboard',user_id=releasedspot.user_id))
    else:
        return render_template("error.html")
    
@app.route("/userdashboard/<user_id>/summary",methods = ["GET","POST"])
def summary(user_id):
    reserved_parking_lots = db.session.query(ReserveSpot, ParkingSpot, ParkingLot)\
    .join(ParkingSpot, ReserveSpot.spot_id == ParkingSpot.id)\
    .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)\
    .filter(ReserveSpot.user_id == user_id).all()
    lots_used = {}
    for reservedspot in reserved_parking_lots:
        if reservedspot[0].leaving_timestamp != None:
            total_time_parked = (reservedspot[0].leaving_timestamp - reservedspot[0].parking_timestamp).seconds
        else:
            total_time_parked = (datetime.now() - reservedspot[0].parking_timestamp).seconds
        if reservedspot[2] not in lots_used.keys():
            lots_used[reservedspot[2]] = {}
            lots_used[reservedspot[2]]['totalcost']  = 0
            lots_used[reservedspot[2]]['totaltime']  = 0
            
        if reservedspot[0].cost != None:
            lots_used[reservedspot[2]]['totalcost'] += reservedspot[0].cost
        lots_used[reservedspot[2]]['totaltime'] += total_time_parked
        
        
    return render_template('summaryuser.html',lots_used=lots_used,user_id = user_id)

# recents = db.session.query(ReserveSpot, ParkingSpot, ParkingLot)\
#     .join(ParkingSpot, ReserveSpot.spot_id == ParkingSpot.id)\
#     .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id)\
#     .filter(ReserveSpot.user_id == user_id)\
#     .order_by(ReserveSpot.id.desc()).all()

