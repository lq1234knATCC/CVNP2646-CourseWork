Overview: 
    This script is designed to load compromise indicators, standardize their formatting, check that they are valid, remove duplicates, filter for high risk indicators, and output a text fille, as well as a json report for siems and a json report for firewalls. 
Usage: 
    simply run python threat_aggregator.py in a directory containing your IOCs
Feed Formats: 
    Each vendor json file has diffirent naming schemes for each element, so we change that by having a check for each naming convention used by the vendors
Normalization Logic: 
    similar to the above, the code changes the varied field names to one consistent name with a 
Deduplication Strategy: 
    each indicator is given a unique key pair, and if a duplicate is encountered its confidence score is compared against the existing indicator, and the more confident one is stored
Filter Criteria:
    in order to display only the relevant threats the script only displays threats it is more than 85% confident, as well as only allowing high and critical threat levels.
Output Formats:
    the script outputs 3 diffirent formats, text for an easily human readable format.
    Siem_Feed - includes ioc value type and threat level
    Firewall_blocklist - includes the ip and the action to take
Test Data:
    tested with the included vendor_a b and c files.
AI Usage: 
    I used the parts of code you provided with chatgpt to help get me a complete version with extra functionality.