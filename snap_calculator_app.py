#!/usr/bin/env python3
"""
SNAP Benefits Calculator - Streamlit App
A simple web interface for calculating SNAP benefits using PolicyEngine US
"""

import streamlit as st
from policyengine_us import Simulation
import numpy as np

# Set page config
st.set_page_config(
    page_title="SNAP Benefits Calculator", page_icon="🍽️", layout="wide"
)

# Title and description
st.title("🍽️ SNAP Benefits Calculator")
st.markdown(
    """
Calculate your estimated SNAP (food stamps) benefits using PolicyEngine US.
This calculator uses federal SNAP rules and state-specific variations.
"""
)

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.header("Household Information")

    # State selection
    state = st.selectbox(
        "State",
        options=[
            "AL",
            "AK",
            "AZ",
            "AR",
            "CA",
            "CO",
            "CT",
            "DE",
            "FL",
            "GA",
            "HI",
            "ID",
            "IL",
            "IN",
            "IA",
            "KS",
            "KY",
            "LA",
            "ME",
            "MD",
            "MA",
            "MI",
            "MN",
            "MS",
            "MO",
            "MT",
            "NE",
            "NV",
            "NH",
            "NJ",
            "NM",
            "NY",
            "NC",
            "ND",
            "OH",
            "OK",
            "OR",
            "PA",
            "RI",
            "SC",
            "SD",
            "TN",
            "TX",
            "UT",
            "VT",
            "VA",
            "WA",
            "WV",
            "WI",
            "WY",
            "DC",
        ],
        index=4,  # Default to CA
    )

    # Household composition
    st.subheader("Household Members")
    num_adults = st.number_input(
        "Number of adults", min_value=1, max_value=10, value=1
    )
    num_children = st.number_input(
        "Number of children", min_value=0, max_value=10, value=2
    )

    # Age inputs
    if num_adults > 0:
        st.markdown("**Adult Ages**")
        adult_ages = []
        for i in range(num_adults):
            age = st.number_input(
                f"Adult {i+1} age",
                min_value=18,
                max_value=100,
                value=35,
                key=f"adult_age_{i}",
            )
            adult_ages.append(age)

    if num_children > 0:
        st.markdown("**Child Ages**")
        child_ages = []
        for i in range(num_children):
            age = st.number_input(
                f"Child {i+1} age",
                min_value=0,
                max_value=17,
                value=10 - i * 2,
                key=f"child_age_{i}",
            )
            child_ages.append(age)

with col2:
    st.header("Income & Expenses")

    # Income
    st.subheader("Monthly Income")
    employment_income = st.number_input(
        "Employment income ($/month)",
        min_value=0,
        max_value=10000,
        value=2000,
        step=100,
        help="Total monthly wages and salaries before taxes",
    )

    self_employment_income = st.number_input(
        "Self-employment income ($/month)",
        min_value=0,
        max_value=10000,
        value=0,
        step=100,
        help="Net income from self-employment",
    )

    unemployment_income = st.number_input(
        "Unemployment benefits ($/month)",
        min_value=0,
        max_value=5000,
        value=0,
        step=50,
        help="Monthly unemployment insurance benefits",
    )

    social_security = st.number_input(
        "Social Security ($/month)",
        min_value=0,
        max_value=5000,
        value=0,
        step=50,
        help="Monthly Social Security benefits",
    )

    # Expenses
    st.subheader("Monthly Expenses")
    rent = st.number_input(
        "Rent or mortgage ($/month)",
        min_value=0,
        max_value=5000,
        value=1200,
        step=50,
        help="Monthly housing payment",
    )

    childcare = st.number_input(
        "Childcare expenses ($/month)",
        min_value=0,
        max_value=2000,
        value=200 if num_children > 0 else 0,
        step=50,
        help="Monthly childcare costs for work or training",
    )

    child_support = st.number_input(
        "Child support payments ($/month)",
        min_value=0,
        max_value=2000,
        value=0,
        step=50,
        help="Court-ordered child support you pay",
    )

    # Utility expenses
    st.subheader("Utilities")
    has_heating_cooling = st.checkbox("Pays for heating/cooling", value=True)
    has_electricity = st.checkbox(
        "Pays for electricity separately", value=True
    )
    has_gas = st.checkbox("Pays for gas separately", value=False)
    has_phone = st.checkbox("Pays for phone", value=True)
    has_water_sewer = st.checkbox("Pays for water/sewer", value=True)

