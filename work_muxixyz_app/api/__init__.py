from flask import Blueprint

api=Blueprint("api",__name__)

from . import management, project, share, status, message
