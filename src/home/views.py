import flask
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask.views import MethodView
from flask_login import login_required
import flask_login
from flask_login import current_user
import models
import re
import json
import datetime as DT


class HomeScreenView(MethodView):
    decorators = [login_required]

    def get(self):
        teaching = models.Course.query.filter_by(teacher_id=current_user.id).all()
        return render_template('home.html',
                               courses_enrolled=current_user.courses,
                               courses_teaching=teaching)


class ClassListView(MethodView):
    def get(self):
        if current_user.is_authenticated():
            teaching = models.Course.query.filter_by(teacher_id=current_user.id).all()
            courses = [c.serialize for c in current_user.courses]
            courses += [c.serialize for c in teaching]
            return flask.json.dumps(courses)
        else:
            return flask.json.dumps([])


class TaskListView(MethodView):
    def get(self):
        tasks = {'current':[], 'complete':[]}
        userResponseIDs = [tr.task_id for tr in current_user.task_responses]
        week_ago = DT.date.today() - DT.timedelta(days=7)
        for c in current_user.courses:
            for t in c.tasks:
                if(t.id in userResponseIDs and t.duedate.date() > week_ago and t.status != "created"):
                    tasks['complete'].append(t.serialize)
                elif(t.duedate.date() > week_ago and t.status != "created"):
                    tasks['current'].append(t.serialize)
        tasks['complete'] = sorted(tasks['complete'], key=lambda k: k['duedate'])
        tasks['current'] = sorted(tasks['current'], key=lambda k: k['duedate'])
        return flask.json.dumps(tasks)    