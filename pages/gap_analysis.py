import streamlit as st
import pandas as pd
import plotly.express as px

st.title("📊 Gap Analysis - LUDIP Planning")

# Load data
alloc = pd.read_csv("data/allocations.csv")
pop = pd.read_csv("data/population.csv")
std = pd.read_csv("data/standards.csv")

# ----------------------------
# COMPUTE REQUIRED AREA
# ----------------------------
total_students = pop["students"].sum()
total_staff = pop["staff"].sum()

required = []

for _, row in std.iterrows():
    facility = row["facility_type"]
    factor = row["sqm_per_person"]

    if facility == "classroom":
        req = total_students * factor
    elif facility == "library":
        req = total_students * factor
    elif facility == "admin":
        req = total_staff * factor
    else:
        req = 0

    required.append({
        "facility_type": facility,
        "required_area": req
    })

required_df = pd.DataFrame(required)

# ----------------------------
# EXISTING AREA
# ----------------------------
existing = alloc.groupby("facility_type")["area_sqm"].sum().reset_index()
existing.columns = ["facility_type", "existing_area"]

# ----------------------------
# MERGE
# ----------------------------
df = pd.merge(required_df, existing, on="facility_type", how="left")
df["existing_area"] = df["existing_area"].fillna(0)

# ----------------------------
# GAP
# ----------------------------
df["gap"] = df["required_area"] - df["existing_area"]

def status(x):
    if x > 0:
        return "🔴 Deficient"
    elif x > -0.2 * df["required_area"].max():
        return "🟡 Near Limit"
    else:
        return "🟢 Adequate"

df["status"] = df["gap"].apply(status)

# ----------------------------
# DISPLAY
# ----------------------------
st.subheader("📋 Summary Table")
st.dataframe(df)

# ----------------------------
# CHART
# ----------------------------
fig = px.bar(
    df,
    x="facility_type",
    y=["required_area", "existing_area"],
    barmode="group",
    title="Required vs Existing Area"
)

st.plotly_chart(fig)

# ----------------------------
# PRIORITY
# ----------------------------
st.subheader("🔥 Priority Facilities")
priority = df[df["gap"] > 0].sort_values(by="gap", ascending=False)

st.dataframe(priority)
