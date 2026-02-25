#!/usr/bin/env python3
from collections import Counter
from datetime import datetime
import json
LogFile = 'auth_test.log'

UserFailCount = Counter() #counter to hold failed attempts per user
IPFailCount = Counter() #counter to hold failed attempts per IP
TotalSuccessCount = 0 #variable to hold total successful attempts total
TotalFailCount = 0 #variable to hold total failed attempts total
TotalEvents = 0 #variable to hold total events processed


with open(LogFile, 'r') as file:
    for line in file:
        line = line.strip()  # remove leading and trailing whitespace
        if not line: #skip empty lines
            continue
        TotalEvents += 1
        parts = line.split()  # split line into parts by whitespace
        # Extract timestamp (first two parts)
        timestamp = parts[0] + " " + parts[1]  # "2024-11-25 03:45:12"
        # Extract key=value pairs (everything after timestamp)
        kv_pairs = parts[2:] # ['event=LOGIN', 'status=FAIL', 'user=admin', 'ip=198.51.100.45']
        data = {} #dictionary to hold key-value pairs

        for kv in kv_pairs: #iterate through key-value pairs
            if '=' in kv: #prevents crashing if there's a malformed key-value pair
                key, value = kv.split('=', 1) #split into key and value
                data[key] = value #add each pair to dictionary
        status = data.get('status') #retrieve status from dictionary
        user = data.get('user') #retrieve user from dictionary
        ip = data.get('ip')     #retrieve ip from dictionary
        if status == 'FAIL': #either increment user and ip fail count
            if user:
                UserFailCount[user] += 1
            if ip:
                IPFailCount[ip] += 1
            TotalFailCount += 1
        elif status == 'SUCCESS': #or increment total success count
            TotalSuccessCount += 1

# Print summary
print(f"Total events processed: {TotalEvents}")
print(f"Total successful attempts: {TotalSuccessCount}")
print(f"Total failed attempts: {TotalFailCount}")

print("\nTop 5 failed users:")
for user, count in UserFailCount.most_common(5):
    print(f"  {user}: {count}")

print("\nTop 5 failed IPs:")
for ip, count in IPFailCount.most_common(5):
    print(f"  {ip}: {count}")


#json report
report = {
    "timestamp": datetime.now().isoformat(),
    "TotalEvents": TotalEvents,
    "TotalSuccessCount": TotalSuccessCount,
    "TotalFailCount": TotalFailCount,
    "TopFailedUsers": UserFailCount.most_common(5),
    "TopFailedIPs": IPFailCount.most_common(5)
}
with open("IncidentReport.json", "w") as f:
    json.dump(report, f, indent=2)

#txt report
with open("IncidentReport.txt", "w") as f:
    f.write(f"Timestamp: {report['timestamp']}\n")
    f.write(f"Total Events: {report['TotalEvents']}\n")
    f.write(f"Total Successful Attempts: {report['TotalSuccessCount']}\n")
    f.write(f"Total Failed Attempts: {report['TotalFailCount']}\n")
    f.write("Top 5 Failed Users:\n")
    for user, count in report["TopFailedUsers"]:
        f.write(f"  {user}: {count}\n")
    f.write("Top 5 Failed IPs:\n")
    for ip, count in report["TopFailedIPs"]:
        f.write(f"  {ip}: {count}\n")


