def suggest_fixes(df):
    suggestions = {}

    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype != "object":
                suggestions[col] = "Fill with median"
            else:
                suggestions[col] = "Fill with mode"

    return suggestions


def auto_clean(df):
    for col in df.columns:
        if df[col].isnull().sum() > 0:
            if df[col].dtype != "object":
                df[col].fillna(df[col].median(), inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)

    df = df.drop_duplicates()

    return df