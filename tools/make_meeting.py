#!/usr/bin/env python
from wikitools import *
import sys
import datetime
import time
import settings
import smtplib
from email.mime.text import MIMEText
from Cheetah.Template import Template
import optparse

parser = optparse.OptionParser()
parser.add_option("-d", "--dry-run", help="Don't actually send mails or edit pages. Just say what would happen.", default=False, action="store_true")
(options, args) = parser.parse_args()

site = wiki.Wiki("http://synhak.org/w/api.php")
site.login(settings.botName, settings.botPassword)

nextMeetingDateText = map(int, page.Page(site, "Next Meeting", followRedir=False).getWikiText().split("/")[1].replace("]", "").split("-"))
nextMeetingDate = datetime.date(nextMeetingDateText[2], nextMeetingDateText[1], nextMeetingDateText[0])
now = datetime.date.today()
if now > nextMeetingDate:
    date = nextMeetingDate+datetime.timedelta(days=7)
elif now == nextMeetingDate:
    time = datetime.date.today()
    print "There is a meeting scheduled for today. Sending mail."
    meetingMailTemplate = page.Page(site, "Meetings/Template/Mail")
    meetingMailTemplateContents = ""
    inTemplate = False
    for line in meetingMailTemplate.getWikiText().split("\n"):
        if "<phongTemplate>" in line:
            inTemplate = True
            continue
        if "</phongTemplate>" in line:
            inTemplate = False
        if inTemplate:
            meetingMailTemplateContents += line+"\n"
    namespace = {'date': nextMeetingDate, 'meetingLink': "http://synhak.org/wiki/Meetings/%d-%d-%d"%(nextMeetingDate.day, nextMeetingDate.month, nextMeetingDate.year)}
    mailTemplate = Template(meetingMailTemplateContents, searchList=[namespace])
    msg = MIMEText(unicode(mailTemplate))
    msg['Subject'] = "REMINDER: Meeting tonight!"
    msg['From'] = "phong@synhak.org <Phong>"
    msg['To'] = "devel@synhak.org, announce@synhak.org"
    s = smtplib.SMTP('localhost')
    if not options.dry_run:
      s.sendmail(msg['From'], msg['To'], msg.as_string())
      s.quit()
    sys.exit(0)
else:
    print "There is already a meeting scheduled for %s"%(nextMeetingDate)
    sys.exit(0)

meetingTemplateRaw = page.Page(site, "Meetings/Template")
meetingTemplateContents = ""
inTemplate = False
for line in meetingTemplateRaw.getWikiText().split("\n"):
    if "<phongTemplate>" in line:
        inTemplate = True
        continue
    if "</phongTemplate>" in line:
        inTemplate = False
    if inTemplate:
        meetingTemplateContents += line+"\n"

namespace = {'date': date}
meetingTemplate = Template(meetingTemplateContents, searchList=[namespace])

newMeetingTitle = "Meetings/%d-%d-%d"%(date.day, date.month, date.year)
print "Next meeting will be at %s"%(newMeetingTitle)

newMeetingPage = page.Page(site, newMeetingTitle)
lastMeetingPage = page.Page(site, "Last Meeting", followRedir=False)
nextMeetingPage = page.Page(site, "Next Meeting", followRedir=False)

print "Writing next meeting page"
if not options.dry_run:
  newMeetingPage.edit(summary="Created new meeting page", bot=True, text=unicode(meetingTemplate))

print "Moving [[Next Meeting]] to [[Last Meeting]]"
if not options.dry_run:
  lastMeetingPage.edit(summary="Update previous meeting", bot=True, text=nextMeetingPage.getWikiText())

print "Updating [[Next Meeting]]"
if not options.dry_run:
  nextMeetingPage.edit(summary="Update next meeting", bot=True, text="#Redirect [[%s]]"%(newMeetingTitle))
