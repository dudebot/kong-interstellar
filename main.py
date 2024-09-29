#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

#tds[0]='wat'
#first level: check title names
#second level: check thread OP

#TODO
#global key scope?
#parent transfer for thread statistics

import cgi

#thread searcher
import urllib2, string, json, codecs
import time

from google.appengine.api import users, mail
from google.appengine.ext import ndb
from google.appengine.ext import db
from google.appengine.api import memcache
import random
import webapp2
feedbackReplies={0:'MY LITTLE KONG CANT BE THIS STRONK',
                1:'THE CBILL INCOME IS TOO DAMN HIGH',
                2:'THIS SITE IS PRETTY MINIMALLY VIABLE. THANKS FOR THE MINIMAL EFFORT',
                3:'HI MOM',
                4:'IS THIS GAME PAY 2 WIN',
                5:'IS LASER A GOON',
                6:'HARUKO A SHIT',
                7:'',
                8:'WHO WAS PHONE'}

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}
class ThreadData(ndb.Model):
  MWOURL = ndb.StringProperty()
  SCURL = ndb.StringProperty()
  #CCURL = ndb.StringProperty()
  MWOThreadNumber = ndb.IntegerProperty()
  SCThreadNumber = ndb.IntegerProperty()
  #CCThreadNumber = ndb.IntegerProperty()
  MWOReplies = ndb.IntegerProperty()
  SCReplies = ndb.IntegerProperty()
  #CCReplies = ndb.IntegerProperty()
  time = ndb.DateTimeProperty(auto_now_add=True)
  when = ndb.FloatProperty()


#initialize shared data
#def check_boojum_server():
  


def update_4chan_json():
  lastMWOThreadNumber=0;
  lastMWOThreadReplyCount=0;
  lastSCThreadNumber=0;
  lastSCThreadReplyCount=0;
  #lastCCThreadNumber=0;
  #lastCCThreadReplyCount=0;
  MWOThreadURL="";
  SCThreadURL="";
  #CCThreadURL="";

  url = "http://boards.4chan.org/vg/catalog"
  req = urllib2.Request(url,headers=hdr)
  page = urllib2.urlopen(req)

  html = page.read()

  startindex = string.find(html,'var catalog = {')
  endindex = string.find(html,'};',startindex)
  #print startindex
  #print endindex

  jsonsection = html[startindex+14:endindex+1]
  dictionary = json.loads(jsonsection);
  old_td = ThreadData.query().order(-ThreadData.time).get()#should return the newest one
  if old_td is None:
    old_td = ThreadData()
 

  for x in dictionary['threads'].keys(): # list of all thread numbers, each thread contains: 
    '''
    r, i, sub, author, tn_w, teaser, lr, tn_h, date, imgurl


    '''


    #print x
    #for y in dictionary['threads'][x]:
    # print y
    if (('mechwarrior' in dictionary['threads'][x]['sub'].lower()) or ('mech warrior' in dictionary['threads'][x]['sub'].lower()))  and \
        ((dictionary['threads'][x]['r'] > lastMWOThreadReplyCount and \
        dictionary['threads'][x]['r'] < 700 ) or lastMWOThreadReplyCount is 0 or lastMWOThreadReplyCount >= 700): 
      MWOThreadURL = 'https://boards.4chan.org/vg/res/'+x
      lastMWOThreadNumber = x
      lastMWOThreadReplyCount = dictionary['threads'][x]['r']
    if 'star citizen' in dictionary['threads'][x]['sub'].lower() and \
        ((dictionary['threads'][x]['r'] > lastSCThreadReplyCount and \
        dictionary['threads'][x]['r'] < 700 ) or lastSCThreadReplyCount is 0 or lastSCThreadReplyCount >= 700): 
      SCThreadURL = 'https://boards.4chan.org/vg/res/'+x
      lastSCThreadNumber = x
      lastSCThreadReplyCount = dictionary['threads'][x]['r']
  
  

