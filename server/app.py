#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    methods= ['GET', 'POST']

    def get(self):
        restaurants = Restaurant.query.all()
        restaurant_list = [
            {
                "id": restaurant.id,
                "name": restaurant.name,
                "address": restaurant.address
            }
            for restaurant in restaurants
        ]
        response = make_response(
            restaurant_list,
            200
        )
        return response
    
class Restaurant_by_id(Resource):
    methods = ['GET', 'DELETE']
    
    def get(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id==id).first()

        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        
        response = make_response(
            restaurant.to_dict(),
            200
        )

        return response
    
    def delete(self, id):
        restaurant = Restaurant.query.filter(Restaurant.id==id).first()

        if not restaurant:
            return {"error": "Restaurant not found"}, 404
        
        db.session.delete(restaurant)
        db.session.commit()

        return '', 204
    
class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()

        pizza_list = [
            {
                "id": pizza.id,
                "name": pizza.name,
                "ingredients": pizza.ingredients
            }
            for pizza in pizzas
        ]

        response = make_response(
            pizza_list,
            200
        )

        return response

class Restaurant_pizzas(Resource):
    def post(self):
        data = request.get_json()

        price = data.get("price")
        pizza_id = data.get("pizza_id")
        restaurant_id = data.get("restaurant_id")

        if not price or not (1 <= price <= 30):
            response_data = {"errors": ["validation errors"]}
            return make_response(response_data, 400)

        pizza = Pizza.query.get(pizza_id)
        if not pizza:
            response_data = {"errors": ["Pizza not found"]}
            return make_response(response_data, 404)

        restaurant = Restaurant.query.get(restaurant_id)
        if not restaurant:
            response_data = {"errors": ["Restaurant not found"]}
            return make_response(response_data, 404)

        new_restaurant_pizza = RestaurantPizza(
            price=price,
            pizza_id=pizza_id,
            restaurant_id=restaurant_id
        )

        db.session.add(new_restaurant_pizza)
        db.session.commit()

        # Prepare response data
        response_data = {
            "id": new_restaurant_pizza.id,
            "pizza": {
                "id": pizza.id,
                "ingredients": pizza.ingredients,
                "name": pizza.name
            },
            "pizza_id": pizza.id,
            "price": new_restaurant_pizza.price,
            "restaurant": {
                "address": restaurant.address,
                "id": restaurant.id,
                "name": restaurant.name
            },
            "restaurant_id": restaurant.id
        }

        return make_response(response_data, 201)


api.add_resource(Restaurants, "/restaurants")
api.add_resource(Restaurant_by_id, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(Restaurant_pizzas, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
