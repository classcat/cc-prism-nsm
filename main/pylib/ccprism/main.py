
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

        #print(self.df_tcp.groupby('orig_h').indices)
        #print(self.df_tcp.groupby('orig_h').__dict__)

        #df_tcp_gby_orig_h = df_tcp.groupby('orig_h')
        #print(df_tcp_gby_orig_h.indices)
        #for key, val in df_tcp_gby_orig_h.indices.items():
        #    print (key)
        #    print(len(val))


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

        buffer += self._make_contents_for_tcp_latest()

        buffer += """<td width="50%" valign="top">"""

        buffer += self._make_contents_for_tcp_group()

        buffer += "</table>"

        return buffer


    def _make_contents_for_tcp_latest(self):
        buffer = ""

        buffer += "<table>"
        buffer += "<caption><strong>最新の TCP 接続</strong></caption>"

        buffer += "<tr><th><th>タイムスタンプ<th>接続元<th>ポート<th>接続先<th>ポート<th>プロトコル</tr>"

        counter = 0
        for index in self.df_tcp.index:

            counter += 1
            if counter>100:
                break
            buffer += "<tr>"
            buffer += "<td>%s" % counter
            #buffer += "<td>%s" % index
            ts = self.df_tcp.ix[index].ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("<b>%H:%M:%S</b>.%f")
            #buffer += "<td>" + datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f %m/%d/%Y")

            orig_h = self.df_tcp.ix[index].orig_h

            resp_h = self.df_tcp.ix[index].resp_h

            buffer += """<td align="center">%s""" % self.df_tcp.ix[index].orig_h
            buffer += """<td align="center">%s""" % self.df_tcp.ix[index].orig_p
            #print(orig_h_name[0])
            #buffer += """<td>%s""" % orig_h_name
            buffer += """<td align="center">%s""" % self.df_tcp.ix[index].resp_h
            buffer += """<td align="center">%s""" % self.df_tcp.ix[index].resp_p
            buffer += """<td align="center">%s""" % self.df_tcp.ix[index].proto

        buffer += "</table>"

        return buffer
        pass


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

    def x_make_contents(self):
        buffer = ""

        if self.is_error:
            buffer += """<div style="color:red;">%s</div""" % self.msg_error
            self.contents = buffer
            return

        data = {
            'ts' : self.list_ts,
            'orig_h' : self.list_orig_h,
            'orig_p' : self.list_orig_p,
            'resp_h' : self.list_resp_h,
            'resp_p' : self.list_resp_p,
            'proto' : self.list_proto,
            'value' : self.list_value
        }

        frame = DataFrame(data)
        #frame = DataFrame(data, index=self.list_ts)
        # frame = DataFrame(data, index=self.list_ts)



        curr_time = datetime.fromtimestamp(time.time()).strftime("%H:%M:%S.%f %m/%d/%Y")

        buffer += """<div>%s</div><br/>""" %curr_time

        #
        # TCP
        #
        buffer += "<h2>最新のネットワーク接続</h2>"

        buffer += "<br/>"

        buffer += """<table><tr><td width="50%">"""

        hosts_by_orig_addr_tcp = OrderedDict()
        hosts_by_resp_addr_tcp = OrderedDict()

        hosts_by_orig_addr_udp = OrderedDict()
        hosts_by_resp_addr_udp = OrderedDict()

        hosts_by_orig_addr_icmp = OrderedDict()
        hosts_by_resp_addr_icmp = OrderedDict()

        buffer += "<table>"
        buffer += "<caption><strong>TCP 接続</strong></caption>"

        buffer += "<tr><th><th>タイムスタンプ<th>接続元<th>orig_p<th>resp_h<th>resp_p<th>proto</tr>"

        counter = 0
        for index in frame[frame['proto'] == 'tcp'].sort_index(ascending=False).index:
        #for index in frame.sort_index(ascending=False).index:
        #for index in frame.index:
        #for ts in frame.sort_index(ascending=False).index: #(axis=0, ascending=False).index:
        # 昇順ソート
        #for ts in frame.sort_index().index: #(axis=0, ascending=False).index:

        #for ts in frame.index: #(axis=0, ascending=False).index:
        #for index in frame.index:
        #for index in frame.sort_index(axis=0, by=['resp_p'], ascending=False).index:
            counter += 1
            if counter>100:
                break
            buffer += "<tr>"
            buffer += "<td>%s" % counter
            #buffer += "<td>%s" % index
            ts = frame.ix[index].ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("<b>%H:%M:%S</b>.%f")
            #buffer += "<td>" + datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f %m/%d/%Y")

            orig_h = frame.ix[index].orig_h
            """
            orig_h_name = ""
            if orig_h in hosts_by_orig_addr_tcp.keys():
                orig_h_name = hosts_by_orig_addr_tcp['orig_h']
            else:
                try:
                    orig_h_name_tuple = socket.gethostbyaddr(orig_h)
                    orig_h_name =  orig_h_name_tuple[0]
                    hosts_by_orig_addr_tcp['orig_h'] = orig_h_name
                except Exception as e:
                    # traceback
                    orig_h_name = "Unknown host"
                    hosts_by_orig_addr_tcp['orig_h'] = orig_h_name
            """

            resp_h = frame.ix[index].resp_h
            """
            resp_h_name = ""
            if resp_h in hosts_by_resp_addr_tcp.keys():
                resp_h_name = hosts_by_resp_addr_tcp['resp_h']
            else:
                try:
                    resp_h_name_tuple = socket.gethostbyaddr(resp_h)
                    resp_h_name = resp_h_name_tuple[0]
                    hosts_by_resp_addr_tcp['resp_h'] = resp_h_name
                except Exception as e:
                    resp_h_name = "Unknown host"
                    hosts_by_resp_addr_tcp['resp_h'] = resp_h_name
            """

            buffer += """<td align="center">%s""" % frame.ix[index].orig_h
            buffer += """<td align="center">%s""" % frame.ix[index].orig_p
            #print(orig_h_name[0])
            #buffer += """<td>%s""" % orig_h_name
            buffer += """<td align="center">%s""" % frame.ix[index].resp_h
            buffer += """<td align="center">%s""" % frame.ix[index].resp_p
            buffer += """<td align="center">%s""" % frame.ix[index].proto
            #buffer += """<td>%s""" % resp_h_name

        buffer += "</table>"

        buffer += """<td width="50%">"""

        buffer += """<table>"""

        print("unique")
        for h in frame.orig_h.unique():
            print (h)

        print(frame.orig_h.value_counts())

        print ("--------")
        #print(frame[frame['proto'] == 'tcp'].orig_h.unique())
        print(frame[frame['proto'] == 'tcp'].orig_h.value_counts())
        print("-----")

        print ("#######")
        df_tcp = frame[frame['proto'] == 'tcp']
        for i in df_tcp.orig_h.unique():
            print (i)
            #print(df_tcp.count(i))

        print ("#######")

        df_tcp_gby_orig_h = df_tcp.groupby('orig_h')
        print(df_tcp_gby_orig_h.indices)
        for key, val in df_tcp_gby_orig_h.indices.items():
            print (key)
            print(len(val))


            #print(df_tcp_gby_orig_h.get_group(key))
        #print(df_tcp_gby_orig_h.get_group('')
        #for i in df_tcp_gby_orig_h['value'].count():
        #    print(i)

