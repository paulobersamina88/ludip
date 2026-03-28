import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="TUP LUDIP Dashboard", layout="wide")

# =========================================================
# HELPERS
# =========================================================
def safe_div(a, b):
    return np.where(b == 0, 0, a / b)

def classify_status(deficit):
    if deficit > 0:
        return "Deficit"
    elif deficit < 0:
        return "Surplus"
    return "Balanced"

def compliance_pct(future_area, required_area):
    if required_area <= 0:
        return 100.0
    return min((future_area / required_area) * 100, 999.0)

# =========================================================
# DEFAULT DATA
# =========================================================
default_facility_data = pd.DataFrame([
    {
        "facility_type": "Classrooms",
        "existing_floor_area_sqm": 1200.0,
        "population": 800,
        "proposed_floor_area_sqm": 600.0,
        "number_of_floors": 3,
        "standard_sqm_per_person": 1.50,
    },
    {
        "facility_type": "Laboratories",
        "existing_floor_area_sqm": 500.0,
        "population": 400,
        "proposed_floor_area_sqm": 300.0,
        "number_of_floors": 2,
        "standard_sqm_per_person": 2.00,
    },
    {
        "facility_type": "Library",
        "existing_floor_area_sqm": 250.0,
        "population": 800,
        "proposed_floor_area_sqm": 250.0,
        "number_of_floors": 2,
        "standard_sqm_per_person": 0.30,
    },
    {
        "facility_type": "Admin",
        "existing_floor_area_sqm": 400.0,
        "population": 100,
        "proposed_floor_area_sqm": 100.0,
        "number_of_floors": 1,
        "standard_sqm_per_person": 6.00,
    },
    {
        "facility_type": "Faculty Room",
        "existing_floor_area_sqm": 180.0,
        "population": 80,
        "proposed_floor_area_sqm": 120.0,
        "number_of_floors": 1,
        "standard_sqm_per_person": 4.00,
    },
])

default_buildings = pd.DataFrame([
    {
        "building_name": "IT Building",
        "existing_gfa_sqm": 2500.0,
        "proposed_additional_gfa_sqm": 500.0,
        "floors": 5,
        "college_owner": "IT",
    },
    {
        "building_name": "Admin Building",
        "existing_gfa_sqm": 900.0,
        "proposed_additional_gfa_sqm": 300.0,
        "floors": 3,
        "college_owner": "Admin",
    },
])

# =========================================================
# SESSION STATE
# =========================================================
if "facility_df" not in st.session_state:
    st.session_state.facility_df = default_facility_data.copy()

if "buildings_df" not in st.session_state:
    st.session_state.buildings_df = default_buildings.copy()

# =========================================================
# TITLE
# =========================================================
st.title("TUP LUDIP Dashboard - Dynamic Planning")
st.caption("Interactive campus space planning, deficit analysis, and visual monitoring for TUP Manila")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("Dashboard Controls")

campus_name = st.sidebar.text_input("Campus", value="TUP Manila")
planning_horizon = st.sidebar.selectbox("Planning Horizon", ["Current", "Short Term", "Medium Term", "Long Term"], index=1)
show_only_deficit = st.sidebar.checkbox("Show deficit items only", value=False)
show_labels = st.sidebar.checkbox("Show chart labels", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("Quick Actions")

if st.sidebar.button("Reset sample data"):
    st.session_state.facility_df = default_facility_data.copy()
    st.session_state.buildings_df = default_buildings.copy()
    st.rerun()

# =========================================================
# TABS
# =========================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Facility Planning Input",
    "Building Inventory",
    "Gap Analysis Visuals"
])

