from policyengine_us.model_api import *


class local_sales_tax(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    label = "Local sales tax"
    unit = USD
    reference = (
        "https://www.irs.gov/pub/irs-prior/i1040sca--2023.pdf#page=5",
        "https://www.irs.gov/pub/irs-prior/i1040sca--2025.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.irs.deductions.itemized.salt_and_real_estate.state_sales_tax_table
        state_code = tax_unit.household("state_code_str", period)
        # The worksheet enters -0- on line 6 in states without a local
        # general sales tax.
        has_local_sales_tax = ~np.isin(state_code, p.no_local_sales_tax_states)
        # Until modeling the local sales tax table, estimate by multiplying by 0.2.
        return has_local_sales_tax * tax_unit("state_sales_tax", period) * 0.2
