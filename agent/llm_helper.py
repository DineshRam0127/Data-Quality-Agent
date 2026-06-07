def generate_fix(issue):

    if "NULL" in issue:
        return """
Root Cause:
Missing values detected.

Pandas Fix:
df['name'].fillna('Unknown', inplace=True)

SQL Fix:
UPDATE employees
SET name='Unknown'
WHERE name IS NULL;
"""

    elif "positive" in issue:
        return """
Root Cause:
Negative salary found.

Pandas Fix:
df['salary'] = df['salary'].abs()

SQL Fix:
UPDATE employees
SET salary=ABS(salary)
WHERE salary<0;
"""

    elif "duplicates" in issue:
        return """
Root Cause:
Duplicate emails found.

Pandas Fix:
df.drop_duplicates(inplace=True)

SQL Fix:
Remove duplicate records.
"""

    elif "emails" in issue:
        return """
Root Cause:
Invalid email format.

Pandas Fix:
Correct email values.

SQL Fix:
UPDATE invalid emails.
"""

    return "No fix available."