#        for a in frame[frame['proto'] == 'tcp'].orig_h.value_counts():
#            print(type(a))
#            print(a)

        #for i in pd.value_counts(frame.orig_h):
        #    print (i)


        #for i in frame.groupby(['orig_h']):
        #    print (i)

        #print(frame.groupby(['orig_h']).orig_h.transform('count'))

            #buffer += "<tr><td>%s" % items

        buffer += """</table>"""


        buffer += """</table>"""

        #
        # UDP
        #
        buffer += "<h2>UDP</h2>"

        buffer += "<table>"
        buffer += "<caption><strong>curr conn</strong></caption>"

        buffer += "<tr><th>ts<th>orig_h<th>orig_p<th>resp_h<th>resp_p<th>proto</tr>"

        counter = 0
        for index in frame[frame['proto'] == 'udp'].sort_index(ascending=False).index:
        #for index in frame.sort_index(ascending=False).index:
        #for index in frame.index:
        #for ts in frame.sort_index(ascending=False).index: #(axis=0, ascending=False).index:
        # 昇順ソート
        #for ts in frame.sort_index().index: #(axis=0, ascending=False).index:

        #for ts in frame.index: #(axis=0, ascending=False).index:
        #for index in frame.index:
        #for index in frame.sort_index(axis=0, by=['resp_p'], ascending=False).index:
            counter += 1
            if counter>50:
                break

            orig_h = frame.ix[index].orig_h
            """
            orig_h_name = ""
            if orig_h in hosts_by_orig_addr_udp.keys():
                orig_h_name = hosts_by_orig_addr_udp['orig_h']
            else:
                try:
                    orig_h_name_tuple = socket.gethostbyaddr(orig_h)
                    orig_h_name =  orig_h_name_tuple[0]
                    hosts_by_orig_addr_udp['orig_h'] = orig_h_name
                except Exception as e:
                    # traceback
                    orig_h_name = "Unknown host"
                    hosts_by_orig_addr_udp['orig_h'] = orig_h_name

            resp_h = frame.ix[index].resp_h
            resp_h_name = ""
            if resp_h in hosts_by_resp_addr_udp.keys():
                resp_h_name = hosts_by_resp_addr_udp['resp_h']
            else:
                try:
                    resp_h_name_tuple = socket.gethostbyaddr(resp_h)
                    resp_h_name = resp_h_name_tuple[0]
                    hosts_by_resp_addr_udp['resp_h'] = resp_h_name
                except Exception as e:
                    resp_h_name = "Unknown host"
                    hosts_by_resp_addr_tcp['resp_h'] = resp_h_name
            """

            buffer += "<tr>"
            buffer += "<td>%s" % counter
            buffer += "<td>%s" % index
            ts = frame.ix[index].ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f %m/%d/%Y")
            buffer += "<td>%s" % frame.ix[index].orig_h
            buffer += "<td>%s" % frame.ix[index].orig_p
            #buffer += "<td>%s" % orig_h_name
            buffer += "<td>%s" % frame.ix[index].resp_h
            buffer += "<td>%s" % frame.ix[index].resp_p
            buffer += "<td>%s" % frame.ix[index].proto
            #buffer += "<td>%s" % resp_h_name

        buffer += "</table>"


        #
        # ICMP
        #
        buffer += "<h2>ICMP</h2>"

        buffer += "<table>"
        buffer += "<caption><strong>curr conn</strong></caption>"

        buffer += "<tr><th>ts<th>orig_h<th>orig_p<th>resp_h<th>resp_p<th>proto</tr>"

        counter = 0
        for index in frame[frame['proto'] == 'icmp'].sort_index(ascending=False).index:
        #for index in frame.sort_index(ascending=False).index:
        #for index in frame.index:
        #for ts in frame.sort_index(ascending=False).index: #(axis=0, ascending=False).index:
        # 昇順ソート
        #for ts in frame.sort_index().index: #(axis=0, ascending=False).index:

        #for ts in frame.index: #(axis=0, ascending=False).index:
        #for index in frame.index:
        #for index in frame.sort_index(axis=0, by=['resp_p'], ascending=False).index:
            counter += 1
            if counter>100:
                break


            orig_h = frame.ix[index].orig_h
            """
            orig_h_name = ""
            if orig_h in hosts_by_orig_addr_icmp.keys():
                orig_h_name = hosts_by_orig_addr_icmp['orig_h']
            else:
                try:
                    orig_h_name_tuple = socket.gethostbyaddr(orig_h)
                    orig_h_name =  orig_h_name_tuple[0]
                    hosts_by_orig_addr_icmp['orig_h'] = orig_h_name
                except Exception as e:
                    # traceback
                    orig_h_name = "Unknown host"
                    hosts_by_orig_addr_icmp['orig_h'] = orig_h_name
            """

            resp_h = frame.ix[index].resp_h
            """
            resp_h_name = ""
            if resp_h in hosts_by_resp_addr_icmp.keys():
                resp_h_name = hosts_by_resp_addr_icmp['resp_h']
            else:
                try:
                    resp_h_name_tuple = socket.gethostbyaddr(resp_h)
                    resp_h_name = resp_h_name_tuple[0]
                    hosts_by_resp_addr_icmp['resp_h'] = resp_h_name
                except Exception as e:
                    resp_h_name = "Unknown host"
                    hosts_by_resp_addr_tcp['resp_h'] = resp_h_name
            """

            buffer += "<tr>"
            buffer += "<td>%s" % counter
            buffer += "<td>%s" % index
            ts = frame.ix[index].ts
            buffer += "<td>" + datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f %m/%d/%Y")
            buffer += "<td>%s" % frame.ix[index].orig_h
            buffer += "<td>%s" % frame.ix[index].orig_p
            #buffer += "<td>%s" % orig_h_name
            buffer += "<td>%s" % frame.ix[index].resp_h
            buffer += "<td>%s" % frame.ix[index].resp_p
            #buffer += "<td>%s" % resp_h_name
            buffer += "<td>%s" % frame.ix[index].proto

        buffer += "</table>"



        self.contents = buffer

        pass

    def x_make_data_basic(self):
        curr_conn_data = {}

        fobj = open("/usr/local/bro/logs/current/conn.log")
        while True:
            line = fobj.readline()
            if not line:
                break

            if line.startswith('#'):
                continue

            print(line)
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


            curr_conn_data[ts_f] = {'orig_h' : orig_h, 'orig_p' : orig_p, 'resp_h' : resp_h, 'resp_p' : resp_p, 'proto' : proto}

        if fobj:
            fobj.close()

        #curr_conn_data2 = OrderedDict()
        #for ts, val in sorted(curr_conn_data.keys(), reverse=True):
        #    curr_conn_data2[ts] =


        # items の tupple (ts, { 'proto': proto}) の key が x[0]
        self.curr_conn_data = OrderedDict(sorted(curr_conn_data.items(), key=lambda x: x[0], reverse=True))

        #self.curr_conn_data = curr_conn_data
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
