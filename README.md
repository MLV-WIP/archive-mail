# Archive Mail Script

## Overview

The `archive-mail-from.py` script automatically organizes email messages by moving them from source folders to destination folders based on sender email address matching patterns. Using IMAP, the script scans specified mail folders for messages matching configured email addresses (both exact text matches and regex patterns) and moves matching messages to designated destination folders.

## Purpose

This script helps automate email organization by:
- Scanning IMAP mail folders for messages from specific senders
- Supporting both exact email address matches and flexible regex pattern matching
- Moving matching messages to organized destination folders
- Providing detailed statistics and processing summaries
- Supporting both simple command-line configuration and rich JSON-based configuration

## Configuration Options

The script supports two configuration approaches:

### 1. JSON Configuration (Recommended)
Rich, expressive configuration supporting multiple archive groups with complex matching rules.

### 2. Command-Line Arguments
Simplified configuration for single archive operations.

**Note**: You can use either approach independently. Command-line arguments can override specific JSON configuration values when both are provided.

## Command-Line Parameters

```
python3 archive-mail-from.py [OPTIONS]
```

### Options

| Parameter | Description |
|-----------|-------------|
| `-j, --jsonconfig` | JSON configuration file path |
| `-i, --imapserver` | IMAP server hostname/IP (overrides JSON config) |
| `-u, --user` | Username for mailbox access (overrides JSON config) |
| `-f, --folder` | Source folder to scan (can specify multiple times) |
| `-s, --sender` | Sender email for exact text match (can specify multiple times) |
| `-r, --senderregex` | Sender email regex pattern (can specify multiple times) |
| `-d, --destination` | Destination folder for matched messages |

## JSON Configuration Format

The JSON configuration file provides rich functionality for defining multiple archive groups:

```json
{
    "server": {
        "host": "your-imap-server.com",
        "user": "username@domain.com"
    },
    "search_folders": [
        "INBOX",
        "Archive"
    ],
    "archive_groups": [
        {
            "name": "Group Name",
            "destination_folder": "Target/Folder/Path",
            "email_match": {
                "text_match": [
                    "exact@email.com",
                    "another@email.com"
                ],
                "regex_match": [
                    "pattern@(domain1|domain2)\\.com",
                    "user[0-9]+@example\\.org"
                ]
            }
        }
    ]
}
```

### Configuration Elements

- **server**: IMAP server connection details
  - `host`: IMAP server hostname or IP
  - `user`: Username for authentication
- **search_folders**: Array of folder names to scan for messages
- **archive_groups**: Array of archive group definitions
  - `name`: Descriptive name for the archive group
  - `destination_folder`: Target folder path for matched messages
  - `email_match`: Matching criteria
    - `text_match`: Array of exact email addresses to match
    - `regex_match`: Array of regex patterns for flexible matching

## Usage Examples

### Using JSON Configuration

```bash
# Use comprehensive JSON configuration
python3 archive-mail-from.py -j config.json

# Use JSON config but override server settings
python3 archive-mail-from.py -j config.json -i different-server.com -u other-user@domain.com
```

### Using Command-Line Arguments

```bash
# Simple exact email match
python3 archive-mail-from.py -i imap.gmail.com -u user@gmail.com -f INBOX -s sender@domain.com -d "Archive/Important"

# Multiple folders and senders with regex
python3 archive-mail-from.py -i imap.server.com -u user@domain.com \
    -f INBOX -f "Sent Items" \
    -s exact@email.com -s another@email.com \
    -r "newsletter.*@company\\.com" \
    -d "Archive/Newsletters"
```

## Script Behavior

1. **Authentication**: Prompts for password securely using `getpass`
2. **Folder Scanning**: Iterates through specified folders and processes messages
3. **Pattern Matching**: Checks each message's sender against configured patterns
4. **Message Moving**: Moves matching messages to destination folders
5. **Progress Reporting**: Shows real-time processing updates and final statistics
6. **Error Handling**: Supports Ctrl+C interruption with summary display

## Output and Reporting

The script provides:
- Real-time message processing updates
- Match notifications with pattern details  
- Move operation results
- Final summary including:
  - Total messages processed
  - Total matches found
  - Breakdown by archive group
  - Detailed operation log

## Dependencies

- Python 3.x
- `imap_tools` library
- Standard libraries: `sys`, `os`, `re`, `getpass`, `signal`, `argparse`, `json`, `time`

## Installation

```bash
pip install imap-tools
```

## Example Template

See `example-template.json` for a sample configuration file with randomized data demonstrating the JSON configuration format.

## Implementation detail

AI (ChatGPT) was used to assist in writing database queries and some python library API calls. The rest of the code was written by hand using iterative development on live servers.

AI (Claude Code) was used to generate the README based on guided prompts and analysis of the code.
