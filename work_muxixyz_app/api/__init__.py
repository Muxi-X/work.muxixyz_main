from flask import Blueprint

api=Blueprint("api",__name__)

from . import management, file, project, share, status, message, search