######


  # #check if the MWO thread needs to be remade
  # if(old_td is not None and old_td.MWOReplies < 740 and lastMWOThreadReplyCount >=740):
  #   timeDifference = time.time() - old_td.when
  #   replyDifference= lastMWOThreadReplyCount-old_td.MWOReplies
  #   remainingReplies=750 - lastMWOThreadReplyCount
  #   if replyDifference ==0:
  #     replyDifference = -1
  #   timeRemaining = remainingReplies * timeDifference / replyDifference
  #   if lastMWOThreadReplyCount>750:
  #     subj = 'MWO Thread Exceeded Bump Limit'
  #     msg='The current thread ('+str(MWOThreadURL)+') has exceeded 750 replies and is currently at '+str(lastMWOThreadReplyCount)+' replies.'
  #   else:
  #     subj ='MWO Thread Approaching Bump Limit'
  #     msg='The current thread ('+str(MWOThreadURL)+') has reached '+str(lastMWOThreadReplyCount)+' replies.' 
  #     if(timeRemaining >= 0):
  #       msg= msg+'\nExtrapolating time until 750 replies: '+str(int(timeRemaining/60))+' minutes'
  #   mail.send_mail(sender="AppEngine Automailer",
  #         to="",
  #         subject=subj,
  #         body=msg)

    



  #td = ThreadData.get_by_id("current")
  #print td
  #if td is None:
  #td_key = ndb.Key(ThreadData, "current")
  td = ThreadData(parent = None,
                  MWOURL=MWOThreadURL,
                  SCURL = SCThreadURL,
                  #CCURL = CCThreadURL,
                  MWOThreadNumber = int(lastMWOThreadNumber),
                  SCThreadNumber = int(lastSCThreadNumber),
                  #CCThreadNumber = int(lastCCThreadNumber),
                  MWOReplies = lastMWOThreadReplyCount,
                  SCReplies = lastSCThreadReplyCount,
                  #CCReplies = lastCCThreadReplyCount,
                  when = time.time())
  #td = ThreadData()
  #put old one back as a child
  
  td.put()

  
  #todo, use set_multi instead


'''
http://pastebin.com/tVwYsfSD
kong SC template  
'''


class MainPage(webapp2.RequestHandler):
    def get(self):
        text = feedbackReplies[random.randint(0, len(feedbackReplies)-1)]
        #self.response.write('thanks diane')
        #return
        '''try:
          ip = self.request.remote_addr
          url = "http://freegeoip.net/json/" + ip
          req = urllib2.Request(url,headers=hdr)
          page = urllib2.urlopen(req)
          data = page.read()
          data = json.loads(data)
          if(data['country_code']!='US'):
            self.response.write("Sorry, KONGORG is not available in your area(s)<br><br>LOL")
            return 
        except Exception, e:
          pass
'''
        
        

        '''
        threadURL = memcache.get(key='threadURL')
        if threadURL == None:
          update_4chan_json()
          print 'threadURL not ready, initializing'
          threadURL = memcache.get(key='threadURL')
          print 'url = '+str(threadURL)
        lastThreadNumber = memcache.get(key='lastThreadNumber')
        lastThreadReplyCount = memcache.get(key='lastThreadReplyCount')
        lastThreadUpdateTime = memcache.get(key='lastThreadUpdateTime')
        '''
        #td_key = ndb.Key(ThreadData, "current")
        timeDifference = 0
        td = ThreadData.query().order(-ThreadData.time).get()#should return the newest one
        if td is None:
          td = ThreadData()
        else:
          timeDifference = time.time() - td.when
        #todo get_multi or unified data structure
        catalogString = "<a href=\"http://boards.4chan.org/vg/catalog\">search manually</a>"
        MWOManualSearchString = catalogString if td.MWOReplies == 0 else ""
        SCManualSearchString = catalogString if td.SCReplies == 0 else ""

        '''ip = self.request.remote_addr  
        url = "http://freegeoip.net/json/" + ip
        req = urllib2.Request(url,headers=hdr)
        page = urllib2.urlopen(req)
        data = page.read()
        data = json.dumps(json.loads(data),indent = 4)+'<br><br>'
        '''
        data = '<a href =\"/randomd\"><button type="button">Find Norris</button></a><br><br>'



