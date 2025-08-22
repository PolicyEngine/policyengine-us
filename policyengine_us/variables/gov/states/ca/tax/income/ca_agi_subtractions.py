from policyengine_us.model_api import *


class ca_agi_subtractions(Variable):
    value_type = float
    entity = TaxUnit
    label = "CA AGI subtractions from federal AGI"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ftb.ca.gov/forms/2021/2021-540-ca-instructions.html"
        "https://www.ftb.ca.gov/forms/2022/2022-540-ca-instructions.html"
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.agi
        total_subtractions = add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
