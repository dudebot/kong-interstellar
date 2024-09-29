import cgi
import urllib2, string, json, codecs
import time
import webapp2


def update_4chan_json():
  lastThreadNumber=0;
  lastThreadReplyCount=0;

  url = "http://boards.4chan.org/vg/catalog"
  page = urllib2.urlopen(url,data=None)

  html = page.read()

  startindex = string.find(html,'var catalog = {')
  endindex = string.find(html,'};',startindex)
  #print startindex
  #print endindex

  jsonsection = html[startindex+14:endindex]+'}'
  dictionary = json.loads(jsonsection);
  threadURL="";

  for x in dictionary['threads'].keys(): # list of all thread numbers, each thread contains: r, i, sub, author, tn_w, teaser, lr, tn_h, date, imgurl
    #print x
    #for y in dictionary['threads'][x]:
    # print y
    if 'mechwarrior online' in dictionary['threads'][x]['teaser'].lower() and \
        ((dictionary['threads'][x]['r'] > lastThreadReplyCount and \
        dictionary['threads'][x]['r'] < 750 ) or lastThreadReplyCount is 0 or lastThreadReplyCount >= 750): 
      threadURL = 'https://boards.4chan.org/vg/res/'+x
      lastThreadNumber = x
      lastThreadReplyCount = dictionary['threads'][x]['r']

  #now do stuff with threadURL and 
  #                  dictionary[threads][lastThreadNumber][...]



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


app = webapp2.WSGIApplication([
    ('/updatethread', UpdateThread) 
], debug=True)