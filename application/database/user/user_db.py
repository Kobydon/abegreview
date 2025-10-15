# application/database/user/user_db.py
from application.extensions.extensions import *
from application.settings.setup import app
from application.settings.settings import *

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_praetorian import Praetorian
from datetime import datetime

# Initialize extensions (ensure these aren't double-initialized elsewhere)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Association Table for Feedback Tags (Many-to-Many)
feedback_tags = db.Table(
    'feedback_tags',
    db.Column('feedback_id', db.Integer, db.ForeignKey('feedback.id'), primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True)
)

# ---------------------------
# User Model
# ---------------------------
class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)

    premium_listing = db.Column(db.String(200))
    normal_listing = db.Column(db.String(200))
    sponsored_ads = db.Column(db.String(200))
    premium_analytics = db.Column(db.String(200))
    review_contest = db.Column(db.String(200))
    subscription = db.Column(db.String(200))
    last_login = db.Column(db.String(255))
    last_logout = db.Column(db.String(255))

    # relationships
    feedbacks = db.relationship('Feedback', back_populates='user', lazy='select', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', lazy='select', cascade='all, delete-orphan')
    saved_places = db.relationship('SavedPlace', back_populates='user', lazy='select', cascade='all, delete-orphan')

    @property
    def identity(self):
        return self.id

    @property
    def rolenames(self):
        return [self.role]

    @classmethod
    def lookup(cls, username):
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def identify(cls, id):
        return cls.query.get(id)


# ---------------------------
# Restaurant Model
# ---------------------------
class Restaurant(db.Model):
    __tablename__ = 'restaurant'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    created_date = db.Column(db.String(200))
    cuisine = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    image = db.Column(db.Text)  # allow large strings
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    menu = db.Column(db.Text)
    hours = db.Column(db.String(100))
    is_featured = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(100))

    # relationships
    feedbacks = db.relationship('Feedback', back_populates='restaurant', lazy='select', cascade='all, delete-orphan')
    saved_by_users = db.relationship('SavedPlace', back_populates='restaurant', lazy='select', cascade='all, delete-orphan')

    # convenience: average rating property (computed on demand)
    @property
    def average_overall(self):
        if not self.feedbacks:
            return None
        total = sum((f.rating_overall or 0) for f in self.feedbacks)
        return round(total / len(self.feedbacks), 2)


# ---------------------------
# Feedback Model
# ---------------------------
class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # Ratings (1-5). Make new columns nullable=True initially to avoid migration issues.
    rating_food = db.Column(db.Integer, nullable=False, default=3)
    rating_service = db.Column(db.Integer, nullable=False, default=3)
    rating_cleanliness = db.Column(db.Integer, nullable=False, default=3)
    rating_value = db.Column(db.Integer, nullable=True)     # backfill then set not-null if you want
    rating_overall = db.Column(db.Integer, nullable=True)   # backfill then set not-null if you want

    # Extra details
    recommend = db.Column(db.Boolean, nullable=True, default=True)  # nullable True during migration
    comment = db.Column(db.Text, nullable=True)

    anonymous = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    likes = db.Column(db.Integer, default=0)

    # relationships (use back_populates for both sides)
    restaurant = db.relationship('Restaurant', back_populates='feedbacks', lazy='joined')
    user = db.relationship('User', back_populates='feedbacks', lazy='joined')

    # convenience method: validate ratings server-side
    def validate_ratings(self):
        for attr in ('rating_food', 'rating_service', 'rating_cleanliness', 'rating_value', 'rating_overall'):
            val = getattr(self, attr)
            if val is None:
                continue
            if not isinstance(val, int) or val < 1 or val > 5:
                return False, f"{attr} must be integer 1..5"
        return True, None


# ---------------------------
# Reply Model
# ---------------------------
class Reply(db.Model):
    __tablename__ = 'reply'

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.Text)
    is_private = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------
# Subscription Model
# ---------------------------
class Subscription(db.Model):
    __tablename__ = 'subscription'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    description = db.Column(db.String(200))
    price = db.Column(db.String(200))


# ---------------------------
# Tag Model
# ---------------------------
class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))


# ---------------------------
# Media Model
# ---------------------------
class Media(db.Model):
    __tablename__ = 'media'

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'))
    file_path = db.Column(db.String(200))
    media_type = db.Column(db.String(10))  # 'image' or 'video'


# ---------------------------
# MenuItem Model
# ---------------------------
class MenuItem(db.Model):
    __tablename__ = 'menu_item'

    id = db.Column(db.Integer, primary_key=True)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image_base64 = db.Column(db.Text)  # store base64 image


# ---------------------------
# Notification Model
# ---------------------------
class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    message = db.Column(db.String(255))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')


# ---------------------------
# Gamification Model
# ---------------------------
class Gamification(db.Model):
    __tablename__ = 'gamification'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    points = db.Column(db.Integer, default=0)
    badges = db.Column(db.String(255))


# ---------------------------
# Moderation Log Model
# ---------------------------
class ModerationLog(db.Model):
    __tablename__ = 'moderation_log'

    id = db.Column(db.Integer, primary_key=True)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id'))
    action = db.Column(db.String(100))
    reason = db.Column(db.String(255))
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


# ---------------------------
# SavedPlace Model
# ---------------------------
class SavedPlace(db.Model):
    __tablename__ = 'saved_place'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    restaurant_id = db.Column(db.Integer, db.ForeignKey('restaurant.id'), nullable=False)

    restaurant = db.relationship('Restaurant', back_populates='saved_by_users')
    user = db.relationship('User', back_populates='saved_places')
