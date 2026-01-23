# --- Variables --
student_name = "Cody"            # string
passpercent = 70                # int (minimum average to pass)
grades = [85, 72, 90, 66, 78]         # list of ints (example grades)

# --- Show the inputs ---
print()
print("=== Grade Calculator ===")
print("Student:", student_name)
print("Grades:", grades)
print("percent needed to pass:", passpercent)
print()

# --- Calculate total and average using a loop ---
print("=== Listing Grades ===")
total = 0
for g in grades:
    print("Grade:", g)
    total += g

average = total / len(grades)

print()
print("=== Summary ===")
print("Total points:", total)
print("Number of grades:", len(grades))
print(f"Average: {average:.2f}")

# --- Determine pass/fail using an if/else ---
if average >= passpercent:
    passed = True
    print("Result: Passing")
else:
    passed = False
    print("Result: Failing")

# --- Optional: Letter grade using if/elif/else ---
if average >= 90:
    letter = "A"
elif average >= 80:
    letter = "B"
elif average >= 70:
    letter = "C"
elif average >= 60:
    letter = "D"
else:
    letter = "F"

print("Letter grade:", letter)

# --- Feedback ---
print()
print("=== Feedback ===")
if passed and letter == "A":
    print("Cant get much better than that!")
elif passed and letter == "B":
    print("Good job! Keep up the good work.")
elif passed and letter == "C":
    print("Still passing, but you can do better.")
elif not passed:
    print("You are not passing at this time.")
