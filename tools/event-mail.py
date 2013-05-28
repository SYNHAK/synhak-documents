#!/usr/bin/env python
import argparse
import spiff
import dateutil.parser
from dateutil import tz
import datetime
import optparse
import settings
from email.mime.text import MIMEText
import smtplib
import synhak

parser = optparse.OptionParser()
parser.add_option("-s", "--state-dir", help="Path to the directory where state is stored between runs", default="~/.local/share/Phong/", metavar="PATH")
parser.add_option("-d", "--dry-run", help="Don't actually send mails or edit pages. Just say what would happen.", default=False, action="store_true")
parser.add_option("-p", "--period", help="Days to look ahead (0 for today)", default=7)
parser.add_option("-e", "--mail", help="Address to send mail to. May be specified multiple times.", default=[], action="append", type="str", dest="mail_addresses")

(options, args) = parser.parse_args()

spiffAPI = spiff.API("https://synhak.org/auth/", verify=False)
api = synhak.API(settings.botName, settings.botPassword, dryRun=options.dry_run, stateDir=options.state_dir)

upcoming = []

period = options.period
dateFormat = "%A, %d. %B %Y %I:%M%p"

for e in spiffAPI.events():
  now = datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
  start = dateutil.parser.parse(e['start']).astimezone(tz.tzlocal())
  end = dateutil.parser.parse(e['end']).astimezone(tz.tzlocal())
  if now < end and now+datetime.timedelta(days=period) > start:
    upcoming.append(e)

if len(upcoming) > 0 and len(options.mail_addresses):
  params = {}
  params['greeting'] = api.randomGreeting()
  params['period'] = period
  for evt in upcoming:
    organizers = []
    for u in evt['organizers']+[evt['creator'],]:
      organizers.append("%s %s"%(u['user']['first_name'], u['user']['last_name']))
    evt['organizers'] = ', '.join(organizers)
  params['upcoming'] = upcoming
  template = synhak.TemplatePage(api, "PhongTemplates/EventMail", params)
  msg = MIMEText(unicode(template))
  msg['Subject'] = "Upcoming Events"
  msg['From'] = 'phong@synhak.org <Phong>'
  msg['To'] = ','.join(options.mail_addresses)
  print "Sending mail to", msg['To']
  if not options.dry_run:
    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], options.mail_addresses, msg.as_string())
    s.quit()
  else:
    print msg.as_string()
