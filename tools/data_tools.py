"""
P1 owns this file — Data & Analysis Engineer.

Every function follows the same contract so P2 can wrap them as agent
tools without guessing: takes a DataFrame + simple args, returns
(result, chart_or_none). Docstrings matter — they're what the agent
reads to decide which tool to call, so keep them precise.
"""
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")  # no GUI backend needed — we're saving figures, not displaying live


def load_csv(file) -> pd.DataFrame:
    """Loads an uploaded CSV file into a DataFrame."""
    return pd.read_csv(file)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Basic cleaning: drops fully-empty rows/columns, strips whitespace
    from string columns, and tries to coerce numeric-looking columns
    that got read in as strings (common with CSVs that have stray
    commas or currency symbols).
    """
    df = df.dropna(axis=0, how="all").dropna(axis=1, how="all")

    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str).str.strip()
            # try to coerce to numeric; if it mostly fails, leave as text
            coerced = pd.to_numeric(df[col].str.replace(",", "").str.replace("$", ""), errors="coerce")
            if coerced.notna().sum() >= 0.9 * len(coerced):
                df[col] = coerced

    return df.reset_index(drop=True)


def get_stats(df: pd.DataFrame, column: str) -> dict:
    """
    Returns mean, median, min, max, std, and count for a numeric column.
    Use this when the user asks about averages, ranges, or summary
    statistics for a single column.
    """
    if column not in df.columns:
        return {"error": f"Column '{column}' not found. Available columns: {list(df.columns)}"}
    series = pd.to_numeric(df[column], errors="coerce").dropna()
    if series.empty:
        return {"error": f"Column '{column}' has no numeric data."}
    return {
        "mean": round(series.mean(), 2),
        "median": round(series.median(), 2),
        "min": round(series.min(), 2),
        "max": round(series.max(), 2),
        "std": round(series.std(), 2),
        "count": int(series.count()),
    }


def filter_data(df: pd.DataFrame, column: str, condition: str, value) -> pd.DataFrame:
    """
    Filters rows where `column` satisfies `condition` against `value`.
    condition must be one of: '==', '!=', '>', '<', '>=', '<='.
    Use this when the user wants a subset of the data, e.g.
    "show me employees with salary over 80000".
    """
    if column not in df.columns:
        return pd.DataFrame({"error": [f"Column '{column}' not found."]})

    ops = {
        "==": lambda s, v: s == v,
        "!=": lambda s, v: s != v,
        ">": lambda s, v: s > v,
        "<": lambda s, v: s < v,
        ">=": lambda s, v: s >= v,
        "<=": lambda s, v: s <= v,
    }
    if condition not in ops:
        return pd.DataFrame({"error": [f"Unsupported condition '{condition}'. Use one of {list(ops.keys())}"]})

    col_data = df[column]
    # try numeric comparison first, fall back to string
    try:
        value_cast = float(value)
        col_data = pd.to_numeric(col_data, errors="coerce")
    except (ValueError, TypeError):
        value_cast = value

    return df[ops[condition](col_data, value_cast)].reset_index(drop=True)


def group_by(df: pd.DataFrame, group_col: str, agg_col: str, agg_func: str = "mean") -> pd.DataFrame:
    """
    Groups by `group_col` and aggregates `agg_col` using agg_func
    ('mean', 'sum', 'count', 'min', 'max'). Use this for questions like
    "average salary by department" or "total sales by region".
    """
    if group_col not in df.columns or agg_col not in df.columns:
        return pd.DataFrame({"error": [f"Column not found. Available: {list(df.columns)}"]})
    if agg_func not in ("mean", "sum", "count", "min", "max"):
        return pd.DataFrame({"error": [f"Unsupported agg_func '{agg_func}'"]})

    numeric_col = pd.to_numeric(df[agg_col], errors="coerce")
    temp = df[[group_col]].copy()
    temp[agg_col] = numeric_col
    result = temp.groupby(group_col)[agg_col].agg(agg_func).reset_index()
    return result.sort_values(by=agg_col, ascending=False).reset_index(drop=True)


def top_n(df: pd.DataFrame, column: str, n: int = 5, ascending: bool = False) -> pd.DataFrame:
    """
    Returns the top (or bottom, if ascending=True) N rows sorted by `column`.
    Use this for "top 5 highest paid employees" or "5 lowest scores" type questions.
    """
    if column not in df.columns:
        return pd.DataFrame({"error": [f"Column '{column}' not found."]})
    sort_col = pd.to_numeric(df[column], errors="coerce")
    temp = df.copy()
    temp["_sort"] = sort_col
    result = temp.sort_values(by="_sort", ascending=ascending).drop(columns="_sort").head(n)
    return result.reset_index(drop=True)


def correlate(df: pd.DataFrame, col1: str, col2: str) -> dict:
    """
    Returns the Pearson correlation coefficient between two numeric columns.
    Use this when the user asks if two variables are related, e.g.
    "is there a correlation between experience and salary?"
    """
    if col1 not in df.columns or col2 not in df.columns:
        return {"error": f"Column not found. Available: {list(df.columns)}"}
    s1 = pd.to_numeric(df[col1], errors="coerce")
    s2 = pd.to_numeric(df[col2], errors="coerce")
    corr = s1.corr(s2)
    if pd.isna(corr):
        return {"error": "Could not compute correlation — check that both columns are numeric."}
    return {"correlation": round(corr, 3), "column_1": col1, "column_2": col2}


def make_chart(df: pd.DataFrame, chart_type: str, x: str, y: str = None, save_path: str = "chart.png"):
    """
    Generates a chart and saves it to save_path. chart_type must be one
    of: 'bar', 'line', 'scatter', 'pie'. For 'pie', only `x` is used
    (categorical column). For others, both x and y are required.
    Use this whenever the user asks to see/visualize/plot/chart data.
    """
    if x not in df.columns:
        return {"error": f"Column '{x}' not found."}

    fig, ax = plt.subplots(figsize=(8, 5))

    try:
        if chart_type == "bar":
            data = df.groupby(x)[y].mean() if y else df[x].value_counts()
            data.plot(kind="bar", ax=ax)
        elif chart_type == "line":
            df.plot(x=x, y=y, kind="line", ax=ax)
        elif chart_type == "scatter":
            df.plot(x=x, y=y, kind="scatter", ax=ax)
        elif chart_type == "pie":
            df[x].value_counts().plot(kind="pie", ax=ax, autopct="%1.1f%%")
        else:
            return {"error": f"Unsupported chart_type '{chart_type}'. Use bar/line/scatter/pie."}
    except Exception as e:
        return {"error": f"Chart generation failed: {e}"}

    ax.set_title(f"{chart_type.title()} chart: {x}" + (f" vs {y}" if y else ""))
    fig.tight_layout()
    fig.savefig(save_path)
    plt.close(fig)
    return {"chart_path": save_path}
