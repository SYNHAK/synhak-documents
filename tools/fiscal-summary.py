#!/usr/bin/env python
import gnucash
import synhak
import optparse
import settings
import datetime
import os
from email.mime.text import MIMEText
import smtplib

parser = optparse.OptionParser()
parser.add_option("-d", "--dry-run", help="Don't actually send mails or edit pages. Just say what would happen.", default=False, action="store_true")
parser.add_option("-s", "--state-dir", help="Path to the directory where state is stored between runs", default="~/.local/share/Phong/", metavar="PATH")
parser.add_option("-w", "--wiki", help="Update the wiki", default=False, action="store_true")
parser.add_option("-e", "--mail", help="Address to send mail to. May be specified multiple times.", default=[], action="append", type="str", dest="mail_addresses")

(options, args) = parser.parse_args()

timestamp = datetime.datetime.fromtimestamp(os.stat(args[0]).st_mtime)
book = gnucash.Book(args[0])

report = []

for acct in book.accounts:
    depth = -1
    root = acct
    while root is not None:
        depth+=1
        root = root.parent

    report.append(' '.join(map(str, ((" "*depth, acct, acct.value)))))

api = synhak.API(settings.botName, settings.botPassword, dryRun=options.dry_run, stateDir=options.state_dir)
params = {"timestamp": timestamp, "report": "\n".join(report), "greeting": api.randomGreeting()}
if options.wiki:
    reportTemplate = synhak.TemplatePage(api, "Financial Report/Template", params)
    reportPage = api.getPage("Financial Report")
    print "Updating [[Financial Report]]"
    if not api._dry:
        reportPage.edit(summary="Report Update", bot=True, text=unicode(reportTemplate))
    else:
        print reportTemplate

if len(options.mail_addresses) > 0:
    reportTemplate = synhak.TemplatePage(api, "Financial Report/Mail Template", params)
    msg = MIMEText(unicode(reportTemplate))
    msg['Subject'] = 'Financial Report'
    msg['From'] = 'phong@synhak.org <Phong>'
    msg['To'] = ','.join(options.mail_addresses)
    print "Sending mail to", msg['To']
    if not api._dry:
        s = smtplib.SMTP('localhost')
        s.sendmail(msg['From'], options.mail_addresses, msg.as_string())
        s.quit()
    else:
        print msg.as_string()
