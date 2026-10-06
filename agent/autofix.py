import pandas as pd

def auto_fix(df):

    # =========================
    # FIX NAME
    # =========================
    if "name" in df.columns:

        df["name"] = (
            df["name"]
            .astype(str)
            .replace(
                ["None", "none", "NULL", "null", "", "nan"],
                "Unknown"
            )
        )

    # =========================
    # FIX DEPARTMENT
    # =========================
    if "department" in df.columns:

        df["department"] = (
            df["department"]
            .astype(str)
            .str.strip()
        )

        df.loc[
            df["department"].isin(
                ["None", "none", "NULL", "null", "", "nan"]
            ),
            "department"
        ] = "Unknown Department"

    # =========================
    # FIX JOINING DATE
    # =========================
    if "joining_date" in df.columns:

        df["joining_date"] = (
            df["joining_date"]
            .astype(str)
            .str.strip()
        )

        df.loc[
            df["joining_date"].isin(
                ["None", "none", "NULL", "null", "", "nan"]
            ),
            "joining_date"
        ] = "Unknown"

    # =========================
    # FIX SALARY
    # =========================
    if "salary" in df.columns:

        def fix_salary(x):

            try:
                value = float(x)

                # negative -> positive
                if value < 0:
                    return abs(value)

                # zero -> Unknown
                if value == 0:
                    return "Unknown"

                return value

            except:
                # text/non-numeric -> Unknown
                return "Unknown"

        df["salary"] = df["salary"].apply(fix_salary)

    # =========================
    # FIX EMAIL
    # =========================
    if "email" in df.columns:

        def fix_email(email):

            email = str(email).strip().lower()

            if email in ["", "nan", "none", "null"]:
                return "unknown@gmail.com"

            if "@" not in email:

                if "gmail.com" in email:
                    username = email.replace(
                        "gmail.com",
                        ""
                    ).rstrip(".")
                    return f"{username}@gmail.com"

                elif "yahoo.com" in email:
                    username = email.replace(
                        "yahoo.com",
                        ""
                    ).rstrip(".")
                    return f"{username}@yahoo.com"

                elif "hotmail.com" in email:
                    username = email.replace(
                        "hotmail.com",
                        ""
                    ).rstrip(".")
                    return f"{username}@hotmail.com"

                elif "outlook.com" in email:
                    username = email.replace(
                        "outlook.com",
                        ""
                    ).rstrip(".")
                    return f"{username}@outlook.com"

                return f"{email}@gmail.com"

            username, domain = email.split("@", 1)

            if domain.strip() == "":
                domain = "gmail.com"

            elif "." not in domain:
                domain += ".com"

            return f"{username}@{domain}"

        df["email"] = df["email"].apply(fix_email)

        df = df.drop_duplicates(
            subset=["email"],
            keep="first"
        )

    return df