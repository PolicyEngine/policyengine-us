from policyengine_us.model_api import *
from numpy import ceil


class mn_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Minnesota exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.revenue.state.mn.us/sites/default/files/2021-12/m1_21_0.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-01/m1_inst_21.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2022-12/m1_22.pdf"
        "https://www.revenue.state.mn.us/sites/default/files/2023-03/m1_inst_22.pdf"
    )
    defined_for = StateCode.MN

    def formula(tax_unit, period, parameters):
        dependents = tax_unit("tax_unit_dependents", period)
        p = parameters(period).gov.states.mn.tax.income.exemptions
        exemptions = p.amount * dependents
        # limit exemptions if federal AGI is above a threshold
        agi = tax_unit("adjusted_gross_income", period)
        filing_status = tax_unit("filing_status", period)
        excess_agi = max_(0, agi - p.agi_threshold[filing_status])
        steps = ceil(excess_agi / p.agi_step_size[filing_status])
        offset_fraction = p.agi_step_fraction * steps
        offset = offset_fraction * exemptions
        return max_(0, exemptions - offset)
