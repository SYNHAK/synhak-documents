#!/usr/bin/env python
from wikitools import *
import datetime
from Cheetah.Template import Template
import os
import json
from email.mime.text import MIMEText
import smtplib
import random

class API(object):
  def __init__(self, username, password, api="http://synhak.org/w/api.php", baseURI="http://synhak.org/wiki/", dryRun=False, stateDir="~/.local/share/Phong/"):
    self._site = wiki.Wiki(api)
    self._dry = dryRun
    self._site.login(username, password)
    self._uri = baseURI
    self._stateDir = os.path.expanduser(stateDir)
    self._state = State(os.path.sep.join((self._stateDir, "state.json")))

  def getPage(self, pageName, *args, **kwargs):
    return page.Page(self._site, pageName, *args, **kwargs)

  def lastMeetingDate(self):
    return self.nextMeetingDate()+datetime.timedelta(days=-7)

  def nextMeetingDate(self):
    stamp = map(int, self.getPage("Next Meeting", followRedir=False).getWikiText().split("/")[1].replace("]", "").split("-"))
    nextDate = datetime.date(stamp[2], stamp[1], stamp[0])
    now = datetime.date.today()
    if now > nextDate:
      nextDate = nextDate+datetime.timedelta(days=7)
    return nextDate

  def getMeeting(self, date):
    return Meeting(self, date)

  def minutesReadyToBeSent(self):
    lastMeeting = self.getMeeting(self.lastMeetingDate())
    return "<phongMinutesNotReady/>" not in lastMeeting.getWikiText()

  def mailLastMinutes(self, addresses=[]):
    lastMeeting = self.getMeeting(self.lastMeetingDate())
    params = lastMeeting.templateParams()
    params['minutes'] = lastMeeting.getWikiText()
    mailTemplate = TemplatePage(self, "Meetings/Template/FinishedMail", params)
    msg = MIMEText(unicode(mailTemplate), _charset="utf-8")
    msg['Subject'] = "Meeting minutes from %s"%(self.lastMeetingDate())
    msg['From'] = "phong@synhak.org <Phong>"
    msg['To'] = ', '.join(addresses)
    print "Sending mail about updated minutes"
    if not self._dry:
      s = smtplib.SMTP('localhost')
      s.sendmail(msg['From'], addresses, msg.as_string())
      s.quit()
      self._state['meetings'][str(self.lastMeetingDate())]['minutesSent'] = True
    else:
      print msg.as_string()

  def alreadySentMinutes(self):
    return bool(self._state['meetings'][str(self.lastMeetingDate())]['minutesSent'])

  def makeNextMeeting(self):
    lastMeeting = self.lastMeetingDate()
    nextMeeting = self.nextMeetingDate()
    nextPage = page.Page(self._site, "Next Meeting", followRedir=False)
    lastPage = page.Page(self._site, "Last Meeting", followRedir=False)

    nextMeetingPage = self.getMeeting(nextMeeting)
    if nextMeetingPage.alreadyExists():
      print "Next meeting page already exists!"
      return False
    template = TemplatePage(self, "Meetings/Template", nextMeetingPage.templateParams())
    print "Creating next meeting at %s"%(nextMeetingPage.templateParams()['meetingLink'])
    if not self._dry:
      nextMeetingPage.edit(summary="Created new meeting page", bot=True, text=unicode(template))
    print "Updating [[Last Meeting]]"
    if not self._dry:
      lastPage.edit(summary="Update previous meeting link", bot=True, text=nextPage.getWikiText())
    print "Updating [[Next Meeting]]"
    if not self._dry:
      nextPage.edit(summary="Update next meeting link", bot=True, text="#Redirect [[Meetings/%s]]"%(Meeting.formatMeetingDate(nextMeeting)))

  def randomGreeting(self):
    greetingPage = page.Page(self._site, "User:Phong/Greetings")
    greetings = []
    for line in greetingPage.getWikiText().split("\n"):
      if line.startswith("*"):
        greetings.append(line[1:].strip())
    return random.choice(greetings)

  def rejectProposal(self, address, subject, reason):
    params = {}
    params['subject'] = subject
    params['greeting'] = self.randomGreeting()
    params['reason'] = reason
    template = TemplatePage(self, "Proposals/Template/RejectMail", params)
    msg = MIMEText(unicode(template))
    msg['Subject'] = "Your proposal was rejected!"
    msg['From'] = 'phong@synhak.org <Phong>'
    msg['To'] = address
    print "Rejecting proposal '%s': %s"%(subject, reason)
    if not self._dry:
      s = smtplib.SMTP('localhost')
      s.sendmail(msg['From'], address, msg.as_string())
      s.quit()
    else:
      print msg

  def addProposal(self, subject, proposalText, date=None, notifyMails=[]):
    if date is None:
      date = datetime.date.today()
    proposalsPage = self.getPage("Proposals/Open")
    table,tableEnd = proposalsPage.getWikiText().split("|}", 2)
    newText = "%s\n|-\n|%s\n|%s|}%s"%(table, date, proposalText, tableEnd)
    print "Updating [[Proposals/Open]]"
    if not self._dry:
      proposalsPage.edit(summary="New proposal added", bot=True, text=newText)
    else:
      print newText
    params = {}
    params['subject'] = subject
    params['text'] = proposalText
    params['greeting'] = self.randomGreeting()
    mailTemplate = TemplatePage(self, "Proposals/Template/Mail", params)
    msg = MIMEText(unicode(mailTemplate))
    msg['Subject'] = 'New Proposal'
    msg['From'] = 'phong@synhak.org <Phong>'
    msg['To'] = ', '.join(notifyMails)
    print "Sending mail to", notifyMails
    if not self._dry:
      s = smtplib.SMTP('localhost')
      s.sendmail(msg['From'], notifyMails, msg.as_string())
      s.quit()
    else:
      print msg

  def isThereAMeetingToday(self):
    now = datetime.date.today()
    if now == self.nextMeetingDate():
      return True

  def remindAboutNextMeeting(self, addresses=[]):
    nextMeeting = self.getMeeting(self.nextMeetingDate())
    mailTemplate = TemplatePage(self, "Meetings/Template/Mail", nextMeeting.templateParams())
    msg = MIMEText(unicode(mailTemplate))
    msg['Subject'] = "REMINDER: Meeting tonight!"
    msg['From'] = "phong@synhak.org <Phong>"
    msg['To'] = ', '.join(addresses)
    print "Sending reminder mail."
    if not self._dry:
      s = smtplib.SMTP('localhost')
      s.sendmail(msg['From'], addresses, msg.as_string())
      s.quit()
      self._state['meetings'][str(self.nextMeetingDate())]['reminderSent'] = True
    else:
      print msg.as_string()

  def alreadyRemindedAboutMeeting(self):
    return bool(self._state['meetings'][str(self.nextMeetingDate())]['reminderSent'])

