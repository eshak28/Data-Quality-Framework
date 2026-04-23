import os
import pandas as pd

UPLOAD_DIR = "data"

os.makedirs(UPLOAD_DIR, exist_ok=True)

def save_file(file):
    filepath = os.path.join(UPLOAD_DIR, file.filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return filepath


def load_csv(filepath):
    return pd.read_csv(filepath)