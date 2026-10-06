from policyengine_us.model_api import *
from policyengine_us.tools.local_sales_tax_rates import (
    state_general_sales_tax_rates,
)


class local_sales_tax_rate(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = "/1"
    label = "Local general sales tax rate"
    documentation = (
        "The local general sales tax rate entered on line 3 of the IRS sales tax "
        "deduction worksheet: the part of the combined state and local rate above "
        "the state general sales tax rate, or 0 when the combined rate is not "
        "above it. The state rate comes from the official state rate files where "
        "PolicyEngine has them, and otherwise from the state table heading. The "
        "California and Nevada headings include their uniform local rates, and "
        "there line 3 is only the part of the combined rate above 7.25% or 6.85%. "
        "Enter the household's local rate to use it instead."
    )
    reference = (
        # State and Local General Sales Tax Deduction Worksheet, lines 3 and 4.
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=4",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=4",
        # Line 3 instructions (California and Nevada; rates changing in-year).
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=6",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=5",
    )

    def formula(household, period, parameters):
        p = parameters(period).gov.irs.deductions.itemized.salt_and_real_estate
        # Line 3 is the local rate: the combined rate less the state's general
        # rate. The table headings print that rate rounded (Minnesota's 6.875%
        # as 6.88% from 2023) or averaged over a mid-year change (South
        # Dakota's 4.35% for 2023), so where the official state files give the
        # state rate, use it, averaged over the days of the year as line 3
        # directs; elsewhere use the heading. The California and Nevada
        # headings include their uniform local rates (table footnotes 3 and
        # 5), and line 3 there is the part of the combined rate above them;
        # Nevada's state files fold its state rate into county rates, so it
        # takes its heading too.
        state = pd.Series(household("state_code_str", period)).astype(str)
        official = state.map(state_general_sales_tax_rates(period.start.year))
        heading_rate = p.state_sales_tax_table.rate[household("state_code", period)]
        state_rate = np.where(official.isna(), heading_rate, official.to_numpy())
        combined_rate = household("combined_sales_tax_rate", period)
        # The combined rate is stored in single precision, so subtract the
        # state rate at the same precision: equal rates then leave exactly 0.
        return max_(combined_rate - state_rate.astype(combined_rate.dtype), 0)
