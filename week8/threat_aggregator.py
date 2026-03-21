import json
from collections import Counter
from datetime import datetime

# -------------------
# Helper Functions
# -------------------

def load_feed(filename): #loads a json file and returns the data as a dictionary
    with open(filename, "r") as f:
        return json.load(f)

def normalize_indicator(indicator: dict, source_name: str) -> dict: #converts different naming conventions to a common format
    normalized = {
        "type": indicator.get("type")
                or indicator.get("indicator_type")
                or indicator.get("category"),

        "value": indicator.get("value")
                 or indicator.get("indicator_value")
                 or indicator.get("ioc"),

        "confidence": indicator.get("confidence")
                      or indicator.get("score")
                      or indicator.get("reliability"),

        "threat_level": indicator.get("threat")
                        or indicator.get("severity")
                        or indicator.get("risk"),

        "sources": [source_name]
    }
    return normalized

def validate_indicators(indicators: list[dict]) -> tuple[list[dict], list[str]]: #amkes sure indicators have required fields, valid types, and confidence scores in the correct range
    valid = []
    errors = []
    allowed_types = {"ip", "domain", "hash", "url"}

    for idx, ind in enumerate(indicators):
        required_fields = ["type", "value", "confidence"]
        missing_fields = [f for f in required_fields if f not in ind or ind[f] is None]
        if missing_fields:
            errors.append(f"Indicator {idx}: missing required fields: {missing_fields}")
            continue

        if ind["type"] not in allowed_types:
            errors.append(f"Indicator {idx}: invalid type '{ind['type']}'")
            continue

        try:
            conf = float(ind["confidence"])
            if not (0 <= conf <= 100):
                errors.append(f"Indicator {idx}: confidence {conf} out of range 0-100")
                continue
        except (ValueError, TypeError):
            errors.append(f"Indicator {idx}: confidence '{ind['confidence']}' is not a number")
            continue

        if not isinstance(ind["value"], str) or not ind["value"].strip():
            errors.append(f"Indicator {idx}: value is empty or not a string")
            continue

        valid.append(ind)
    return valid, errors

def deduplicate_indicators(indicators: list[dict]) -> tuple[list[dict], int]: #removes duplicates based on type and value, merges sources, and keeps the highest confidence score
    unique: dict[tuple, dict] = {}
    duplicate_count = 0

    for ind in indicators: #ensure sources is a list and create a key based on type and value
        key = (ind.get("type"), ind.get("value"))
        sources = ind.get("sources", [])
        if not isinstance(sources, list):
            sources = [sources]
        ind["sources"] = sources

        if key not in unique: #store it if it is unique
            unique[key] = ind
            continue

        duplicate_count += 1
        existing = unique[key]
        merged_sources = set(existing.get("sources", [])) | set(ind.get("sources", [])) #merge sources from original and duplicate
        existing_conf = existing.get("confidence", 0) or 0
        new_conf = ind.get("confidence", 0) or 0

        if new_conf > existing_conf: #keeps higer confidence indicator
            ind["sources"] = list(merged_sources)
            unique[key] = ind
        else:
            existing["sources"] = list(merged_sources)

    return list(unique.values()), duplicate_count

def filter_indicators( #filters based on confidence, threat level and type.
    indicators: list[dict],
    min_conf: float = 85,
    levels: list[str] = None,
    types: list[str] = None
) -> list[dict]:
    if levels is None:
        levels = ["high", "critical"]
    if types is None:
        types = ["ip", "domain"]

    return [
        ind for ind in indicators
        if ind.get("confidence", 0) >= min_conf
        and ind.get("threat_level") in levels
        and ind.get("type") in types
    ]

def transform_to_firewall(indicators: list[dict]) -> dict: #changes formatting to match firewall blocklist requirements, including action, priority and reason
    entries = []
    for ind in indicators:
        entry = {
            "address": ind["value"],
            "action": "block",
            "priority": "high" if ind["threat_level"] == "critical" else "medium",
            "reason": f"Threat level: {ind['threat_level']}, Confidence: {ind['confidence']}%",
            "sources": ind["sources"]
        }
        entries.append(entry)
    return {
        "generated_at": datetime.now().isoformat(),
        "total_entries": len(entries),
        "blocklist": entries
    }

def transform_to_siem(indicators: list[dict]) -> dict: #changes formatting to match SIEM feed requirements, including ioc type, value, threat level, confidence score, first seen date and sources
    siem_entries = []
    for ind in indicators:
        entry = {
            "ioc_value": ind["value"],
            "ioc_type": ind["type"],
            "threat_level": ind["threat_level"],
            "confidence_score": ind["confidence"],
            "first_seen": ind.get("first_seen", ""),
            "sources": ind["sources"]
        }
        siem_entries.append(entry)
    return {
        "generated_at": datetime.now().isoformat(),
        "total_indicators": len(siem_entries),
        "indicators": siem_entries
    }

