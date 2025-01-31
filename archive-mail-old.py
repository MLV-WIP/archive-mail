#! /usr/local/bin/python3

import sys, os, re, getpass, signal, argparse, json, time, datetime

from imap_tools import MailBox, MailBoxFolderManager, MailBoxTls, MailMessage, AND, UidRange, H


class ArchiveGroup:
    def __init__(self, jsonconfig = None, name = None, dest = None, text_match = None, regex_match = None):
        if jsonconfig:
            self.name = jsonconfig['name']
            self.destination_folder = jsonconfig['destination_folder']
            self.text_match = [ ]
            if 'text_match' in jsonconfig['email_match']:
                self.text_match = jsonconfig['email_match']['text_match']
            self.regex_match = [ ]
            if 'regex_match' in jsonconfig['email_match']:
                for rm in jsonconfig['email_match']['regex_match']:
                    self.regex_match.append(re.compile(rm))
        else:
            self.name = name
            self.destination_folder = dest
            self.text_match = text_match
            self.regex_match = regex_match

    def __repr__(self):
        return f"ArchiveGroup: '{self.name}', '{self.destination_folder}', {self.text_match}, {self.regex_match}"

archiveGroups = [ ]


def ctrlcHandler(sig, frame):
    print("\n\n------------")
    summarize()
    print("------------\n")
    sys.exit(1)


results = [ ]
message_count = 0
message_folder_count = { }

def summarize():
    for f in message_folder_count:
        print(f"{f}: {message_folder_count[f]}")
    print(f"Messages processed: {message_count}")


#----------------------------------------------------------------------------
#
# main
#

args = None

def parseArgs():
    parser = argparse.ArgumentParser(description="IMAP4 mail archiver by age")
    parser.add_argument("-i", "--imapserver", help="Mail server IP or hostname; overrides JSON config if provided", required=True)
    parser.add_argument("-u", "--user", help="Username of mailbox user; overrides JSON config if provided", required=True)
    parser.add_argument("-f", "--folder", help="Folder to scan for messages (accepts multiple)", action="append", required=True)
    parser.add_argument("-d", "--destination", help="Destination folder messages are moved to", required=True)
    parser.add_argument("-D", "--days", help="Specifies age in days for archiving old email")
    parser.add_argument("-W", "--weeks", help="Specifies age in weeks for archiving old email")
    parser.add_argument("-M", "--months", help="Specifies age in months for archiving old email")
    parser.add_argument("-Y", "--years", help="Specifies age in months for archiving old email")

    global args
    args = parser.parse_args()

parseArgs()

folderNames = [ ]

mailServer = args.imapserver
username = args.user

signal.signal(signal.SIGINT, ctrlcHandler)


#----------------------------------------------------------------------------
#
# export mail FROM mail server TO database
#

print(f"EXPORT mail server: {mailServer}, username: {username}")

oldDate = datetime.datetime.now()
ageSpecified = False
if args.years:
    oldDate -= datetime.timedelta(days=(365.24 * int(args.years)))
    ageSpecified = True
if args.months:
    oldDate -= datetime.timedelta(days=(30.45 * args.months))
    ageSpecified = True
if args.weeks:
    oldDate -= datetime.timedelta(weeks=args.weeks)
    ageSpecified = True
if args.days:
    oldDate -= datetime.timedelta(days=args.days)
    ageSpecified = True
if not ageSpecified:
    oldDate -= datetime.timedelta(days=365.24)
    print(f"Defaulting age for archive to one year in the past")
print(f"Archive emails older than {oldDate}")

query = AND(date_lt=oldDate.date())

if args.folder:
    for folder in args.folder:
        folderNames.append(folder.lower())
print(f"Scanning folders: {folderNames}")

destFolder = args.destination

userpass = getpass.getpass()
with MailBox(mailServer).login(username, userpass) as mailbox:
    for folderName in folderNames:
        mailbox.folder.set(folderName)
        stat = mailbox.folder.status()
        print(f"{folderName}: {stat}")
        message_folder_count[folderName] = 0

        for msg in mailbox.fetch(query, headers_only=True):
            print(f"Msg UID: {msg.uid}, folder: {folderName}, date: {msg.date}, subj: '{msg.subject[0:19]}', len: {len(msg.text or msg.html)}, from: {msg.from_}")
            message_count += 1

            res = mailbox.move(msg.uid, destination_folder=destFolder)
            print(f"  ({message_count}) Moved message {folderName}/{msg.uid} {msg.date} {msg.from_}; result {res}")

            #result = f"  {msg.uid} '{folderName}'->'{destFolder}' {msg.date} {msg.from_} '{msg.subject[0:19]}': {res}"
            #results.append(result)

            message_folder_count[folderName] += 1

summarize()
