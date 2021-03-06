
##############################################################
# ClassCat(R) Prism for HIDS
#  Copyright (C) 2015 ClassCat Co.,Ltd. All rights reseerved.
##############################################################

# ===  Notice ===
# all python scripts were written by masao (@classcat.com)
#
# === History ===
# 02-aug-15 : fixed for beta.
#

import os,sys
import re

from flask import Flask, session, request, redirect, render_template, url_for
from flask import jsonify, make_response


from .view import View

class Login(View):

    LOGIN_HEADER = """\
<!-- OSSEC UI header -->

<div id="header">
  <div id="headertitle">
      <table>
      <tr>
        <td>
          &nbsp;&nbsp;<a href="http://www.ossec.net/">
          <img width="191" height="67" src="static/img/ossec_webui.png" title="Go to OSSEC.net" alt="Go to OSSEC.net"/></a>
        </td>

        <td>
          <img width="107" height="38" src="static/img/webui.png"/><br>&nbsp;&nbsp; <i>Version 0.8</i>
        </td>
      </tr>
      </table>
  </div>

  <!-- <ul id="nav">
  <li><a href="main" title="Main">Main</a></li>
  <li><a href="search" title="Search events">Search</a></li>
  <li><a href="syscheck" title="Integrity checking">Integrity checking</a></li>
  <li><a href="stats" title="Stats">Stats</a></li>
  <li><a href="help" title="Help">About</a></li>
  </ul> -->
</div>

<!-- END OF HEADER -->
"""

    LOGIN_HEADER_JA = """\
<!-- OSSEC UI header -->

<div id="header">
  <div id="headertitle">
    <table style="background:orange;" width="100%" cellspacing=0 cellpadding=0>
    <tr>
        <td><div style="color:royalblue;font-size:24pt;font-weight:bold;font-family:'Times New Roman'">&nbsp;&nbsp;ClassCat&reg; Prism <span style="font-style:italic;">for HIDS</span></div>
        <td width="405px"><img src="static/ccimg/cc_logo_with_softlayer.png"/>
    </tr>
    </table>
  </div>

  <!-- <ul id="nav">
  <li><a href="main" title="Main">メイン</a></li>
  <li><a href="search" title="Search events">Alert 検索</a></li>
  <li><a href="syscheck" title="Integrity checking">整合性チェック</a></li>
  <li><a href="stats" title="Stats">統計情報</a></li>
  <li><a href="help" title="Help">About</a></li>
  </ul> -->
</div>

<!-- END OF HEADER -->
"""


    def __init__(self, request, conf, is_error):
        super().__init__(request, conf)

        self.is_error = is_error

        self._make_contents()
        self._make_html()

    def _make_contents(self):
        req       = self.request
        is_post = self.is_post
        form     = req.form

        buffer = ""

        buffer += """
<form method="post" action="/login">
User name:
<input type="text" name="in_user" size="16"/>
&nbsp;
Password:
<input type="password" name="in_pass" size="16"/>
&nbsp;
<button type="submit" class="button" onClick="return check_form();">&nbsp;Login&nbsp;</button>
</form>

<script language="JavaScript">
<!--
function check_form () {
    var form = document.forms[0];
    if (form.in_user.value.length == 0) {
        alert('User name required.');
        return false;
    }
    if (form.in_pass.value.length == 0) {
        alert('Password required');
        return false;
    }
    return true;
}
-->
</script>

"""

        if self.is_error:
            buffer += """<br/><span style="color:red;">&gt;&gt; Authentication failure.</span>"""

        self.contents = buffer


    def _make_html(self):
        tmpl_head  = View.HEAD
        tmpl_header = Login.LOGIN_HEADER
        tmpl_footer = View.FOOTER

        meta_refresh = ""
        if self.is_main:
            meta_refresh = '    <meta http-equiv="refresh" content="90" />'

        if self.is_lang_ja:
            tmpl_head = View.HEAD_JA
            tmpl_header = Login.LOGIN_HEADER_JA
            tmpl_footer = View.FOOTER_JA

        self.html = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
%s
</head>

<body>
    <br/>
%s

<div id="container">
  <div id="content_box">
  <div id="content" class="pages">
  <a name="top"></a>

  <!-- BEGIN: content -->

  %s

  <!-- END: content -->

  <br /><br />
  <br /><br />
  </div>
  </div>

%s

</div>
</body>
</html>
""" % (tmpl_head, tmpl_header, self.contents, tmpl_footer)

#    def getHtml(self):
#        return self.html


### End of Scrpit ###
