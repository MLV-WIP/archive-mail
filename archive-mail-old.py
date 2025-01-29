#! /usr/local/bin/python3

import sys, os, re, getpass, signal, argparse, json, time

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


message_group_count = { }

def incrMsgGrp(name):
    if name in message_group_count:
        message_group_count[name] += 1
    else:
        message_group_count[name] = 1


results = [ ]
message_count = 0
matches = 0

def summarize():
    for result in results:
        print(result)
    print(f"Messages processed: {message_count}")
    print(f"Matches found: {matches}")
    for f in message_group_count:
        print(f"\t{f}: {message_group_count[f]}")


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
    parser.add_argument("-M", "--months", help="Specifies age in months for archiving old email")
    parser.add_argument("-Y", "--years", help="Specifies age in months for archiving old email")

    global args
    args = parser.parse_args()

parseArgs()

mailServer = ""
username = ""

folderNames = [ ]

if args.jsonconfig:
    with open(args.jsonconfig, 'r') as file:
        config = json.load(file)

        if config:
            if 'server' in config:
                mailServer = config['server']['host']
                username = config['server']['user']
            
            for sf in config['search_folders']:
                folderNames.append(sf.lower())

            for ag_data in config['archive_groups']:
                ag = ArchiveGroup(ag_data)
                archiveGroups.append(ag)

if args.imapserver: # override config file
    mailServer = args.imapserver

if args.user: # override config file
    username = args.user

signal.signal(signal.SIGINT, ctrlcHandler)


#----------------------------------------------------------------------------
#
# export mail FROM mail server TO database
#

print(f"EXPORT mail server: {mailServer}, username: {username}")

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

if args.folder:
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

destFolder = args.destination

ag = ArchiveGroup(name="", dest=destFolder, text_match=stringAddrs, regex_match=regexAddrs)

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

                for ag in archiveGroups:
                    for addr in ag.text_match:
                        if msg.from_.lower() == addr:
                            print(f"matched {msg.from_}")
                            found = True
                            break
                    if not found:
                        for addr in ag.regex_match:
                            m = addr.match(msg.from_)
                            if m:
                                print(f"matched {msg.from_} ({addr.pattern})")
                                found = True
                                break
                    if found:
                        print(f">>> Found match for {ag.name}")
                        matches += 1
                        incrMsgGrp(ag.name)

                        res = mailbox.move(msg.uid, ag.destination_folder)
                        print(f"\aMoved message {msg.uid}; result {res}")
                        time.sleep(1.0)

                        result = f"{msg.uid} '{folderName}' '{ag.destination_folder}' {msg.date} {msg.from_} '{msg.subject[0:19]}': {res}"
                        results.append(result)

                        break

            message_count += 1

summarize()
