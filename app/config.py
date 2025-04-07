# app/config.py

import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dothucong.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False