# =========================================================
# TAB 1: OVERVIEW
# =========================================================
with tab1:
    st.subheader(f"{campus_name} - Planning Overview")

    # Editable building data
    buildings_df = st.session_state.buildings_df.copy()
    buildings_df["future_gfa_sqm"] = buildings_df["existing_gfa_sqm"] + buildings_df["proposed_additional_gfa_sqm"]

    # Editable facility data
    facility_df = st.session_state.facility_df.copy()
    facility_df["required_floor_area_sqm"] = facility_df["population"] * facility_df["standard_sqm_per_person"]
    facility_df["future_added_area_sqm"] = facility_df["proposed_floor_area_sqm"] * facility_df["number_of_floors"]
    facility_df["future_total_area_sqm"] = facility_df["existing_floor_area_sqm"] + facility_df["future_added_area_sqm"]
    facility_df["deficit_sqm"] = facility_df["required_floor_area_sqm"] - facility_df["future_total_area_sqm"]
    facility_df["surplus_sqm"] = facility_df["future_total_area_sqm"] - facility_df["required_floor_area_sqm"]
    facility_df["compliance_pct"] = facility_df.apply(
        lambda row: compliance_pct(row["future_total_area_sqm"], row["required_floor_area_sqm"]), axis=1
    )
    facility_df["status"] = facility_df["deficit_sqm"].apply(classify_status)

    total_buildings = len(buildings_df)
    total_existing_gfa = buildings_df["existing_gfa_sqm"].sum()
    total_future_gfa = buildings_df["future_gfa_sqm"].sum()
    total_population = facility_df["population"].sum()
    total_required = facility_df["required_floor_area_sqm"].sum()
    total_existing = facility_df["existing_floor_area_sqm"].sum()
    total_future = facility_df["future_total_area_sqm"].sum()
    total_deficit = max(total_required - total_future, 0)
    overall_compliance = 100 if total_required == 0 else (total_future / total_required) * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Buildings", f"{total_buildings}")
    c2.metric("Existing GFA (sqm)", f"{total_existing_gfa:,.0f}")
    c3.metric("Future GFA (sqm)", f"{total_future_gfa:,.0f}")
    c4.metric("Total Population", f"{total_population:,.0f}")
    c5.metric("Required Area (sqm)", f"{total_required:,.0f}")
    c6.metric("Overall Compliance", f"{overall_compliance:,.1f}%")

    c7, c8, c9 = st.columns(3)
    c7.metric("Existing Functional Area (sqm)", f"{total_existing:,.0f}")
    c8.metric("Future Functional Area (sqm)", f"{total_future:,.0f}")
    c9.metric("Remaining Deficit (sqm)", f"{total_deficit:,.0f}")

    st.markdown("### LUDIP Motivation Tracker")
    progress_value = float(min(overall_compliance, 100.0)) / 100.0
    st.progress(progress_value, text=f"Campus planning compliance progress: {min(overall_compliance, 100.0):.1f}%")

    if overall_compliance < 60:
        st.warning("Campus area provision is still significantly below the required standard. More space programming is needed.")
    elif overall_compliance < 90:
        st.info("Campus planning is improving, but several facilities still have notable deficits.")
    else:
        st.success("Campus planning is approaching or exceeding the required standards for many facilities.")

# =========================================================
# TAB 2: FACILITY PLANNING INPUT
# =========================================================
with tab2:
    st.subheader("Dynamic Facility Planning Input")
    st.caption("Add rows, revise standards, and let the dashboard compute required area and deficits automatically.")

    edited_facility_df = st.data_editor(
        st.session_state.facility_df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "facility_type": st.column_config.TextColumn("Facility Type", required=True),
            "existing_floor_area_sqm": st.column_config.NumberColumn("Existing Floor Area (sqm)", min_value=0.0, step=10.0),
            "population": st.column_config.NumberColumn("Population Served", min_value=0, step=10),
            "proposed_floor_area_sqm": st.column_config.NumberColumn("Proposed Floor Area / Floor (sqm)", min_value=0.0, step=10.0),
            "number_of_floors": st.column_config.NumberColumn("No. of Floors", min_value=0, step=1),
            "standard_sqm_per_person": st.column_config.NumberColumn("Standard (sqm/person)", min_value=0.0, step=0.1, format="%.2f"),
        }
    )

    st.session_state.facility_df = edited_facility_df.copy()

    calc_df = edited_facility_df.copy()
    calc_df["required_floor_area_sqm"] = calc_df["population"] * calc_df["standard_sqm_per_person"]
    calc_df["future_added_area_sqm"] = calc_df["proposed_floor_area_sqm"] * calc_df["number_of_floors"]
    calc_df["future_total_area_sqm"] = calc_df["existing_floor_area_sqm"] + calc_df["future_added_area_sqm"]
    calc_df["deficit_sqm"] = calc_df["required_floor_area_sqm"] - calc_df["future_total_area_sqm"]
    calc_df["surplus_sqm"] = calc_df["future_total_area_sqm"] - calc_df["required_floor_area_sqm"]
    calc_df["compliance_pct"] = calc_df.apply(
        lambda row: compliance_pct(row["future_total_area_sqm"], row["required_floor_area_sqm"]), axis=1
    )
    calc_df["status"] = calc_df["deficit_sqm"].apply(classify_status)

    if show_only_deficit:
        display_df = calc_df[calc_df["deficit_sqm"] > 0].copy()
    else:
        display_df = calc_df.copy()

    st.markdown("### Computed Requirements and Deficits")
    st.dataframe(
        display_df[[
            "facility_type",
            "population",
            "existing_floor_area_sqm",
            "proposed_floor_area_sqm",
            "number_of_floors",
            "standard_sqm_per_person",
            "required_floor_area_sqm",
            "future_total_area_sqm",
            "deficit_sqm",
            "compliance_pct",
            "status",
        ]],
        use_container_width=True,
        hide_index=True
    )

    csv = calc_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download computed facility table as CSV",
        data=csv,
        file_name="tup_ludip_facility_gap_analysis.csv",
        mime="text/csv"
    )