class StateVar(object):
  def __init__(self, value=None, parent=None):
    self._value = value
    self._parent = parent
    self._data = {}

  def __getitem__(self, key):
    assert isinstance(key, str)
    if key not in self._data:
      self._data[key] = StateVar()
    return self._data[key]

  def __setitem__(self, key, value):
    assert isinstance(key, str)
    self._data[key] = StateVar(value)

  def __delitem__(self, key):
    assert isinstance(key, str)
    del self._data[key]
    self.save()

  def __cmp__(self, other):
    if not isinstance(other, type(self._value)):
      return False
    return self._value.__cmp__(self._value)

  def __unicode__(self):
    return self._value.__unicode__()

  def __str__(self):
    return self._value.__str__()

  def __repr__(self):
    return repr(self.toDict())

  def __nonzero__(self):
    if self._value is None:
      return False
    return self._value.__nonzero__()
  
  def save(self):
    if self._parent is not None:
      self._parent.save()

  def toDict(self):
    keys = {}
    for key in self._data.iterkeys():
      keys[key] = self._data[key].toDict()
    d = {}
    if self._value is not None:
      d['value'] = self._value
    if len(keys) > 0:
      d['keys'] = keys
    return d

  def loadFromDict(self, data):
    if 'value' in data:
      self._value = data['value']
    if 'keys' in data:
      for key in data['keys']:
        self._data[key] = StateVar()
        self._data[key].loadFromDict(data['keys'][key])

class State(StateVar):
  def __init__(self, filename):
    super(State, self).__init__()
    self._filename = filename
    self.load()

  def load(self, filename=None):
    if filename == None:
      filename = self._filename
    data = json.load(open(filename))
    self.loadFromDict(data)

  def save(self, filename=None):
    if filename == None:
      filename = self._filename
    if not os.path.exists(os.path.dirname(filename)):
      os.makedirs(os.path.dirname(filename))
    json.dump(self.toDict(), open(filename, "w"), indent=4)

  def __del__(self):
    self.save()

