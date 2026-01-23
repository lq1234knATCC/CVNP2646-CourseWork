
def validate_ip(ip_address):
    """
    Validates if a string is a valid IPv4 address.
    Returns True if valid, False otherwise.
    """
    try:
        # Split the IP address by dots
        octets = ip_address.split('.')

        # Must have exactly 4 parts
        if len(octets) != 4:
            return False

        # Check each octet
        for octet in octets:
            # Each octet must be digits only
            if not octet.isdigit():
                return False

            # Convert to integer
            num = int(octet)

            # Check if in valid range (0-255)
            if num < 0 or num > 255:
                return False

        # All checks passed
        return True

    except ValueError:
        # If conversion to int fails, treat as invalid
        return False


# ---- Test code ----
test_ips = [
    "192.168.1.1",        # Valid
    "10.0.0.1",           # Valid
    "256.1.1.1",          # Invalid (256 > 255)
    "192.168.1",          # Invalid (only 3 octets)
    "abc.def.ghi.jkl",    # Invalid (not numbers)
    "192.168.1.1.1",      # Invalid (5 octets)
]

print("IP Address Validator")
print("=" * 40)
for ip in test_ips:
    result = "✅ VALID" if validate_ip(ip) else "❌ INVALID"
    print(f"{ip:20} → {result}")
