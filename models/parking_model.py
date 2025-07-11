from .database import db
from datetime import datetime 

class ParkingLot(db.Model):
    __tablename__ = 'parking_lot'
    id = db.Column(db.Integer, primary_key=True)
    prime_location_name = db.Column(db.String, nullable=False, unique = True)
    price = db.Column(db.Integer,  nullable=False)
    address = db.Column(db.String, nullable=False)
    pincode = db.Column(db.Integer, nullable=False)
    maximum_number_of_spots = db.Column(db.Integer, nullable=False)
    
class ParkingSpot(db.Model):
    __tablename__ = 'parking_spot'
    id = db.Column(db.Integer, primary_key=True)
    lot_id = db.Column(db.Integer, db.ForeignKey("parking_lot.id"), nullable = False)
    status = db.Column(db.Boolean, nullable = False, default=True) # 'True' for available


class ReserveSpot(db.Model):
    __tablename__ = 'reserveparkingspot'
    id = db.Column(db.Integer, primary_key=True)
    spot_id = db.Column(db.Integer,db.ForeignKey('parking_spot.id'), nullable=False)
    user_id = db.Column(db.Integer,db.ForeignKey('users.id'), nullable=False)
    vehicle_no = db.Column(db.String,nullable = False)
    parking_timestamp = db.Column(db.DateTime, nullable=False, default=datetime.now)
    leaving_timestamp = db.Column(db.DateTime)
    cost = db.Column(db.Integer)