from mini_redis import *
from flask import Flask
from flask_restplus import Resource, Api, reqparse

app = Flask(__name__)
api = Api(app, version='1.0', title='MiniRedis API', description='API implementing a subset of Redis operations')
keys_ns = api.namespace('keys', description='Operations with simple keys')
db_ns = api.namespace('db', description='Operations regarding the storage')
sets_ns = api.namespace('sets', description="Operations with sorted sets")


@keys_ns.route('/<string:key>')
class KeysResource(Resource):
    def get(self, key):
        """Get the value stored on the key"""
        return get(key)

    @keys_ns.param('value', 'The value intended to set on the key', required=True)
    @keys_ns.param('seconds', 'Expiration time of the value in seconds')
    def put(self, key):
        """Set a value on the key, with or without expiration time"""
        parser = reqparse.RequestParser()
        parser.add_argument('value', type=str, trim=True)
        parser.add_argument('seconds', type=float, required=False)
        args = parser.parse_args()
        return set_key(key, args['value'], args['seconds'])

    @keys_ns.param('keys', 'List of space-delimited keys to delete')
    def delete(self, key):
        """Delete the key"""
        parser = reqparse.RequestParser()
        parser.add_argument('keys', type=str, required=False)
        args = parser.parse_args()
        return delete(key, args['keys'])

    def post(self, key):
        """Increment the key value, if numeric"""
        return incr(key)


@db_ns.route('/')
class DbResource(Resource):
    def get(self):
        """Returns the number of keys stored"""
        return db_size()


@sets_ns.route('/<string:key>')
class SetsResource(Resource):
    @sets_ns.route('/<string:key>/card')
    class CardinalityResource(Resource):
        def get(self, key):
            """Returns the cardinality of the set stored on the key"""
            return z_card(key)

    @sets_ns.route('/<string:key>/rank')
    class RankResource(Resource):
        @sets_ns.param('member', 'Key of the set member', required=True)
        def get(self, key):
            """Returns the rank of the member in the set stored on the key"""
            parser = reqparse.RequestParser()
            parser.add_argument('member', type=str, trim=True)
            args = parser.parse_args()
            return z_rank(key, args['member'])

    @sets_ns.param('stop', 'Stop of the range, if negative represents an offset from the end', required=True)
    @sets_ns.param('start', 'Start of the range, if negative represents an offset from the end', required=True)
    def get(self, key):
        """Returns a range of members from the set stored on the key"""
        parser = reqparse.RequestParser()
        parser.add_argument('start', type=int)
        parser.add_argument('stop', type=int)
        args = parser.parse_args()
        return z_range(key, args['start'], args['stop'])

    @sets_ns.param('scores', 'Space-delimited scores to add on the set, same length as the members list', required=True)
    @sets_ns.param('members', 'Space-delimited members to add on the set, same length as the scores list', required=True)
    def put(self, key):
        """Add the specified members and scores to the set stored on the key, or creates the set with the members and scores"""
        parser = reqparse.RequestParser()
        parser.add_argument('members', type=str)
        parser.add_argument('scores', type=str)
        args = parser.parse_args()
        return z_add(key, args['members'], args['scores'])


if __name__ == '__main__':
    app.run(debug=True, port=8080)
