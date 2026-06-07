import pandas as pd
import re

def validate(df, rules):

    failures = []

    # Ensure rules and checks exist before looping
    if not rules or "checks" not in rules:
        return failures

    for rule in rules["checks"]:

        column = rule["column"]
        rule_type = rule["type"]

        # SAFEGUARD: If the column specified in the YAML doesn't exist in the uploaded CSV, 
        # log it as a schema issue and skip to the next rule instead of crashing.
        if column not in df.columns:
            failures.append({
                "issue": f"Schema Error: Expected column '{column}' was not found in the uploaded CSV file.",
                "rows": df.head(0)  # Safe empty dataframe with structural headers
            })
            continue

        if rule_type == "not_null":

            bad_rows = df[df[column].isnull()]

            if not bad_rows.empty:
                failures.append({
                    "issue": f"{column} contains NULL values",
                    "rows": bad_rows
                })

        elif rule_type == "positive":

            bad_rows = df[df[column] <= 0]

            if not bad_rows.empty:
                failures.append({
                    "issue": f"{column} should be positive",
                    "rows": bad_rows
                })

        elif rule_type == "unique":

            bad_rows = df[df[column].duplicated(keep=False)]

            if not bad_rows.empty:
                failures.append({
                    "issue": f"{column} contains duplicates",
                    "rows": bad_rows
                })

        elif rule_type == "email":

            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

            bad_rows = df[
                ~df[column].astype(str).str.match(pattern)
            ]

            if not bad_rows.empty:
                failures.append({
                    "issue": f"{column} contains invalid emails",
                    "rows": bad_rows
                })

    return failures