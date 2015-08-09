import os,sys
import re
import traceback
import socket

from flask import Flask, session, request, redirect, render_template, url_for
from flask import jsonify, make_response

from datetime import *

from collections import OrderedDict

#import os_lib_agent
#import os_lib_alerts
#import os_lib_syscheck
from pandas import Series, DataFrame
import pandas as pd

from .view import View

class Test2(View):

    def __init__(self, request, conf):
        super().__init__(request, conf, is_main=True)

        self._make_data()

        self._make_contents()
        self._make_html()


    def _make_data(self):
        #curr_conn_data = {}

        self.list_ts = []
        self.list_orig_h = []
        self.list_orig_p = []
        self.list_resp_h = []
        self.list_resp_p = []
        self.list_proto = []

        fobj = open("/usr/local/bro/logs/current/conn.log")
        while True:
            line = fobj.readline()
            if not line:
                break

            if line.startswith('#'):
                continue

            #print(line)
            tokens = line.split("\t")
            #print(a)
            #print(a[0])
            #print(type(a[0]))
            #print(float(a[0]))
            #print(datetime.fromtimestamp(float(a[0])).strftime("%m/%d/%Y %H:%M"))

            """
#fields ts      uid     id.orig_h       id.orig_p       id.resp_h       id.resp_p       proto   \
service duration        orig_bytes      resp_bytes      conn_state      local_orig      local_resp      missed_bytes    history orig_pkts       orig_ip_bytes   resp_pkts       resp_ip_bytes   tunnel_parents
#types  time    string  addr    port    addr    port    enum \
string  interval        count   count   string  bool    bool    count   string  count   count   count   count   set[string]
1438927107.563117 (0)      C8qURL1yuLliVffFhh      192.168.0.50 (2)    59391 (3)   104.16.4.175 (4)   80 (5)     tcp (6)     \
-       90.273254       0       13961   SHR     T
       F       0       hCadf   0       0       29      15133   (empty)
            """
            ts_f = float(tokens[0])
            orig_h = tokens[2]
            orig_p = tokens[3]
            resp_h = tokens[4]
            resp_p = tokens[5]
            proto = tokens[6]

            self.list_ts.append(ts_f)
            self.list_orig_h.append(orig_h)
            self.list_orig_p.append(orig_p)
            self.list_resp_h.append(resp_h)
            self.list_resp_p.append(resp_p)
            self.list_proto.append(proto)

            #curr_conn_data[ts_f] = {'orig_h' : orig_h, 'orig_p' : orig_p, 'resp_h' : resp_h, 'resp_p' : resp_p, 'proto' : proto}

        if fobj:
            fobj.close()

        #curr_conn_data2 = OrderedDict()
        #for ts, val in sorted(curr_conn_data.keys(), reverse=True):
        #    curr_conn_data2[ts] =


        # items の tupple (ts, { 'proto': proto}) の key が x[0]
        #self.curr_conn_data = OrderedDict(sorted(curr_conn_data.items(), key=lambda x: x[0], reverse=True))

        #self.curr_conn_data = curr_conn_data
        pass

    def _make_contents(self):
        data = {
#            'ts' : self.list_ts,
            'orig_h' : self.list_orig_h,
            'orig_p' : self.list_orig_p,
            'resp_h' : self.list_resp_h,
            'resp_p' : self.list_resp_p,
            'proto' : self.list_proto
        }

        #frame = DataFrame(data, columns=['ts'])

        frame = DataFrame(data, index=self.list_ts)

        #print(frame.columns)

        #for i in frame.index:
        #    print (frame.ix[i])
        pass


    def x_make_contents(self):
        req    = self.request
        conf  = self.conf

        form  = req.form

        is_post = self.is_post
        is_lang_ja = self.is_lang_ja

        #curr_conn_data = self.curr_conn_data

        buffer = ""

        buffer += "<table>"
        buffer += "<caption><strong>curr conn</strong></caption>"

        buffer += "<tr><th>ts<th>orig_h<th>orig_p<th>resp_h<th>resp_p<th>proto</tr>"

        counter = 0
        for ts, vals in self.curr_conn_data.items():
            counter += 1
            if counter>50:
                break
            print(ts)
            print (vals)
            buffer += "<tr>"
            #buffer += "<td>%s" % ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f %m/%d/%Y.") #+ "%04d" % (datetime.fromtimestamp(ts).microsecond // 1000)
            #print now.strftime("%Y%m%d%H%M%S.") + "%04d" % (now.microsecond // 1000)

            # buffer += "<td>" + datetime.fromtimestamp(ts).strftime("%m/%d/%Y %H:%M")

            buffer += "<td>" + vals['orig_h']
            #try:
            #    buffer += "<td>" + socket.gethostbyaddr(vals['orig_h'])[0]
            #except Exception as e:
            #    buffer += "<td>-"
            buffer += "<td>" + vals['orig_p']

            buffer += "<td>" + vals['resp_h']
            buffer += "<td>" + vals['resp_p']
            #try:
            #    buffer += "<td>" + socket.gethostbyaddr(vals['resp_h'])[0]
            #except Exception as e:
            #    buffer += "<td>-"

            # socket.gethostbyaddr("203.141.142.18")
            # ('my8.interlink.or.jp', [], ['203.141.142.18'])


            buffer += "<td>" + vals['proto']
            buffer += "</tr>"

        buffer += "</table>"


        self.contents = buffer



### End of Script ###