# Calculate button
if st.button("Calculate SNAP Benefits", type="primary"):
    with st.spinner("Calculating..."):
        # Build the situation dictionary
        people = {}

        # Add adults
        for i in range(num_adults):
            person_id = f"adult_{i}"
            people[person_id] = {
                "age": adult_ages[i] if num_adults > 0 else 35,
            }
            # Add income to first adult
            if i == 0:
                people[person_id]["employment_income"] = employment_income * 12
                people[person_id]["self_employment_income"] = (
                    self_employment_income * 12
                )
                people[person_id]["unemployment_compensation"] = (
                    unemployment_income * 12
                )
                people[person_id]["social_security"] = social_security * 12
                people[person_id]["child_support_expense"] = child_support * 12
                people[person_id]["rent"] = rent * 12

        # Add children
        for i in range(num_children):
            person_id = f"child_{i}"
            people[person_id] = {
                "age": child_ages[i] if num_children > 0 else 10,
            }

        # Create member list
        members = list(people.keys())

        # Build situation
        situation = {
            "people": people,
            "spm_units": {
                "spm_unit": {
                    "members": members,
                    "childcare_expenses": childcare * 12,
                    "heating_cooling_expense": (
                        50 * 12 if has_heating_cooling else 0
                    ),
                    "electricity_expense": 30 * 12 if has_electricity else 0,
                    "gas_expense": 20 * 12 if has_gas else 0,
                    "phone_expense": 35 * 12 if has_phone else 0,
                    "water_expense": 25 * 12 if has_water_sewer else 0,
                    "sewage_expense": 25 * 12 if has_water_sewer else 0,
                }
            },
            "households": {
                "household": {
                    "members": members,
                    "state_code": state,
                }
            },
            "tax_units": {
                "tax_unit": {
                    "members": members,
                }
            },
        }

        try:
            # Create simulation
            sim = Simulation(situation=situation)
            period = "2024-01"

            # Calculate SNAP benefits
            snap_benefit = sim.calculate("snap", period)
            is_eligible = sim.calculate("is_snap_eligible", period)

            # Get additional details
            snap_gross_income = sim.calculate("snap_gross_income", period)
            snap_net_income = sim.calculate("snap_net_income", period)
            snap_deductions = sim.calculate("snap_deductions", period)
            snap_fpg = sim.calculate("snap_fpg", period)
            max_allotment = sim.calculate("snap_max_allotment", period)
            expected_contribution = sim.calculate(
                "snap_expected_contribution", period
            )

            # Get eligibility test results
            meets_gross = sim.calculate("meets_snap_gross_income_test", period)
            meets_net = sim.calculate("meets_snap_net_income_test", period)
            meets_asset = sim.calculate("meets_snap_asset_test", period)

            # Display results
            st.divider()

            # Main result box
            if is_eligible[0]:
                st.success(f"### ✅ Eligible for SNAP Benefits")
                col_res1, col_res2, col_res3 = st.columns(3)
                with col_res1:
                    st.metric(
                        "Monthly SNAP Benefit", f"${snap_benefit[0]:,.0f}"
                    )
                with col_res2:
                    st.metric(
                        "Annual SNAP Benefit", f"${snap_benefit[0] * 12:,.0f}"
                    )
                with col_res3:
                    st.metric(
                        "Max Possible Benefit", f"${max_allotment[0]:,.0f}"
                    )
            else:
                st.error("### ❌ Not Eligible for SNAP Benefits")
                st.write(
                    "Your household does not meet the eligibility requirements."
                )

            # Detailed breakdown
            with st.expander("View Detailed Calculation"):
                col_det1, col_det2 = st.columns(2)

                with col_det1:
                    st.markdown("#### Eligibility Tests")
                    st.write(
                        f"• Gross Income Test: {'✅ Pass' if meets_gross[0] else '❌ Fail'}"
                    )
                    st.write(
                        f"• Net Income Test: {'✅ Pass' if meets_net[0] else '❌ Fail'}"
                    )
                    st.write(
                        f"• Asset Test: {'✅ Pass' if meets_asset[0] else '❌ Fail'}"
                    )

                    st.markdown("#### Income Calculation")
                    st.write(
                        f"• Gross Income: ${snap_gross_income[0]:,.0f}/month"
                    )
                    st.write(
                        f"• Total Deductions: ${snap_deductions[0]:,.0f}/month"
                    )
                    st.write(f"• Net Income: ${snap_net_income[0]:,.0f}/month")

                with col_det2:
                    st.markdown("#### Poverty Guidelines")
                    st.write(
                        f"• Federal Poverty Guideline: ${snap_fpg[0]:,.0f}/month"
                    )
                    st.write(
                        f"• Gross Income Limit (130% FPG): ${snap_fpg[0] * 1.3:,.0f}/month"
                    )
                    st.write(
                        f"• Net Income Limit (100% FPG): ${snap_fpg[0]:,.0f}/month"
                    )

                    if is_eligible[0]:
                        st.markdown("#### Benefit Calculation")
                        st.write(f"• Max Allotment: ${max_allotment[0]:,.0f}")
                        st.write(
                            f"• Expected Contribution: ${expected_contribution[0]:,.0f}"
                        )
                        st.write(f"• Final Benefit: ${snap_benefit[0]:,.0f}")

        except Exception as e:
            st.error(f"Error calculating benefits: {str(e)}")
            st.info("Please check your inputs and try again.")

# Add information section
with st.sidebar:
    st.header("ℹ️ About SNAP")
    st.markdown(
        """
    **SNAP** (Supplemental Nutrition Assistance Program), formerly known as food stamps,
    helps low-income individuals and families buy food.

    **Eligibility is based on:**
    - Household size and composition
    - Income (gross and net)
    - Assets (in some cases)
    - Work requirements

    **This calculator:**
    - Uses PolicyEngine US for calculations
    - Follows federal SNAP rules
    - Includes state-specific variations
    - Provides estimates only

    **Note:** This is an estimate. Actual benefits may vary.
    Apply through your state's SNAP office for official determination.
    """
    )

    st.divider()
    st.caption("Powered by PolicyEngine US")
