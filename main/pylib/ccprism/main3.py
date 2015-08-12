
##############################################################
# ClassCat(R) Prism for HIDS
#  Copyright (C) 2015 ClassCat Co.,Ltd. All rights reseerved.
##############################################################

# === History ===

#

import os,sys
import re
import traceback
import socket

from flask import Flask, session, request, redirect, render_template, url_for
from flask import jsonify, make_response

from datetime import *
import time

from pandas import Series, DataFrame
import pandas as pd

#from pyspark import SparkContext
#from pyspark import SparkConf

import pyspark
from pyspark import SparkContext
from pyspark.sql import SQLContext

#sc =SparkContext()
#sqlContext = SQLContext(sc)



from collections import OrderedDict

from .view import View

from .ccspark import CCSpark

class Main3(View):

    def __init__(self, request, conf):
        super().__init__(request, conf, is_main=True)

        self.is_data_error = False
        self.msg_data_error = ""

        #print(aaa)

        #sc = SparkContext()
        #global g_sc


        self._make_data()
        self._make_contents()
        self._make_html()


    def x_make_data(self):
        sc = CCSpark.SC
        mydata = sc.textFile("/usr/local/bro/logs/current/conn.log")
        print(mydata.count())
        for a in mydata.collect():
            print(a)
        #sqlContext = SQLContext(CCSpark.SC)
        #sqlContext = SQLContext(View.SC)
        #sdf = sqlContext.createDataFrame(pdf)
        pass


    def _make_data(self):
        list_ts = []
        list_orig_h = []
        list_orig_p = []
        list_resp_h = []
        list_resp_p = []
        list_proto = []
        #list_value = []

        fobj = None
        try:
            fobj = open("/usr/local/bro/logs/current/conn.log")
        except Exception as e:
            self.is_data_error = True
            self.msg_data_error = "%s" % e
            return

        while True:
            line = fobj.readline()
            if not line:
                break

            if line.startswith('#'):
                continue

            tokens = line.split("\t")

            ts_f = float(tokens[0])
            orig_h = tokens[2]
            orig_p = tokens[3]
            resp_h = tokens[4]
            resp_p = tokens[5]
            proto = tokens[6]


            list_ts.append(ts_f)
            list_orig_h.append(orig_h)
            list_orig_p.append(orig_p)
            list_resp_h.append(resp_h)
            list_resp_p.append(resp_p)
            list_proto.append(proto)
            #list_value.append(1)

            # curr_conn_data[ts_f] = {'orig_h' : orig_h, 'orig_p' : orig_p, 'resp_h' : resp_h, 'resp_p' : resp_p, 'proto' : proto}

        if fobj:
            fobj.close()


        data = {
            'ts' : list_ts,
            'orig_h' : list_orig_h,
            'orig_p' : list_orig_p,
            'resp_h' : list_resp_h,
            'resp_p' : list_resp_p,
            'proto' : list_proto,
            #'value' : list_value
        }

        pdf = DataFrame(data)

        sqlContext = SQLContext(CCSpark.getSC())
        #sqlContext = SQLContext(View.SC)
        sdf = sqlContext.createDataFrame(pdf)

        #print(sdf)

        #self.df_tcp = df[df['proto'] == 'tcp'].sort_index(ascending=False)


    def _make_contents(self):
        buffer = ""

        self.contents = buffer
