from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class tn_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Tennessee LIHEAP regular assistance"
    documentation = (
        "Tennessee's single annual regular award from the statewide benefit "
        "matrix, by household size group, income group and energy burden, "
        "applied as heating assistance from October through May and as "
        "cooling assistance from June through September (2026 Policy Manual "
        "page 35; the FY2026 plan's component dates are October 1 to April 30 "
        "for heating and May 1 to September 30 for cooling). Verified for "
        "FY2026 and FY2027 (the posted LI-12 matrix, with the FY2027 plan and "
        "manual in draft). Earlier years are unverified estimates: they "
        "backfill the FY2026 values and do not reproduce the priority-points "
        "matrix Tennessee used before FY2026. Crisis assistance and "
        "weatherization are out of scope."
    )
    defined_for = "tn_liheap_eligible"
    reference = (
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/2026-LIHEAP-Eligible-Income-Household-Size-Benefits.pdf",
        # PDF pages 1-4
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/2027-LIHEAP-LI-12-Eligible-Income-Benefit-Matrix.pdf#page=1",
        # PDF pages 12, 25, 31-32, 34-35
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/LIHEAP-2026-Policy-Manual-for-Tennessee.pdf#page=12",
        # PDF pages 4, 9
        "https://liheapch.acf.gov/docs/2026/state-plans/TN_Plan_2026.pdf#page=4",
        # PDF pages 28-31
        "https://dogvxws799i6n.cloudfront.net/wp-content/uploads/LIHEAP-26-Workshop-Powerpoint-09.16.25.pdf#page=28",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tn.thda.liheap
        income = spm_unit("tn_liheap_countable_income", period)
        energy_cost = spm_unit("tn_liheap_energy_cost", period)
        # Annual cost over annual income stands in for the 12-month average
        # energy cost over 30-day income. Heat included in the rent counts
        # only separately billed energy, so its column is a lower bound. The
        # ratio is computed in float64 so a burden printed at a column start
        # rounds onto that start.
        has_income = income > 0
        income_64 = income.astype(np.float64)
        burden = np.divide(
            energy_cost.astype(np.float64),
            income_64,
            out=np.zeros_like(income_64),
            where=has_income,
        )
        # Ordinary half-up rounding (the manual's example rounds 0.0878822197
        # to 8.79%), so a tie such as 0.12145 reaches the 0.1215 column start;
        # np.round would round it half to even, to 0.1214.
        scale = 10**p.payment.burden_decimals
        rounded_burden = np.floor(burden * scale + 0.5) / scale
        burden_column = p.payment.burden_column
        # Households with zero income receive the highest burden column.
        column = where(
            has_income,
            burden_column.calc(rounded_burden),
            burden_column.amounts[-1],
        )
        size = spm_unit("tn_liheap_household_size", period)
        size_group = p.payment.size_group.calc(size)
        p_group = p.payment.income_group
        if p_group.uses_fpg_rates:
            state_group = spm_unit.household("state_group_str", period)
            guideline = fpg(
                size,
                state_group,
                period,
                parameters,
                year_lag=p.eligibility.fpg_year_lag,
            )
            # The matrix prints the tops in cents. Rounding the rate-derived
            # tops to cents keeps an income at a printed top in that group
            # (size 3 group C: 26,650 x 1.17 is 31,180.4999... in floating
            # point, printed $31,180.50).
            tops = [np.round(guideline * p_group.fpg_rate[group], 2) for group in "ABC"]
        else:
            table_size = clip(size, 1, p_group.max_table_size)
            tops = [p_group.top[group][table_size] for group in "ABC"]
        # Income groups A-D are numbered 1-4; group D runs to the income
        # limit.
        income_group = 1
        for top in tops:
            income_group = income_group + (income > top)
        amount = p.payment.amount[size_group][income_group][column]
        # The FY2026 manual lets an applicant whose home uses propane as a
        # deliverable fuel apply a smaller benefit to propane at the minimum
        # payment (page 25). A household with propane heat or a propane bill
        # is assumed to take that option. A heat-in-rent benefit is paid on
        # the landlord's energy vendor account named on the LI-05 agreement,
        # so a rental heated with propane included in the rent takes it too.
        # No supplement or bill cap applies.
        heating_type = spm_unit("heating_type", period)
        propane_heat = heating_type == heating_type.possible_values.PROPANE
        propane_bill = spm_unit("bottled_gas_expense", period) > 0
        propane = propane_heat | propane_bill
        return where(propane, max_(amount, p.payment.propane_minimum), amount)
