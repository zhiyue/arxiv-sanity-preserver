# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import Celery

__author__ = 'zhiyue'

app = Celery('arxiv', include=['tasks'])

app.config_from_object('config')

if __name__ == '__main__':
    app.start()
