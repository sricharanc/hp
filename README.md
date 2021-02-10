# HF Email App
---

## Introduction

HF Email application is a standalone application for downloading, applying filter rules and perform various message actions over a single email message.
The email message can be present in any email client such as Gmail, Outlook, etc. Currently supports Gmail.

## Pre-requisites

```bash
python >=3.7.3
mysql >=5.7.16
```

For other requirements refer the requirements.txt file.

## Support

Currently supports the gmail API. Support can be additionally added for other clients as well.

## Design

Refer to the design folder to understand more about the design.

## Usage

### To authorize new email
```bash
python scripts/authorize_new_email_account.py abc@gmail.com gmail
```

### To fetch emails for a specific account
```bash
python scripts/fetch_emails.py specific_email abc@gmail.com gmail
```

### To fetch emails for all emails configured in our application
```bash
python scripts/fetch_emails.py all_emails
```

### To add new filter
```bash
python scripts/add_new_filter.py /host/hp/filter_rules/rule1.json
```

### To apply all exisiting filter to new email messages
```bash
python scripts/apply_filter.py
```
