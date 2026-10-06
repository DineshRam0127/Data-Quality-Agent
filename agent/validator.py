import pandas as pd
import re

def validate(df, rules):

    failures = []

    if not rules or "checks" not in rules:
        return failures

    for rule in rules["checks"]:

        column = rule["column"]
        rule_type = rule["type"]

        # Check column exists
        if column not in df.columns:

            failures.append({
                "issue": f"Schema Error: Expected column '{column}' was not found",
                "rows": df.head(0)
            })

            continue

        # =========================
        # NOT NULL CHECK
        # =========================

        if rule_type == "not_null":

            bad_rows = df[
    df[column].isnull() |
    (df[column].astype(str).str.strip() == "") |
    (df[column].astype(str).str.lower() == "none") |
    (df[column].astype(str).str.lower() == "null")
]

            if not bad_rows.empty:

                failures.append({
                    "issue": f"{column} contains NULL values",
                    "rows": bad_rows
                })

        # =========================
        # POSITIVE NUMBER CHECK
        # =========================

        elif rule_type == "positive":

            try:

                numeric_col = pd.to_numeric(
                    df[column],
                    errors="coerce"
                )

                bad_rows = df[
                    (numeric_col <= 0) |
                    (numeric_col.isna())
                ]

                if not bad_rows.empty:

                    failures.append({
                        "issue": f"{column} contains invalid or non-positive values",
                        "rows": bad_rows
                    })

            except Exception as e:

                failures.append({
                    "issue": f"Validation Error in column '{column}': {str(e)}",
                    "rows": df.head(0)
                })

        # =========================
        # UNIQUE CHECK
        # =========================

        elif rule_type == "unique":

            bad_rows = df[
                df[column].duplicated(
                    keep=False
                )
            ]

            if not bad_rows.empty:

                failures.append({
                    "issue": f"{column} contains duplicates",
                    "rows": bad_rows
                })

        # =========================
        # EMAIL CHECK
        # =========================

        elif rule_type == "email":

            pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

            bad_rows = df[
                ~df[column]
                .astype(str)
                .str.match(pattern)
            ]

            if not bad_rows.empty:

                failures.append({
                    "issue": f"{column} contains invalid emails",
                    "rows": bad_rows
                })

    return failures