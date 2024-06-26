#!/usr/bin/env python3

from flask import request, session, make_response, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe
import traceback

class Signup(Resource):
    def post(self):
            json = request.get_json()
            user = User(
                username=json.get('username'),
                image_url = json.get('image_url'),
                bio = json.get('bio')
            )
            user.password_hash = json.get('password')
            
            try:
                db.session.add(user)
                db.session.commit()
                user_dict= user.to_dict()
                session['user_id'] = user.id

                response= make_response(jsonify(user_dict),201)
                return response
            except:
                response= {"error":"User not valid"}
                return make_response(response,422)
            
class CheckSession(Resource):
      def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user and request.endpoint != "signup":
            return user.to_dict()
        else:
            return {'message': '401: Not Authorized'}, 401

class Login(Resource):

    def post(self):
        username = request.get_json()['username']
        user = User.query.filter(User.username == username).first()

        password = request.get_json()['password']

        if user is not None and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        else: 
            return {'error': 'Invalid username or password'}, 401


class Logout(Resource):
  
    def delete(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user: # just add this line!
            session['user_id'] = None
            return {'message': '204: No Content'}, 204
        else:
            return {'message': '401: Not Authorized'}, 401
      
class RecipeIndex(Resource):
    def get(self): 
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user: 
            user_recipes = []
            recipes=Recipe.query.filter(Recipe.user_id == session.get('user_id')).all()
            for recipe in recipes:
                recipe_dic = recipe.to_dict()
                user_recipes.append(recipe_dic)

            return make_response(jsonify(user_recipes), 200)
        else:
            return {'message': '401: Not Authorized'}, 401
        
    def post(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            json = request.get_json()
            try:
                recipe = Recipe(
                    title=json.get('title'),
                    instructions=json.get('instructions'),
                    minutes_to_complete=json.get('minutes_to_complete'),
                    user_id=user.id
                )
                db.session.add(recipe)
                db.session.commit()
                recipe_dict = recipe.to_dict()
                response = make_response(jsonify(recipe_dict), 201)
                return response
            except ValueError as e:
                response = {"error": str(e)}
                return make_response(jsonify(response), 422)
        else:
            return {'message': '401: Not Authorized'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)