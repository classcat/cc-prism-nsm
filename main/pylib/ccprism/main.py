
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

from collections import OrderedDict

from .view import View

class Main(View):

    def __init__(self, request, conf):
        super().__init__(request, conf, is_main=True)

        self.is_data_error = False
        self.msg_data_error = ""

        self._make_data()
        self._make_contents()
        self._make_html()


    def _make_data(self):
        self.list_ts = []
        self.list_orig_h = []
        self.list_orig_p = []
        self.list_resp_h = []
        self.list_resp_p = []
        self.list_proto = []
        self.list_value = []

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


            self.list_ts.append(ts_f)
            self.list_orig_h.append(orig_h)
            self.list_orig_p.append(orig_p)
            self.list_resp_h.append(resp_h)
            self.list_resp_p.append(resp_p)
            self.list_proto.append(proto)
            self.list_value.append(1)

            # curr_conn_data[ts_f] = {'orig_h' : orig_h, 'orig_p' : orig_p, 'resp_h' : resp_h, 'resp_p' : resp_p, 'proto' : proto}

        if fobj:
            fobj.close()


        data = {
            'ts' : self.list_ts,
            'orig_h' : self.list_orig_h,
            'orig_p' : self.list_orig_p,
            'resp_h' : self.list_resp_h,
            'resp_p' : self.list_resp_p,
            'proto' : self.list_proto,
            'value' : self.list_value
        }

        df = DataFrame(data)

        self.df_tcp = df[df['proto'] == 'tcp'].sort_index(ascending=False)


    def _make_contents(self):
        buffer = ""

        curr_time = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f %m/%d/%Y")

        buffer += """<div>%s</div><br/>""" %curr_time

        buffer += "<h2>最新のネットワーク接続</h2>"

        buffer += "<br/>"

        if self.is_data_error:
            buffer += """<div style="color:red;">%s</div""" % self.msg_data_error
            self.contents = buffer
            return

        buffer += self._make_contents_for_tcp()

        self.contents = buffer


    def _make_contents_for_tcp(self):
        buffer = ""

        buffer += """<table><tr><td width="50%">"""

        buffer += self._make_contents_tcp_latest_incoming()

        buffer += "<br/>"

        buffer += self._make_contents_tcp_latest_outgoing()

        buffer += "<br/>"

        buffer += self._make_contents_tcp_latest_others()

        #buffer += self._make_contents_for_tcp_latest()

        buffer += """<td width="50%" valign="top">"""

        buffer += self._make_contents_for_tcp_group()

        buffer += "<br/>"

        buffer += self._make_contents_for_tcp_group2()

        buffer += "</table>"

        return buffer


    def _make_contents_tcp_latest_incoming(self):
        buffer = ""

        myip = self.conf.myip


        #df_outgoing = self.df_tcp[self.df_tcp['orig_h'] == myip]

        buffer += "<table>"
        buffer += "<caption><strong>最新の TCP 接続 (Incoming)</strong></caption>"

        buffer += "<tr><th><th>タイムスタンプ<th>接続元<th>ポート<th>接続先<th>ポート<th>プロトコル</tr>"

        #print(self.df_tcp.resp_h == myip)

        #print(self.df_tcp[ self.df_tcp.resp_h == myip] )

        counter = 0
        df_incoming = self.df_tcp[self.df_tcp['resp_h'] == myip]
        for index in df_incoming.index:
            counter += 1
            if counter>50:
                break
            row = df_incoming.ix[index]

            buffer += "<tr>"
            buffer += """<td>%s""" % counter
            ts = row.ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("<b>%H:%M:%S</b>.%f")

            buffer += """<td align="center">%s""" % row.orig_h
            buffer += """<td align="center">%s""" % row.orig_p
            buffer += """<td align="center">%s""" % row.resp_h
            buffer += """<td align="center">%s""" % row.resp_p
            buffer += """<td align="center">%s""" % row.proto

        buffer += "</table>"

        return buffer


    def _make_contents_tcp_latest_outgoing(self):
        buffer = ""

        myip = self.conf.myip

        buffer += "<table>"
        buffer += "<caption><strong>最新の TCP 接続 (Outgoing)</strong></caption>"

        buffer += "<tr><th><th>タイムスタンプ<th>接続元<th>ポート<th>接続先<th>ポート<th>プロトコル</tr>"

        counter = 0
        #df_incoming = self.df_tcp[self.df_tcp['resp_h'] == myip]
        df_outgoing = self.df_tcp[self.df_tcp['orig_h'] == myip]

        for index in df_outgoing.index:
            counter += 1
            if counter>50:
                break
            row = df_outgoing.ix[index]

            buffer += "<tr>"
            buffer += """<td>%s""" % counter
            ts = row.ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("<b>%H:%M:%S</b>.%f")

            buffer += """<td align="center">%s""" % row.orig_h
            buffer += """<td align="center">%s""" % row.orig_p
            buffer += """<td align="center">%s""" % row.resp_h
            buffer += """<td align="center">%s""" % row.resp_p
            buffer += """<td align="center">%s""" % row.proto

        buffer += "</table>"

        return buffer


    def _make_contents_tcp_latest_others(self):
        buffer = ""

        myip = self.conf.myip

        buffer += "<table>"
        buffer += "<caption><strong>最新の TCP 接続 (Others)</strong></caption>"

        buffer += "<tr><th><th>タイムスタンプ<th>接続元<th>ポート<th>接続先<th>ポート<th>プロトコル</tr>"

        counter = 0
        #df_incoming = self.df_tcp[self.df_tcp['resp_h'] == myip]
        #df_others = self.df_tcp[ self.df_tcp['orig_h'] != myip ]

        #df_others = self.df_tcp[(self.df_tcp.orig_h != myip) and (self.df_tcp.resp_h != myip)]

        df_others_tmp = self.df_tcp[self.df_tcp.orig_h != myip]
        df_others = df_others_tmp[df_others_tmp.resp_h != myip]

        for index in df_others.index:
            counter += 1
            if counter>50:
                break
            row = df_outgoing.ix[index]

            buffer += "<tr>"
            buffer += """<td>%s""" % counter
            ts = row.ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("<b>%H:%M:%S</b>.%f")

            buffer += """<td align="center">%s""" % row.orig_h
            buffer += """<td align="center">%s""" % row.orig_p
            buffer += """<td align="center">%s""" % row.resp_h
            buffer += """<td align="center">%s""" % row.resp_p
            buffer += """<td align="center">%s""" % row.proto

        buffer += "</table>"

        return buffer



    def _make_contents_for_tcp_group(self):
        buffer = ""
        buffer += "<table>"
        buffer += "<caption><strong>TCP 接続元上位</strong></caption>"

        buffer += "<tr><th>接続元<th>ホスト名<th>総数</tr>"

        group = {}
        for index, array in self.df_tcp.groupby('orig_h').indices.items():
            group[index] = len(array)

        counter = 0
        for k, v in sorted(group.items(), key=lambda x:x[1], reverse=True):
            counter += 1
            if counter > 10:
                break
            buffer += "<tr>"
            buffer += """<td>%s""" % k

            host_name = "-"
            try:
                h = socket.gethostbyaddr(k)
                host_name = h[0]
            except Exception as e:
                pass

            buffer += "<td>%s" % host_name

            buffer += """<td align="right">%s""" % v

        buffer += "</table>"

        buffer += "<br/>"

        buffer += "<table>"
        buffer += "<caption><strong>TCP 接続先上位</strong></caption>"

        buffer += "<tr><th>接続元<th>ホスト名<th>総数</tr>"

        group2 = {}
        for index, array in self.df_tcp.groupby('resp_h').indices.items():
            group2[index] = len(array)

        counter2 = 0
        for k, v in sorted(group2.items(), key=lambda x:x[1], reverse=True):
            counter2 += 1
            if counter2 > 10:
                break
            buffer += "<tr>"
            buffer += """<td>%s""" % k

            host_name = "-"
            try:
                h = socket.gethostbyaddr(k)
                host_name = h[0]
            except Exception as e:
                pass

            buffer += "<td>%s" % host_name

            buffer += """<td align="right">%s""" % v

        buffer += "</table>"

        return buffer



    def _make_contents_for_tcp_group2(self):

        myip = "192.168.0.50"

        buffer = ""

        df_incoming = self.df_tcp[self.df_tcp['resp_h'] == myip]
        df_outgoing = self.df_tcp[self.df_tcp['orig_h'] == myip]

        buffer += "<table>"
        buffer += "<caption><strong>TCP incoming 接続 接続元上位</strong></caption>"

        buffer += "<tr><th>接続元<th>ホスト名<th>総数</tr>"

        group = {}
        for index, array in df_incoming.groupby('orig_h').indices.items():
            group[index] = len(array)

        counter = 0
        for k, v in sorted(group.items(), key=lambda x:x[1], reverse=True):
            counter += 1
            if counter > 10:
                break
            buffer += "<tr>"
            buffer += """<td>%s""" % k

            host_name = "-"
            try:
                h = socket.gethostbyaddr(k)
                host_name = h[0]
            except Exception as e:
                pass

            buffer += "<td>%s" % host_name

            buffer += """<td align="right">%s""" % v

        buffer += "</table>"

        buffer += "<br/>"

        buffer += "<table>"
        buffer += "<caption><strong>TCP outgoing 接続先上位</strong></caption>"

        buffer += "<tr><th>接続元<th>ホスト名<th>総数</tr>"

        group2 = {}
        for index, array in df_outgoing.groupby('resp_h').indices.items():
            group2[index] = len(array)

        counter2 = 0
        for k, v in sorted(group2.items(), key=lambda x:x[1], reverse=True):
            counter2 += 1
            if counter2 > 10:
                break
            buffer += "<tr>"
            buffer += """<td>%s""" % k

            host_name = "-"
            try:
                h = socket.gethostbyaddr(k)
                host_name = h[0]
            except Exception as e:
                pass

            buffer += "<td>%s" % host_name

            buffer += """<td align="right">%s""" % v

        buffer += "</table>"


        return buffer




### End of Script ###
