import pandas as pd


def calculate_quality_score(df, failures):

    total_rows = len(df)

    if total_rows == 0:
        return {
            "overall": 100,
            "completeness": 100,
            "validity": 100,
            "uniqueness": 100,
            "consistency": 100
        }

    # Completeness
    missing_cells = df.isnull().sum().sum()
    total_cells = df.shape[0] * df.shape[1]

    completeness = max(
        0,
        round(
            ((total_cells - missing_cells)
             / total_cells) * 100
        )
    )

    # Validity
    validity_penalty = 0

    for failure in failures:
        if (
            "invalid emails" in failure["issue"]
            or
            "positive" in failure["issue"]
        ):
            validity_penalty += len(failure["rows"])

    validity = max(
        0,
        round(
            100 - ((validity_penalty / total_rows) * 100)
        )
    )

    # Uniqueness
    duplicate_penalty = 0

    for failure in failures:
        if "duplicates" in failure["issue"]:
            duplicate_penalty += len(failure["rows"])

    uniqueness = max(
        0,
        round(
            100 - ((duplicate_penalty / total_rows) * 100)
        )
    )

    # Consistency
    schema_errors = 0

    for failure in failures:
        if "Schema Error" in failure["issue"]:
            schema_errors += 1

    consistency = max(
        0,
        100 - (schema_errors * 20)
    )

    overall = round(
        (
            completeness
            + validity
            + uniqueness
            + consistency
        ) / 4
    )

    return {
        "overall": overall,
        "completeness": completeness,
        "validity": validity,
        "uniqueness": uniqueness,
        "consistency": consistency
    }