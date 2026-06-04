# encoding: utf-8
from flask_restful import Resource, request
from app import logging 
""" , git_tag_version """

LOGGER = logging.getLogger(__name__)


class Home(Resource):
    def get(self):
        return {'name': 'aurora API', 'version': 1}, 200

""" class Version(Resource):
    def get(self):
        return {'name': 'aurora API', 'version': git_tag_version}, 200

class ClientIp(Resource):
    def get(self):
        return {'ip': request.remote_addr}, 200 """
