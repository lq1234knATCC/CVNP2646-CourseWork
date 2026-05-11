Overview
This is a phishing analysis tool meant to parse and detect if an email may be malicious using some common indicators of a phishing attacks, like keywords trying to make you act quickly or reset a password, attachment types and double endings on attachments, like a file named taxes.txt.exe. It assigns all emails a risk value that could be used to determine what is in need of addressing first or to find the biggest threats. it reads over an email.json file and has other files like whitelist that can be used to expand the amount of domains that the program will think of as safe. this week it also features working domain detection including subdomains. an example of this is one of my whitelisted domains being microsoft.com, but an email with accounts.microsoft.com is also considered safe because it is included in the subdomain. this tool is similar to something you could see deployed at a large company in thier it department.

Problem Statement
Email phishing attacks are easily the most present threats in the online world the sources I have seen varied in numbers quite a bit, but I have seen sites claim 75-90% of cyberattacks originate from phishing. phishing attacks are successful because the socially manipulate the reader by using spoofed sender addresses, fake links, and pushy language this tool tackles some of those big issues to hopefully reduce the amount of successful phishing attacks for the group using it.

Features
Biggest Fatures are that it can find phishing indicators like, suspicious urls, domain spoofing, reply-to vs reply from header inconsistencies or attachment types like .exes, and also detecting double file names, there is also a whitelist where you can add known trusted domains, finally it assigns a risk score and a final verdict, telling you how risky it is according to the system I created. the console output is also very human readable.

Install instruction, prerequisites and examples.
you can either clone the git repo, or download and unzip it all. python 3 and pytest are needed to use all features of the script.
run with the following command, emails.json can be anything containing your email json data (sample shortened for readme)
python .\phishfinder.py .\emails.json
[INFO] Loading input file...
[INFO] Analyzing 3 emails...

================= ANALYSIS SUMMARY =================

ID: 12345
Score: 13
Verdict: high risk
Indicators:
  - Keyword detected: verify
  - Keyword detected: password
  - Keyword detected: suspended
  - Keyword detected: immediately
  - Suspicious URL: http://evilhost.ru/login
  - Link text does not match actual URL
  - Reply-To domain mismatch
  - Suspicious attachment: invoice.pdf.exe

----------------------------------------------------
[INFO] Results written to analysis_report.json

Sample input and output - this is one of the emails in email.json and the matching section of output
{
      "email_id": "67678",
      "headers": {
        "from": "Microsoft Support <support@microsoft.com>",
        "reply_to": "support@microsoft.com",
        "return_path": "support@microsoft.com",
        "subject": "Your recent account activity",
        "date": "2026-04-20T10:15:00Z",
        "authentication_results": "spf=pass; dkim=pass",
        "received": [
          "from mail.microsoft.com (40.92.0.1)",
          "by mx.company.com with ESMTPS"
        ]
      },
      "body": {
        "text": "Hello, we noticed a recent sign-in to your account. If this was you, no further action is needed. You can review your activity anytime by visiting your account page.",
        "html": "<html><body><p>You can review your activity at <a href=\"https://account.microsoft.com\">https://account.microsoft.com</a></p></body></html>"
      },
      "attachments": []
    }
input ^  ---  output v
{
      "email_id": "67678",
      "score": 2,
      "verdict": "low risk",
      "risk_level_numeric": 2,
      "indicator_count": 1,
      "findings": [
        "Suspicious URL: https://account.microsoft.com</a"
      ],
      "iocs": {
        "urls": [
          "https://account.microsoft.com</a",
          "https://account.microsoft.com"
        ],
        "domains": [
          "account.microsoft.com<",
          "account.microsoft.com"
        ],
        "ips": [
          "40.92.0.1"
        ],
        "hashes": []
      }
    }

Running Tests
python -m pytest -v

Project structure overview
CapstoneProject
|
Week15
 |-- analysis_report.json
 |-- emails.json
 |-- indicators.json
 |-- iocs.json
 |-- whitelist.json
 |-- phishfinder.py
 |-- test_phishfinder.py