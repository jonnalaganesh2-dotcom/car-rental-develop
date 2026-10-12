import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Take input from user
students = []
n = int(input("Enter number of students: "))

for i in range(n):
    print(f"\nEnter details for Student {i+1}:")
    name = input("Name: ")
    maths = int(input("Maths Marks: "))
    science = int(input("Science Marks: "))
    english = int(input("English Marks: "))
    
    students.append({
        "Name": name,
        "Maths": maths,
        "Science": science,
        "English": english
    })

# Step 2: Convert to DataFrame
df = pd.DataFrame(students)

# Step 3: Calculate total and percentage
df["Total"] = df[["Maths", "Science", "English"]].sum(axis=1)
df["Percentage"] = (df["Total"] / 300) * 100

# Step 4: Assign grades
def assign_grade(p):
    if p >= 80:
        return "A"
    elif p >= 60:
        return "B"
    elif p >= 40:
        return "C"
    else:
        return "Fail"

df["Grade"] = df["Percentage"].apply(assign_grade)

# Step 5: Round percentages to 2 decimals
df["Percentage"] = df["Percentage"].round(2)

# Step 6: Show summary (formatted output)
print("\n📊 Student Report:")
print(df.to_string(index=False))

print("\n🔹 Class Average Marks:")
print(df[["Maths", "Science", "English"]].mean().round(1))

topper = df.loc[df["Total"].idxmax()]
print("\n🏆 Topper:")
for col, val in topper.items():
    print(f"{col:12} {val}")

# Step 7: Plot performance
plt.figure(figsize=(8,5))
df.plot(x="Name", y=["Maths", "Science", "English"], kind="bar")
plt.title("Subject-wise Performance")
plt.xlabel("Students")
plt.ylabel("Marks")
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()
