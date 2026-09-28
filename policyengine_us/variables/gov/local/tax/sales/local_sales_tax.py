from policyengine_us.model_api import *


class local_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local sales tax"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sca--2022.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2024.pdf#page=4",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax_table
        state_code = tax_unit.household("state_code_str", period)
        # Full-year residents of these jurisdictions "skip lines 2 through 5,
        # enter -0- on line 6" of the worksheet.
        has_local_sales_tax = ~np.isin(state_code, p.no_local_sales_tax_states)
        # Elsewhere the worksheet uses the Optional Local Sales Tax Tables
        # (line 2) or the ratio of the local to the state rate (lines 3-5),
        # which need locality sales tax rates. Until those are modeled,
        # PolicyEngine approximates the local amount as 20% of the state
        # amount. This is not an IRS value.
        return has_local_sales_tax * tax_unit("state_sales_tax", period) * 0.2
