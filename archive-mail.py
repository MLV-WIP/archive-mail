#! /usr/local/bin/python3

import sys, os, re, getpass, signal, uuid, email, hashlib, argparse, datetime

from imap_tools import MailBox, MailBoxFolderManager, MailBoxTls, MailMessage, AND, UidRange, H


def ctrlcHandler(sig, frame):
    print("------------\n\n")


#----------------------------------------------------------------------------
#
# main
#

args = None

def parseArgs():
    parser = argparse.ArgumentParser(description="IMAP4 mail exporter/importer")
    parser.add_argument("-i", "--imapserver", help="Mail server IP or hostname", required=True)
    parser.add_argument("-u", "--user", help="Username of mailbox user", required=True)
    parser.add_argument("-f", "--folder", help="Folder to scan for messages (accepts multiple)", action="append", required=True)
    parser.add_argument("-s", "--sender", help="Sender email address to scan (text match) (accepts multiple)", action="append")
    parser.add_argument("-r", "--senderregex", help="Sender email address to scan (regex match) (accepts multiple)", action="append")
    parser.add_argument("-t", "--target", help="Target folder messages are moved to", required=True)

    global args
    args = parser.parse_args()

parseArgs()

username = args.user

#signal.signal(signal.SIGINT, ctrlcHandler)


#----------------------------------------------------------------------------
#
# export mail FROM mail server TO database
#

mailServer = args.imapserver

print(f"EXPORT mail server: {mailServer}, username: {username}")

global message_count
message_count = 0
matches = 0

query = AND(all=True)
"""
if args.month:
    lastMonth = datetime.datetime.now() - datetime.timedelta(days=31)
    query = AND(date_gte=lastMonth.date())
elif args.week:
    lastWeek = datetime.datetime.now() - datetime.timedelta(weeks=1)
    query = AND(date_gte=lastWeek.date())
else:
    query = AND(all=True)
"""

folderNames = [ ]
for folder in args.folder:
    folderNames.append(folder.lower())
print(f"Scanning folders: {folderNames}")

stringAddrs = [ ]
if args.sender:
    for addr in args.sender:
        stringAddrs.append(addr.lower())
    print(f"String-match addresses: {stringAddrs}")

regexAddrs = [ ]
if args.senderregex:
    for addr in args.senderregex:
        reAddr = re.compile(addr, re.IGNORECASE)
        regexAddrs.append(reAddr)
    print(f"Regex address matchers: {len(regexAddrs)}")

targetFolder = args.target

results = [ ]

userpass = getpass.getpass()
with MailBox(mailServer).login(username, userpass) as mailbox:
    for folderName in folderNames:
        mailbox.folder.set(folderName)
        stat = mailbox.folder.status()
        print(f"{folderName}: {stat}")

        for msg in mailbox.fetch(query, headers_only=True):
            print(f"Msg UID: {msg.uid}, folder: {folderName}, date: {msg.date}, subj: '{msg.subject[0:19]}', len: {len(msg.text or msg.html)}, from: {msg.from_}")

            if msg.from_:
                found = False
                for addr in stringAddrs:
                    if msg.from_.lower() == addr:
                        print(f"matched {msg.from_}")
                        found = True
                        break
                if not found:
                    for addr in regexAddrs:
                        m = addr.match(msg.from_)
                        if m:
                            print(f"matched {msg.from_} ({addr.pattern})")
                            found = True
                            break
                if found:
                    print(">>> Found match")
                    matches += 1

                    res = mailbox.move(msg.uid, targetFolder)
                    print(f"Moved message {msg.uid}; result {res}")

                    result = f"{msg.uid} {folderName} {msg.date} {msg.from_} {msg.subject[0:19]}: {res}"
                    results.append(result)

            message_count += 1

for result in results:
    print(result)
print(f"Messages processed: {message_count}")
print(f"Matches found: {matches}")