# =========================================================
# TAB 3: BUILDING INVENTORY
# =========================================================
with tab3:
    st.subheader("Dynamic Building Inventory")
    st.caption("Track building-level GFA and proposed future expansion.")

    edited_buildings_df = st.data_editor(
        st.session_state.buildings_df,
        use_container_width=True,
        num_rows="dynamic",
        hide_index=True,
        column_config={
            "building_name": st.column_config.TextColumn("Building Name", required=True),
            "existing_gfa_sqm": st.column_config.NumberColumn("Existing GFA (sqm)", min_value=0.0, step=10.0),
            "proposed_additional_gfa_sqm": st.column_config.NumberColumn("Proposed Additional GFA (sqm)", min_value=0.0, step=10.0),
            "floors": st.column_config.NumberColumn("Floors", min_value=1, step=1),
            "college_owner": st.column_config.TextColumn("College/Unit Owner"),
        }
    )

    st.session_state.buildings_df = edited_buildings_df.copy()

    building_view = edited_buildings_df.copy()
    building_view["future_gfa_sqm"] = building_view["existing_gfa_sqm"] + building_view["proposed_additional_gfa_sqm"]

    st.dataframe(building_view, use_container_width=True, hide_index=True)

# =========================================================
# TAB 4: GAP ANALYSIS VISUALS
# =========================================================
with tab4:
    st.subheader("Gap Analysis Visuals")

    visual_df = st.session_state.facility_df.copy()
    visual_df["required_floor_area_sqm"] = visual_df["population"] * visual_df["standard_sqm_per_person"]
    visual_df["future_added_area_sqm"] = visual_df["proposed_floor_area_sqm"] * visual_df["number_of_floors"]
    visual_df["future_total_area_sqm"] = visual_df["existing_floor_area_sqm"] + visual_df["future_added_area_sqm"]
    visual_df["deficit_sqm"] = visual_df["required_floor_area_sqm"] - visual_df["future_total_area_sqm"]
    visual_df["status"] = visual_df["deficit_sqm"].apply(classify_status)
    visual_df["compliance_pct"] = visual_df.apply(
        lambda row: compliance_pct(row["future_total_area_sqm"], row["required_floor_area_sqm"]), axis=1
    )

    if show_only_deficit:
        visual_df = visual_df[visual_df["deficit_sqm"] > 0].copy()

    col1, col2 = st.columns(2)

    with col1:
        chart1 = alt.Chart(visual_df).transform_fold(
            ["existing_floor_area_sqm", "future_total_area_sqm", "required_floor_area_sqm"],
            as_=["Area Type", "Area (sqm)"]
        ).mark_bar().encode(
            x=alt.X("facility_type:N", title="Facility Type"),
            y=alt.Y("Area (sqm):Q"),
            color=alt.Color("Area Type:N"),
            tooltip=["facility_type", "Area Type", "Area (sqm)"]
        ).properties(
            title="Existing vs Future vs Required Area",
            height=420
        )
        st.altair_chart(chart1, use_container_width=True)

    with col2:
        chart2 = alt.Chart(visual_df).mark_bar().encode(
            x=alt.X("facility_type:N", title="Facility Type"),
            y=alt.Y("deficit_sqm:Q", title="Deficit (sqm)"),
            color=alt.condition(
                alt.datum.deficit_sqm > 0,
                alt.value("#d62728"),
                alt.value("#2ca02c")
            ),
            tooltip=["facility_type", "deficit_sqm", "status"]
        ).properties(
            title="Facility Deficit / Surplus",
            height=420
        )
        st.altair_chart(chart2, use_container_width=True)

    st.markdown("### Compliance by Facility")

    compliance_chart = alt.Chart(visual_df).mark_bar().encode(
        x=alt.X("facility_type:N", title="Facility Type"),
        y=alt.Y("compliance_pct:Q", title="Compliance (%)"),
        tooltip=["facility_type", alt.Tooltip("compliance_pct:Q", format=".1f")]
    ).properties(
        height=420
    )

    if show_labels:
        text = alt.Chart(visual_df).mark_text(
            dy=-10
        ).encode(
            x="facility_type:N",
            y="compliance_pct:Q",
            text=alt.Text("compliance_pct:Q", format=".1f")
        )
        st.altair_chart(compliance_chart + text, use_container_width=True)
    else:
        st.altair_chart(compliance_chart, use_container_width=True)

    st.markdown("### Priority Facilities for LUDIP Completion")
    priority_df = visual_df.sort_values("deficit_sqm", ascending=False).copy()
    st.dataframe(
        priority_df[[
            "facility_type",
            "required_floor_area_sqm",
            "future_total_area_sqm",
            "deficit_sqm",
            "compliance_pct",
            "status"
        ]],
        use_container_width=True,
        hide_index=True
    )