#print lastThreadNumbervim  
        self.response.write("""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta name="description" content="Kong Interstellar Security Solutions"/>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Kong Strong</title>
<link rel="stylesheet" type="text/css" href="/static/main.css"> 
</head>
<script>
function clearContents(element) {
  element.select();

  //todo, apply select only once, or revert to .value = '';
}
</script>
<body>
<!--iframe width="1" height="1" src="http://www.youtube.com/embed/Fh6pv_sLgVQ?autoplay=1" frameborder="0" allowfullscreen></iframe-->
<div class="container">
  <div class="sidebar1">
    <ul class="nav"> 
      <li><a href="https://robertsspaceindustries.com/orgs/KONG/">Kong Org Page</a></li>
      <li><a href="https://docs.google.com/document/d/1TIyQgvjShP21p3aCxfL6ffSnL9etXgIUOaph7S2ru_g/edit?hl=en&amp;pli=1">Kong SC Asset List</a></li>
      <li><a href="https://docs.google.com/spreadsheets/d/1t_bq2Q3Bvoj0U-q-1Yi0QUAgkR2UnkgmNzhcmqG3aD4/edit#gid=0">Kong Potato List</a></li>
      <li><a href="/triplist">List of Trips (old)</a></li>
      <li><a href="ventrilo://konginterstellar.typefrag.com:13270/servername=Kong_Ventrilo">Kong Vent Server</a></li>
      <li><a href="/static/Hangappdropbox.zip">Ships_Illum backup</a></li>
      
      
    </ul>
  </div><!-- end sidebar1 -->
  
  <div class="content">
    <h>This hub is designed for KONGSTRONG's insatiable desire for WRECKING PUBBIES across the Gaymerverse.<br><i>Enjoy your stay</i></h><br><br>""")
        if td is not None:
          #self.response.write('<a href =\"'+threadURL+'\">Current MWO Thread</a> '+
          self.response.write('<a href =\'currentmwo\'>Current MWO Thread</a> '+ 
            str(td.MWOReplies)+ ' replies '+ MWOManualSearchString + '<br>' +
            '<a href =\'currentsc\'>Current Star Citizen Thread</a> '+ 
            str(td.SCReplies)+ ' replies '+ SCManualSearchString + '<br>' +
            'Automatically updated '+
             #datetime.datetime.fromtimestamp(dictionary['threads'][lastThreadNumber]['date']).strftime('%Y-%m-%d %H:%M:%S')+
             str(int(timeDifference/60))+
             ' minute(s) ago  <a href="/tasks/updatethread" >Refresh</a><br><br>'+data)
        self.response.write("""\
    <form action="/feedback" method="post" target="_blank">
      <div><textarea onfocus="clearContents(this);"name="content" rows="3" cols="60">%s</textarea></div>
      <div><input type="submit" value="Give Feedback"></div>
    </form>
    <br><br>
    <img src="/static/Harvester_Ant2.jpg" title="A better world. A perfect world." /><br><br>
    
  </div><!-- end content -->

</div><!-- end container -->
</body>

</html>

""" % text)





class Feedback(webapp2.RequestHandler):

    def get(self):
        self.response.write("""\
<html>
  <body>
    Leave feedback here. If you want a response back, please leave some identifiable information.<br><br>

    <form action="/feedback" method="post" target="_blank">
      <div><textarea name="content" rows="3" cols="60"></textarea></div>
      <div><input type="submit" value="Give Feedback"></div>
    </form>
    
  </body>
    
</html>
""")


    def post(self):
        # if self.request.get('content') in feedbackReplies.values():
          self.response.write('<html><body>Thanks for the feedback fogget (You could try actually typing something though).</body></html>')
        # else:
        #   ip = self.request.remote_addr
        #   self.response.write('<html><body>Thanks for the feedback faget.</body></html>')
        #   url = "http://freegeoip.net/json/" + ip
        #   req = urllib2.Request(url,headers=hdr)
        #   page = urllib2.urlopen(req)
        #   data = page.read()
        #   data = json.dumps(json.loads(data),indent = 4)
        #   mail.send_mail(sender="AppEngine Automailer",
        #     to="",
        #     subject="Kong-Interstellar App Engine Feedback",
        #     body=cgi.escape(self.request.get('content')+' \n\n'+data))
        # #self.redirect('/')





