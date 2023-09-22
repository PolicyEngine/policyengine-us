import streamlit as st

st.set_page_config(layout="wide")

st.title("PUF imputation")

import pandas as pd
import numpy as np

puf = pd.read_csv("~/Downloads/puf_2015.csv")
demographics = pd.read_csv("~/Downloads/demographics_2015.csv")

# Variables to match on without demographics:
# - Filing status
# - Adult dependents

from policyengine_us import Microsimulation

simulation = Microsimulation()

cps_data = simulation.calculate_dataframe(
    [
        # Variables to match on.
        "filing_status",
        "tax_unit_count_dependents",
        "tax_unit_children",
        "people",
    ]
)

# Apply renames as computations.
# Exemptions: The IRS caps at 3 per type in the PUF.
EXEMPTION_CAP = 3
# XOCAH: Exemptions for Children Living at Home
cps_data["XOCAH"] = np.minimum(cps_data.tax_unit_children, EXEMPTION_CAP)

# XOODEP: Exemptions for Other Dependents.
cps_data["XOODEP"] = np.minimum(
    cps_data.tax_unit_count_dependents - cps_data.tax_unit_children,
    EXEMPTION_CAP,
)

RENAMES = dict(
    filing_status={
        "SINGLE": 1,
        "JOINT": 2,
        "WIDOW": 2,
        "SEPARATE": 3,
        "HEAD_OF_HOUSEHOLD": 4,
    }
)

cps_data["MARS"] = cps_data.filing_status.replace(RENAMES["filing_status"])

cps_data["XTOT"] = cps_data.people

cps_data = cps_data[["MARS", "XOCAH", "XOODEP"]]

INPUT_VARIABLES = ["MARS", "XOCAH", "XOODEP"]

OUTPUT_VARIABLES = [
    "E00200",  # Salaries and wages
    "E00300",  # Interest received
    "E00400",  # Tax-exempt interest income
    "E00600",  # Dividends included in AGI
    "E00650",  # Qualified Dividends
    "E00700",  # State income tax refunds
    "E00800",  # Alimony received
    "E00900",  # Business or profession (Schedule C) net profit/loss (+/-)
    "E01000",  # Net capital gain or loss (+/-)
    "E01100",  # Capital gain distributions reported on Form 1040
    "E01200",  # Other gains (or loss) (+/-)
    "E01400",  # Taxable IRA distribution
    "E01500",  # Total pensions and annuities received
    "E01700",  # Pensions and annuities included in AGI
    "E02000",  # Schedule E net income or loss (+/-)
    "E02100",  # Schedule F net profit/loss (+/-)
    "E02300",  # Unemployment compensation in AGI
    "E02400",  # Gross Social Security benefits
    "E02500",  # Social Security benefits in AGI
]

puf_data = puf[INPUT_VARIABLES + OUTPUT_VARIABLES]

puf_data = puf_data[puf_data.MARS != 0]

st.subheader("Training data")

with st.expander("PUF training data"):
    st.dataframe(puf_data)

with st.expander("CPS data in PUF format for imputation"):
    st.dataframe(cps_data)

from survey_enhance import Imputation


@st.cache_resource
def load_model():
    IMPUTE = False

    if IMPUTE:
        income = Imputation()
        income.train(
            puf_data[INPUT_VARIABLES],
            puf_data[OUTPUT_VARIABLES],
            num_trees=100,
        )
        income.save("income.pkl")
    else:
        income = Imputation.load("income.pkl")

    return income


income = load_model()

# cps_imputation_predictions = income.predict(cps_data[INPUT_VARIABLES])

# imputed_cps = pd.concat([cps_data.copy(), cps_imputation_predictions], axis=1)

st.subheader("Household estimator")

col1, col2 = st.columns(2)

with col1:
    mars = st.selectbox(
        "MARS", ["SINGLE", "JOINT", "WIDOW", "SEPARATE", "HEAD_OF_HOUSEHOLD"]
    )
    child_dependents = st.number_input(
        "Child dependents", min_value=0, max_value=10, value=0
    )
    adult_dependents = st.number_input(
        "Adult dependents", min_value=0, max_value=10, value=0
    )


def get_predictions(input_data, num_predictions):
    predictions = []
    for step in range(num_predictions):
        predictions.append(income.predict(input_data))

    prediction_df = pd.concat(predictions)
    return prediction_df


with col2:
    mars = RENAMES["filing_status"][mars]

    progress_bar = st.progress(0)
    prediction_df = get_predictions(
        [[mars, child_dependents, adult_dependents]], 100
    )

    import plotly.express as px

    variable = st.selectbox("Variable", OUTPUT_VARIABLES)

    distribution = px.histogram(
        prediction_df[variable], nbins=300
    ).update_layout(
        title=f"{variable} distribution",
        xaxis_title=variable,
        yaxis_title="Count",
        xaxis_tickformat="$",
        showlegend=False,
    )

    st.plotly_chart(distribution)
