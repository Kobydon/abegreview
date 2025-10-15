from flask import Blueprint, jsonify, request
from application.extensions.extensions import *
from application.settings.setup import app
from application.database.user.user_db import db, User, Restaurant,Feedback,Subscription,MenuItem,SavedPlace
from datetime import datetime
import flask_praetorian
from datetime import datetime, timedelta
from flask_marshmallow import Marshmallow

restaurant = Blueprint("restaurant", __name__)

ma = Marshmallow(app)

class RestaurantSchema(ma.Schema):
    feedbacks = ma.Nested('FeedbackSchema', many=True)

    class Meta:
        fields = (
            "id", "owner_id", "location", "contact", "cuisine", "name",
            "image", "menu", "hours", "is_featured", "feedbacks", "status",
            "waiter", "quantity", "onetime", "table"
        )
class FeedbackSchema(ma.Schema):
    class Meta:
        fields = (
            "id", "restaurant_id", "user_id",
            "rating_food", "rating_service", "rating_cleanliness",
            "rating_value", "rating_overall", "recommend",
            "comment", "anonymous", "timestamp", "likes"
        )



class SubscriptionSchema(ma.Schema):
            class Meta:
                fields = ("id", "name", "description", "price")

class MenuItemSchema(ma.Schema):
    class Meta:
        fields = ("id", "restaurant_id", "description", "price","name","image_base64")

menu_item_schema = MenuItemSchema()
menu_items_schema = MenuItemSchema(many=True)

scubscription_schema = SubscriptionSchema(many=True)


feedback_schema = FeedbackSchema()
feedbacks_schema = FeedbackSchema(many=True)

restaurant_schema = RestaurantSchema()
restaurants_schema = RestaurantSchema(many=True)



@restaurant.route("/add_restaurant", methods=["POST"])
@flask_praetorian.auth_required
def add_restaurant():
    try:
        name = request.json["name"]
        location = request.json["location"]
        cuisine = request.json.get("cuisine", "")
        contact = request.json.get("contact", "")
        image = request.json.get("image", "")
        hours = request.json.get("hours", "")
        owner_id = flask_praetorian.current_user().id

        restaurant = Restaurant(
            name=name,
            location=location,
            cuisine=cuisine,
            contact=contact,
            owner_id=owner_id,image=image,
            created_date=datetime.now(),
            hours=hours,
            status="Pending"
        )
        db.session.add(restaurant)
        db.session.commit()

        return restaurant_schema.jsonify(restaurant), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@restaurant.route("/restaurants", methods=["GET"])
def get_all_restaurants():
    try:
        all_restaurants = Restaurant.query.all()
        return restaurants_schema.jsonify(all_restaurants), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@restaurant.route("/mine_restaurants", methods=["GET"])
@flask_praetorian.auth_required
def mine_restaurants():
    try:
        all_restaurants = Restaurant.query.filter_by(owner_id=flask_praetorian.current_user().id).all()
        result = restaurants_schema.dump(all_restaurants)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@restaurant.route("/restaurants/<int:id>", methods=["GET"])
