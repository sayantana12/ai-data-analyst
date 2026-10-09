
from io import BytesIO
import pandas as pd
import streamlit as st


MAX_FILE_MB = 50


def validate_csv(uploaded_file):
    """Validate and load a Streamlit UploadedFile without changing user data."""
    try:
        raw = uploaded_file.getvalue()
        if not raw:
            return False, "The file is empty.", None

        size_mb = len(raw) / (1024 * 1024)
        if size_mb > MAX_FILE_MB:
            return False, f"File is {size_mb:.1f} MB; limit is {MAX_FILE_MB} MB.", None

        df = pd.read_csv(BytesIO(raw))

        if df.empty:
            return False, "CSV contains no rows.", None

        if len(df.columns) == 0:
            return False, "CSV contains no columns.", None

        # Strip accidental whitespace from column names and reject duplicates.
        df.columns = [str(c).strip() for c in df.columns]
        if len(set(df.columns)) != len(df.columns):
            return False, "CSV contains duplicate column names.", None

        return True, "Valid CSV.", df
    except Exception as exc:
        return False, f"Could not parse CSV: {exc}", None


def combine_files(frames, names):
    """Combine CSVs while preserving their source filename."""
    if len(frames) == 1:
        out = frames[0].copy()
        out["_source_file"] = names[0]
        return out

    all_columns = sorted(set().union(*(set(f.columns) for f in frames)))
    normalized = []
    for frame, name in zip(frames, names):
        x = frame.copy()
        for col in all_columns:
            if col not in x.columns:
                x[col] = pd.NA
        x["_source_file"] = name
        normalized.append(x[all_columns + ["_source_file"]])
    return pd.concat(normalized, ignore_index=True)


@st.cache_data(show_spinner=False)
def dataset_profile(df):
    rows = []
    for col in df.columns:
        s = df[col]
        rows.append(
            {
                "column": col,
                "dtype": str(s.dtype),
                "non_null": int(s.notna().sum()),
                "missing": int(s.isna().sum()),
                "unique": int(s.nunique(dropna=True)),
                "example": s.dropna().astype(str).head(1).tolist()[0] if s.notna().any() else "",
            }
        )
    return pd.DataFrame(rows)


@st.cache_data(show_spinner=False)
def data_quality_report(df):
    col_rows = []
    for col in df.columns:
        s = df[col]
        col_rows.append(
            {
                "column": col,
                "dtype": str(s.dtype),
                "missing": int(s.isna().sum()),
                "missing_pct": round(float(s.isna().mean() * 100), 2),
                "unique": int(s.nunique(dropna=True)),
            }
        )

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "missing_cells": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "columns": pd.DataFrame(col_rows),
    }
