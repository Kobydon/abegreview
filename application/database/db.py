# from application.extensions.extensions import *
# from application.settings.setup import app
# from application.settings.settings import *


# db = SQLAlchemy(app)

# migrate = Migrate(app, db)



# class User(UserMixin,db.Model):
#     id = db.Column(db.Integer,primary_key =True)
#     username = db.Column(db.String(255),unique=True)
#     password = db.Column(db.String(255))
#     admin = db.Column(db.Boolean)
#     created_date = db.Column(DateTime(timezone=True), default=func.now())
    

#     Receive_by  = db.relationship('Notiication', 
#     foreign_keys ='Notiication.receive_by_id',
#     backref = 'reciever',
#     lazy=True
    
#     )


#     Sender_by  = db.relationship('Notiication', 
#     foreign_keys ='Notiication.doctor_id',
#     backref = 'sender',
#     lazy=True
    
#     )
    
    

#     @property
#     def unhashed_password(self):

#          raise AttributeError('cannot view unhased password')

#     @unhashed_password.setter
#     def unhashed_password(self,unhashed_password):
#          self.password = generate_password_hash(unhashed_password )



#     answers_requested  = db.relationship('Ads', 
#     foreign_keys ='Ads.post_by_id',
#     backref = 'seller',
#     lazy=True
    
#     )


#     promo_by  = db.relationship('Promo_request', 
#     foreign_keys ='Promo_request.promo_by_id',
#     backref = 'promoter',
#     lazy=True
    
#     )



# class Notiication(db.Model):

#     id = db.Column(db.Integer,primary_key =True)
#     name = db.Column(db.String(100))
#     message = db.Column(db.String(100))
#     #email = db.Column(db.String(100))
#    # date = db.Column(db.String(100))request.args
#     receive_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))
#     doctor_id = db.Column(db.Integer,db.ForeignKey('user.id'))



# class Ads(db.Model):
   
#     id = db.Column(db.Integer,primary_key =True)
#     condition = db.Column(db.String(255))
#     phone = db.Column(db.String(233))
#     category = db.Column(db.String(255))
#     description = db.Column(db.String(255))
#     brand = db.Column(db.String(255))
#     negotiable = db.Column(db.String(255))
#     price = db.Column(db.String(255))
#     city = db.Column(db.String(255))
#     post_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))
#     image = db.Column(LargeBinary)
#     image_name = db.Column(db.String(255))
#     mimetype =  db.Column(db.String(255))
#     post_on = db.Column(DateTime(timezone=True), default=func.now())
    


# class Promote(db.Model):

#     id = db.Column(db.Integer,primary_key =True)
#     condition = db.Column(db.String(255))
#     phone = db.Column(db.String(233))
#     category = db.Column(db.String(255))
#     description = db.Column(db.String(255))
#     brand = db.Column(db.String(255))
#     negotiable = db.Column(db.String(255))
#     price = db.Column(db.String(255))
#     city = db.Column(db.String(255))
#     promo_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))
#     image = db.Column(LargeBinary)
#     image_name = db.Column(db.String(255))
#     mimetype =  db.Column(db.String(255))
#     post_on = db.Column(DateTime(timezone=True), default=func.now())
#     promoted_on = db.Column(DateTime(timezone=True), default=func.now())

# class  news_letter(db.Model):
#     id = db.Column(db.Integer,primary_key =True)
#     email = db.Column(db.String(200),unique=True)

# class Promo_request(db.Model):

#     id = db.Column(db.Integer,primary_key =True)
#     condition = db.Column(db.String(255))
#     phone = db.Column(db.String(233))
#     category = db.Column(db.String(255))
#     description = db.Column(db.String(255))
#     brand = db.Column(db.String(255))
#     negotiable = db.Column(db.String(255))
#     price = db.Column(db.String(255))
#     city = db.Column(db.String(255))
#     promo_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))
#     image = db.Column(LargeBinary)
#     image_name = db.Column(db.String(255))
#     mimetype =  db.Column(db.String(255))
#     post_on = db.Column(DateTime(timezone=True), default=func.now())
#     #post_by_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    