import streamlit as st

st.title("CPS calibration explorer")

import pandas as pd
import plotly.express as px

df = pd.read_csv("training_log.csv.gz", compression="gzip").drop(columns=["Unnamed: 0"])
df["error"] = df.value - df.target
df["relative_error"] = df.value / df.target - 1

metric = st.selectbox("Select a metric", df.name.unique())

comparison_type = st.selectbox("Select a comparison", [
    "Absolute against target",
    "Relative against target",
    "Error relative change",
])

def add_target_line(fig, target):
    # Add dashed horizontal line at target
    fig.add_shape(
        type="line",
        x0=0, #paper
        y0=target,
        x1=1,
        y1=target,
        line=dict(
            color="gray",
            dash="dash",
        ),
        xref="paper",
        yref="y",
    )
    return fig

if comparison_type == "Absolute against target":
    fig = px.line(df[df.name == metric], x="epoch", y="value", title=metric).update_layout(
        yaxis_range=[0, df[df.name == metric].target.iloc[0] * 2],
    )
    target = df[df.name == metric].target.iloc[0]
    # Add dashed horizontal line at target
    fig = add_target_line(fig, target)
    st.plotly_chart(fig)
elif comparison_type == "Relative against target":
    fig = px.line(
        df[df.name == metric],
        x="epoch",
        y="relative_error",
        title=metric,
    ).update_layout(
        yaxis_tickformat="+.0%",
        yaxis_range=[-1, 1],
    )
    fig = add_target_line(fig, 0)
    st.plotly_chart(fig)
elif comparison_type == "Error relative change":
    error_at_start = df[df.name == metric].sort_values("epoch").error.iloc[0]
    error_at_epoch = df[df.name == metric].error / error_at_start - 1
    error_df = pd.DataFrame({
        "epoch": df[df.name == metric].epoch.values,
        "error_relative_change": error_at_epoch.values,
    })
    fig = px.line(
        error_df,
        x="epoch",
        y=["error_relative_change"],
        title=metric,
    ).update_layout(
        yaxis_tickformat="+.0%",
        yaxis_range=[-1, 1],
    )
    fig = add_target_line(fig, 0)
    st.plotly_chart(fig)

st.dataframe(df)