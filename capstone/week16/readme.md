# PhishFinder

A Python tool designed to analyze, assign risk values, and categorize emails based on common threat indicators for phising emails.

## 🎯 Problem Statement

The problem this aims to solve is end users being tricked by phishing emails. users can input their emails into the email.json file, and the program will determine a risk value for the email based on multiple things. it will analyze the email header and the body of the email for any text encouraging you to act quickly, or phrases like unauthorized access, in addition to text, it will look at any attachments and flag any executable files, as well as any urls included. urls can be added to a whitelist to reduce false flags. it will assign an email a risk score and a human readable report based on all of those factors.

in a company setting, something like this could be applied to emails before the end user even gets them to try to mitigate the amount of phishing emails they receive.

## ✨ Features

- Configurable list of phishing related keywords
- Configurable list of whitelisted urls, anything else is deemed suspicious
- Analyzes the email headers to find Reply-To mismatches
- Identifies email attachments and will flag executable files as suspicious
- Has weighted scoring to better determine what is deemed high risk
- Instant feedback in the command line, as well as a json report
- Supports analysis of multiple emails at the same time
- 

## 📋 Prerequisites

- Python 3.10 or newer. Pytest if you want to run the test files.

## ⚙️ Installation

```bash
git clone https://github.com/lq1234knATCC/CVNP2646-CourseWork/tree/main/capstone/week16
```

## 🚀 Usage

```bash
python src/phishfinder.py data/emails.json
```

## 📁 Project Structure

```
phishfinder/
├── README.md
├── AI_USAGE.md
├── requirements.txt
├── src/
│   ├── __init__.py
│   └── main.py
├── tests/
│   └── test_main.py
└── data/
    ├── sample_input.json
    └── sample_output.json
```

## 🧪 Running Tests

```bash
pytest tests/ -v
```

## 📚 Course Context

This project was developed as part of CVNP2646-90 PYTHON/JSON.

## 📄 License

This project is for educational purposes.

---
*Built with Python | 2026*