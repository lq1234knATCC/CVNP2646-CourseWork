import json
from datetime import datetime
from collections import Counter

def load_inventory(filepath):
    """Load host inventory from JSON file"""
    with open(filepath, 'r') as file:
        data = json.load(file)
    return data

def calculate_days_since_patch(host):
    #Calculate number of days since last patch
    last_patch_date = datetime.strptime(host['last_patch_date'], '%Y-%m-%d')
    return (datetime.now() - last_patch_date).days

def calculate_risk_score(host):
    score = 0

    #criticality
    criticality_points = {"critical": 40, "high": 25, "medium": 10, "low": 5}
    score += criticality_points.get(host.get('criticality'), 0)

    #patch age
    days = host.get('days_since_patch', 0)
    if days > 90:
        score += 30
    elif days > 60:
        score += 20
    elif days > 30:
        score += 10

    #environment
    env_points = {"production": 15, "staging": 8, "development": 3}
    score += env_points.get(host.get('environment'), 0)
    #tags
    tags = host.get('tags', [])
    if "pci-scope" in tags:
        score += 10
    if "hipaa" in tags:
        score += 10
    if "internet-facing" in tags:
        score += 15

    return min(score, 100)

def get_risk_level(score): 
    #Convert numeric score to risk level string
    if score >= 70:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 25:
        return "medium"
    else:
        return "low"

def filter_high_risk_hosts(hosts, threshold=50):
    #Return hosts with risk_score >= threshold
    return [h for h in hosts if h['risk_score'] >= threshold]

def sort_hosts_by_risk(hosts):
    #Sort hosts by risk_score descending
    return sorted(hosts, key=lambda h: h['risk_score'], reverse=True)

def generate_json_report_file(hosts, high_risk_hosts, output_file='high_risk_report.json'):
    #Generate JSON report and write to file
    risk_dist = Counter(h['risk_level'] for h in hosts)
    
    report = {
        "report_date": datetime.now().isoformat(),
        "report_type": "High Risk Host Assessment",
        "total_hosts": len(hosts),
        "total_high_risk": len(high_risk_hosts),
        "risk_distribution": {
            "critical": risk_dist.get('critical', 0),
            "high": risk_dist.get('high', 0),
            "medium": risk_dist.get('medium', 0),
            "low": risk_dist.get('low', 0)
        },
        "high_risk_hosts": [
            {
                "hostname": h['hostname'],
                "risk_score": h['risk_score'],
                "risk_level": h['risk_level'],
                "days_since_patch": h['days_since_patch'],
                "criticality": h['criticality'],
                "environment": h['environment'],
                "tags": h.get('tags', [])
            }
            for h in high_risk_hosts
        ]
    }

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"[INFO] JSON report written to {output_file}")

def generate_text_summary_file(hosts, high_risk_hosts, output_file='patch_summary.txt'):
    #Generate simplified text summary and write to file (ASCII-safe)
    lines = []
    
    lines.append("=" * 60)
    lines.append("     WEEKLY PATCH COMPLIANCE SUMMARY REPORT")
    lines.append("=" * 60)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    
    # Executive summary
    lines.append("EXECUTIVE SUMMARY")
    lines.append("-" * 60)
    risk_dist = Counter(h['risk_level'] for h in hosts)
    critical_count = risk_dist.get('critical', 0)
    
    lines.append(f"Total Systems Analyzed:        {len(hosts)}")
    lines.append(f"High-Risk Systems Identified:  {len(high_risk_hosts)} ({len(high_risk_hosts)/len(hosts)*100:.1f}%)")
    lines.append(f"Critical Priority Systems:     {critical_count}")
    
    very_old = sum(1 for h in hosts if h['days_since_patch'] > 90)
    lines.append(f"Immediate Action Required:     {very_old} systems >90 days unpatched")
    lines.append("")
    
    # Risk distribution (simpler, no ≥ symbol)
    lines.append("RISK DISTRIBUTION")
    lines.append("-" * 60)
    lines.append(f"Critical (70+ points):         {risk_dist.get('critical', 0)} systems")
    lines.append(f"High (50-69 points):           {risk_dist.get('high', 0)} systems")
    lines.append(f"Medium (25-49 points):         {risk_dist.get('medium', 0)} systems")
    lines.append(f"Low (0-24 points):             {risk_dist.get('low', 0)} systems")
    lines.append("")
    
    # Top 5 highest risk
    lines.append("TOP 5 HIGHEST RISK SYSTEMS")
    lines.append("-" * 60)
    for i, host in enumerate(high_risk_hosts[:5], 1):
        lines.append(f"{i}. {host['hostname']} (Score: {host['risk_score']}, {host['risk_level'].title()})")
        lines.append(f"   Last Patched: {host['days_since_patch']} days ago | {host['environment'].title()} | Tags: {', '.join(host.get('tags', []))}")
        lines.append("")
    
    # Recommended actions
    lines.append("RECOMMENDED ACTIONS")
    lines.append("-" * 60)
    lines.append("IMMEDIATE (Next 48 hours):")
    lines.append(f"- Patch {critical_count} critical-risk systems")
    lines.append("")
    lines.append("THIS WEEK (Next 7 days):")
    lines.append(f"- Schedule maintenance windows for {len(high_risk_hosts)} high-risk production systems")
    lines.append("")
    
    # Compliance notes
    lines.append("COMPLIANCE NOTES")
    lines.append("-" * 60)
    pci_count = sum(1 for h in hosts if 'pci-scope' in h.get('tags', []) and h['days_since_patch'] > 30)
    if pci_count > 0:
        lines.append(f"PCI-DSS: {pci_count} systems in PCI scope require immediate attention")
    lines.append("=" * 60)
    
    text_output = "\n".join(lines)

    # Write ASCII-safe text file
    with open(output_file, 'w') as f:
        f.write(text_output)

    print(f"[INFO] Text summary written to {output_file}")
    print(text_output)

def analyze_inventory(hosts): #Calculate derived values and risk scores for each host
    for host in hosts:
        host['days_since_patch'] = calculate_days_since_patch(host)
        host['risk_score'] = calculate_risk_score(host)
        host['risk_level'] = get_risk_level(host['risk_score'])
    return hosts

def main():
    #Configuration
    INPUT_FILE = "host_inventory.json"
    RISK_THRESHOLD = 50

    hosts = load_inventory(INPUT_FILE)

    if not hosts:
        print("No data loaded. Exiting.")
        exit()

    analyzed_hosts = analyze_inventory(hosts)

    high_risk_hosts = filter_high_risk_hosts(analyzed_hosts, RISK_THRESHOLD)

    
    generate_json_report_file(analyzed_hosts, high_risk_hosts)
    generate_text_summary_file(analyzed_hosts, high_risk_hosts)

    print("Reports generated successfully.")

if __name__ == "__main__":
    main()
