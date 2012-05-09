#!/usr/bin/env python
from wikitools import *
import datetime
import time
import settings
from Cheetah.Template import Template

date = datetime.date(2012, 5, 15)
site = wiki.Wiki("http://synhak.org/w/api.php")
site.login(settings.botName, settings.botPassword)

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
newMeetingPage.edit(summary="Created new meeting page", bot=True, text=unicode(meetingTemplate))

print "Moving [[Next Meeting]] to [[Last Meeting]]"
lastMeetingPage.edit(summary="Update previous meeting", bot=True, text=nextMeetingPage.getWikiText())

print "Updating [[Next Meeting]]"
nextMeetingPage.edit(summary="Update next meeting", bot=True, text="#Redirect [[%s]]"%(newMeetingTitle))
