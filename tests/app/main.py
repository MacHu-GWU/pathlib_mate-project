#!/usr/bin/env python
# -*- coding: utf-8 -*-


class User(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name


user_data = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 3, "name": "Cathy"},
]