class UpdateThread(webapp2.RequestHandler):

    def get(self):
      startTime = time.time()
      update_4chan_json()
      endTime = time.time()
      self.response.write("""\
<html>
  <body>
    Page refreshed in """+str(endTime-startTime)[0:5]+"""\
    seconds<br>
  </body>
<html>""")
      self.redirect('/')



class Changes(webapp2.RequestHandler):

    def get(self):
      self.response.write("""\
<html>
  <body>
    <ul>
      <li>Round Table talk organizer (still no design doc yet hue)</li>
      <li>Possibly a text-only archiver (only if foolz doesn't currently)</li>
      <li>Refactor to properly handle Django templating</li>
      <li>More complete trip list (for now, post your tripcode in feedback <a href="/feedback">here</a>)</li> 
      <li>zomg none!!!11</li>

  </body>
<html>""")


class RoundTable(webapp2.RequestHandler):

    def get(self):
      self.response.write("""\
<html>
  <body>
    RoundTable Development page<br>
  </body>
<html>""")

class TripList(webapp2.RequestHandler):

    def get(self):
      self.response.write("""\
Norris J Packard !tHEACeA2Qk <br>
Valkyrie !!Jp/jtFv+A3H <br>
Whispers !!140zmBipcsK <br>
Lyteros !ltrF5DB6H. <br>
dudebot !fpDudeBoTY <br>
Totally Not GoldCast !z0KXYZctEU <br>
Noblesse Oblige !w1OqvVniJE<br>
JadeKitsune !!mDEkqzZ04+A<br>
Greg !ZYC7SjJsWo<br>
BeakieHelmet !3t7ozAJqSw    """)

class RedirectCurrentMWO(webapp2.RequestHandler):

    def get(self):
      td = ThreadData.query().order(-ThreadData.time).get()
      self.redirect(str(td.MWOURL)+'#bottom')

class RedirectCurrentSC(webapp2.RequestHandler):

    def get(self):
      td = ThreadData.query().order(-ThreadData.time).get()
      self.redirect(str(td.SCURL)+'#bottom')

class RedirectCurrentCC(webapp2.RequestHandler):

    def get(self):
      td = ThreadData.query().order(-ThreadData.time).get()
      self.redirect(str(td.CCURL)+'#bottom')

class RedirectRandomD(webapp2.RequestHandler):

    def get(self):
      #get /d/ catalog data
      url = "http://boards.4chan.org/d/catalog"
      req = urllib2.Request(url,headers=hdr)
      page = urllib2.urlopen(req)
      html = page.read()
      startindex = string.find(html,'var catalog = {')
      endindex = string.find(html,'};',startindex)
      jsonsection = html[startindex+14:endindex+1]
      catalog = json.loads(jsonsection);

      #grab random OP
      threadURL = 'http://boards.4chan.org/d/thread/'+random.choice(catalog['threads'].keys())
      threadURL = threadURL.encode('ascii','ignore')
      #redirect to thread
      self.redirect(threadURL)

class RedirectNew(webapp2.RequestHandler):
    
    def get(self):
      self.redirect('http://kong-interstellar2.appspot.com')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/feedback',Feedback),
    ('/tasks/updatethread',UpdateThread),
    ('/roundtable',RoundTable),
    ('/currentmwo',RedirectCurrentMWO),
    ('/currentsc',RedirectCurrentSC),
    #('/currentcc',RedirectCurrentCC),
    ('/randomd',RedirectRandomD),
    ('/changes',Changes),
    ('/triplist',TripList)
], debug=True)