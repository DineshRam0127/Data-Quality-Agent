import pandas as pd

def auto_fix(df):

    # Fix missing names
    if "name" in df.columns:
        df["name"] = (
            df["name"]
            .fillna("Unknown")
            .replace("", "Unknown")
        )

    # Fix salary issues
    if "salary" in df.columns:
        df["salary"] = pd.to_numeric(
            df["salary"],
            errors="coerce"
        ).fillna(0)

        # Convert negative values to positive
        df["salary"] = df["salary"].abs()

    # Fix email issues
    if "email" in df.columns:

        def fix_email(email):

            email = str(email).strip()

            # Empty email
            if email == "" or email.lower() == "nan":
                return "unknown@gmail.com"

            # Missing @
            if "@" not in email:
                email = email + "@gmail.com"

            username, domain = email.split("@", 1)

            # Missing domain
            if domain.strip() == "":
                domain = "gmail.com"

            # Missing extension
            if "." not in domain:
                domain += ".com"

            return f"{username}@{domain}"

        # Apply email corrections
        df["email"] = df["email"].apply(fix_email)

        # Make duplicate emails unique instead of deleting rows
        email_counter = {}
        unique_emails = []

        for email in df["email"]:

            if email not in email_counter:
                email_counter[email] = 0
                unique_emails.append(email)

            else:
                email_counter[email] += 1

                username, domain = email.split("@", 1)

                new_email = (
                    f"{username}{email_counter[email]}"
                    f"@{domain}"
                )

                unique_emails.append(new_email)

        df["email"] = unique_emails

    return df