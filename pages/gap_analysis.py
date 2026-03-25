
import streamlit as st
import pandas as pd

st.title("Gap Analysis")

alloc = pd.read_csv("data/allocations.csv")
pop = pd.read_csv("data/population.csv")
std = pd.read_csv("data/standards.csv")

st.write("Allocations:", alloc)
st.write("Population:", pop)
st.write("Standards:", std)
