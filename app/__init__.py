# coding=utf-8
from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from flask import Flask

app = Flask(__name__)
user = os.environ['USER_DB']
password = os.environ['PASSWORD_DB']
host = os.environ['HOST_DB']

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://{}:{}@{}:5432/{}'.format(user, password, host, user)
from app.views import *
