import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from database.models import setup_db, Movie, Actor, db
from auth.auth import AuthError, requires_auth

MOVIES_PER_PAGE = 10


def paginate_movies(request, selection):
    """
    Uses MOVIES_PER_PAGE to determine how many movies to display
    per page.
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * MOVIES_PER_PAGE
    end = start + MOVIES_PER_PAGE

    movies = [movie.format() for movie in selection]
    current_movies = movies[start:end]

    return current_movies


ACTORS_PER_PAGE = 10


def paginate_actors(request, selection):
    """
    Uses ACTORS_PER_PAGE to determine how many actors to display
    per page.
    """
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * ACTORS_PER_PAGE
    end = start + ACTORS_PER_PAGE

    actors = [actor.format() for actor in selection]
    current_actors = actors[start:end]

    return current_actors


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    CORS(app)

    CORS(app, resources={r"/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headders', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    @app.route('/')
    def home():
        return jsonify({
            'success': True,
            'message': 'Casting Agency Home Page'
        })

    @app.route('/actors', methods=['GET'])
    # @requires_auth('get:actors')
    def get_actors(payload):
        '''
        Displays all actors
        Will abort if no actors are found
        '''
        selection = Actor.query.order_by(Actor.name).all()
        actor_info = paginate_actors(request, selection)

        if len(actor_info) == 0:
            abort(404)

        actors = [actor.format() for actor in actor_info]

        return jsonify({
            'success': True,
            'actors': actors,
            'total_actors': len(Actor.query.all())
        })

    @app.route('/movies', methods=['GET'])
    # @requires_auth('get:movies')
    def get_movies():
        '''
        Displays all movies
        Will abort if no movies are found
        '''
        selection = Movie.query.order_by(Movie.title).all()
        movie_info = paginate_movies(request, selection)

        if len(movie_info) == 0:
            abort(404)

        movies = [movie.format() for movie in movie_info]

        return jsonify({
            'success': True,
            'movies': movies,
            'total_movies': len(Movie.query.all())
        })

    @app.route('/actors/<int:actor_id>', methods=['PATCH'])
    # @requires_auth('patch:actors')
    def update_actor(payload, movie_id):
        '''
        Staff and Managers will be able to update actors
        Will abort if update is missing information
        '''
        body = request.get_json()
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')

        if not name and not age and not gender:
            abort(400)

        actor = Actor.query.get_or_404(actor_id)

        try:
            if name:
                actor.name = name
            if age:
                actor.age = age
            if gender:
                actor.gender = gender
            actor.update()
            return jsonify({
                'success': True,
                'actor': actor.format()
            })
        except:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    # @requires_auth('patch:movies')
    def update_movie(payload, movie_id):
        '''
        Staff and Managers will be able to update movies
        Will abort if update is missing information
        '''
        body = request.get_json()
        title = body.get('title')
        release = body.get('release')

        if not title and not release:
            abort(400)

        movie = Movie.query.get_or_404(movie_id)

        try:
            if title:
                movie.title = title
            if release:
                movie.release = release
                movie.update()
                return jsonify({
                    'success': True,
                    'movie': movie.format()
                })
        except:
            abort(422)

    @app.route('/actors/<int:actor_id>', methods=['DELETE'])
    # @requires_auth('delete:actors')
    def delete_actors(payload, actor_id):
        '''
        Manages will be able to delete actors
        Will abort if id is invalid
        '''
        actor = Actor.query.get_or_404(actor_id)

        try:
            actor.delete()
            return jsonify({
                'success': True,
                'delete': actor_id
            })
        except:
            abort(422)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    # @requires_auth('delete:movies')
    def delete_movies(payload, movie_id):
        '''
        Managers will be able to delete movies
        will abort if movie is invalid
        '''
        movie = Movie.query.get_or_404(movie_id)

        try:
            movie.delete()
            return jsonify({
                'success': True,
                'delete': movie_id
            })
        except:
            abort(422)

    @app.route('/actors', methods=['POST'])
    # @requires_auth('post:actors')
    def create_actor(token):
        '''
        Allows only managers to create new actors
        Will abort if information is incomplete
        '''
        body = request.get_json()
        name = body.get('name')
        age = body.get('age')
        gender = body.get('gender')

        if not name or not age or not gender:
            abort(400)

        try:
            actor = Actor(name=name, age=age, gender=gender)
            actor.insert()

            return jsonify({
                'success': True,
                'actor': actor.format()
            })
        except:
            abort(422)

    @app.route('/movies', methods=['POST'])
    # @requires_auth('post:movies')
    def create_movie(token):
        '''
        Allows only managers to create new movies
        Will abort if information is incomplete
        '''
        body = request.get_json()
        title = body.get('title')
        release = body.get('release')

        if not title or not release:
            abort(400)

        try:
            movie = Actor(title=title, release=release)
            movie.insert()

            return jsonify({
                'success': True,
                'movie': movie.format()
            })
        except:
            abort(422)

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error
        }), error.status_code

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    return app


APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)
