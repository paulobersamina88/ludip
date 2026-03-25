import streamlit as st
import pandas as pd

st.set_page_config(page_title="TUP LUDIP Dashboard", layout="wide")

st.title("TUP LUDIP Dashboard - Phase 1")
st.caption("Campus space and infrastructure planning overview")

buildings = pd.read_csv("data/buildings.csv")
allocations = pd.read_csv("data/allocations.csv")
population = pd.read_csv("data/population.csv")

total_buildings = len(buildings)
total_gfa = buildings["total_gfa_sqm"].sum()
total_students = population["students"].sum()
total_people = population["students"].sum() + population["faculty"].sum() + population["staff"].sum()
total_allocated = allocations["area_sqm"].sum()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Buildings", total_buildings)
c2.metric("Total GFA (sqm)", f"{total_gfa:,.0f}")
c3.metric("Students", f"{total_students:,.0f}")
c4.metric("Allocated Area (sqm)", f"{total_allocated:,.0f}")

st.subheader("Building Inventory")
st.dataframe(buildings, use_container_width=True)

st.subheader("Facility Allocation Summary")
facility_summary = allocations.groupby("facility_type", as_index=False)["area_sqm"].sum()
st.dataframe(facility_summary, use_container_width=True)

st.subheader("Population Summary")
st.dataframe(population, use_container_width=True)
