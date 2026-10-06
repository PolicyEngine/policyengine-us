from policyengine_us.model_api import *


class local_sales_tax_rate(Variable):
    value_type = float
    entity = Household
    definition_period = YEAR
    unit = "/1"
    label = "Local general sales tax rate"
    documentation = (
        "The local general sales tax rate entered on line 3 of the IRS sales tax "
        "deduction worksheet: the part of the combined state and local rate above "
        "the state rate in the state's table heading, or 0 when the combined rate "
        "is not above it. The California and Nevada headings include their "
        "uniform local rates, so there it is the part of the combined rate above "
        "7.25% or 6.85%. Enter the household's local rate to use it instead."
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
        # Line 4: the state rate in the state table heading. The California and
        # Nevada headings include their uniform local rates (table footnotes 3
        # and 5); Alaska and the states without a state table have 0.
        heading_rate = p.state_sales_tax_table.rate[household("state_code", period)]
        combined_rate = household("combined_sales_tax_rate", period)
        # The combined rate is stored in single precision, so subtract the
        # heading rate at the same precision: equal rates then leave exactly 0.
        return max_(combined_rate - heading_rate.astype(combined_rate.dtype), 0)
