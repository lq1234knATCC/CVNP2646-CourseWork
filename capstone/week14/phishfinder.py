import json
import sys
import re

def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to read {filename}: {e}")
        return None


class PhishingAnalyzer:
    def __init__(self, indicators, whitelist):
        self.keywords = ["urgent", "verify", "password", "suspended", "immediately"]
        self.indicators = indicators
        self.whitelist = whitelist

    def analyze_email(self, email):
        findings = []
        iocs = {
            "urls": [],
            "domains": [],
            "ips": [],
            "hashes": []
        }

        score = 0

        headers = email.get("headers", {})
        body = email.get("body", {})
        attachments = email.get("attachments", [])

        text_body = body.get("text", "").lower()
        html_body = body.get("html", "").lower()

        # --------------------
        # 1. Keyword Detection
        # --------------------
        for word in self.keywords:
            if word in text_body:
                findings.append(f"Keyword detected: {word}")
                score += 1

        # --------------------
        # 2. URL Extraction
        # --------------------
        urls = re.findall(r'https?://\S+', html_body)
        for url in urls:
            domain = self.extract_domain(url)

            iocs["urls"].append(url)
            iocs["domains"].append(domain)

            findings.append(f"Suspicious URL: {url}")
            score += 2

        # --------------------
        # 3. Header Analysis
        # --------------------
        from_field = headers.get("from", "")
        reply_to = headers.get("reply_to", "")

        if "paypal" in from_field.lower() and "paypaI" in from_field:
            findings.append("Possible domain spoofing in FROM address")
            score += 2

        if reply_to and reply_to not in from_field:
            findings.append("Reply-To mismatch detected")
            score += 1

        # Extract IPs from Received headers
        received_headers = headers.get("received", [])
        for line in received_headers:
            ips = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
            for ip in ips:
                iocs["ips"].append(ip)

        # --------------------
        # 4. Attachment Analysis
        # --------------------
        for file in attachments:
            filename = file.get("filename", "")
            file_hash = file.get("hash")

            if file_hash:
                iocs["hashes"].append(file_hash)

            if filename.endswith(".exe") or ".exe" in filename:
                findings.append(f"Suspicious attachment: {filename}")
                score += 3

        # --------------------
        # Final Verdict
        # --------------------
        if score >= 6:
            verdict = "high risk"
        elif score >= 3:
            verdict = "medium risk"
        else:
            verdict = "low risk"

        return {
            "email_id": email.get("email_id"),
            "score": score,
            "verdict": verdict,
            "findings": findings,
            "iocs": iocs
        }

    def extract_domain(self, url):
        try:
            return url.split("/")[2]
        except:
            return "unknown"
    
def main():
    if len(sys.argv) < 2:
        print("Usage: python phishing_detector.py <input.json>")
        return

    input_file = sys.argv[1]
    output_file = "analysis_report.json"

    print("[INFO] Loading input file...")

    data = load_json_file(input_file)

    if not data:
        print("[ERROR] No data loaded")
        return

    emails = data.get("emails", [])

    if not emails:
        print("[ERROR] No emails found in input file")
        return

    analyzer = PhishingAnalyzer(indicators={}, whitelist={})

    print(f"[INFO] Analyzing {len(emails)} emails...")

    results = []

    for email in emails:
        result = analyzer.analyze_email(email)
        results.append(result)

    output = {
        "total_emails": len(emails),
        "results": results
    }

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"[INFO] Results written to {output_file}")

    except Exception as e:
        print(f"[ERROR] Failed to write output: {e}")

if __name__ == "__main__":
    main()

