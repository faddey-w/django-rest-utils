__author__ = 'faddey'

from fabric.api import local

def run():
    local('python manage.py runserver')
