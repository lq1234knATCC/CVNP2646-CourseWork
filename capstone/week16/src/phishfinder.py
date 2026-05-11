import json
import sys
import re
import logging
from urllib.parse import urlparse

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)

def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    except FileNotFoundError:
        logging.error(f"File not found: {filename}")
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in {filename}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    return None


class PhishingAnalyzer:
    def __init__(self, indicators, whitelist):
        self.keywords = ["urgent", "verify", "password", "suspended", "immediately"]
        self.indicators = indicators
        self.whitelist = whitelist

        # scoring weights to improve scoring
        self.weights = {
            "keyword": 1,
            "url": 2,
            "spoofing": 2,
            "attachment": 3,
            "header": 2,
            "anomaly": 1
        }

    # --------------------
    # Validation
    # --------------------
    def validate_email(self, email):
        if not isinstance(email, dict):
            raise ValueError("Invalid email format (must be a dictionary)")

        if "headers" not in email or "body" not in email:
            raise ValueError("Email missing required fields: headers or body")

        if not isinstance(email.get("headers"), dict):
            raise ValueError("Headers must be a dictionary")

        if not isinstance(email.get("body"), dict):
            raise ValueError("Body must be a dictionary")

    # --------------------
    # Helpers
    # --------------------
    def extract_domain(self, url):
        try:
            return urlparse(url).netloc.lower()
        except:
            return "unknown"

    def extract_domain_from_email(self, email_str):
        try:
            return email_str.split("@")[-1].replace(">", "").strip().lower()
        except:
            return "unknown"

    def normalize_domain(self, domain):
        return domain.replace("www.", "").lower()

    def is_whitelisted(self, domain): #determine if domain or subdomain is in whitelist
        domain = self.normalize_domain(domain)

        for safe in self.whitelist:
            safe = self.normalize_domain(safe)

            if domain == safe or domain.endswith("." + safe):
                return True

        return False

    # --------------------
    # Main Analysis
    # --------------------
    def analyze_email(self, email):
        self.validate_email(email)

        findings = []
        iocs = {
            "urls": set(),
            "domains": set(),
            "ips": set(),
            "hashes": set()
        }

        score = 0

        headers = email.get("headers") or {}
        body = email.get("body") or {}
        attachments = email.get("attachments") or []

        text_body = (body.get("text") or "").lower()
        html_body = (body.get("html") or "").lower()

        # --------------------
        # 1. Keyword Detection
        # --------------------
        for word in self.keywords:
            if word in text_body:
                findings.append(f"Keyword detected: {word}")
                score += self.weights["keyword"]

        # --------------------
        # 2. URL Extraction + Link Mismatch
        # --------------------
        urls = re.findall(r'https?://[^\s">]+', html_body)

        for url in urls:
            domain = self.extract_domain(url)

            iocs["urls"].add(url)
            iocs["domains"].add(domain)

        if not self.is_whitelisted(domain):
            findings.append(f"Suspicious URL: {url}")
            score += self.weights["url"]
        else:
            findings.append(f"Whitelisted domain: {domain}")    

        # Detect display vs actual link mismatch
        link_matches = re.findall(r'<a href="(.*?)">(.*?)</a>', html_body)
        for real_url, display_text in link_matches:
            if self.normalize_domain(display_text) not in real_url:
                findings.append("Link text does not match actual URL")
                score += self.weights["spoofing"]

        # --------------------
        # 3. Header Analysis
        # --------------------
        from_field = (headers.get("from") or "").lower()
        reply_to = (headers.get("reply_to") or "").lower()
        from_domain = self.extract_domain_from_email(from_field)
        reply_domain = self.extract_domain_from_email(reply_to)

        if self.is_whitelisted(from_domain):
            score = max(score - 2, 0)
        else:
            # Only flag issues if NOT trusted
            if any(char.isdigit() for char in from_domain):
                findings.append("Suspicious domain contains numbers")
                score += self.weights["anomaly"]

            if "login" in from_domain or "secure" in from_domain:
                findings.append("Suspicious domain keyword detected")
                score += self.weights["anomaly"]    

        if reply_to and from_domain != reply_domain:
            findings.append("Reply-To domain mismatch")
            score += self.weights["header"]

        # --------------------
        # SPF / DKIM
        # --------------------
        auth_results = (headers.get("authentication_results") or "").lower()

        if "spf=fail" in auth_results:
            findings.append("SPF check failed")
            score += self.weights["header"]

        if "dkim=fail" in auth_results:
            findings.append("DKIM check failed")
            score += self.weights["header"]

        received_headers = headers.get("received") or []

        if len(received_headers) < 2:
            findings.append("Unusual email routing (few Received headers)")
            score += self.weights["anomaly"]

        for line in received_headers:
            ips = re.findall(r'\d+\.\d+\.\d+\.\d+', line)
            for ip in ips:
                iocs["ips"].add(ip)

        # --------------------
        # 4. Attachment Analysis
        # --------------------
        for file in attachments:
            filename = file.get("filename", "").lower()
            file_hash = file.get("hash")

            if file_hash:
                iocs["hashes"].add(file_hash)

            if filename.endswith(".exe") or ".exe" in filename:
                findings.append(f"Suspicious attachment: {filename}")
                score += self.weights["attachment"]

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
    "risk_level_numeric": score,  # clearer naming
    "indicator_count": len(findings),
    "findings": findings,
    "iocs": {
        "urls": list(iocs["urls"]),
        "domains": list(iocs["domains"]),
        "ips": list(iocs["ips"]),
        "hashes": list(iocs["hashes"])
    }
}


def main():
    if len(sys.argv) < 2:
        print("Usage: python phishing_detector.py <input.json>")
        return

    input_file = sys.argv[1]
    output_file = "analysis_report.json"

    logging.info("Loading input file...")

    data = load_json_file(input_file)

    if not data:
        logging.error("No data loaded")
        return

    emails = data.get("emails", [])

    if not emails:
        logging.error("No emails found in input file")
        return

    analyzer = PhishingAnalyzer(indicators={}, whitelist=[])

    logging.info(f"Analyzing {len(emails)} emails...")

    results = []

    # ----------------------------
    # Analysis loop
    # ----------------------------
    for email in emails:
        try:
            result = analyzer.analyze_email(email)
            results.append(result)
        except Exception as e:
            logging.error(f"Failed to analyze email: {e}")

    # ----------------------------
    # Console output
    # ----------------------------
    print("\n================= ANALYSIS SUMMARY =================\n")

    for result in results:
        print(f"ID: {result['email_id']}")
        print(f"Score: {result['score']}")
        print(f"Verdict: {result['verdict']}")
        print("Indicators:")

        if result["findings"]:
            for f in result["findings"]:
                print(f"  - {f}")
        else:
            print("  - None")

        print("\n----------------------------------------------------\n")

    # ----------------------------
    # JSON output
    # ----------------------------
    output = {
        "total_emails": len(emails),
        "results": results
    }

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        logging.info(f"Results written to {output_file}")

    except Exception as e:
        logging.error(f"Failed to write output: {e}")


if __name__ == "__main__":
    main()