"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, json
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

#USER ENDPOINT
@app.route('/users', methods=['GET'])
def get_all_user():
    users= User.query.all()
    users_list = list(map(lambda obj: obj.serialize(), users))
    response = {
        "status": "ok",
        "response": users_list
    }
    return jsonify(response), 200

#PLANET ENDPOINTS
@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets= Planet.query.all()
    planets_list = list(map(lambda obj: obj.serialize(), planets))
    response = {
        "status": "ok",
        "response": planets_list
    }
    return jsonify(response), 200

@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet= Planet.query.get(planet_id)
    return jsonify(planet.serialize()), 200


#CHARACTER ENDPOINTS
@app.route('/characters', methods=['GET'])
def get_all_characters():
    characters= Character.query.all()
    characters_list = list(map(lambda obj: obj.serialize(), characters))
    response = {
        "status": "ok",
        "response": characters_list
    }
    print(response)
    return jsonify(response), 200

@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character= Character.query.get(character_id)
    return jsonify(character.serialize()), 200


#FAVORITE ENDPOINTS
@app.route('/addFavorite', methods=['POST'])
def add_favorite():
    body = json.loads(request.data)
    favorite_model = Favorite(user_id = body["user_id"],planet_id = body["planet_id"],character_id = body["character_id"])
    db.session.add(favorite_model)
    db.session.commit()
    return jsonify("msj"),200

@app.route('/favorite/<int:_user_id>', methods=['GET'])
def get_favorties(_user_id):
    favorites= Favorite.query.filter_by(user_id=_user_id).all()
    favoritess= Favorite.query.join(User).add_columns(Planet.name,Character.name,User.name).filter_by(id=_user_id).join(Planet).join(Character).all()
    favorites_list= list(map(lambda obj: obj.serialize(), favorites))
    response = {
        "status": "ok",
        "response": favorites_list
    }
    print(favoritess)
    return jsonify("a"), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
