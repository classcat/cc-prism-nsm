#!/usr/bin/env python
# -*- coding: utf-8 -*-

##############################################################
# ClassCat(R) Prism for NSM
#  Copyright (C) 2015 ClassCat Co.,Ltd. All rights reseerved.
##############################################################

# ===  Notice ===
#
# === History ===

#

import os,sys
import locale

from flask import Flask, session, request, redirect, render_template, url_for
from flask import jsonify, make_response

from ccp_conf import CCPConf

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ClassCat Prism for NSM - The secret key which cipers the cookie'

@app.before_request
def before_request():
    if session.get('is_authenticated'):
        return

    if request.path.startswith('/static/'):
        return

    if request.path == '/login':
        return

    return redirect('/login')


###########
### Root ###
###########

@app.route("/")
def root():
    return redirect("/main")


############
### Log In###
############

@app.route("/login", methods = ['GET', 'POST'])
def login():
    from ccprism.login import Login

    ccpconf = CCPConf()

    is_error = False
    if request.method == 'POST':
        user = request.form.get('in_user')
        pswd = request.form.get('in_pass')

        if user == ccpconf.username and pswd == ccpconf.password:
            session['is_authenticated'] = True
            return redirect('/')
        else:
            is_error = True

    cclogin = Login(request, ccpconf, is_error)

    return cclogin.getHtml()


############
### Logout ###
############

@app.route("/logout", methods= ['GET'])
def logout():
    session.clear()
    return redirect('/')


###########
### Main ###　
###########

@app.route("/main", methods = ['GET'])
def main():
    from ccprism.main import Main

    ccmain = Main(request, CCPConf())
    return ccmain.getHtml()

@app.route("/curr_conn", methods = ['GET'])
def curr_conn():
    from ccprism.curr_conn import CurrConn

    curr_conn = CurrConn(request, CCPConf())
    return curr_conn.getHtml()

@app.route("/test1", methods = ['GET'])
def test1():
    from ccprism.test1 import Test1

    cctest1 = Test1(request, CCPConf())
    return cctest1.getHtml()


@app.route("/test2", methods = ['GET'])
def test2():
    from ccprism.test2 import Test2

    cctest2 = Test2(request, CCPConf())
    return cctest2.getHtml()


if __name__ == "__main__":
    ccprism_home = os.environ['CCPRISM_HOME']
    sys.path.insert(0, ccprism_home + "/main/pylib")

    #print(locale.getlocale())
    #locale.setlocale(locale.LC_ALL, "")
    #print(locale.getlocale())
    #locale.setlocale(locale.LC_ALL, "")

    app.run(host="0.0.0.0", port=5001, debug=True)


### End of Script ###
