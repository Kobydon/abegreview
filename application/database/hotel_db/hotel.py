from application.extensions.extensions import *
from application.settings.setup import app
from application.settings.settings import *
from application.database.user.user_db import User

#========  Room database =================#
db = SQLAlchemy(app)






class Room(db.Model):
   
    id = db.Column(db.Integer,primary_key =True)
    room_number = db.Column(db.String(200))
    room_type = db.Column(db.String(255))
    floor = db.Column(db.String(233))
    duration = db.Column(db.String(255))
    occupied_by = db.Column(db.String(255),nullable=True)
    session = db.Column(db.String(255))
    type = db.Column(db.String(255))
    maintanace_state = db.Column(db.String(255),nullable=True)
    occupancy_state = db.Column(db.String(255))
    assignee = db.Column(db.String(255))
    task = db.Column(db.String(10))
    picture_one = db.Column(LargeBinary)
    picture_two = db.Column(LargeBinary)
    picture_three = db.Column(LargeBinary)
    status = db.Column(db.String(100),nullable=True)
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))


class Room_Type(db.Model):
   
    id = db.Column(db.Integer,primary_key =True)
   
    room_type = db.Column(db.String(255))
    base_query = db.Column(db.String(233))
    kids_occupancy = db.Column(db.String(255))
    extral_bed_price = db.Column(db.String(255),nullable=True)
    bace_price= db.Column(db.String(255))
    type = db.Column(db.String(255))
    aminities = db.Column(db.String(255),nullable = True)
    description = db.Column(db.String(200))
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))


    
#========  Guest database =================#

class Guest(db.Model):
   
    id = db.Column(db.Integer,primary_key =True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(233))
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    dob = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    room = db.Column(db.String(255))
    room_number = db.Column(db.String(255))
    country = db.Column(db.String(255))

    region = db.Column(db.String(255))
    city = db.Column(db.String(233))
    id_type = db.Column(db.String(255))
    id_number = db.Column(db.String(255))
    address = db.Column(db.String(255))
    id_photo = db.Column(db.String(255))
    remark = db.Column(db.String(255))
    id_number = db.Column(db.String(255))
    arrival_date = db.Column(db.String(255))
    checkout_date = db.Column(db.String(255))
    work = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    created_date = db.Column(DateTime(timezone=True), default=func.now())
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))


    
#========  Employee database =================#
  
class Employee(db.Model):
   
    id = db.Column(db.Integer,primary_key =True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(233))
    username = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    dob = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    department = db.Column(db.String(233))
    designation = db.Column(db.String(255))
    country = db.Column(db.String(255))
    region = db.Column(db.String(255))
    phone_number = db.Column(db.String(255))
    city = db.Column(db.String(255))
    gender = db.Column(db.String(233))
    address = db.Column(db.String(255))
    id_type = db.Column(db.String(255))
    id_number = db.Column(db.String(255))
    id_photo = db.Column(LargeBinary)

    date_of_join = db.Column(db.String(255))
    remark = db.Column(db.String(233))
    salary = db.Column(db.String(255))
    session = db.Column(db.String(255))
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    created_date = db.Column(DateTime(timezone=True), default=func.now())
    
  


    
#========  Payment database =================#
  
class Payment(db.Model):
   
    name = db.Column(db.Integer,primary_key =True)
    amount = db.Column(db.String(255))
    duration = db.Column(db.String(233))
    floor = db.Column(db.String(255))
    method = db.Column(db.String(255))
    room = db.Column(db.String(255))
    number_of_night = db.Column(db.String(255))
    payment_date = db.Column(db.String(255))
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))
   
    
  

    
#========  Todo database =================#
  
class Todo(db.Model):
   
    name = db.Column(db.Integer,primary_key =True)
    time = db.Column(db.String(255))
    Worker = db.Column(db.String(233))
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    
    
  

class Reservation(db.Model):
   
    id = db.Column(db.Integer,primary_key =True)
    guestname = db.Column(db.String(255))
    reservation_type = db.Column(db.String(233))
    country = db.Column(db.String(255))
    guest_language = db.Column(db.String(255))
    purpose = db.Column(db.String(255))
    night = db.Column(db.String(255))
    arrival_date = db.Column(db.String(255))
    checkin_time = db.Column(db.String(233))
    checkout_time = db.Column(db.String(255))
    number_of_adult = db.Column(db.String(255))
    number_of_children = db.Column(db.String(255))
    room_type = db.Column(db.String(255))
    room_number = db.Column(db.String(255))
    rate = db.Column(db.String(233))
    rate_amount = db.Column(db.String(255))
    discount_type = db.Column(db.String(255))
    discount_value = db.Column(db.String(255))
  

    payment_method = db.Column(db.String(255))
    status = db.Column(db.String(233))
 
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    created_date = db.Column(DateTime(timezone=True), default=func.now())


class Group_Reservation(db.Model):
   
    id = db.Column(db.Integer,primary_key =True)
    guestname = db.Column(db.String(255))
    reservation_type = db.Column(db.String(233))
    country = db.Column(db.String(255))
    guest_language = db.Column(db.String(255))
    purpose = db.Column(db.String(255))
    night = db.Column(db.String(255))
    arrival_date = db.Column(db.String(255))
    checkin_time = db.Column(db.String(233))
    checkout_time = db.Column(db.String(255))
    number_of_adult = db.Column(db.String(255))
    number_of_children = db.Column(db.String(255))
    room_type = db.Column(db.String(255))
    room_number = db.Column(db.String(255))
    rate = db.Column(db.String(233))
    rate_amount = db.Column(db.String(255))
    discount_type = db.Column(db.String(255))
    discount_value = db.Column(db.String(255))
  

    payment_method = db.Column(db.String(255))
    status = db.Column(db.String(233))
 
    created_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))

    created_date = db.Column(DateTime(timezone=True), default=func.now())

    