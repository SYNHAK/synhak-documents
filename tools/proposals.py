#!/usr/bin/env python
from email.utils import parseaddr
from email.parser import Parser
from email.mime.text import MIMEText
import smtplib
import synhak
import settings
import optparse
import sys
import subprocess

parser = optparse.OptionParser()
parser.add_option("-d", "--dry-run", help="Don't actually send mails or edit pages. Just say what would happen.", default=False, action="store_true")
parser.add_option("-m", "--read-mail", help="Read a mail from stdin and handle it", default=False, action="store_true")
parser.add_option("-s", "--state-dir", help="Path to the directory where state is stored between runs", default="~/.local/share/Phong/", metavar="PATH")
parser.add_option("-e", "--send-mail", help="Address to send mail to. May be specified multiple times.", default=[], action="append", type="str", dest="mail_addresses")
parser.add_option("-l", "--mailman-whitelist", help="Mailman list(s) to check the sender against for whitelisting", default=[], action="append", type="str", dest="mailman_lists")
(options, args) = parser.parse_args()

api = synhak.API(settings.botName, settings.botPassword, dryRun=options.dry_run, stateDir=options.state_dir)

if options.read_mail:
  parser = Parser()
  msg = parser.parse(sys.stdin)
  proposalText = None
  for part in msg.walk():
    if part.get_content_type() == "text/plain":
      proposalText = part.get_payload()
      break

  whitelist = []
  for mailmanList in options.mailman_lists:
    for mail in subprocess.check_output(["/usr/lib/mailman/bin/list_members", mailmanList]).split("\n"):
      whitelist.append(mail.strip())

  fromAddr = parseaddr(msg.get('From'))[1]
  if fromAddr in whitelist or len(whitelist) == 0:
    api.addProposal(msg.get('Subject'), proposalText, notifyMails=options.mail_addresses)
  else:
    api.rejectProposal(fromAddr, msg.get('Subject'), "You must be a member of SYNHAK.")
