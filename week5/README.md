Organizer.py - Sorts files into 8 folders based on the file extension, and generates a report documenting it.

Usage - run in command line with the folder you want sorted as an argument
    example: python organizer.py C:\Users\YourUser\Downloads

Features - automatically creates folders that documents will be sorted into, generates Json and Txt reports with time and date stamps for documentation, tracks total files moved, and displays any errors

Supported Filetypes - anything not in this table will be in the other folder, table can be added to easily
   "Documents": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".svg"],
    "Videos": [".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv"],
    "Audio": [".mp3", ".wav", ".m4a", ".aac", ".ogg"],
    "Archives": [".zip", ".tar", ".gz", ".rar", ".7z"],
    "Scripts": [".py", ".js", ".sh", ".rb", ".pl"],
    "Applications": [".dmg", ".pkg", ".app"],

Example Output - only sorted 3 files to keep readme short
[*]Organizing files in: c:\Users\lq1234kn\Documents\python json\CVNP2646-CourseWork\week5\test_downloads
[*]Total files moved: 7
[*]Files moved per category:
    documents: 1
    images: 0
    archives: 2
    videos: 0
    audio: 0
    other: 4
[*] JSON report saved as organization_report.json
[*] TXT report generated and saved as organization_report.txt

Pathlib Vs os.path I was new to both of these, and everything I saw online said pathlib is more widely used and more modern.
AI Usage - I used AI to review partly functional code, error checking, as well as for some error handling, as well as to help me understand concepts, like why we are using certian. I was sure to fully understand any AI code I implimented. I used ChatGpt or VScode Copilot
Challenges - much of this assignment was a challenge for me, I feel like the web app does not provide enough info, so I had to look up videos explaining things in pathlib, like checking for a file, or getting parts of a filepath.