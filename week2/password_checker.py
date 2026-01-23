
def check_password_strength(password):
    """
    Evaluates password strength based on multiple criteria.

    Args:
        password (str): The password to evaluate

    Returns:
        str: Strength rating with feedback
    """
    score = 0
    feedback = []

    # Check length
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Too short (minimum 8 characters)")

    # Check for uppercase letters
    if any(c.isupper() for c in password):
        score += 1
    else:
        feedback.append("Add uppercase letters")

    # Check for lowercase letters
    if any(c.islower() for c in password):
        score += 1
    else:
        feedback.append("Add lowercase letters")

    # Check for digits
    if any(c.isdigit() for c in password):
        score += 1
    else:
        feedback.append("Add numbers")

    # Check for special characters
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if any(c in special_chars for c in password):
        score += 1
    else:
        feedback.append("Add special characters")

    # Determine strength rating
    if score <= 2:
        rating = "WEAK ❌"
    elif score <= 4:
        rating = "MEDIUM ⚠️"
    else:
        rating = "STRONG ✅"

    # Build result message
    if feedback:
        return f"{rating} - Issues: {', '.join(feedback)}"
    else:
        return f"{rating} - Excellent password!"


# Test cases
test_passwords = [
    "weak",             # Weak
    "Password1",        # Medium (missing special char)
    "Pass123!",         # Strong
    "VeryStr0ng!Pass",  # Strong
    "12345678",         # Weak (only numbers)
]

print("Password Strength Checker")
print("=" * 60)
for pwd in test_passwords:
    result = check_password_strength(pwd)
    print(f"'{pwd}' → {result}")
    print()
