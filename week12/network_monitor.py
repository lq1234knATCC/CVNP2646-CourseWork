import sys
import json
import argparse
from pathlib import Path

def log_debug(msg):
    if CURRENT_LOG_LEVEL == "DEBUG":
        print(f"[DEBUG] {msg}")

def log_info(msg):
    if CURRENT_LOG_LEVEL in ["DEBUG", "INFO"]:
        print(f"[INFO] {msg}")

def log_warning(msg):
    if CURRENT_LOG_LEVEL in ["DEBUG", "INFO", "WARNING"]:
        print(f"[WARNING] {msg}")

def log_error(msg):
    print(f"[ERROR] {msg}")

def load_traffic_log(filename):
    lines = read_log_file(filename)
    packets, _ = parse_packets(lines)
    return packets

class NetworkConfig:
    def __init__(self, port_scan_threshold=25, syn_flood_threshold=100):
        self.port_scan_threshold = port_scan_threshold
        self.syn_flood_threshold = syn_flood_threshold
        self.debug = True
        self.output_file = "results.json"


def read_log_file(filename):
    with open(filename, 'r') as f:
        return f.readlines()


def parse_packet_line(line):
    line = line.strip()

    if not line:
        raise ValueError("Empty line")

    parts = [p.strip() for p in line.split(",")]

    if len(parts) != 6:
        raise ValueError("Invalid number of fields")

    try:
        return {
            "src_ip": parts[0],
            "dst_ip": parts[1],
            "src_port": int(parts[2]),
            "dst_port": int(parts[3]),
            "protocol": parts[4],
            "flags": parts[5]
        }
    except ValueError:
        raise ValueError("Invalid port value")


def parse_packets(lines):
    packets = []
    errors = 0

    for i, line in enumerate(lines):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        try:
            packet = parse_packet_line(line)
            packets.append(packet)
            log_debug(f"Parsed packet {i}")
        except ValueError:
            errors += 1
            log_error(f"Failed to parse line {i}: {line}")

    return packets, errors

def get_unique_src_ips(packets):
    return list(set(p["src_ip"] for p in packets))


def detect_port_scan(packets, ip, threshold):
    ports = set()

    for p in packets:
        if p.get("src_ip") == ip:
            ports.add(p.get("dst_port"))

    return len(ports) > threshold


def detect_syn_flood(packets, ip, threshold):
    count = 0

    for p in packets:
        if p.get("src_ip") == ip:
            if p.get("protocol") == "TCP" and "SYN" in p.get("flags", ""):
                count += 1

    return count > threshold

def detect_port_scans(packets, config):
    results = []
    src_ips = get_unique_src_ips(packets)

    for ip in src_ips:
        if detect_port_scan(packets, ip, config.port_scan_threshold):
            log_warning(f"PORT SCAN DETECTED from {ip}")
            results.append(ip)

    return results


def detect_syn_floods(packets, config):
    results = []
    src_ips = get_unique_src_ips(packets)

    for ip in src_ips:
        if detect_syn_flood(packets, ip, config.syn_flood_threshold):
            log_warning(f"SYN FLOOD DETECTED from {ip}")
            results.append(ip)

    return results

def analyze_traffic(packets, config):
    return {
        "total_packets": len(packets),
        "port_scans": detect_port_scans(packets, config),
        "syn_floods": detect_syn_floods(packets, config)
    }

def generate_json_report(results, output_file="results.json"):
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    log_info(f"JSON report written to {output_file}")

def run_monitor():
    if len(sys.argv) < 2:
        log_error("Usage: python network_monitor.py <log_file>")
        sys.exit(1)

    config = NetworkConfig()
    log_file = sys.argv[1]

    log_info("Starting network monitor...")
    log_info(f"Reading file: {log_file}")

    lines = read_log_file(log_file)
    packets, errors = parse_packets(lines)

    log_info(f"Parsed {len(packets)} packets with {errors} errors")

    results = analyze_traffic(packets, config)

    generate_json_report(results, config.output_file)

    log_info("Done!")

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Network Traffic Monitor - Detect suspicious patterns',
        epilog='Example: %(prog)s traffic.log -o results.json -v'
    )

    parser.add_argument(
        'input_file',
        type=Path,
        help='Path to network traffic log (CSV format)'
    )

    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('results.json'),
        help='Output file (default: results.json)'
    )

    parser.add_argument(
        '--port-scan-threshold', '-p',
        type=int,
        default=25,
        metavar='N',
        help='Port scan threshold (default: 25)'
    )

    parser.add_argument(
        '--syn-flood-threshold', '-s',
        type=int,
        default=100,
        metavar='N',
        help='SYN flood threshold (default: 100)'
    )

    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging verbosity'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable debug output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    return parser

def validate_args(args: argparse.Namespace) -> None:
    if not args.input_file.exists():
        raise FileNotFoundError(f"Input file not found: {args.input_file}")

    if not args.input_file.is_file():
        raise ValueError(f"Input path is not a file: {args.input_file}")

    if args.port_scan_threshold < 1:
        raise ValueError("Port scan threshold must be positive")

    if args.syn_flood_threshold < 1:
        raise ValueError("SYN flood threshold must be positive")

    if args.verbose:
        args.log_level = 'DEBUG'

CURRENT_LOG_LEVEL = "INFO"

def setup_logging(log_level="INFO"):
    global CURRENT_LOG_LEVEL
    CURRENT_LOG_LEVEL = log_level
    return True

def main() -> int:
    parser = create_parser()
    args = parser.parse_args()

    try:
        validate_args(args)

        setup_logging(args.log_level)
        log_info("Network Monitor v1.0.0 starting")

        config = NetworkConfig(
            port_scan_threshold=args.port_scan_threshold,
            syn_flood_threshold=args.syn_flood_threshold
        )

        packets = load_traffic_log(str(args.input_file))
        results = analyze_traffic(packets, config)

        # Write output file
        generate_json_report(results, str(args.output))

        # Summary output
        print("\n✓ Analysis complete")
        print(f"  Total packets: {results['total_packets']}")
        print(f"  Port scans: {len(results['port_scans'])}")
        print(f"  SYN floods: {len(results['syn_floods'])}")

        return 0

    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())