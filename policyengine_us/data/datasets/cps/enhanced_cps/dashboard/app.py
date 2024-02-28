import pandas as pd
import plotly.express as px
from policyengine_core.charts import *
import streamlit as st
import numpy as np
from policyengine_us.data.storage import STORAGE_FOLDER

st.set_page_config(layout="wide")

st.title("PolicyEngine US microdata dashboard")

df = pd.read_csv(STORAGE_FOLDER / "dataset_losses.csv.gz")

df["abs_rel_error"] = (df.value / df.target - 1).abs()

left, right = st.columns(2)
with left:
    metric = st.selectbox("Metric", df.name.unique())
with right:
    time_period = st.selectbox("Time period", df.time_period.unique())

df.dataset = df.dataset.replace(
    {
        "cps_2023": "CPS (2022)",
        "enhanced_cps_2023": "Enhanced CPS",
        "puf_2023": "PUF (2015)",
    }
)


def capitalise(string):
    return string[0].upper() + string[1:]


fig = px.bar(
    df[(df.name == metric) & (df.time_period == time_period)],
    x="dataset",
    y="value",
    color="dataset",
    title=f"{capitalise(metric)} in {time_period}",
    color_discrete_map={
        "CPS (2022)": DARK_GRAY,
        "Enhanced CPS": BLUE,
        "PUF (2015)": GRAY,
    },
).update_layout(
    yaxis_title="Absolute relative error",
    xaxis_title="Dataset",
    showlegend=False,
)

# Add dotted line for truth

true_value = df[
    (df.name == metric) & (df.time_period == time_period)
].target.mean()
fig.add_shape(
    type="line",
    x0=-0.5,
    y0=true_value,
    x1=2.5,
    y1=true_value,
    line=dict(
        color=MEDIUM_DARK_GRAY,
        width=3,
        dash="dash",
    ),
)

st.plotly_chart(format_fig(fig), use_container_width=True)

st.dataframe(df, use_container_width=True)
