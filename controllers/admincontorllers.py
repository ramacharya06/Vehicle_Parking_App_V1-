import os
from math import ceil 
from flask import Flask, render_template, redirect, url_for, request
from models.database import db
from models import user_model, parking_model 
from models.user_model import *
from models.parking_model import *
from datetime import datetime 
from flask import current_app as app

@app.route("/admin",methods = ["GET","POST"])
def adminlogin():
    if request.method == "GET":
        return render_template("adminlogin.html")
    elif request.method == "POST":
        password = request.form.get("password")
        
        if password == Admin.query.first().password:
            return redirect(url_for("admindashboard"))
        else:
            return render_template("adminlogin.html",worngpass = True)
    else:
        return render_template("error.html")
    
@app.route("/admin/dashboard")
def admindashboard():
    parking_lots = ParkingLot.query.all()
    parking_spots = dict()
    for lot in parking_lots:
        spots = ParkingSpot.query.filter_by(lot_id = lot.id).all()
        parking_spots[lot] = dict()
        parking_spots[lot]['occupiedspots'] = len([i.id for i in spots if i.status == False ])
        parking_spots[lot]['totalspots'] = lot.maximum_number_of_spots
        parking_spots[lot]['spots'] = spots
    return render_template("adminDashboard.html",parking_lots=parking_lots,parking_spots = parking_spots)
    
    
@app.route("/admin/reg_users")
def adminregistered_user():
    users = User.query.all()
    return render_template("registereduserslistadmin.html",users = users)
        
@app.route("/admin/add_lot", methods = ["GET","POST"])
def adminadd_lot():
    if request.method == "GET":
        return render_template("createparkinglotadmin.html")
    elif request.method == "POST":
        prime_location_name = request.form.get("prime_location_name")
        address  = request.form.get("address")
        pincode = request.form.get("pincode")
        price = request.form.get("price")
        maximum_number_of_spots = request.form.get("maximum_number_of_spots")
        if ParkingLot.query.filter_by(prime_location_name = prime_location_name).first() == None:
            new_lot = ParkingLot(prime_location_name = prime_location_name,address = address, pincode = pincode, price = price, maximum_number_of_spots = maximum_number_of_spots)
            db.session.add(new_lot)
            db.session.flush()
            new_spots = []
            for i in range(int(maximum_number_of_spots)):
                new_spot = ParkingSpot(lot_id = new_lot.id)
                new_spots.append(new_spot)
            db.session.add_all(new_spots)
            db.session.commit()
            return redirect(url_for("admindashboard"))
        else:
            return render_template("createparkinglotadmin.html",exist = True)            
    else:
        return render_template("error.html")


@app.route("/admin/edit_lot/<lot_id>", methods = ["GET","POST"])
def adminedit_lot(lot_id):
    if request.method == "GET":
        lot = ParkingLot.query.filter_by(id=lot_id).first()
        
        return render_template("editparkinglotadmin.html",prime_location_name = lot.prime_location_name,address  = lot.address,pincode = lot.pincode,price = lot.price,maximum_number_of_spots = lot.maximum_number_of_spots,lot_id = lot_id)
    elif request.method == "POST":
        prime_location_name = request.form.get("prime_location_name")
        address  = request.form.get("address")
        pincode = request.form.get("pincode")
        price = request.form.get("price")
        maximum_number_of_spots = request.form.get("maximum_number_of_spots")
        update_lot = ParkingLot.query.filter_by(id = lot_id).first()
        if ParkingLot.query.filter_by(prime_location_name = prime_location_name).first() and update_lot.prime_location_name != prime_location_name:
            return render_template("editparkinglotadmin.html",use_diff_loc = True) 
        update_lot.prime_location_name = prime_location_name  
        update_lot.address = address 
        update_lot.pincode = pincode
        update_lot.price = price
        spots = ParkingSpot.query.filter_by(lot_id = lot_id)
        occupiedspots = len([i.id for i in spots if i.status == False ])
        if int(maximum_number_of_spots)-occupiedspots <0:
            return render_template("editparkinglotadmin.html",max_usr = True)
        else:
            new_spots_required = int(maximum_number_of_spots) - int(update_lot.maximum_number_of_spots)
            # print(new_spots_required,update_lot.maximum_number_of_spots,maximum_number_of_spots)
            update_lot.maximum_number_of_spots = maximum_number_of_spots 
            if new_spots_required <0:
                for i in range(abs(int(new_spots_required))):
                    spot = ParkingSpot.query.filter_by(lot_id = lot_id).filter_by(status = True).first()
                    db.session.delete(spot)
            elif new_spots_required>0:
                for i in range(int(new_spots_required)):
                    spot = ParkingSpot(lot_id = lot_id)
                    db.session.add(spot)
            db.session.commit()
            return redirect(url_for("admindashboard"))          
    else:
        return render_template("error.html")
    
    
@app.route("/admin/view_spot_details/<spot_id>")
def adminview_spot_details(spot_id):
    spot = ParkingSpot.query.filter_by(id=spot_id).first()
    return render_template("viewspotdetailsadmin.html",spot = spot)


@app.route("/admin/view_spot_details/<spot_id>/view_details")
def adminoccupied_spot_details(spot_id):
    reservedspot = ReserveSpot.query.filter_by(spot_id = spot_id).first()
    cost_perhr = ParkingLot.query.filter_by(id = spot_id).first().price
    current_time = datetime.now()
    total_time_parked = ceil((current_time - reservedspot.parking_timestamp).seconds/3600)
    return render_template('occupiedSpotDetailsAdmin.html',reservedspot = reservedspot,cost = cost_perhr*total_time_parked)


@app.route("/admin/summary")
def adminsummary():
    spots = ParkingLot.query.all()
    most_proficable_lots = ParkingLot.query.order_by((ParkingLot.price*ParkingLot.maximum_number_of_spots).desc()).all()
    lots = db.session.query(ReserveSpot, ParkingSpot, ParkingLot)\
    .join(ParkingSpot, ReserveSpot.spot_id == ParkingSpot.id)\
    .join(ParkingLot, ParkingSpot.lot_id == ParkingLot.id).all()
    parking_lots_occupied = {}
    for reservedspot in lots:
        if reservedspot[2] not in parking_lots_occupied.keys():
            parking_lots_occupied [reservedspot[2]] = 0
        parking_lots_occupied [reservedspot[2]] +=1
    parking_lots_occupied = dict(sorted(parking_lots_occupied.items(), key=lambda item: item[1],reverse = True))
    return render_template('summaryadmin.html', parking_lots_occupied = parking_lots_occupied, most_proficable_lots = most_proficable_lots)
    
@app.route("/admin/delete/<lot_id>")
def admindelete(lot_id):
    delete_lot = ParkingLot.query.filter_by(id = lot_id).first()
    for spot in ParkingSpot.query.filter_by(lot_id=lot_id).all():
        ReserveSpot.query.filter_by(spot_id=spot.id).delete()
        db.session.delete(spot)
    db.session.delete(delete_lot)
    db.session.commit()
    return redirect(url_for('admindashboard'))
    
    