import os
import unittest
import json
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from database.models import setup_db, Actor, Movie

class CastingTestCase(unittest.TestCase):
    '''This class represents the casting test case'''

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = 'agency_test'
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        self.casting_assistant =''
        self.executive_producer =''
        self.casting_director =''

        self.new_actor = {
            'name': 'Test_Name',
            'age': 87,
            'gender': 'Male'
        }

        self.new_movie = {
            'title': 'Test_Title',
            'release': datetime(2087, 7, 24)
        }

        self.incomplete_actor = {
            'name': 'Test_Name',
            'age': 78
        }

        self.incomplete_movie = {
            'title': 'Test_Title'
        }

        #binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        '''Executed after each test'''
        pass

    '''
    Test Below
    '''

    def test_get_actors(self):
        res = self.client().get('/actors',
              headers='Authorization': f'Bearer {self.casting_assistant}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        self.assertTrue(data['total_actors'])

    def test_get_movies(self):
        res = self.client().get('/movies',
              headers='Authorization': f'Bearer {self.executive_producer}'))
        data = json.load(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        self.assertTrue(data['total_movies'])

    def test_update_actor(self):
        res = self.client().patch('/actors/7', json=self.new_actor,
              headers='Authorization': f'Bearer {self.casting_director}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'])

    def test_update_actor_does_not_exist(self):
        res = self.client().patch('/actors/107', json=self.new_actor,
              headers='Authorization': f'Bearer {self.casting_director}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable'))

    def test_update_actor_unauthorized(self):
        res = self.client().patch('/actors/7', json=self.new_actor,
              headers='Authorization': f'Bearer {self.casting_assistant}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Permission not found')

    def test_update_movie(self):
        res self.client().patch('/movies/7', json=self.new_movie,
            headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])

    def test_update_movie_does_not_exist(self):
        res = self.client().patch('/movies/107', json=self.new_movie,
              headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable'))

    def test_update_movie_unauthorized(self):
        res = self.client().patch('/movies/7', json=self.new_movie,
              headers='Authorization': f'Bearer {self.casting_assistant}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Premission not found')

    def test_actor_delete(self):
        res = self.client().delete('/actors/3',
              headers='Authorization': f'Bearer {self.casting_director}')
        data = json.loads(res.data)

        actor = Actor.query.filter(Actor.id == 3).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['delete'], 3)

    def test_actor_delete_does_not_exist(self):
        res = self.client().delete('/actors/103',
              headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    def test_actor_delete_unauthorized(self):
        res = self.client().delete('/actors/3',
              headers='Authorization': f'Bearer {self.casting_assistant}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Premission not found')

    def test_movie_delete(self):
        res = self.client().delete('/movies/3',
              headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        movie = Movie.query.filter(Movie.id == 3).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['delete'], 3)

    def test_movie_delete_does_not_exist(self):
        res = self.client().delete('/movies/103',
              headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_movie_delete_unauthorized(self):
        res = self.client().delete('/movies/3',
              headers='Authorization': f'Bearer {self.casting_director}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Premission not found')

    def test_create_actor(self):
        res = self.client().post('/actors', json=self.new_actor,
              headers='Authorization': f'Bearer {self.casting_director}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actor'])

    def test_create_actor_incomplete(self):
        res = self.client().post('/actors', json=self.incomplete_actor,
              headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_create_actor_unauthorized(self):
        res = self.client().post('/actors', json=self.new_actor,
              headers='Authorization': f'Bearer {self.casting_assistant}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Premission not found')

    def test_create_movie(self):
        res = self.client().post('/movies', json=self.new_movie,
              headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movie'])

    def test_create_movie_incomplete(self):
        res = self.client().post('/movies', json=self.incomplete_movie,
              headers='Authorization': f'Bearer {self.executive_producer}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

    def test_create_movie_unauthorized(self):
        res = self.client().post('/movies', json=self.new_movie,
              headers='Authorization': f'Bearer {self.casting_director}')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 403)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Premission not found')
