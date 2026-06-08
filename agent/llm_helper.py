def generate_fix(issue):

    if "NULL" in issue:
        return """
Root Cause:
Missing values detected.

Pandas Fix:
df['name'] = df['name'].fillna('Unknown')

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
SET salary = ABS(salary)
WHERE salary < 0;
"""

    elif "duplicates" in issue:
        return """
Root Cause:
Duplicate email records detected.

Pandas Fix:
df = df.drop_duplicates(subset=['email'])

SQL Fix:
DELETE FROM employees
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM employees
    GROUP BY email
);
"""

    elif "emails" in issue:
        return """
Root Cause:
Invalid email format detected.

Pandas Fix:
import re

pattern = r'^[\\w\\.-]+@[\\w\\.-]+\\.\\w+$'

df = df[
    df['email'].astype(str).str.match(pattern)
]

SQL Fix:
DELETE FROM employees
WHERE email NOT LIKE '%@%.%';

Alternative SQL Fix:
UPDATE employees
SET email='valid@example.com'
WHERE email NOT LIKE '%@%.%';
"""

    elif "Schema Error" in issue:
        return """
Root Cause:
Required column is missing from uploaded CSV.

Pandas Fix:
Add the missing column before validation.

Example:
df['salary'] = 0

SQL Fix:
ALTER TABLE employees
ADD COLUMN salary INTEGER;
"""

    elif "type" in issue.lower():
        return """
Root Cause:
Invalid datatype detected.

Pandas Fix:
import pandas as pd

df['salary'] = pd.to_numeric(
    df['salary'],
    errors='coerce'
)

SQL Fix:
ALTER TABLE employees
MODIFY salary INTEGER;
"""

    return """
Root Cause:
Data quality issue detected.

Pandas Fix:
Inspect affected rows and apply appropriate data cleaning operations such as:

df.fillna()
df.drop_duplicates()
df.replace()
df.astype()

SQL Fix:
Review affected records and perform corrective operations using SQL statements.

Example:

UPDATE table_name
SET column_name = corrected_value
WHERE condition;
"""