class TemplatePage(object):
  def __init__(self, api, pageName, searchList):
    self._page = page.Page(api._site, pageName)
    self._search = searchList

  @staticmethod
  def extractTemplateContents(text):
    contents = ""
    inTemplate = False
    for line in text.split("\n"):
      if "<phongTemplate>" in line:
        inTemplate = True
        continue
      if "</phongTemplate>" in line:
        inTemplate = False
      if inTemplate:
        contents += line+"\n"
    return contents

  def __unicode__(self):
    return self.toString()

  def __str__(self):
    return self.__unicode__()

  def toString(self):
    template = Template(TemplatePage.extractTemplateContents(self._page.getWikiText()), self._search)
    return unicode(template)

class MeetingMeta(object):
  def __init__(self, meeting, infoboxText):
    self._meeting = meeting
    self._raw = infoboxText
    self.params = {}
    args = self._raw.split('|')
    curArg = []
    realArgs = []
    for arg in args[1:]:
      if "=" in arg and len(curArg) > 0:
        realArgs.append('|'.join(curArg).strip())
        curArg = []
      curArg.append(arg)
    if len(curArg) > 0:
      realArgs.append('|'.join(curArg))
    for arg in realArgs:
      try:
        (param, value) = map(lambda x:x.strip(), arg.split('=', 1))
      except ValueError:
        print "Couldn't pull metadata from", arg
        raise
      self.params[param] = value

  def __repr__(self):
    ret = "{{Infobox_meeting\n"
    params = []
    if len(self.params) > 0:
      ret += "|"
    for k,v in self.params.iteritems():
      params.append("%s = %s"%(k, v))
    ret += '\n|'.join(params)
    ret += "\n}}"
    return ret

  def __eq__(self, other):
    if len(self.params) != len(other.params):
      return False
    for k,v in self.params.iteritems():
      if k in other.params:
        if v != other.params[k]:
          return False
      else:
        return False
    return True

class Meeting(page.Page):

  @staticmethod
  def formatMeetingDate(date):
    assert isinstance(date, datetime.date)
    return "%d-%d-%d"%(date.day, date.month, date.year)

  def __init__(self, api, date, *args, **kwargs):
    self._date = date
    self._pageName = "Meetings/%s"%(Meeting.formatMeetingDate(date))
    self._api = api
    super(Meeting, self).__init__(api._site, self._pageName, *args, **kwargs)

  def templateParams(self):
    return {
      'date': self._date,
      'meetingLink': "%s%s"%(self._api._uri, self._pageName),
      'greeting': self._api.randomGreeting(),
      'next': "%s"%(self.nextMeeting()._pageName),
      'previous': "%s"%(self.previousMeeting()._pageName)
    }

  def nextMeeting(self):
    if self.alreadyExists() and 'next' in self.meta().params:
      (day, month, year) = map(int,
          self.meta().params['next'].split('/')[1].split('-'))
      stamp = datetime.date(day=day, month=month, year=year)
      return self._api.getMeeting(stamp)
    return self._api.getMeeting(self._date + datetime.timedelta(days=7))

  def previousMeeting(self):
    if self.alreadyExists() and 'previous' in self.meta().params:
      (day, month, year) = map(int,
          self.meta().params['previous'].split('/')[1].split('-'))
      stamp = datetime.date(day=day, month=month, year=year)
      return self._api.getMeeting(stamp)
    return self._api.getMeeting(self._date + datetime.timedelta(days=-7))

  def meta(self):
    templates = self.getWikiText().split('{{')
    for template in templates:
      if template.startswith('Infobox'):
        (infobox,foo) = template.split('}}', 1)
        return MeetingMeta(self, infobox)

  def setMeta(self, meta):
    if self.meta() == meta:
      return
    text = ''
    templates = self.getWikiText().split('{{')
    for template in templates:
      if template.startswith('Infobox'):
        (infobox, foo) = template.split('}}', 1)
        text += repr(meta) + foo
      else:
        text += template
    self.edit(summary="Update meeting links", bot=True, text=text)

  def adjustSequenceLinks(self):
    previous = self.previousMeeting()
    next = self.nextMeeting()
    meta = self.meta()
    meta.params['previous'] = previous._pageName
    meta.params['next'] = next._pageName
    self.setMeta(meta)

  def alreadyExists(self):
    try:
      self.getWikiText()
      return True
    except:
      return False

if __name__ == "__main__":
  import settings
  api = API(settings.botName, settings.botPassword)
  api.makeNextMeeting()
