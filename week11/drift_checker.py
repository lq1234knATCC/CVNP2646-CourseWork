import json
import os


# -----------------------------
# Step 1: JSON Loading
# -----------------------------
def load_json(file_path):
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERROR] Invalid JSON in {file_path}: {e}")
        return None


# -----------------------------
# Step 2: DriftResult Class
# -----------------------------
class DriftResult:
    CRITICAL_KEYWORDS = ["password", "secret", "admin", "root", "enabled"]
    
    def __init__(self, path, drift_type, baseline_value, current_value):
        self.path = path
        self.drift_type = drift_type
        self.baseline_value = baseline_value
        self.current_value = current_value
        self.severity = self._calculate_severity()
    CRITICAL_KEYWORDS = ["password", "secret", "admin", "root", "enabled"]
    def _calculate_severity(self):
        for keyword in self.CRITICAL_KEYWORDS:
            if keyword in self.path.lower():
                return "high"

        if self.drift_type == "missing":
            return "medium"

        return "low"

    def __str__(self):
        symbol_map = {
            "missing": "[-]",
            "extra": "[+]",
            "changed": "[~]"
        }
        symbol = symbol_map.get(self.drift_type, "[?]")
        return f"{symbol} {self.path} ({self.severity})"

    def to_dict(self):
        return {
            "path": self.path,
            "type": self.drift_type,
            "baseline": self.baseline_value,
            "current": self.current_value,
            "severity": self.severity
        }

    def is_critical(self):
        return self.severity == "high"


# -----------------------------
# Step 3–6: Full Comparison Engine
# -----------------------------
def compare_configs(baseline, current, path=""):
    results = []

    # Case 1: Both dicts
    if isinstance(baseline, dict) and isinstance(current, dict):
        baseline_keys = set(baseline.keys())
        current_keys = set(current.keys())

        # Missing keys
        for key in baseline_keys - current_keys:
            full_path = f"{path}.{key}" if path else key
            results.append(DriftResult(full_path, "missing", baseline[key], None))

        # Extra keys
        for key in current_keys - baseline_keys:
            full_path = f"{path}.{key}" if path else key
            results.append(DriftResult(full_path, "extra", None, current[key]))

        # Recurse into common keys
        for key in baseline_keys & current_keys:
            full_path = f"{path}.{key}" if path else key
            results.extend(
                compare_configs(baseline[key], current[key], full_path)
            )

    # Case 2: Both lists
    elif isinstance(baseline, list) and isinstance(current, list):
        max_len = max(len(baseline), len(current))

        for i in range(max_len):
            idx_path = f"{path}[{i}]"

            if i >= len(baseline):
                results.append(DriftResult(idx_path, "extra", None, current[i]))
            elif i >= len(current):
                results.append(DriftResult(idx_path, "missing", baseline[i], None))
            else:
                results.extend(
                    compare_configs(baseline[i], current[i], idx_path)
                )

    # Case 3: Leaf values
    else:
        if baseline != current:
            results.append(DriftResult(path, "changed", baseline, current))

    return results

# -----------------------------
# Run Script
# -----------------------------
def main():
    # Load JSON files FIRST
    baseline = load_json("baseline.json")
    current = load_json("current.json")

    # Stop if loading failed
    if baseline is None or current is None:
        return

    # Run comparison
    results = compare_configs(baseline, current)

    # Print results
    print("=== Drift Results ===")
    for r in results:
        print(r)

    # Summary (recommended)
    print("\n=== Summary ===")
    print(f"Total findings: {len(results)}")

    high = sum(1 for r in results if r.severity == "high")
    medium = sum(1 for r in results if r.severity == "medium")
    low = sum(1 for r in results if r.severity == "low")

    print(f"High: {high}, Medium: {medium}, Low: {low}")
if __name__ == "__main__":
    main()