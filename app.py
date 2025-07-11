import os
from math import ceil 
from flask import Flask, render_template, redirect, url_for, request
from models.database import db
from models import user_model, parking_model 
from models.user_model import *
from models.parking_model import *
from datetime import datetime 

current_dir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "testdb.sqlite3") 
db.init_app(app)
app.app_context().push()
with app.app_context():
    db.create_all() 
    if not Admin.query.first():
        admin = Admin(password="admin")
        db.session.add(admin)
        db.session.commit()

from controllers.admincontorllers import *
from controllers.usercontrollers import *
    
if __name__ == "__main__":
    app.run(debug=True)