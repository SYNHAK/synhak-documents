#!/usr/bin/env python
import synhak
import settings
import optparse

parser = optparse.OptionParser()
parser.add_option("-d", "--dry-run", help="Don't actually send mails or edit pages. Just say what would happen.", default=False, action="store_true")
parser.add_option("-r", "--remind", help="Send out the reminder mail, if one is needed.", default=False, action="store_true")
parser.add_option("-w", "--wiki", help="Update the wiki", default=False, action="store_true")
parser.add_option("-s", "--state-dir", help="Path to the directory where state is stored between runs", default="~/.local/share/Phong/", metavar="PATH")
parser.add_option("-m", "--minutes", help="Send mail about posted minutes", default=False, action="store_true")
(options, args) = parser.parse_args()

api = synhak.API(settings.botName, settings.botPassword, dryRun=options.dry_run, stateDir=options.state_dir)

if options.minutes:
  if api.alreadySentMinutes():
    print "Already mailed out the last meeting minutes."
  elif api.minutesReadyToBeSent():
    api.mailLastMinutes()
  else:
    print "Minutes not yet ready to be sent."

if options.wiki:
  api.makeNextMeeting()

if options.remind:
  if api.isThereAMeetingToday():
    if api.alreadyRemindedAboutMeeting():
      print "Already sent a mail for today."
    else:
      api.remindAboutNextMeeting()
  else:
    print "No meeting today. Not sending reminder mail."