def get_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        return restaurant_schema.jsonify(restaurant)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@restaurant.route("/restaurants/<int:id>", methods=["PUT"])
@flask_praetorian.auth_required
def update_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        if restaurant.owner_id != flask_praetorian.current_user().id:
            return jsonify({"error": "Unauthorized access"}), 403

        restaurant.name = request.json.get("name", restaurant.name)
        restaurant.location = request.json.get("location", restaurant.location)
        restaurant.cuisine = request.json.get("cuisine", restaurant.cuisine)
        restaurant.contact = request.json.get("contact", restaurant.contact)

        db.session.commit()
        return restaurant_schema.jsonify(restaurant)
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@restaurant.route("/restaurants/<int:id>", methods=["DELETE"])
@flask_praetorian.auth_required
def delete_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        if restaurant.owner_id != flask_praetorian.current_user().id:
            return jsonify({"error": "Unauthorized access"}), 403

        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({"message": "Restaurant deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@restaurant.route("/restaurants/search", methods=["GET"])
def searchi_restaurants():
    try:
        query = request.args.get("query", "")
        cuisine = request.args.get("cuisine", "")
        location = request.args.get("location", "")

        results = Restaurant.query.filter(
            Restaurant.name.ilike(f"%{query}%"),
            Restaurant.location.ilike(f"%{location}%"),
            Restaurant.cuisine.ilike(f"%{cuisine}%")
        ).all()

        return restaurants_schema.jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



@restaurant.route("/restaurants/<int:id>/claim", methods=["POST"])
@flask_praetorian.auth_required
def claim_restaurant(id):
    try:
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return jsonify({"error": "Restaurant not found"}), 404

        restaurant.owner_id = flask_praetorian.current_user().id
        db.session.commit()
        return jsonify({"message": "Restaurant claimed successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@restaurant.route("/my_restaurant_feedback", methods=["GET"])
@flask_praetorian.auth_required
def my_restaurant_feedback():
    try:
        user = flask_praetorian.current_user()
        # if user.subscription != "premium":
        #     return jsonify({"error": "Upgrade to premium to access feedback."}), 403

        restaurants = Restaurant.query.filter_by(owner_id=user.id).all()
        restaurant_ids = [r.id for r in restaurants]

        feedbacks = Feedback.query.filter(Feedback.restaurant_id.in_(restaurant_ids)).all()

        class FeedbackSchema(ma.Schema):
            class Meta:
                fields = ("id", "restaurant_id", "rating_food", "rating_service",
                          "rating_cleanliness", "comment", "anonymous", "timestamp")

        schema = FeedbackSchema(many=True)
        return jsonify(schema.dump(feedbacks))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@restaurant.route("/get_subcription", methods=["GET"])
@flask_praetorian.auth_required
def get_subcription():
    sub = Subscription.query.all()
    results = scubscription_schema.dump(sub)
    return jsonify(results)

@restaurant.route("/add_feedback", methods=["POST"])
@flask_praetorian.auth_required
def add_feedback():
    try:
        data = request.get_json()
        user_id = flask_praetorian.current_user().id
        feedback = Feedback(
            user_id=user_id,
            restaurant_id=data["restaurant_id"],
            rating_food=data["rating_food"],
            rating_service=data["rating_service"],
            rating_cleanliness=data["rating_cleanliness"],
            comment=data.get("comment", ""),
            anonymous=data.get("anonymous", False),
            timestamp=datetime.utcnow()
        )
        db.session.add(feedback)
        db.session.commit()
        return feedback_schema.jsonify(feedback), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# 📥 Get All Feedbacks for My Restaurant
@restaurant.route("/my_restaurant_feedback", methods=["GET"])
@flask_praetorian.auth_required
def get_my_feedbacks():
    try:
        user = flask_praetorian.current_user()
        my_restaurant = Restaurant.query.filter_by(owner_id=user.id).first()
        if not my_restaurant:
            return jsonify([])

        feedbacks = Feedback.query.filter_by(restaurant_id=my_restaurant.id).order_by(Feedback.timestamp.desc()).all()
        return feedbacks_schema.jsonify(feedbacks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ✏️ Update Feedback
@restaurant.route("/update_feedback/<int:feedback_id>", methods=["PUT"])
@flask_praetorian.auth_required
def update_feedback(feedback_id):
    try:
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({"error": "Feedback not found"}), 404

        user = flask_praetorian.current_user()
        if feedback.user_id != user.id:
            return jsonify({"error": "Not authorized"}), 403

        data = request.get_json()
        feedback.rating_food = data.get("rating_food", feedback.rating_food)
        feedback.rating_service = data.get("rating_service", feedback.rating_service)
        feedback.rating_cleanliness = data.get("rating_cleanliness", feedback.rating_cleanliness)
        feedback.comment = data.get("comment", feedback.comment)
        feedback.anonymous = data.get("anonymous", feedback.anonymous)

        db.session.commit()
        return feedback_schema.jsonify(feedback), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ❌ Delete Feedback
@restaurant.route("/delete_feedback/<int:feedback_id>", methods=["DELETE"])
@flask_praetorian.auth_required
def delete_feedback(feedback_id):
    try:
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({"error": "Feedback not found"}), 404

        user = flask_praetorian.current_user()
        if feedback.user_id != user.id:
            return jsonify({"error": "Not authorized"}), 403

        db.session.delete(feedback)
        db.session.commit()
        return jsonify({"message": "Feedback deleted"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    

from sqlalchemy import extract, func

@restaurant.route("/monthly_review_stats", methods=["GET"])
@flask_praetorian.auth_required
def monthly_review_stats():
    try:
        user = flask_praetorian.current_user()
        restaurants = Restaurant.query.filter_by(owner_id=user.id).all()
        restaurant_ids = [r.id for r in restaurants]

        # Group feedbacks by month and count or average ratings
        stats = (
            db.session.query(
                extract('month', Feedback.timestamp).label('month'),
                func.count(Feedback.id).label('review_count'),
                func.avg(Feedback.rating_food).label('avg_food'),
                func.avg(Feedback.rating_service).label('avg_service'),
                func.avg(Feedback.rating_cleanliness).label('avg_cleanliness')
            )
            .filter(Feedback.restaurant_id.in_(restaurant_ids))
            .group_by(extract('month', Feedback.timestamp))
            .all()
        )

        result = [
            {
                "month": int(month),
                "review_count": review_count,
                "avg_food": float(avg_food or 0),
                "avg_service": float(avg_service or 0),
                "avg_cleanliness": float(avg_cleanliness or 0),
            }
            for month, review_count, avg_food, avg_service, avg_cleanliness in stats
        ]
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@restaurant.route("/restaurant/<int:restaurant_id>/menu", methods=["GET"])
@flask_praetorian.auth_required
def get_menu_items(restaurant_id):
    items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return jsonify(menu_items_schema.dump(items))


@restaurant.route("/restaurant/menu", methods=["POST"])
@flask_praetorian.auth_required
def add_menu_item():
    user=flask_praetorian.current_user()
    restaurant = Restaurant.query.filter_by(owner_id=flask_praetorian.current_user().id).first()
    if user.id != restaurant.owner_id :
    # or user.normal_listing != 'yes':
        return jsonify({"message": "Access denied"}), 403

    data = request.get_json()
    item = MenuItem(
        restaurant_id=restaurant.id,
        name=data["name"],
        description=data.get("description", ""),
        price=data["price"],
        image_base64=data.get("image_base64", "")
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(menu_item_schema.dump(item))


@restaurant.route("/restaurant/menu/<int:item_id>", methods=["PUT"])
@flask_praetorian.auth_required
def edit_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    user=flask_praetorian.current_user()

    data = request.get_json()
    item.name = data.get("name", item.name)
    item.description = data.get("description", item.description)
    item.price = data.get("price", item.price)
    item.image_base64 = data.get("image_base64", item.image_base64)
    db.session.commit()
    return jsonify(menu_item_schema.dump(item))


@restaurant.route("/restaurant/menu/<int:item_id>", methods=["DELETE"])
@flask_praetorian.auth_required
def delete_menu_item(item_id):
    item = MenuItem.query.get_or_404(item_id)
    user=flask_praetorian.current_user()
    
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item deleted successfully"})

@restaurant.route('/search_restaurants', methods=['POST'])


@flask_praetorian.auth_required
def search_restaurants():
    data = request.get_json()
    query = data.get('query', '').strip().lower()
    
    if not query:
        return jsonify([])

    search = Restaurant.query.filter(
        (Restaurant.name.ilike(f"%{query}%")) |
        (Restaurant.location.ilike(f"%{query}%")) |
        (Restaurant.cuisine.ilike(f"%{query}%"))
    ).all()

    results = restaurants_schema.dump(search)
    return jsonify(results)


@restaurant.route('/restaurant/<int:id>', methods=['GET'])
def get_restaurants(id):
    restaurant = Restaurant.query.get_or_404(id)
    schema = RestaurantSchema()
    return schema.dump(restaurant)


@restaurant.route('/restaurant/save/<int:restaurant_id>', methods=['POST'])
@flask_praetorian.auth_required
def save_restaurant(restaurant_id):
    user_id = flask_praetorian.current_user().id
    existing = SavedPlace.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if existing:
        return jsonify({'message': 'Already saved'}), 200

    saved = SavedPlace(user_id=user_id, restaurant_id=restaurant_id)
    db.session.add(saved)
    db.session.commit()
    return jsonify({'message': 'Saved successfully'}), 201

@restaurant.route('/restaurant/saved', methods=['GET'])
@flask_praetorian.auth_required
def get_saved_restaurants():
    user_id = flask_praetorian.current_user().id
    saved = SavedPlace.query.filter_by(user_id=user_id).all()
    result = [
        RestaurantSchema().dump(s.restaurant) for s in saved
    ]
    return jsonify(result)

@restaurant.route('/restaurant/remove_saved/<int:restaurant_id>', methods=['DELETE'])
@flask_praetorian.auth_required
def remove_saved_restaurant(restaurant_id):
    user_id = flask_praetorian.current_user().id
    saved = SavedPlace.query.filter_by(user_id=user_id, restaurant_id=restaurant_id).first()
    if not saved:
        return jsonify({'message': 'Not found'}), 404

    db.session.delete(saved)
    db.session.commit()
    return jsonify({'message': 'Removed from saved places'}), 200



@restaurant.route("/rate_property", methods=["POST"])
@flask_praetorian.auth_required
def rate_property():
    data = request.get_json()

    restaurant_id = data.get("restaurant_id")
    rating_food = data.get("rating_food")            # Food Quality
    rating_service = data.get("rating_service")      # Service
    rating_cleanliness = data.get("rating_cleanliness")  # Cleanliness & Ambience
    rating_value = data.get("rating_value")          # Value for Money
    rating_overall = data.get("rating_overall")      # Overall Stars

    recommend = data.get("recommend", True)          # Would recommend? Yes/No
    comment = data.get("comment", "")
    anonymous = data.get("anonymous", False)

    # Validate all ratings 1–5
    for r in [rating_food, rating_service, rating_cleanliness, rating_value, rating_overall]:
        if not isinstance(r, int) or r < 1 or r > 5:
            return jsonify({"error": "All ratings must be integers between 1 and 5"}), 400

    feedback = Feedback(
        user_id=flask_praetorian.current_user().id,
        restaurant_id=restaurant_id,
        rating_food=rating_food,
        rating_service=rating_service,
        rating_cleanliness=rating_cleanliness,
        rating_value=rating_value,
        rating_overall=rating_overall,
        recommend=recommend,
        comment=comment,
        anonymous=anonymous,
        timestamp=datetime.utcnow()
    )

    db.session.add(feedback)
    db.session.commit()

    return feedback_schema.jsonify(feedback), 201



@restaurant.route("/get_menu/<int:restaurant_id>", methods=["GET"])
def get_menu(restaurant_id):
    menu_items = MenuItem.query.filter_by(restaurant_id=restaurant_id).all()
    return menu_items_schema.jsonify(menu_items)

@restaurant.route('/analytics/premium/<int:restaurant_id>', methods=['GET'])
@flask_praetorian.auth_required
def get_premium_analytics(restaurant_id):
    try:
        # Get date range from query parameters
        days = request.args.get('days', default=30, type=int)
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Base query for the restaurant
        base_query = Feedback.query.filter(
            Feedback.restaurant_id == restaurant_id,
            Feedback.timestamp >= start_date
        )
        
        # 1. Percentage of users rating service low (1–2 stars)
        total_feedbacks = base_query.count()
        low_service_feedbacks = base_query.filter(
            Feedback.rating_service.in_([1, 2])
        ).count()
        
        low_service_percentage = (low_service_feedbacks / total_feedbacks * 100) if total_feedbacks > 0 else 0
        
        # 2. Suggestions collected (comments)
        suggestions = base_query.filter(
            Feedback.comment.isnot(None),
            Feedback.comment != ''
        ).with_entities(
            Feedback.comment,
            Feedback.timestamp,
            Feedback.rating_service,
            Feedback.rating_overall
        ).order_by(Feedback.timestamp.desc()).all()
        
        # 3. Time-based trends (convert SQL date string to ISO manually)
        daily_trends = db.session.query(
            func.date(Feedback.timestamp).label('date'),
            func.avg(Feedback.rating_service).label('avg_service'),
            func.avg(Feedback.rating_food).label('avg_food'),
            func.avg(Feedback.rating_cleanliness).label('avg_cleanliness'),
            func.avg(Feedback.rating_overall).label('avg_overall'),
            func.count(Feedback.id).label('feedback_count')
        ).filter(
            Feedback.restaurant_id == restaurant_id,
            Feedback.timestamp >= start_date
        ).group_by(
            func.date(Feedback.timestamp)
        ).order_by(
            func.date(Feedback.timestamp)
        ).all()
        
        # 4. Rating distribution for service
        service_distribution = db.session.query(
            Feedback.rating_service,
            func.count(Feedback.id).label('count')
        ).filter(
            Feedback.restaurant_id == restaurant_id,
            Feedback.timestamp >= start_date
        ).group_by(
            Feedback.rating_service
        ).order_by(
            Feedback.rating_service
        ).all()
        
        # 5. Overall statistics
        avg_ratings = db.session.query(
            func.avg(Feedback.rating_service).label('avg_service'),
            func.avg(Feedback.rating_food).label('avg_food'),
            func.avg(Feedback.rating_cleanliness).label('avg_cleanliness'),
            func.avg(Feedback.rating_overall).label('avg_overall')
        ).filter(
            Feedback.restaurant_id == restaurant_id,
            Feedback.timestamp >= start_date
        ).first()
        
        # 6. Recommendation rate
        recommend_stats = db.session.query(
            Feedback.recommend,
            func.count(Feedback.id).label('count')
        ).filter(
            Feedback.restaurant_id == restaurant_id,
            Feedback.timestamp >= start_date,
            Feedback.recommend.isnot(None)
        ).group_by(
            Feedback.recommend
        ).all()
        
        total_recommendations = sum(stat.count for stat in recommend_stats if stat.recommend)
        total_with_recommendation = sum(stat.count for stat in recommend_stats)
        recommendation_rate = (total_recommendations / total_with_recommendation * 100) if total_with_recommendation > 0 else 0
        
        # Prepare response
        return jsonify({
            'success': True,
            'analytics': {
                'summary': {
                    'total_feedbacks': total_feedbacks,
                    'low_service_percentage': round(low_service_percentage, 2),
                    'recommendation_rate': round(recommendation_rate, 2),
                    'average_ratings': {
                        'service': round(avg_ratings.avg_service or 0, 2),
                        'food': round(avg_ratings.avg_food or 0, 2),
                        'cleanliness': round(avg_ratings.avg_cleanliness or 0, 2),
                        'overall': round(avg_ratings.avg_overall or 0, 2)
                    }
                },
                'suggestions': [
                    {
                        'comment': suggestion.comment,
                        'timestamp': suggestion.timestamp.isoformat() if isinstance(suggestion.timestamp, datetime) else str(suggestion.timestamp),
                        'service_rating': suggestion.rating_service,
                        'overall_rating': suggestion.rating_overall
                    } for suggestion in suggestions
                ],
                'time_trends': [
                    {
                        'date': str(trend.date),  # FIX: directly convert to string
                        'avg_service': float(trend.avg_service or 0),
                        'avg_food': float(trend.avg_food or 0),
                        'avg_cleanliness': float(trend.avg_cleanliness or 0),
                        'avg_overall': float(trend.avg_overall or 0),
                        'feedback_count': trend.feedback_count
                    } for trend in daily_trends
                ],
                'service_distribution': [
                    {
                        'rating': dist.rating_service,
                        'count': dist.count,
                        'percentage': round((dist.count / total_feedbacks * 100), 2) if total_feedbacks > 0 else 0
                    } for dist in service_distribution
                ]
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
