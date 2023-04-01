from policyengine_us.model_api import *


class mn_exemptions_count(Variable):
    value_type = float
    entity = TaxUnit
    label = "number of Minnesota exemptions"
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
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        joint = filing_status == statuses.JOINT
        hoh = filing_status == statuses.HEAD_OF_HOUSEHOLD
        adults = where(joint | hoh, 2, 1)
        dependents = tax_unit("tax_unit_dependents", period)
        return adults + dependents
