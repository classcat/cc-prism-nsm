
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

class Main2(View):

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




    def _make_data(self):
        sc = CCSpark.getSC()

        raw_ds = sc.textFile("/usr/local/bro/logs/current/conn.log")

        # Skip comments
        raw_ds2 = raw_ds.filter(lambda line: not line.startswith('#'))

        # Split to get tokens.
        ds = raw_ds2.map(lambda line:line.split('\t'))

        #fields ts(0)     uid(1)     id.orig_h(2)       id.orig_p(3)       id.resp_h(4)      id.resp_p(5)      proto(6)   service duration        orig_bytes      resp_bytes      conn_state      local_orig      local_resp      missed_bytes    history orig_pkts       orig_ip_bytes   resp_pkts       resp_ip_bytes   tunnel_parents
        #types  time    string  addr    port    addr    port    enum    string  interval        count   count   string  bool    bool    count   string  count   count   count   count   set[string]

        self.ds_tcp = ds.filter(lambda x: x[6] == 'tcp').sortBy(lambda x: x[0], ascending=False)

        count = 0
        for a in self.ds_tcp.collect():
            count += 1
            if count>10:
                break
            print(a[6])

        #ds_tcp = ds.filter(lambda line:)

        #noHeaderRDD = dataset.zipWithIndex().filter(lambda (row,index): index > 6).keys()

        #print(dataset.count())

        #for a in ds2.collect():
        #    print(a[0])
        #sqlContext = SQLContext(CCSpark.SC)
        #sqlContext = SQLContext(View.SC)
        #sdf = sqlContext.createDataFrame(pdf)
        pass


    def x_make_data(self):
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

        sqlContext = SQLContext(CCSpark.SC)
        #sqlContext = SQLContext(View.SC)
        sdf = sqlContext.createDataFrame(pdf)

        #print(sdf)

        #self.df_tcp = df[df['proto'] == 'tcp'].sort_index(ascending=False)


    def _make_contents(self):
        buffer = ""

        curr_time = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f %m/%d/%Y")

        buffer += """<div>%s</div><br/>""" %curr_time

        buffer += "<h2>最新のネットワーク接続</h2>"

        buffer += "<br/>"

        #if self.is_data_error:
        #    buffer += """<div style="color:red;">%s</div""" % self.msg_data_error
        #    self.contents = buffer
        #    return

        buffer += self._make_contents_for_tcp()

        self.contents = buffer


    def _make_contents_for_tcp(self):
        buffer = ""

        buffer += """<table><tr><td width="50%">"""

        buffer += self._make_contents_tcp_latest_incoming()

        buffer += "<br/>"

        #buffer += self._make_contents_tcp_latest_outgoing()

        buffer += "<br/>"

        #buffer += self._make_contents_tcp_latest_others()

        buffer += """<td width="50%" valign="top">"""

        #buffer += self._make_contents_tcp_incoming_upper()

        buffer += "<br/>"

        #buffer += self._make_contents_tcp_outgoing_upper()

        buffer += "</table>"

        return buffer


    def _make_contents_tcp_latest_incoming(self):
        buffer = ""

        myip = self.conf.myip

        buffer += "<table>"
        buffer += "<caption><strong>最新の TCP 接続 (Incoming)</strong></caption>"

        buffer += "<tr><th><th>タイムスタンプ<th>接続元<th>ポート<th>接続先<th>ポート<th>プロトコル</tr>"

        print (self.ds_tcp.count())

        #fields ts(0)     uid(1)     id.orig_h(2)       id.orig_p(3)       id.resp_h(4)      id.resp_p(5) proto(6)

        #        self.ds_tcp = ds.filter(lambda x: x[6] == 'tcp')
        ds_tcp_incoming = self.ds_tcp.filter(lambda x: x[4] == myip)

        counter = 0
        for row in ds_tcp_incoming.collect():
            counter +=  1
            if counter > 50:
                break

            ts = float(row[0])
            orig_h = row[2]
            orig_p = row[3]
            resp_h = row[4]
            resp_p = row[5]
            proto = row[6]

            buffer += "<tr>"
            buffer += """<td>%s""" % counter
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("<b>%H:%M:%S</b>.%f")
            buffer += """<td align="center">%s""" % orig_h
            buffer += """<td align="center">%s""" % orig_p
            buffer += """<td align="center">%s""" % resp_h
            buffer += """<td align="center">%s""" % resp_p
            buffer += """<td align="center">%s""" % proto

#        counter = 0
#        df_incoming = self.df_tcp[self.df_tcp['resp_h'] == myip]
#        for index in df_incoming.index:
#            counter += 1
#            if counter>50:
#                break
#            row = df_incoming.ix[index]
#
#            buffer += "<tr>"
#            buffer += """<td>%s""" % counter
#            ts = row.ts
#            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("<b>%H:%M:%S</b>.%f")
#
#            buffer += """<td align="center">%s""" % row.orig_h
#            buffer += """<td align="center">%s""" % row.orig_p
#            buffer += """<td align="center">%s""" % row.resp_h
#            buffer += """<td align="center">%s""" % row.resp_p
#            buffer += """<td align="center">%s""" % row.proto

        buffer += "</table>"

        return buffer
