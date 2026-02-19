#!/usr/bin/env python3
from pathlib import Path
import shutil
import json
from datetime import datetime
import sys

CATEGORIES = {   # Define category mappings
    "documents": ["pdf", "doc", "docx", "txt", "rtf", "odt"],
    "images": ["jpg", "jpeg", "png", "gif", "bmp", "svg"],
    "archives": ["zip", "tar", "gz", "rar", "7z"],
    "executables": ["exe", "msi", "bat", "sh"],
    "videos": ["mp4", "avi", "mkv", "mov"],
    "audio": ["mp3", "wav", "flac", "aac"],
}

def get_extension(filename): #Extract and normalize file extension
    path = Path(filename)
    ext = path.suffix.lower()  #force lowercase
    return ext[1:] if ext else ""  # remove the leading dot
    pass


def categorizeFile(filename):
    extension = filename.split(".")[-1].lower()
    if extension in ["pdf", "docx", "txt"]: #if it is one of these 3, document
        return "documents"
    elif extension in ["jpg", "png", "gif"]: #otherwise keep checking
        return "images"
    elif extension in ["zip", "tar", "gz", "rar", "7z"]:
        return "archives"
    elif extension in ["mp4", "avi", "mkv", "mov"]:
        return "videos"
    elif extension in ["mp3", "wav", "flac", "aac"]:
        return "audio"
    else:
        return "other"


def moveFile(sourceDir):
    sourceDir = Path(sourceDir) #makes sourceDir a Path object
    fileCount = 0 #starts counter at 0
    categoryCounts = {  # count per category
        "documents": 0,
        "images": 0,
        "archives": 0,
        "videos": 0,
        "audio": 0,
        "other": 0
    }
    errors = [] #holds errors
    for file in sourceDir.iterdir():
        if file.is_file(): #checks to see it is not a directory
            fileCount += 1 #increments count each time a file is moved
            try:
                category = categorizeFile(file.name) #categorizes file
                if category in categoryCounts:
                    categoryCounts[category] += 1 #increments count each time a file is moved
                else:
                    categoryCounts["other"] += 1
                categoryDir = sourceDir / category #joins sourceDirectory with the category to make a new path with the directory at the end
                categoryDir.mkdir(exist_ok=True) #creates the directory if it doesnt exist
                dest_path = categoryDir / file.name 
                i = 1
                while dest_path.exists(): #if the path exists, add a number to the end of the file name to avoid overwriting
                    dest_path = categoryDir / f"{file.stem}({i}){file.suffix}" 
                    i += 1
                shutil.move(file, categoryDir / dest_path) #shutil.move moves file to the new directory, the new path is made by joining the categoryDir with the file name
            except Exception as e:
                errors.append(f"{file.name}: {e}")   # store error
                print(f"[!] Error moving {file.name}: {e}")  # print error
    return fileCount, categoryCounts, errors
           

def JsonReport(stats, source_dir):
    report = {
        "timestamp": datetime.now().isoformat(),
        "source_directory": str(source_dir),
        "total_files": stats[0],
        "categories": stats[1],
        "organized": sum(stats[1].values())
    }

    # Save the report to a JSON file
    with open("organization_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4)
    return report
    pass



def TextReport(stats, output_file="organization_report.txt"):


    total_files, category_counts, errors = stats
    lines = []

    lines.append("Timestamp: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("")

    # Summary
    lines.append("SUMMARY")
    lines.append("-" * 40)
    lines.append("Total files scanned: " + str(total_files))
    lines.append("Files organized per category:")
    for cat, count in category_counts.items():
        percent = (count / total_files * 100) if total_files else 0
        lines.append(f"  {cat}: {count} ({percent:.1f}%)")
    
    # Errors
    if errors:
        lines.append("")
        lines.append("ERRORS / WARNINGS")
        lines.append("-" * 40)
        for err in errors:
            lines.append("  - " + str(err))

    # Footer
    lines.append("=" * 40)
    lines.append("End of Report")

    # Write to TXT file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return lines #return lines for printing to console
    pass


def main():
    # Get directory from command line or use default
    sourceDir = sys.argv[1] if len(sys.argv) > 1 else str(Path.home() / "Downloads") 
    #accepts arguments, or defaults to the Downloads folder
    print(f"[*]Organizing files in: {sourceDir}")

    # Move files and get stats
    total_files, category_counts, errors = moveFile(sourceDir)

    print(f"[*]Total files moved: {total_files}")
    print(f"[*]Files moved per category:")
    for cat, count in category_counts.items():
        print(f"    {cat}: {count}")
    

    # Generate JSON report
    json_report = JsonReport((total_files, category_counts, errors), sourceDir)
    print("[*] JSON report saved as organization_report.json")

    # Generate text report
    txt_path = Path(__file__).parent / "organization_report.txt"
    text_report = TextReport((total_files, category_counts, errors), txt_path)
    print("[*] TXT report generated and saved as organization_report.txt")


if __name__ == "__main__":
    main()