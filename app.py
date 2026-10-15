from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent

def load_csv(path):
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception as exc:
            st.warning(f"Could not read {path.name}: {exc}")
    return pd.DataFrame()

st.set_page_config(page_title="Data Quality & MIS Dashboard", page_icon="📊", layout="wide")
st.title("Customer Data Quality & MIS Reporting")
st.caption("Automated data checks, exception tracking, and management reporting.")

quality = load_csv(ROOT / "reports" / "data_quality_report.csv")
exceptions = load_csv(ROOT / "reports" / "sales_exceptions.csv")
summary = load_csv(ROOT / "reports" / "mis_summary.csv")
customers = load_csv(ROOT / "data" / "processed" / "customers_reviewed.csv")
sales = load_csv(ROOT / "data" / "processed" / "sales_cleaned.csv")

a, b, c, d = st.columns(4)
a.metric("Customers reviewed", f"{len(customers):,}")
b.metric("Cleaned sales records", f"{len(sales):,}")
c.metric("Quality checks", f"{len(quality):,}")
d.metric("Records flagged", f"{len(exceptions):,}")

st.subheader("MIS Summary")
if not summary.empty:
    st.dataframe(summary, use_container_width=True, hide_index=True)
else:
    st.info("Run the pipeline scripts to generate the MIS summary.")

left, right = st.columns(2)
with left:
    st.subheader("Data Quality Report")
    if quality.empty:
        st.info("No quality report found yet.")
    else:
        st.dataframe(quality, use_container_width=True, hide_index=True)

with right:
    st.subheader("Sales Exceptions")
    if exceptions.empty:
        st.success("No sales exceptions found.")
    else:
        st.dataframe(exceptions, use_container_width=True, hide_index=True)

st.subheader("Cleaned Sales Data")
if not sales.empty:
    st.dataframe(sales.head(100), use_container_width=True, hide_index=True)
    st.download_button(
        "Download cleaned sales CSV",
        sales.to_csv(index=False).encode("utf-8"),
        "sales_cleaned.csv",
        "text/csv",
    )

st.subheader("Reviewed Customer Data")
if not customers.empty:
    st.dataframe(customers.head(100), use_container_width=True, hide_index=True)
    st.download_button(
        "Download reviewed customers CSV",
        customers.to_csv(index=False).encode("utf-8"),
        "customers_reviewed.csv",
        "text/csv",
    )
