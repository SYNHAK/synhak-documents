#!/usr/bin/env python
import synhak
import settings
import optparse
import datetime

parser = optparse.OptionParser()
parser.add_option("-s", "--state-dir", default="~/.local/share/Phong/")

(options, args) = parser.parse_args()

api = synhak.API(settings.botName, settings.botPassword, dryRun=True,
    stateDir=options.state_dir)

current = api.getMeeting(api.nextMeetingDate())
while current.alreadyExists():
  print current.templateParams()['previous'], '<-', current._pageName, '->', current.templateParams()['next']
  current.adjustSequenceLinks()
  previous = current.previousMeeting()
  if not previous.alreadyExists():
    date = current._date
    for i in range(1, 14):
      print "Couldn't find %s, looking back %d days..."%(previous._pageName, i)
      date += datetime.timedelta(days=-i)
      check = api.getMeeting(date)
      if check.alreadyExists():
        previous = check
        break
  if not previous.alreadyExists():
    print "Couldn't find the meeting before", current._pageName
    break
  current = previous
