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
parser.add_option("-p", "--period", help="Days to look ahead (0 to only handle today's events)", default=7)
parser.add_option("-w", "--wiki", help="Update the wiki", default=False, action="store_true")
parser.add_option("-e", "--mail", help="Address to send mail to. May be specified multiple times.", default=[], action="append", type="str", dest="mail_addresses")

(options, args) = parser.parse_args()

spiffAPI = spiff.API("https://synhak.org/auth/", verify=False)
api = synhak.API(settings.botName, settings.botPassword, dryRun=options.dry_run, stateDir=options.state_dir)

upcoming = []
today = []

period = options.period
dateFormat = "%A, %d. %B %Y %I:%M%p"

for e in spiffAPI.events():
  now = datetime.datetime.utcnow().replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
  start = dateutil.parser.parse(e['start']).astimezone(tz.tzlocal())
  end = dateutil.parser.parse(e['end']).astimezone(tz.tzlocal())
  if period > 0 and now < end and now+datetime.timedelta(days=period) > start:
    upcoming.append(e)
  if now < end and now+datetime.timedelta(days=1) > start:
    today.append(e)
  e['start'] = start.strftime(dateFormat)
  e['end'] = end.strftime(dateFormat)

params = {}
params['greeting'] = api.randomGreeting()
params['period'] = period
mailEvents = []
for evt in upcoming:
  if bool(api._state['events'][str(evt['id'])]['mailSent']) == False:
    mailEvents.append(evt)
  organizers = []
  for u in evt['organizers']+[evt['creator'],]:
    organizers.append("%s %s"%(u['user']['first_name'], u['user']['last_name']))
  evt['organizers'] = ', '.join(organizers)
params['upcoming'] = upcoming
params['newEvents'] = mailEvents
params['today'] = today

if options.wiki:
  reportTemplate = synhak.TemplatePage(api, "PhongTemplates/EventList", params)
  reportPage = api.getPage("PhongPages/EventList")
  print "Updating [[PhongPages/EventList]]"
  if not options.dry_run:
    reportPage.edit(summary="Event Update", bot=True, text=unicode(reportTemplate))
  else:
    print reportTemplate

if len(options.mail_addresses) > 0 and (len(mailEvents) > 0 or len(today) > 0):
  mailTemplate = synhak.TemplatePage(api, "PhongTemplates/EventMail", params)
  msg = MIMEText(unicode(mailTemplate))
  msg['Subject'] = "Upcoming Events for %s"%(datetime.date.today().strftime("%A %d %B %Y"))
  msg['From'] = 'phong@synhak.org <Phong>'
  msg['To'] = ','.join(options.mail_addresses)
  print "Sending mail to", msg['To']
  for evt in mailEvents:
    api._state['events'][str(evt['id'])]['mailSent'] = True
  if not options.dry_run:
    s = smtplib.SMTP('localhost')
    s.sendmail(msg['From'], options.mail_addresses, msg.as_string())
    s.quit()
  else:
    print msg.as_string()
