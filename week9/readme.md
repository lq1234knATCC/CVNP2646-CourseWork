Overview - 
    this patch_tracker.py file is made to check the patch status of multiple systems to spot high risk systems. it does this by opening the host_inventory.json file and calculating how long the system has gone without an update and assigns a risk factor based on that.
Risk Scoring Algorithm - 
    Criticality, Patch Age, Environment, PCI Scope, HIPAA, Internet-facing are the tags, and they have a point value assigned to them based on what value they return
CIS Benchmark Alignment - 
    CIS 7.3 is timely remediation of vulnerabilities - this helps you do that by highlighting devices that have gone the longest without security patches.
Functions Overview - 
    load_inventory() – Loads host data from a JSON file
    calculate_days_since_patch() – calculates days since last patch
    calculate_risk_score - calculates risk score
    get_risk_level - Convert numeric score to risk level string
    filter_high_risk_hosts - Return hosts with risk_score >= threshold
    sort_hosts_by_risk - Sort hosts by risk_score descending
    generate_json_report_file - Generate JSON report and write to file
    generate_text_summary_file - Generate simplified text summary and write to file
    analyze_inventory - Calculate derived values and risk scores for each host
Sample Output - 
[INFO] JSON report written to high_risk_report.json
[INFO] Text summary written to patch_summary.txt
============================================================
     WEEKLY PATCH COMPLIANCE SUMMARY REPORT
============================================================
Generated: 2026-03-25 20:48:42

EXECUTIVE SUMMARY
------------------------------------------------------------
Total Systems Analyzed:        20
High-Risk Systems Identified:  9 (45.0%)
Critical Priority Systems:     2
Immediate Action Required:     0 systems >90 days unpatched

RISK DISTRIBUTION
------------------------------------------------------------
Critical (70+ points):         2 systems
High (50-69 points):           7 systems
Medium (25-49 points):         10 systems
Low (0-24 points):             1 systems

TOP 5 HIGHEST RISK SYSTEMS
------------------------------------------------------------
1. FIN-WKS-001 (Score: 75, Critical)
   Last Patched: 39 days ago | Production | Tags: pci-scope, internet-facing

2. FIN-WKS-002 (Score: 60, High)
   Last Patched: 55 days ago | Production | Tags: pci-scope, encrypted     

3. ENG-WKS-001 (Score: 50, High)
   Last Patched: 43 days ago | Production | Tags: developer-tools, source-code-access

4. ENG-WKS-002 (Score: 50, High)
   Last Patched: 37 days ago | Production | Tags: linux, container-host    

5. IT-ADM-001 (Score: 65, High)
   Last Patched: 32 days ago | Production | Tags: privileged-access, domain-joined

RECOMMENDED ACTIONS
------------------------------------------------------------
IMMEDIATE (Next 48 hours):
- Patch 2 critical-risk systems

THIS WEEK (Next 7 days):
- Schedule maintenance windows for 9 high-risk production systems

COMPLIANCE NOTES
------------------------------------------------------------
PCI-DSS: 3 systems in PCI scope require immediate attention
============================================================
Reports generated successfully.


Testing - 
    Tested with the provided host_inventory.json file