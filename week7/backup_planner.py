import json
import random
from datetime import datetime



# --------------------------------------------------
# STEP 1 - Load JSON configuration
# --------------------------------------------------

def load_config(filepath):

    try: #open file
        with open(filepath, "r") as file:
            config = json.load(file)
            return config

    #stops the program if there is a major JSON formatting error
    except json.JSONDecodeError as e:
        print(f"JSON syntax error: {e}")
        return None

    #stops the program if the file is not found
    except FileNotFoundError:
        print("Configuration file not found.")
        return None


# --------------------------------------------------
# STEP 2 - Validate Required Fields
# --------------------------------------------------

def validate_required_fields(config): #checks that required fields all exist

    errors = [] #dictionary to store error messages

    required_fields = ["plan_name", "sources", "destination"] #list of fields that is required in the config

    for field in required_fields: #loops through required fields to check if they are in the config appends error if they are not
        if field not in config:
            errors.append(f"Missing required field: '{field}'")

    return errors


# --------------------------------------------------
# STEP 3 - Validate Types
# --------------------------------------------------

def validate_types(config):
    errors = []

    if "plan_name" in config and not isinstance(config["plan_name"], str): #checks that the plan_name field is a string and adds an error if it is not
        errors.append(f"'plan_name' must be a string, got {type(config['plan_name']).__name__}")

    if "sources" in config and not isinstance(config["sources"], list): #checks that the sources field is a list and adds an error if it is not
        errors.append(f"'sources' must be a list, got {type(config['sources']).__name__}")

    if "destination" in config and not isinstance(config["destination"], dict): #checks that the destination field is a dictionary and adds an error if it is not
        errors.append(f"'destination' must be a dictionary")

    # Validate optional field if present
    if "version" in config and not isinstance(config["version"], str): 
        errors.append("'version' must be a string")

    return errors


# --------------------------------------------------
# STEP 4 - Validate Values
# --------------------------------------------------

def validate_values(config): #checks that values are of the expected format

    errors = []

    sources = config.get("sources", [])

    # Ensure sources list is not empty
    if len(sources) == 0:
        errors.append("Sources list cannot be empty.")

    for i, source in enumerate(sources): #for each source, perform the below checks

        # Ensure path exists
        if "path" not in source:
            errors.append(f"Source {i}: missing 'path' field")

        # Ensure path is not blank
        elif not source["path"].strip():
            errors.append(f"Source {i}: 'path' cannot be empty")

        # Check any included patterns are a list
        if "include_patterns" in source and not isinstance(source["include_patterns"], list):
            errors.append(f"Source {i}: 'include_patterns' must be a list")

    #retrieve destination field from config
    destination = config.get("destination", {})

    if "base_path" not in destination: #append error if the destination field does not contain a base_path field
        errors.append("Destination missing 'base_path'")

    return errors

def validate_config(config): # combines all validation steps into one function

    errors = []

    errors.extend(validate_required_fields(config))
    errors.extend(validate_types(config))
    errors.extend(validate_values(config))

    return (len(errors) == 0, errors)


# --------------------------------------------------
# STEP 5 - Simulation (Pattern-Based Fake Files)
# --------------------------------------------------

def simulate_backup(config):
    """Generate a dry-run simulation using fake file data."""
    operations = []

    for source in config['sources']:
        num_files = random.randint(5, 15)
        files = []

        for i in range(num_files):
            size_mb = round(random.uniform(1, 100), 1)
            name = f"{source['name'].lower().replace(' ', '_')}_{i+1:03d}.log"
            files.append({"name": name, "size_mb": size_mb})

        operations.append({
            "source_name": source['name'],
            "source_path": source['path'],
            "files": files
        })

    total_files = sum(len(op['files']) for op in operations)
    total_size = round(
        sum(f['size_mb'] for op in operations for f in op['files']), 1
    )

    return {
        "plan_name": config['plan_name'],
        "mode": "DRY-RUN",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_sources": len(operations),
            "total_files": total_files,
            "total_size_mb": total_size
        },
        "operations": operations
    }

# -----------------------------
# REPORT FUNCTION
# -----------------------------
def generate_report(report_data):
    """Print formatted dry-run simulation report and write to sample_report.txt."""
    sep = "=" * 70
    thin = "-" * 70

    # Open file for writing report
    with open("sample_report.txt", "w") as report_file:

        def output(line=""):
            print(line)
            report_file.write(line + "\n")

        output(sep)
        output(f"{'BACKUP PLAN DRY-RUN SIMULATION':^70}")
        output(sep)
        output(f"Plan: {report_data['plan_name']}")
        output(f"Mode: {report_data['mode']} (no files will be copied)")
        output(f"Timestamp: {report_data.get('timestamp', 'N/A')}")
        output()

        s = report_data['summary']
        output("SUMMARY")
        output(thin[:7])
        output(f"Total Sources:  {s['total_sources']}")
        output(f"Total Files:    {s['total_files']}")
        output(f"Total Size:     {s['total_size_mb']} MB")
        output()

        for i, op in enumerate(report_data['operations'], 1):
            output(f"SOURCE {i}: {op['source_name']}")
            output(f"Path: {op['source_path']}")
            output(f"Files: {len(op['files'])}")
            for f in op['files'][:3]:
                output(f"  -> {f['name']} ({f['size_mb']} MB)")
            remaining = len(op['files']) - 3
            if remaining > 0:
                output(f"  ... and {remaining} more files")
            output()

        output(sep)
        output("DRY-RUN complete. No files were copied.")
        output(sep)


# -----------------------------
# MAIN PROGRAM
# -----------------------------
def main():
    """Orchestrate the backup planning pipeline."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python backup_planner.py ")
        sys.exit(1)

    filepath = sys.argv[1]

    # Step 1: Load
    config = load_config(filepath)
    if config is None:
        sys.exit(1)

    # Step 2: Validate
    is_valid, errors = validate_config(config)
    if not is_valid:
        print(f"Validation FAILED. {len(errors)} error(s) found:")
        for i, err in enumerate(errors, 1):
            print(f"  [{i}] {err}")
        sys.exit(1)

    print("Validation PASSED.")

    # Step 3: Simulate
    report_data = simulate_backup(config)

    # Step 4: Report
    generate_report(report_data)


if __name__ == "__main__":
    main()