def generate_summary_report(indicators: list[dict], duplicates_removed: int) -> str: #creates a text summary report with total indicators, duplicates removed, and top 5 indicators by confidence
    report_lines = [
        f"Threat Intelligence Summary Report - {datetime.now().isoformat()}",
        f"Total indicators after deduplication: {len(indicators)}",
        f"Duplicates removed: {duplicates_removed}",
        "",
        "Top 5 indicators by confidence:"
    ]
    sorted_inds = sorted(indicators, key=lambda x: x.get("confidence", 0), reverse=True)
    for ind in sorted_inds[:5]:
        report_lines.append(
            f"- {ind['type'].upper()} {ind['value']} | "
            f"Threat: {ind['threat_level']} | "
            f"Confidence: {ind['confidence']}% | "
            f"Sources: {', '.join(ind['sources'])}"
        )
    return "\n".join(report_lines)

def analyze_indicators(indicators: list[dict]): #analysis by counting the distribution of types, threat levels and sources among the indicators
    type_counter = Counter(ind.get("type") for ind in indicators)
    threat_counter = Counter(ind.get("threat_level") for ind in indicators)
    source_counter = Counter()
    for ind in indicators:
        for src in ind.get("sources", []):
            source_counter[src] += 1
    return type_counter, threat_counter, source_counter

def generate_statistics(loaded, valid, deduped, filtered): 
    type_counts = Counter(ind["type"] for ind in filtered)
    severity_counts = Counter(ind["threat_level"] for ind in filtered)
    source_counts = Counter()
    for ind in deduped:
        for src in ind.get("sources", []):
            source_counts[src] += 1
    return {
        "total_loaded": loaded,
        "valid_count": valid,
        "unique_count": len(deduped),
        "filtered_count": len(filtered),
        "duplicates_removed": loaded - len(deduped),
        "type_distribution": dict(type_counts),
        "severity_distribution": dict(severity_counts),
        "source_contribution": dict(source_counts)
    }

all_indicators = []

# Load and normalize feeds
for filename, source in [("vendor_a.json", "VendorA"), 
                         ("vendor_b.json", "VendorB"), 
                         ("vendor_c.json", "VendorC")]:
    feed = load_feed(filename)

indicators_list = (
    feed.get("indicators")
    or feed.get("data")
    or feed.get("threats")
)

if indicators_list is None:
    raise ValueError(f"Unsupported feed format in {filename}")

for ind in indicators_list:
    all_indicators.append(normalize_indicator(ind, source))

print(f"Total indicators loaded: {len(all_indicators)}")

# Validate
valid_indicators, validation_errors = validate_indicators(all_indicators)
print(f"Valid indicators: {len(valid_indicators)}, Errors: {len(validation_errors)}")

# Deduplicate
unique_indicators, dup_count = deduplicate_indicators(valid_indicators)
print(f"Unique indicators: {len(unique_indicators)}, Duplicates removed: {dup_count}")

# Filter
filtered_indicators = filter_indicators(unique_indicators)
print(f"Filtered indicators: {len(filtered_indicators)}")

# Transform outputs
firewall_data = transform_to_firewall(filtered_indicators)
siem_data = transform_to_siem(filtered_indicators)
summary_text = generate_summary_report(unique_indicators, dup_count)

# Save files
with open("firewall_blocklist.json", "w") as f:
    json.dump(firewall_data, f, indent=2)

with open("siem_feed.json", "w") as f:
    json.dump(siem_data, f, indent=2)

with open("summary_report.txt", "w") as f:
    f.write(summary_text)

# Analyze indicators
type_dist, threat_dist, source_dist = analyze_indicators(filtered_indicators)
stats = generate_statistics(
    loaded=len(all_indicators),
    valid=len(valid_indicators),
    deduped=unique_indicators,
    filtered=filtered_indicators
)

# Print stats
print("\n=== Threat Intelligence Pipeline Statistics ===")
print(f"Total indicators loaded: {stats['total_loaded']}")
print(f"Valid indicators: {stats['valid_count']}")
print(f"Unique indicators (after deduplication): {stats['unique_count']}")
print(f"Filtered indicators: {stats['filtered_count']}")
print(f"Duplicates removed: {stats['duplicates_removed']}")
print("\nType distribution:", stats['type_distribution'])
print("Threat level distribution:", stats['severity_distribution'])
print("Source contributions:", stats['source_contribution'])